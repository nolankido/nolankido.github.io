"""Turn 163: independent 6-4 bubble-shove review with explicit ICM unknowns.

The source is an archived public narration, not an audited contemporaneous
hand history or a reproducible solver solution. Tests preserve that boundary.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import check_live
import poker_finder
import poker_library
import poker_reading

GUIDE = "/poker/reviewing-a-hand/"
BUBBLE = "/downloads/poker-hand-review-example-64o.md"
AK = "/downloads/poker-hand-review-example-ak.md"
BLANK = "/downloads/poker-hand-review.md"
LABEL = "Annotated hand review examples"
RESULT = "## 6. Result, recorded only after the decision analysis"
NAV = ('<nav class="poker-jump" aria-label="' + LABEL +
       '"><a href="' + AK + '">See a worked A-K review with two separate decisions</a>'
       '<a href="' + BUBBLE + '">6-4 bubble decision</a></nav>')


def example_problems(document: str) -> list[str]:
    errors = []
    parts = [m.group(1) for m in re.finditer(r"(?m)^## ([1-7])\. ", document)]
    if parts != list("1234567"):
        errors.append("Each of seven post-play study stages must appear exactly once")
    sections = document.split(RESULT)
    if len(sections) != 2:
        return errors + ["Showdown must have a single, distinct result heading"]
    before, after = sections
    for forbidden in ("A-K suited", "shove was profitable", "won when a four", "showed A-K"):
        if forbidden in before:
            errors.append("Outcome or claimed solved verdict leaked into the decision: " + forbidden)
    for needed in ("A-K suited", "6-4 offsuit won", "full five-card board",
                   "not the full calling range"):
        if needed not in after:
            errors.append("Missing outcome or showdown limitation: " + needed)
    for needed in (
        "13 players remain; 10 places paid",
        "8,000", "15,000", "148,000 / 15,000 = 9.87 BB",
        "if", "before posting", "140,000",
        "big-blind ante", "dead money", "live big blind",
        "exact payout", "covers", "covered by", "calling range",
        "No contemporaneous at-table thought record",
        "without exact relevant stacks, payouts",
        "no defensible numerical chip-EV or ICM verdict",
        "November 3, 2026",
        "newer public video cut was not independently retimed",
    ):
        if needed not in document:
            errors.append("Missing recorded fact or uncertainty bound: " + needed)
    for url in (
        "/poker/episodes/portland-meadows-ep1/#hand-64o-record",
        "/poker/episodes/portland-meadows-ep1/#hand-64o-review",
        "/poker/six-to-ten-bb-tournament-decisions/#bridge-sb",
    ):
        if url not in document:
            errors.append("Missing original record, exercise or lesson reference: " + url)
    if any(value in document for value in (
        "\u2014", "<script", "<iframe", "onclick=", "utm_source=", "t=6:08",
        "guaranteed profitable", "verified solver result",
    )):
        errors.append("No invented ranges, unsafe markup or unverified cut timestamps")
    return errors


class BubbleHandReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = (ROOT / BUBBLE.lstrip("/")).read_text(encoding="utf-8")
        cls.blank = (ROOT / BLANK.lstrip("/")).read_text(encoding="utf-8")
        cls.ak = (ROOT / AK.lstrip("/")).read_text(encoding="utf-8")
        cls.source = (ROOT / "_source/poker/reviewing-a-hand.html").read_text(encoding="utf-8")
        cls.public = (ROOT / "poker/reviewing-a-hand/index.html").read_text(encoding="utf-8")

    def test_archived_source_and_conditional_stack_calculations_are_respected(self):
        self.assertEqual(example_problems(self.example), [])
        self.assertAlmostEqual(148000 / 15000, 9.87, places=2)
        self.assertEqual(148000 - 8000, 140000)
        archived = (ROOT / "_source/poker/portland-meadows-ep1.html").read_text(encoding="utf-8")
        for anchor in ("hand-64o-record", "hand-64o-review"):
            self.assertEqual(archived.count('id="' + anchor + '"'), 1)
        for token in ("13 players remain with 10 paid", "8,000 / 15,000 / 15,000",
                      "About 148,000", "6-4 offsuit", "big blind calls with A-K suited",
                      "The favorable result does not prove the shove was good"):
            self.assertIn(token, archived)
        self.assertNotIn("A-K suited", self.example.split(RESULT)[0])

    def test_blank_sheet_has_both_examples_and_stays_generic_and_private(self):
        self.assertEqual(len(re.findall(r"(?m)^## [1-7]\. ", self.blank)), 7)
        self.assertIn("A private, editable record", self.blank)
        self.assertIn("Keep other people's identifying information", self.blank)
        self.assertIn("Stopping point", self.blank)
        self.assertIn("reported recollection", self.blank)
        self.assertIn(AK, self.blank)
        self.assertIn(BUBBLE, self.blank)
        for excluded in ("Nolan", "148,000", "61,000", "A-K suited"):
            self.assertNotIn(excluded, self.blank)
        self.assertIn("### Decision A:", self.ak)
        self.assertIn("### Decision B:", self.ak)

    def test_general_guide_offers_two_examples_without_new_search_prose(self):
        self.assertEqual(self.source.count(NAV), 1)
        self.assertEqual(self.public.count(NAV), 1)
        self.assertIn(self.source, self.public)
        self.assertIn("Fictional example / No-limit hold'em", self.source)
        self.assertIn("The button faces 5 BB more to call, not 7 BB", self.source)
        stripped = self.source.replace(NAV, "")
        self.assertEqual(poker_finder.GuideText(self.source).sections,
                         poker_finder.GuideText(stripped).sections)
        self.assertEqual(poker_reading.VisibleHeadings(self.source).headings,
                         poker_reading.VisibleHeadings(stripped).headings)
        self.assertEqual(len(poker_reading.VisibleHeadings(self.source).headings), 6)
        self.assertEqual(poker_library.minutes(self.source), 4)
        self.assertIn('class="reader-outline-count">6 sections', self.public)
        self.assertIn("About 4 min read", self.public)
        self.assertEqual(build.build_outputs()[Path("poker/reviewing-a-hand/index.html")],
                         self.public)

    def test_both_example_downloads_are_registered_and_resolve(self):
        endpoints = check_live.targets()
        for url in (BLANK, AK, BUBBLE):
            with self.subTest(url=url):
                self.assertEqual(endpoints[url],
                                 (200, (ROOT / url.lstrip("/")).read_bytes()))
        self.assertIn('href="' + BUBBLE + '"', self.public)
        self.assertIn('href="' + AK + '"', self.public)

    def test_original_dates_and_sitemap_stay_synchronized(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        record = next(p for p in pages if p["path"] == GUIDE)
        self.assertEqual(record["date"], "2026-10-05")
        self.assertEqual(record["updated"], "2026-11-16")
        schema = json.loads(re.search(
            r'<script type="application/ld\+json">([\s\S]*?)</script>', self.public
        ).group(1))
        self.assertEqual(schema["dateModified"], "2026-11-16")
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        dates = {node.findtext(ns + "loc"): node.findtext(ns + "lastmod") for node in sitemap}
        self.assertEqual(dates["https://nolankido.com" + GUIDE], "2026-11-16")

    def test_counterfactual_mutations_cannot_claim_a_solver_or_showdown_ahead_of_time(self):
        wrongs = (
            self.example.replace("## 6. Result, recorded only after the decision analysis",
                                 "## 6. Early showdown", 1),
            self.example.replace("The actual range has not been measured.",
                                 "A-K suited was the known calling range.", 1),
            self.example.replace("no defensible numerical chip-EV or ICM verdict",
                                 "guaranteed profitable", 1),
            self.example.replace("13 players remain; 10 places paid",
                                 "11 players remain; 10 places paid", 1),
            self.example.replace("8,000", "7,000", 1),
            self.example.replace("/poker/episodes/portland-meadows-ep1/#hand-64o-record",
                                 "/poker/episodes/invalid/#hand-64o-record", 1),
        )
        for index, changed in enumerate(wrongs):
            with self.subTest(index=index):
                self.assertTrue(example_problems(changed))


if __name__ == "__main__":
    unittest.main()
