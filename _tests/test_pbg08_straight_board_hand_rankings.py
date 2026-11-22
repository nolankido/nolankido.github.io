"""PBG-08: two native straight-board outcomes and preserved viewer-guide contracts.

The card evaluator checks this exact teaching fixture independently of its
written answer. It is not a poker solver or at-table strategy tool.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import poker_library

HAND_SOURCE = " _source/poker/hand-rankings.html".strip()
HAND_PUBLIC = "poker/hand-rankings/index.html"
BASICS_SOURCE = "_source/poker/holdem-basics.html"
BASICS_PUBLIC = "poker/holdem-basics/index.html"
ANCHOR = "board-straight-check"
HREF = "/poker/hand-rankings/#board-straight-check"
RANKS = "23456789TJQKA"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def question_block(html: str) -> str:
    pattern = (r'<aside class="viewer-example" id="' + ANCHOR +
               r'"[\s\S]*?</aside>')
    matches = re.findall(pattern, html)
    if len(matches) != 1:
        raise ValueError("One standalone board-straight exercise is required")
    return matches[0]


def attrs(block: str) -> dict[str, str]:
    opening = block.split(">", 1)[0] + ">"
    return dict(re.findall(r'([\w-]+)="([^"]*)"', opening))


def straight_high(cards: list[str]) -> int:
    """Calculate a straight's highest card from seven card codes."""
    rank_set = {RANKS.index(card[0]) + 2 for card in cards}
    if 14 in rank_set:
        rank_set.add(1)
    return max((highest for highest in range(5, 15)
                if all(x in rank_set for x in range(highest - 4, highest + 1))),
               default=0)


def results(block: str) -> tuple[int, int, int]:
    a = attrs(block)
    board = a["data-board"].split()
    hero = a["data-a"].split()
    original = a["data-b"].split()
    variant = a["data-b-variant"].split()
    for second in (original, variant):
        nine = board + hero + second
        if len(nine) != 9 or len(set(nine)) != 9:
            raise ValueError("Repeated physical card or wrong card count")
        for hand in (hero, second):
            cards = board + hand
            if max(Counter(card[-1] for card in cards).values()) >= 5:
                raise ValueError("Unexpected flush overrides straight comparison")
            if len({card[0] for card in cards}) != 7:
                raise ValueError("Unexpected pair overrides unique straight ranks")
    return (straight_high(board + hero),
            straight_high(board + original),
            straight_high(board + variant))


def audit_errors(html: str) -> list[str]:
    errors = []
    try:
        block = question_block(html)
        scores = results(block)
    except (ValueError, KeyError, IndexError) as exc:
        return ["Invalid or missing two-case exercise"]
    if scores != (11, 10, 11):
        errors.append("Correct original winner and alternate tie not represented")
    for token in (
        "Board: 6♠ 7♥ 8♦ 9♣ 10♠",
        "Player A: J♦ 2♣",
        "Player B: A♣ K♦",
        "If B replaces A♣ with J♣",
        "<strong>First: A wins.</strong>",
        "a jack-high straight",
        "a ten-high straight",
        "<strong>After B receives J♣: tie.</strong>",
        "suits cannot decide the winner",
        "<summary>Reveal both best-five answers</summary>",
    ):
        if token not in block:
            errors.append("Missing explanation: " + token)
    if block.count('<details class="poker-details" id="board-straight-answer">') != 1:
        errors.append("Answer must use one native details element")
    if "onclick=" in block or "<script" in block or "umami.track" in block:
        errors.append("Exercise must work without injected tracking or scripts")
    return errors


class BoardStraightLessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hand_source = read(HAND_SOURCE)
        cls.hand_public = read(HAND_PUBLIC)
        cls.basics_source = read(BASICS_SOURCE)
        cls.basics_public = read(BASICS_PUBLIC)

    def test_exact_new_exercise_in_source_and_published_page(self):
        self.assertEqual(question_block(self.hand_source), question_block(self.hand_public))
        self.assertEqual(audit_errors(self.hand_source), [])

    def test_first_case_is_jack_high_beating_ten_high(self):
        self.assertEqual(results(question_block(self.hand_source))[:2], (11, 10))
        self.assertIn("Holding an ace does not extend this board straight",
                      question_block(self.hand_source))

    def test_replacing_the_ace_with_a_jack_makes_a_tie(self):
        hero, old_b, new_b = results(question_block(self.hand_source))
        self.assertGreater(hero, old_b)
        self.assertEqual(hero, new_b)

    def test_both_cases_use_seven_distinct_hand_cards_and_no_flush(self):
        a = attrs(question_block(self.hand_source))
        self.assertEqual(a["data-board"].split(), ["6s", "7h", "8d", "9c", "Ts"])
        self.assertEqual(a["data-a"].split(), ["Jd", "2c"])
        self.assertEqual(a["data-b"].split(), ["Ac", "Kd"])
        self.assertEqual(a["data-b-variant"].split(), ["Jc", "Kd"])
        self.assertEqual(results(question_block(self.hand_source)), (11, 10, 11))

    def test_false_winner_text_is_detected(self):
        changed = self.hand_source.replace("<strong>First: A wins.</strong>",
                                           "<strong>First: B wins.</strong>", 1)
        self.assertTrue(audit_errors(changed))
        changed = self.hand_source.replace("<strong>After B receives J♣: tie.</strong>",
                                           "<strong>After B receives J♣: B wins.</strong>", 1)
        self.assertTrue(audit_errors(changed))

    def test_invalid_second_jack_or_repeated_card_fails_closed(self):
        changed = self.hand_source.replace('data-b-variant="Jc Kd"',
                                           'data-b-variant="5c Kd"', 1)
        self.assertTrue(audit_errors(changed))
        changed = self.hand_source.replace('data-b-variant="Jc Kd"',
                                           'data-b-variant="Jd Kd"', 1)
        self.assertTrue(audit_errors(changed))

    def test_five_nav_destinations_and_fragment_are_true(self):
        nav = re.search(r'<nav class="poker-jump" aria-label="On this page">(.*?)</nav>',
                        self.hand_public, re.S)
        self.assertIsNotNone(nav)
        links = re.findall(r'href="#([^"]+)"', nav.group(1))
        self.assertEqual(links, ["rankings", "ties", ANCHOR, "compare", "practice-next"])
        for target in links:
            self.assertEqual(self.hand_public.count('id="' + target + '"'), 1)

    def test_four_original_visual_showdowns_and_ten_rank_cards_remain(self):
        for content in (self.hand_source, self.hand_public):
            self.assertEqual(content.count('class="viewer-matchup"'), 4)
            self.assertEqual(content.count('data-winner='), 4)
            self.assertEqual(content.count('data-rank-cards='), 10)
            self.assertEqual(content.count('class="viewer-board-grid viewer-best-five"'), 4)
            self.assertEqual(content.count('class="poker-details viewer-question"'), 4)

    def test_no_global_viewer_question_count_increase(self):
        self.assertNotIn('class="poker-details viewer-question"',
                         question_block(self.hand_public))
        self.assertEqual(self.hand_source.count("board-straight-answer"), 1)

    def test_existing_free_card_practice_and_sources_remain(self):
        for content in (self.hand_source, self.hand_public):
            for target in (
                '/poker/free-poker-learning-path/#card-basics',
                '/poker/follow-along/',
                '/downloads/poker-beginner-study-card.txt',
                'https://www.pokerstars.com/poker/games/rules/hand-rankings/',
            ):
                self.assertIn('href="' + target + '"', content)
            self.assertIn("Four fictional showdowns", content)
            self.assertNotIn(chr(0x2014), content)

    def test_short_rules_guide_links_to_practice_and_keeps_general_rankings(self):
        for content in (self.basics_source, self.basics_public):
            self.assertEqual(content.count('href="' + HREF + '"'), 1)
            self.assertGreaterEqual(content.count('href="/poker/hand-rankings/"'), 1)
            self.assertIn('id="walkthrough"', content)
        self.assertEqual(poker_library.minutes(self.basics_source), 4)
        self.assertIn("About 4 min read", self.basics_public)

    def test_reading_times_and_release_runner_stay_consistent(self):
        self.assertEqual(poker_library.minutes(self.hand_source), 5)
        self.assertIn("About 5 min read", self.hand_public)
        runner = read("_scripts/local_release_checks.py")
        self.assertIn("test_pbg08_straight_board_hand_rankings.py", runner)
        self.assertIn("test_viewer_guides.py", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml")
            for p in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
