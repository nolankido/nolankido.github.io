"""Turn 166: a new fictional case must remain unanswered until a separate key.

The checks protect exact pot arithmetic, evidence labels, refusal to invent
outcomes, source/render parity, and all three earlier worked review routes.
They do not claim an optimal poker decision.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import check_live
import poker_finder
import poker_library
import poker_reading

QUESTION = "/downloads/poker-hand-review-practice-01.md"
KEY = "/downloads/poker-hand-review-practice-01-key.md"
BLANK = "/downloads/poker-hand-review.md"
GUIDE_SOURCE = ROOT / "_source/poker/reviewing-a-hand.html"
GUIDE_PUBLIC = ROOT / "poker/reviewing-a-hand/index.html"

PRACTICE_NAV = (
    '<nav class="poker-jump" aria-label="Practice and worked hand reviews">'
    '<a href="' + QUESTION + '">Try a new case</a>'
    '<a href="/downloads/poker-hand-review-example-ak.md">A-K: two decisions</a>'
    '<a href="/downloads/poker-hand-review-example-64o.md">6-4: bubble shove</a>'
    '<a href="/downloads/poker-hand-review-example-77.md">Sevens: four-handed reshove</a>'
    '</nav>'
)

KEY_ROW_CHECKS = (
    ("Hero's stack behind **after posts**", "**72,000**"),
    ("Current pot **before response**", "**20,000**"),
    ("Extra amount to **call**", "**6,000**"),
    ("Pot **after call**", "**26,000**"),
    ("Chips behind **after call**", "**66,000**"),
    ("Extra amount to **reraise to 24,000**", "**20,000**"),
    ("Chips behind immediately **after reraise**", "**52,000**"),
    ("**Uncalled portion returned**", "**14,000**"),
    ("**Awarded pot after refund**", "**26,000**"),
)


def practice_errors(question: str, key: str, guide: str, blank: str) -> list[str]:
    issues = []
    questions = [m.group(1) for m in re.finditer(r"(?m)^## ([1-7])\. ", question)]
    answers = [m.group(1) for m in re.finditer(r"(?m)^## ([1-7])\. ", key)]
    if questions != list("1234567") or answers != list("1234567"):
        issues.append("Both case and key require seven ordered review sections")
    for token in (
        "Fictional six-handed", "14 players remaining, 10 paid",
        "Small blind **2,000**, big blind **4,000**, **big-blind ante 4,000**",
        "**80,000 chips at the start of the hand, before posting**",
        "**96,000 chips**", "to 10,000 total",
        "raises in the preceding six hands",
        "reraise **to 24,000 total**",
        "The cutoff's hypothetical fold",
        "**Stop here.**",
    ):
        if token not in question:
            issues.append("Question lost stipulated facts or outcome barrier: " + token)
    stop = question.find("**Stop here.**")
    key_link = "https://nolankido.com" + KEY
    if question.count(key_link) != 1 or stop < 0 or question.find(key_link) < stop:
        issues.append("Key must be linked once only after the stop barrier")
    for leaked in ("**72,000**", "**20,000**", "**6,000**",
                   "**26,000**", "**66,000**", "**52,000**",
                   "**14,000**", "**92,000**", "23.1%"):
        if leaked in question:
            issues.append("Question leaked an arithmetic answer: " + leaked)
    for row_label, answer in KEY_ROW_CHECKS:
        row = next((line for line in key.splitlines()
                    if line.startswith("| ") and row_label in line), "")
        if not row or row.split("|")[-2].strip() != answer:
            issues.append("Incorrect or missing checking-key ledger row: " + row_label)
    for needed in (
        "52,000 behind + 14,000 refund + 26,000 pot = **92,000**",
        "**12,000 net chip gain**",
        "6,000 / 26,000", "23.1%",
        "not a 26,000 profit",
        "not a verified range",
        "no actual showdown",
        "no actual showdown, board, winner or opponent holding",
        "No actual opponent hand",
        "A missed check suggests",
    ):
        if needed.lower() not in key.lower():
            issues.append("Key lost truth boundary or arithmetic: " + needed)
    if "guaranteed profitable" in question + key or "optimal poker action" in question + key:
        issues.append("These exercises cannot claim a strategy verdict")
    if guide.count(PRACTICE_NAV) != 1:
        issues.append("Guide must offer one question-first practice route")
    if KEY in guide:
        issues.append("Guide must not expose the checking key before the exercise")
    if ("https://nolankido.com" + QUESTION) not in blank:
        issues.append("Private worksheet must offer the unseen practice")
    if KEY in blank:
        issues.append("Private worksheet must not skip the exercise")
    for text in (question, key, guide, blank):
        if any(x in text for x in ("\u2014", "<script", "<iframe", "onclick=", "utm_source=")):
            issues.append("No active markup, tracking or em dashes")
    return issues


class OutcomeBlindPracticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.question = (ROOT / QUESTION.lstrip("/")).read_text(encoding="utf-8")
        cls.key = (ROOT / KEY.lstrip("/")).read_text(encoding="utf-8")
        cls.blank = (ROOT / BLANK.lstrip("/")).read_text(encoding="utf-8")
        cls.guide = GUIDE_SOURCE.read_text(encoding="utf-8")
        cls.public = GUIDE_PUBLIC.read_text(encoding="utf-8")

    def test_question_is_unseen_and_answers_are_separate(self):
        self.assertEqual(practice_errors(
            self.question, self.key, self.guide, self.blank), [])
        self.assertNotIn("K-K", self.question)
        self.assertNotIn("A-T offsuit", self.question)
        self.assertIn("no actual showdown", self.key.lower())

    def test_pot_call_refund_and_final_stack_are_exact(self):
        behind = 80000 - 4000 - 4000
        pot = 2000 + 4000 + 4000 + 10000
        call = 10000 - 4000
        raise_extra = 24000 - 4000
        refund = 24000 - 10000
        matched_award = 10000 + 10000 + 2000 + 4000
        self.assertEqual((behind, pot, call), (72000, 20000, 6000))
        self.assertEqual((pot + call, behind - call), (26000, 66000))
        self.assertEqual((raise_extra, behind - raise_extra), (20000, 52000))
        self.assertEqual((refund, matched_award), (14000, 26000))
        self.assertEqual(behind - raise_extra + refund + matched_award, 92000)
        self.assertAlmostEqual(call / (pot + call) * 100, 23.1, places=1)

    def test_public_guide_keeps_search_prose_and_old_examples(self):
        self.assertIn(self.guide, self.public)
        self.assertEqual(self.public.count(PRACTICE_NAV), 1)
        stripped = self.guide.replace(PRACTICE_NAV, "")
        self.assertEqual(poker_finder.GuideText(self.guide).sections,
                         poker_finder.GuideText(stripped).sections)
        self.assertEqual(poker_reading.VisibleHeadings(self.guide).headings,
                         poker_reading.VisibleHeadings(stripped).headings)
        self.assertEqual(len(poker_reading.VisibleHeadings(self.guide).headings), 6)
        self.assertEqual(poker_library.minutes(self.guide), 4)
        self.assertIn('class="reader-outline-count">6 sections', self.public)
        self.assertIn("About 4 min read", self.public)
        self.assertEqual(build.build_outputs()[Path("poker/reviewing-a-hand/index.html")],
                         self.public)
        for path in ("poker-hand-review-example-ak.md",
                     "poker-hand-review-example-64o.md",
                     "poker-hand-review-example-77.md"):
            self.assertIn("/downloads/" + path, PRACTICE_NAV)

    def test_downloads_are_registered_for_read_only_live_checks(self):
        targets = check_live.targets()
        for route in (QUESTION, KEY, BLANK):
            with self.subTest(route=route):
                self.assertEqual(targets[route],
                                 (200, (ROOT / route.lstrip("/")).read_bytes()))

    def test_wrong_answers_or_question_leaks_are_rejected(self):
        mutations = (
            (self.question.replace(
                "## 2. Action: rebuild the chip ledger",
                "## 2. Action: rebuild the chip ledger\n\nThe pot is **20,000**.", 1),
             self.key, self.guide, self.blank),
            (self.question.replace(
                "**Stop here.**", "The check key is available here.", 1),
             self.key, self.guide, self.blank),
            (self.question, self.key.replace(
                "| **14,000** |", "| **12,000** |", 1),
             self.guide, self.blank),
            (self.question, self.key.replace(
                "| **6,000** |", "| **10,000** |", 1),
             self.guide, self.blank),
            (self.question, self.key, self.guide.replace(
                'href="' + QUESTION + '"', 'href="' + KEY + '"', 1),
             self.blank),
            (self.question, self.key, self.guide, self.blank.replace(
                "Outcome-blind fictional practice (questions first): ",
                "Skip the questions: ", 1).replace(QUESTION, KEY, 1)),
        )
        for idx, (question, key, guide, blank) in enumerate(mutations):
            with self.subTest(index=idx):
                self.assertTrue(practice_errors(question, key, guide, blank))


if __name__ == "__main__":
    unittest.main()
