"""PBG-09: same AJs/button preflop hand with two different prior-action states.

The comparison is a fictional mechanics exercise, not a strategy chart,
a solver recommendation or a sample of actual opponent responses.
All tests are offline; no network, analytics, wager or GitHub Actions.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
START_SOURCE = "_source/poker/starting-hand-decisions.html"
START_PUBLIC = "poker/starting-hand-decisions/index.html"
POSITION_SOURCE = "_source/poker/position-and-stacks.html"
POSITION_PUBLIC = "poker/position-and-stacks/index.html"
ID = "check-record"
ROUTE = "/poker/starting-hand-decisions/#study-record"
FOLLOWUP = "/poker/facing-preflop-raises/"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def exercise(html: str) -> str:
    pattern = r'<details class="poker-details viewer-question" id="' + ID + r'"[^>]*>.*?</details>'
    matches = re.findall(pattern, html, re.S)
    if len(matches) != 1:
        raise ValueError("One final native Exercise 8 is required")
    return matches[0]


def numbers(block: str) -> dict[str, int]:
    opening = block.split(">", 1)[0]
    values = dict(re.findall(r'data-([a-z-]+)="([0-9]+)"', opening))
    expected = {
        "small-blind", "big-blind", "button-stack", "cutoff-stack",
        "small-blind-stack", "big-blind-stack", "cutoff-raise-to",
    }
    if set(values) != expected:
        raise ValueError("Unexpected study fixture keys")
    result = {key: int(value) for key, value in values.items()}
    if (result["small-blind"] <= 0
            or result["big-blind"] < result["small-blind"]
            or result["cutoff-raise-to"] <= result["big-blind"]
            or min(result["button-stack"], result["cutoff-stack"],
                   result["small-blind-stack"], result["big-blind-stack"]) <= 0):
        raise ValueError("Invalid blind, raise or stack inputs")
    return result


def arithmetic(block: str) -> dict[str, int]:
    d = numbers(block)
    sb, bb, raise_to = (d["small-blind"], d["big-blind"], d["cutoff-raise-to"])
    return {
        "raised_pot_before_button": raise_to + sb + bb,
        "raised_extra_to_call": raise_to,
        "raised_pot_after_button_call": 2 * raise_to + sb + bb,
        "unopened_pot_before_button": sb + bb,
        "unopened_extra_to_call": bb,
        "unopened_pot_after_button_call": sb + 2 * bb,
        "button_starting_bb": d["button-stack"] // bb,
        "vs_cutoff_effective_bb": min(d["button-stack"], d["cutoff-stack"]) // bb,
        "vs_small_blind_effective_bb": min(d["button-stack"], d["small-blind-stack"]) // bb,
        "vs_big_blind_effective_bb": min(d["button-stack"], d["big-blind-stack"]) // bb,
    }


def audit_errors(html: str) -> list[str]:
    try:
        block = exercise(html)
        values = arithmetic(block)
    except (ValueError, KeyError, ZeroDivisionError):
        return ["Missing or invalid AJs button scenario"]
    errors = []
    expected = {
        "raised_pot_before_button": 9,
        "raised_extra_to_call": 6,
        "raised_pot_after_button_call": 15,
        "unopened_pot_before_button": 3,
        "unopened_extra_to_call": 2,
        "unopened_pot_after_button_call": 5,
        "button_starting_bb": 75,
        "vs_cutoff_effective_bb": 30,
        "vs_small_blind_effective_bb": 75,
        "vs_big_blind_effective_bb": 75,
    }
    if values != expected:
        errors.append("Computed pot, call price or effective stacks changed")
    for token in (
        "150 / 2 = 75 BB",
        "9-chip pot",
        "Calling costs 6 and creates 15",
        "1 + 2 = 3",
        "Calling the live big blind costs 2, creating 5",
        "Both blinds can respond",
        "60 chips = 30 BB",
        "150 = 75 BB",
        "In B, the cutoff folded",
        "An unopened-pot chart cannot answer the already-raised scene",
        "not an optimal fold, call or raise",
        'href="' + FOLLOWUP + '"',
        "Exercise 8: Compare a cutoff raise with an unopened button pot",
    ):
        if token not in block:
            errors.append("Missing or incorrect explanation: " + token)
    if block.count("<summary>") != 1 or block.count("</summary>") != 1:
        errors.append("Native answer reveal must have one summary")
    if "<script" in block or "onclick=" in block or "data-umami-event" in block:
        errors.append("No interactive analytics or script required")
    return errors


class ButtonActionContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(START_SOURCE)
        cls.public = read(START_PUBLIC)
        cls.position = read(POSITION_SOURCE)
        cls.position_public = read(POSITION_PUBLIC)

    def test_source_public_comparison_is_exact(self):
        self.assertEqual(exercise(self.source), exercise(self.public))
        self.assertEqual(audit_errors(self.source), [])
        self.assertEqual(audit_errors(self.public), [])

    def test_two_action_states_change_only_known_pot_and_call_cost(self):
        v = arithmetic(exercise(self.source))
        self.assertEqual(
            (v["raised_pot_before_button"], v["raised_extra_to_call"],
             v["raised_pot_after_button_call"]), (9, 6, 15))
        self.assertEqual(
            (v["unopened_pot_before_button"], v["unopened_extra_to_call"],
             v["unopened_pot_after_button_call"]), (3, 2, 5))

    def test_effective_stacks_still_depend_on_remaining_opponents(self):
        v = arithmetic(exercise(self.source))
        self.assertEqual(
            (v["button_starting_bb"], v["vs_cutoff_effective_bb"],
             v["vs_small_blind_effective_bb"], v["vs_big_blind_effective_bb"]),
            (75, 30, 75, 75))
        self.assertIn("In B, the cutoff folded", exercise(self.source))

    def test_same_cards_and_button_in_both_scenes(self):
        section = self.source.split('<h2 id="study-record">', 1)[1].split(
            '<h2 id="study-template">', 1)[0]
        self.assertIn("Same A♠ J♠, same button, different action", section)
        self.assertIn("In scene A the cutoff raises to 6", section)
        self.assertIn("In scene B the cutoff folds", section)
        self.assertIn("Two early seats fold", section)

    def test_bad_pot_or_call_claim_is_detected(self):
        for old, new in (
            ("9-chip pot", "10-chip pot"),
            ("creates 15", "creates 14"),
            ("1 + 2 = 3", "1 + 2 = 4"),
            ("creating 5", "creating 6"),
        ):
            with self.subTest(old=old):
                changed = self.source.replace(old, new, 1)
                self.assertTrue(audit_errors(changed))

    def test_bad_fixture_stacks_or_raise_fail_closed(self):
        for old, new in (
            ('data-cutoff-raise-to="6"', 'data-cutoff-raise-to="8"'),
            ('data-button-stack="150"', 'data-button-stack="100"'),
            ('data-big-blind="2"', 'data-big-blind="0"'),
        ):
            with self.subTest(old=old):
                self.assertTrue(audit_errors(self.source.replace(old, new, 1)))

    def test_original_eight_reveal_questions_remain(self):
        ids = ("check-features", "check-position", "check-action",
               "check-price", "check-depth", "check-effective",
               "check-future", ID)
        for content in (self.source, self.public):
            self.assertEqual(content.count('class="poker-details viewer-question"'), 8)
            for id_value in ids:
                self.assertEqual(content.count('id="' + id_value + '"'), 1)
            self.assertEqual(content.count("<details"), content.count("</details>"))

    def test_last_exercise_still_inside_same_section_and_before_template(self):
        for content in (self.source, self.public):
            a = content.index('id="study-record"')
            b = content.index('id="' + ID + '"')
            c = content.index('id="study-template"')
            self.assertLess(a, b)
            self.assertLess(b, c)
            self.assertIn('href="/poker/reading-preflop-charts/"', content)

    def test_position_lesson_crosslink_matches_real_target(self):
        for content in (self.position, self.position_public):
            self.assertEqual(content.count('href="' + ROUTE + '"'), 1)
        self.assertIn('id="study-record"', self.public)
        target = read("poker/facing-preflop-raises/index.html")
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com' + FOLLOWUP + '">',
            target)

    def test_book_disclosure_and_free_practice_are_preserved(self):
        for content in (self.source, self.public):
            self.assertEqual(
                content.count('href="/books/how-to-play-no-limit-texas-holdem/"'), 1)
            self.assertIn('href="/poker/free-poker-learning-path/"', content)
            self.assertIn("No solver outputs or claimed optimal ranges", content)
            self.assertNotIn("umami.track(", content)

    def test_reading_time_and_existing_publication_metadata_remain_stable(self):
        self.assertIn("About 17 min read", self.public)
        self.assertIn("About 5 min read", self.position_public)
        self.assertIn('"dateModified": "2026-10-16"', self.public)
        self.assertNotIn(chr(0x2014), self.source)
        self.assertNotIn(chr(0x2014), self.position)

    def test_manual_release_includes_regression_and_no_actions(self):
        runner = read("_scripts/local_release_checks.py")
        self.assertIn("test_pbg09_button_action_contrast.py", runner)
        self.assertIn("glob('*_browser.py')", runner)
        self.assertTrue((ROOT / "_tests/preflop_browser.py").is_file())
        self.assertIn("['_scripts/build.py', '--check']", runner)
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(
            p.is_file() and p.suffix.lower() in (".yaml", ".yml")
            for p in folder.iterdir()))


if __name__ == "__main__":
    unittest.main()
