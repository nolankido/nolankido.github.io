"""Turn 162: an annotated two-decision poker hand review and a reusable blank sheet.

The example is grounded in published first-person narration but is not a
reconstructed official hand history, independent range read, or solver result.
"""
from __future__ import annotations

import json
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

GUIDE = "/poker/reviewing-a-hand/"
EXAMPLE = "/downloads/poker-hand-review-example-ak.md"
BLANK = "/downloads/poker-hand-review.md"
SOURCE = ROOT / "_source/poker/reviewing-a-hand.html"
PUBLIC = ROOT / "poker/reviewing-a-hand/index.html"
EXERCISE_LABEL = "Practice and worked hand reviews"
PRACTICE = "/downloads/poker-hand-review-practice-01.md"
BUBBLE_EXAMPLE = "/downloads/poker-hand-review-example-64o.md"
SEVENS_EXAMPLE = "/downloads/poker-hand-review-example-77.md"
SHOWDOWN_ANCHOR = "standoff-showdown"


def exercise_errors(guide: str, example: str, blank: str) -> list[str]:
    failures = []
    nav = ('<nav class="poker-jump" aria-label="' + EXERCISE_LABEL +
           '"><a href="' + PRACTICE + '">Try a new case</a>'
           '<a href="' + EXAMPLE + '">A-K: two decisions</a>'
           '<a href="' + BUBBLE_EXAMPLE + '">6-4: bubble shove</a>'
           '<a href="' + SEVENS_EXAMPLE + '">Sevens: four-handed reshove</a></nav>')
    if guide.count(nav) != 1:
        failures.append("Exactly one labeled worked-example navigation is required")
    if example.count("### Decision A:") != 1 or example.count("### Decision B:") != 1:
        failures.append("Two explicitly distinct decision snapshots are required")
    head = example.split("## 6. Result, kept separate from both decisions")
    if len(head) != 2 or any(token in head[0] for token in ("K-K", "Q-Q")):
        failures.append("Revealed opponents must not leak into earlier decision sections")
    if not all(term in example for term in (
        "61,000 - 15,000 = approximately 46,000",
        "10.17 BB", "9,000", "6,000",
        "contested pot", "No solver or ICM calculation",
        "retrospective description", "No contemporaneous at-table note",
    )):
        failures.append("The evidence/stack ledger, unknowns or source limits were lost")
    if "Do not assign an exact pot-odds percentage" not in example:
        failures.append("No complete contested pot is available for odds")
    if not all(url in example for url in (
        "/poker/episodes/portland-meadows-standoff/#standoff-first-decision",
        "/poker/episodes/portland-meadows-standoff/#standoff-second-review",
        "/poker/episodes/portland-meadows-standoff/#standoff-showdown",
    )):
        failures.append("Three archival source/decision references are needed")
    if len(re.findall(r"(?m)^## [1-7]\. ", example)) != 7:
        failures.append("Annotated example must follow all seven sheet sections")
    if len(re.findall(r"(?m)^## [1-7]\. ", blank)) != 7:
        failures.append("Blank sheet must remain seven-part and reusable")
    if not all(term in blank for term in (
        "Decision label and point in the action sequence",
        "Original evidence source", "reported recollection", "after a squeeze",
        "already in the pot", "ICM-prize value",
        "Stopping point", "later recollection",
        "poker-hand-review-example-ak.md",
    )):
        failures.append("Blank sheet lacks source, sequential decision or stopping checks")
    if any(value in guide + example + blank for value in (
        "\u2014", "<script", "<iframe", "onclick=", "utm_source=", "t=6:08",
    )):
        failures.append("No unreviewed timecodes, tracking or active embeds")
    return failures


class TwoDecisionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")
        cls.example = (ROOT / EXAMPLE.lstrip("/")).read_text(encoding="utf-8")
        cls.blank = (ROOT / BLANK.lstrip("/")).read_text(encoding="utf-8")

    def test_two_decisions_unknowns_and_outcome_separation(self):
        self.assertEqual(exercise_errors(self.guide, self.example, self.blank), [])
        self.assertIn("K-K", self.example.split("## 6. Result")[1])
        self.assertIn("Q-Q", self.example.split("## 6. Result")[1])
        self.assertEqual(61000 - 15000, 46000)
        self.assertAlmostEqual(61000 / 6000, 10.17, places=2)
        self.assertEqual(15000 - 6000, 9000)
        original = (ROOT / "_source/poker/portland-meadows-standoff.html").read_text(encoding="utf-8")
        for anchor in ("standoff-first-decision", "standoff-second-decision", "standoff-showdown"):
            self.assertEqual(original.count('id="' + anchor + '"'), 1)
        for fact in ("About 61,000", "Approximately 46,000", "15,000",
                     "9,000", "pocket kings", "pocket queens"):
            self.assertIn(fact.lower(), original.lower())

    def test_blank_remains_private_generic_and_has_source_labels(self):
        self.assertIn("A private, editable record", self.blank)
        self.assertIn("Keep other people's identifying information", self.blank)
        self.assertIn("Write the action in order", self.blank)
        self.assertIn("What you thought at the table", self.blank)
        self.assertIn("Result, recorded separately", self.blank)
        self.assertNotIn("Nolan", self.blank)
        self.assertNotIn("61,000", self.blank)
        self.assertNotIn("K-K", self.blank)

    def test_source_and_compiled_are_in_sync_without_search_outline_change(self):
        self.assertIn(self.guide, self.public)
        self.assertEqual(self.public.count('aria-label="' + EXERCISE_LABEL + '"'), 1)
        nav = re.search(
            '<nav class="poker-jump" aria-label="' + EXERCISE_LABEL +
            '">[\\s\\S]*?</nav>\\n', self.guide
        )
        self.assertIsNotNone(nav)
        stripped = self.guide.replace(nav.group(0), "")
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

    def test_static_downloads_registered_in_read_only_live_verifier(self):
        targets = check_live.targets()
        for p in (BLANK, EXAMPLE):
            with self.subTest(route=p):
                self.assertIn(p, targets)
                self.assertEqual(targets[p], (200, (ROOT / p.lstrip("/")).read_bytes()))
        self.assertIn('href="' + EXAMPLE + '"', self.public)

    def test_guide_and_prior_publication_dates_are_preserved(self):
        entry = next(p for p in json.loads((ROOT / "_source/pages.json").read_text())
                     if p["path"] == GUIDE)
        self.assertEqual(entry["date"], "2026-10-05")
        self.assertEqual(entry["updated"], "2026-11-16")
        self.assertIn('"dateModified": "2026-11-16"', self.public)
        self.assertIn("Published October 5, 2026", self.guide)
        self.assertIn("November 16 with links to three source-documented hands", self.guide)

    def test_wrong_links_hindsight_contamination_and_missing_stopping_point_fail(self):
        for modified in (
            exercise_errors(self.guide.replace(EXAMPLE, "/downloads/incorrect.md", 1),
                            self.example, self.blank),
            exercise_errors(self.guide, self.example.replace(
                "### Decision B:", "### One indistinct decision:", 1), self.blank),
            exercise_errors(self.guide, self.example.replace(
                "## 6. Result, kept separate from both decisions", "## 6. Result", 1),
                self.blank),
            exercise_errors(self.guide, self.example.replace(
                "No solver or ICM calculation", "Verified solver calculation", 1), self.blank),
            exercise_errors(self.guide, self.example, self.blank.replace(
                "Stopping point", "Claimed conclusion", 1)),
        ):
            self.assertTrue(modified)


if __name__ == "__main__":
    unittest.main()
