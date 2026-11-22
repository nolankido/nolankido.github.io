"""PBG-10: exact face-up turn outs, native lesson and download contracts.

Runs offline with Python's standard library. No solver recommendations,
real hand histories, visitor tracking or claimed book sales.
"""
from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/poker/poker-math-reference.html"
PUBLIC = "poker/poker-math-reference/index.html"
WORKSHEET = "downloads/holdem-clean-outs-turn-study.md"
CHECKER = "downloads/holdem-clean-outs-turn-verify.py"
ID = "clean-outs-turn-check"
DETAILS_ID = "clean-outs-turn-answer"
BOOK = "/books/how-to-play-no-limit-texas-holdem/"

sys.path.insert(0, str(ROOT / "_scripts"))
import poker_library

spec = importlib.util.spec_from_file_location("_pbg10_cleanouts", ROOT / CHECKER)
assert spec is not None and spec.loader is not None
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def lesson(html: str) -> str:
    matches = re.findall(
        r'<aside class="viewer-example" id="' + ID + r'"[^>]*>.*?</aside>',
        html, flags=re.S)
    if len(matches) != 1:
        raise ValueError("Exactly one original clean-outs lesson required")
    return matches[0]


def inputs(block: str) -> dict[str, str]:
    return dict(re.findall(r'([\w-]+)="([^"]*)"', block.split(">", 1)[0]))


def errors_for_exercise(html: str) -> list[str]:
    try:
        block = lesson(html)
    except ValueError as exc:
        return [str(exc)]
    problems = []
    expected = {
        "data-hero": "Ah Jh",
        "data-villain": "7d Qc",
        "data-board": "Kh 7h 7c 2d",
        "data-pot-before-bet": "60",
        "data-opponent-bet": "20",
    }
    items = inputs(block)
    for key, expected_value in expected.items():
        if items.get(key) != expected_value:
            problems.append("Wrong fixture " + key)
    for snippet in (
        "A♥ J♥", "K♥ 7♥ 7♣ 2♦", "7♦ Q♣",
        "Nine hearts complete a flush",
        "2♥ and Q♥ give the opponent a full house",
        "7/44 ≈ 15.91%", "9/44 ≈ 20.45%",
        "20/100 = 20%", "(7 × 80 − 37 × 20)/44",
        "−4.09 chips", "fictional model",
        'href="/' + WORKSHEET + '" download',
        'href="/' + CHECKER + '" download',
    ):
        if snippet not in block:
            problems.append("Missing explanation " + snippet)
    if (block.count('<details class="poker-details" id="' + DETAILS_ID + '">') != 1
            or block.count("<summary>") != 1 or block.count("</summary>") != 1):
        problems.append("Native answer reveal damaged")
    if any(token in block for token in ("onclick=", "<script", "umami.track", "data-umami-event")):
        problems.append("No interactive tracking or script allowed in exercise")
    return problems


class CleanOutsPBG10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(SOURCE)
        cls.public = read(PUBLIC)

    def test_published_native_lesson_matches_its_source(self):
        self.assertEqual(lesson(self.source), lesson(self.public))
        self.assertEqual(errors_for_exercise(self.source), [])

    def test_literal_cards_match_exact_enumeration_fixture(self):
        q = inputs(lesson(self.source))
        self.assertEqual(q["data-hero"].split(), list(verifier.HERO))
        self.assertEqual(q["data-villain"].split(), list(verifier.VILLAIN))
        self.assertEqual(q["data-board"].split(), list(verifier.TURN_BOARD))
        self.assertEqual(int(q["data-pot-before-bet"]), verifier.POT_BEFORE_BET)
        self.assertEqual(int(q["data-opponent-bet"]), verifier.BET)

    def test_44_rivers_and_seven_winning_heart_cards(self):
        actual = verifier.enumerate_rivers()
        self.assertEqual(actual["unknown"], 44)
        self.assertEqual(len(actual["wins"]), 7)
        self.assertEqual(len(actual["losses"]), 37)
        self.assertEqual(actual["ties"], [])
        self.assertEqual(set(actual["wins"]),
                         {"3h", "4h", "5h", "6h", "8h", "9h", "Th"})

    def test_raw_nine_flush_completions_have_two_dirty_hearts(self):
        actual = verifier.enumerate_rivers()
        self.assertEqual(len(actual["hearts"]), 9)
        self.assertEqual(actual["dirty_hearts"], ["2h", "Qh"])
        for card in ("2h", "Qh"):
            self.assertIn(card, actual["losses"])

    def test_best_seven_hand_ranking_checks_dirty_flush_rivers(self):
        for river in ("2h", "Qh"):
            hero = verifier.best_seven((*verifier.HERO, *verifier.TURN_BOARD, river))
            villain = verifier.best_seven((*verifier.VILLAIN, *verifier.TURN_BOARD, river))
            self.assertEqual(hero[0], 5, "Hero has a made flush")
            self.assertEqual(villain[0], 6, "Opponent has a full house")
            self.assertLess(hero, villain)
        clean = verifier.best_seven((*verifier.HERO, *verifier.TURN_BOARD, "3h"))
        trips = verifier.best_seven((*verifier.VILLAIN, *verifier.TURN_BOARD, "3h"))
        self.assertGreater(clean, trips)

    def test_price_equity_and_ev_use_exact_fractions(self):
        result = verifier.audit()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["actual_equity_fraction"], "7/44")
        self.assertEqual(result["raw_heart_completion_fraction"], "9/44")
        self.assertEqual(result["call_price_fraction"], "1/5")
        self.assertEqual(Fraction(7, 44) * 100 - 20, Fraction(-45, 11))
        self.assertEqual(result["call_ev_chips"], -4.09)

    def test_counting_raw_heart_completions_reverses_ev_sign(self):
        result = verifier.audit()
        self.assertLess(Fraction(result["actual_equity_fraction"]), Fraction(1, 5))
        self.assertGreater(Fraction(result["raw_heart_completion_fraction"]), Fraction(1, 5))
        self.assertEqual(Fraction(result["mistaken_raw_heart_ev_fraction_chips"]),
                         Fraction(5, 11))
        self.assertGreater(result["mistaken_raw_heart_ev_chips"], 0)

    def test_wrong_opponent_or_bet_fails_checker_status(self):
        with patch.object(verifier, "VILLAIN", ("7d", "5c")):
            self.assertEqual(verifier.audit()["status"], "fail")
        with patch.object(verifier, "BET", 25):
            self.assertEqual(verifier.audit()["status"], "fail")

    def test_duplicate_or_illegal_cards_cannot_be_enumerated(self):
        with self.assertRaises(ValueError):
            verifier.enumerate_rivers(hero=("7d", "Jh"))
        with self.assertRaises(ValueError):
            verifier.enumerate_rivers(villain=("7x", "Qc"))

    def test_bad_on_site_claims_are_detected(self):
        for old, new in (
            ("7/44 ≈ 15.91%", "9/44 ≈ 20.45%"),
            ("2♥ and Q♥ give the opponent a full house", "All nine hearts win"),
            ("(7 × 80 − 37 × 20)/44", "(9 × 80 − 35 × 20)/44"),
        ):
            with self.subTest(old=old):
                tampered = self.source.replace(old, new, 1)
                self.assertTrue(errors_for_exercise(tampered))

    def test_worksheet_and_checker_are_real_public_downloads(self):
        sheet = read(WORKSHEET)
        checker = read(CHECKER)
        self.assertIn("7 wins, 37 losses and no ties", sheet)
        self.assertIn("-4.09", sheet)
        self.assertIn("2♥", sheet)
        self.assertIn("Q♥", sheet)
        self.assertIn('def enumerate_rivers(', checker)
        self.assertIn("No network", checker)
        for path in (WORKSHEET, CHECKER):
            self.assertIn('href="/' + path + '" download', self.public)

    def test_existing_math_reference_identity_and_study_remain(self):
        for doc in (self.source, self.public):
            self.assertEqual(doc.count('href="' + BOOK + '"'), 1)
            self.assertIn('href="/downloads/poker-math-reference.md" download', doc)
            self.assertIn("90 / 300 = 30%", doc)
            self.assertIn("90 / 210 = 42.86%", doc)
            self.assertEqual(doc.count('class="poker-details viewer-question"'), 3)
            self.assertIn("C(7,5) = 21", doc)
        self.assertIn("not an official", read("books/how-to-play-no-limit-texas-holdem/index.html"))

    def test_reading_time_remains_five_minutes(self):
        self.assertEqual(poker_library.minutes(self.source), 5)
        self.assertIn("About 5 min read", self.public)
        self.assertNotIn(chr(0x2014), self.source)
        self.assertNotIn(chr(0x2014), read(WORKSHEET))

    def test_local_release_runner_registers_regressions_and_offline_checker(self):
        runner = read("_scripts/local_release_checks.py")
        self.assertIn("test_pbg10_clean_outs_turn.py", runner)
        self.assertIn("holdem-clean-outs-turn-verify.py", runner)
        self.assertIn("test_pbg09_button_action_contrast.py", runner)
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(
            f.suffix.lower() in (".yaml", ".yml") for f in folder.iterdir()))


if __name__ == "__main__":
    unittest.main()
