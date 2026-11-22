"""PBG-07: source-backed full Hold'em guide, changed-range river EV and navigation.

Read-only and offline. All decision models are explicitly fictional.
This test does not certify a real betting range or poker solver recommendation.
"""
from __future__ import annotations

from fractions import Fraction
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/no-limit-holdem-guide.html"
PUBLIC = ROOT / "poker/no-limit-holdem-guide/index.html"
BOOK = "/books/how-to-play-no-limit-texas-holdem/"
EV_ID = "guide-check-bluff-mix"
SPECIALIST = "/poker/turn-and-river-decisions/#catching-a-bluff"
STARTING = "/poker/starting-hand-decisions/"
sys.path.insert(0, str(ROOT / "_scripts"))
import poker_library


def details(text: str) -> str:
    expression = (
        r'<details class="poker-details viewer-question" id="' +
        EV_ID + r'">(.*?)</details>'
    )
    matches = re.findall(expression, text, flags=re.S)
    if len(matches) != 1:
        raise ValueError("Exactly one native river EV question is required")
    return matches[0]


def expected_chips(bluff_units: int, value_units: int) -> Fraction:
    """Relative to folding, ignoring future action, rake, side pots and ties."""
    n = bluff_units + value_units
    if n <= 0 or bluff_units < 0 or value_units < 0:
        raise ValueError("Invalid teaching weights")
    return Fraction(bluff_units, n) * 90 - Fraction(value_units, n) * 30


def exercise_errors(content: str) -> list[str]:
    errors = []
    try:
        block = details(content)
    except ValueError as exc:
        return [str(exc)]
    for token in ("$30", "$60", "$90", "$120", "30/120 = 25%",
                  "2/12 = 16.67%", "4/12 = 33.33%",
                  "EV(call) = (2/12 × $90) - (10/12 × $30)",
                  "EV(call) = (4/12 × $90) - (8/12 × $30)",
                  "<strong>-$10</strong>", "<strong>+$10</strong>",
                  "Three bluffs in twelve break even",
                  "Assume no ties, fees or side pots",
                  "hypothetical betting weights",
                  "not real opponents or legal card combinations",
                  'href="' + SPECIALIST + '"'):
        if token not in block:
            errors.append("Missing or changed worked-model claim: " + token)
    if block.count("<summary>") != 1 or block.count("</summary>") != 1:
        errors.append("Missing unique accessible summary")
    if "<script" in block or "onclick=" in block:
        errors.append("Practice answer must work without JavaScript")
    if expected_chips(2, 10) != -10 or expected_chips(4, 8) != 10:
        errors.append("Exact fractional model differs from stated payoff")
    return errors


class PokerGuidePBG07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")

    def test_one_new_native_question_matches_source_and_generated_page(self):
        self.assertEqual(details(self.source), details(self.public))
        self.assertEqual(exercise_errors(self.source), [])
        self.assertEqual(exercise_errors(self.public), [])
        self.assertEqual(self.source.count('id="' + EV_ID + '"'), 1)

    def test_river_call_math_is_exact_at_three_bluff_mixes(self):
        self.assertEqual(Fraction(30, 120), Fraction(1, 4))
        self.assertEqual(Fraction(2, 12), Fraction(1, 6))
        self.assertEqual(Fraction(4, 12), Fraction(1, 3))
        self.assertEqual(expected_chips(2, 10), Fraction(-10))
        self.assertEqual(expected_chips(3, 9), Fraction(0))
        self.assertEqual(expected_chips(4, 8), Fraction(10))

    def test_false_ev_claim_is_rejected(self):
        bad = self.source.replace("<strong>+$10</strong>",
                                  "<strong>+$12</strong>", 1)
        self.assertTrue(exercise_errors(bad))
        bad = self.source.replace("30/120 = 25%", "30/90 = 25%", 1)
        self.assertTrue(exercise_errors(bad))

    def test_missing_challenge_or_changed_number_of_outcomes_is_rejected(self):
        self.assertTrue(exercise_errors(self.source.replace(
            'id="' + EV_ID + '"', 'id="missing-bluff-mix"', 1)))
        bad = self.source.replace("4/12 = 33.33%", "4/12 = 25%", 1)
        self.assertTrue(exercise_errors(bad))

    def test_practice_does_not_pretend_hero_knows_opponent_range(self):
        block = details(self.source)
        self.assertIn("equally weighted betting cases", block)
        self.assertIn("A usable range estimate needs the board", block)
        self.assertIn("betting frequencies", block)
        self.assertIn("with folding worth $0", block)
        self.assertNotIn("solver says", block.lower())
        self.assertNotIn("guaranteed profit", block.lower())

    def test_new_preflop_study_route_is_inside_opening_reader_table(self):
        row = ('<tr><td>Practice a starting-hand choice</td><td>Use '
               '<a href="' + STARTING + '">eight changed-input preflop exercises</a> '
               'before memorizing a chart</td></tr>')
        self.assertEqual(self.source.count(row), 1)
        self.assertEqual(self.public.count(row), 1)
        self.assertLess(self.public.index(row),
                        self.public.index('id="the-rules-and-action-order"'))
        target = (ROOT / STARTING.lstrip("/") / "index.html").read_text(encoding="utf-8")
        self.assertEqual(target.count(
            '<link rel="canonical" href="https://nolankido.com' + STARTING + '">'), 1)

    def test_river_practice_deep_link_is_existing_free_article(self):
        path, anchor = SPECIALIST.split("#")
        target = (ROOT / path.lstrip("/") / "index.html").read_text(encoding="utf-8")
        self.assertEqual(target.count('id="' + anchor + '"'), 1)
        self.assertIn('href="' + SPECIALIST + '"', details(self.public))
        self.assertNotIn("amazon.com", details(self.public).lower())

    def test_existing_free_practice_questions_are_not_replaced(self):
        for element in ("guide-check-call", "guide-check-price", "guide-check-board",
                        EV_ID):
            with self.subTest(element=element):
                self.assertEqual(self.source.count('id="' + element + '"'), 1)
                self.assertEqual(self.public.count('id="' + element + '"'), 1)
        self.assertIn("$30 / $120 = 25%", self.public)
        self.assertIn('href="/poker/beginner-checkpoint/"', self.source)

    def test_book_provenance_and_two_contextual_routes_preserved(self):
        for html in (self.source, self.public):
            self.assertEqual(html.count('href="' + BOOK + '"'), 1)
            self.assertEqual(html.count(
                'href="' + BOOK + '#poker-book-first-exercise"'), 1)
            self.assertIn('href="/downloads/holdem-river-call-check-worksheet.md"', html)
            self.assertIn("not a verified retail excerpt", html)
            self.assertNotIn('href="https://www.amazon.com/dp/', html)

    def test_section_heading_outline_and_original_dates_are_stable(self):
        self.assertEqual(len(re.findall(r'<h2\b', self.source)), 13)
        self.assertEqual(len(re.findall(r'<h3\b', self.source)), 62)
        self.assertIn('id="worked-review-example"', self.source)
        self.assertIn('id="draws-pot-odds-and-expected-value"', self.source)
        self.assertIn('2026-10-14', self.public)
        self.assertIn('"dateModified": "2026-11-20"', self.public)
        self.assertNotIn(chr(0x2014), self.source)

    def test_editorial_reading_time_stays_consistent(self):
        self.assertEqual(poker_library.minutes(self.source), 49)
        self.assertIn("About 49 min read", self.public)

    def test_release_runner_includes_regressions_and_no_github_actions(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_pbg07_no_limit_guide.py", runner)
        self.assertIn("test_pbg06_beginner_intent_map.py", runner)
        self.assertIn("['_scripts/build.py', '--check']", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            f.suffix.lower() in (".yml", ".yaml") for f in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
