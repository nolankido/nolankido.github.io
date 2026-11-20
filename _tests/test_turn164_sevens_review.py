"""Turn 164: complete four-handed pocket-sevens review without hindsight or invented ICM.

The source is a first-person archived-version narration, not an audited
hand history, contemporaneous opponent-range log or solver output.
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
BLANK = "/downloads/poker-hand-review.md"
SEVENS = "/downloads/poker-hand-review-example-77.md"
AK = "/downloads/poker-hand-review-example-ak.md"
BUBBLE = "/downloads/poker-hand-review-example-64o.md"
RESULT = "## 6. Result and later tournament outcome, kept separate"
PRACTICE = "/downloads/poker-hand-review-practice-01.html"
NAV = ('<nav class="poker-jump" aria-label="Practice and worked hand reviews">'
       '<a href="' + PRACTICE + '">Try a new case</a>'
       '<a href="' + AK + '">A-K: two decisions</a>'
       '<a href="' + BUBBLE + '">6-4: bubble shove</a>'
       '<a href="' + SEVENS + '">Sevens: four-handed reshove</a></nav>')


def review_problems(example: str) -> list[str]:
    errors = []
    parts = [match.group(1) for match in re.finditer(r"(?m)^## ([1-7])\. ", example)]
    if parts != list("1234567"):
        errors.append("The seven after-play worksheet stages are missing or out of order")
    sections = example.split(RESULT)
    if len(sections) != 2:
        return errors + ["Outcome must appear under one separate result heading"]
    before, after = sections

    for secret in ("A-T offsuit", "pocket sevens held", "$2,900", "$5,100"):
        if secret in before:
            errors.append("Showdown or later payout appears before the decision: " + secret)
    for needed in ("A-T offsuit", "pocket sevens held", "$2,900", "$5,100",
                   "complete board", "not the full calling range"):
        if needed not in after:
            errors.append("Result or outcome limitation missing: " + needed)

    required = (
        "Four players remain at the final table",
        "15,000", "30,000", "585,000 / 30,000 = 19.5 BB",
        "before posting", "525,000", "45,000 additional chips",
        "big-blind ante", "dead money",
        "75,000", "2.5 BB", "big blind", "pocket sevens",
        "button's opening range is not its calling range",
        "opening range AND distinct call-versus-reshove range",
        "No contemporaneous at-table thought record",
        "November 3, 2026", "not a verified timestamp",
        "final-table prize value", "no defensible numeric chip-EV or ICM verdict",
        "full four-handed payout ladder",
    )
    for needed in required:
        if needed.lower() not in example.lower():
            errors.append("Missing reported fact or explicit uncertainty: " + needed)

    for route in (
        "/poker/episodes/portland-meadows-ep1/#hand-77-record",
        "/poker/episodes/portland-meadows-ep1/#hand-77-review",
        "/poker/short-stack-decisions/#depths",
        "/poker/short-stack-decisions/#icm-call",
    ):
        if route not in example:
            errors.append("Missing archival or study link: " + route)

    if any(bad in example for bad in (
        "\u2014", "<script", "<iframe", "onclick=", "utm_source=", "t=9:00",
        "verified solver solution", "guaranteed profitable",
    )):
        errors.append("Unsupported cut timestamp, definitive advice or active markup")
    return errors


class SevensReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = (ROOT / SEVENS.lstrip("/")).read_text(encoding="utf-8")
        cls.blank = (ROOT / BLANK.lstrip("/")).read_text(encoding="utf-8")
        cls.guide = (ROOT / "_source/poker/reviewing-a-hand.html").read_text(encoding="utf-8")
        cls.public = (ROOT / "poker/reviewing-a-hand/index.html").read_text(encoding="utf-8")
        cls.episode = (ROOT / "_source/poker/portland-meadows-ep1.html").read_text(encoding="utf-8")
        cls.episode_public = (ROOT / "poker/episodes/portland-meadows-ep1/index.html").read_text(encoding="utf-8")

    def test_sevens_review_keeps_ranges_and_showdown_separate(self):
        self.assertEqual(review_problems(self.sample), [])
        self.assertEqual(585000 / 30000, 19.5)
        self.assertEqual(75000 / 30000, 2.5)
        self.assertEqual(75000 - 30000, 45000)
        self.assertEqual(585000 - 30000 - 30000, 525000)

        source = self.episode[self.episode.index('id="hand-77-record"'):]
        source = source[:source.index("</section>")]
        self.assertIn("Cutoff folds; button raises to 75,000 total", source)
        self.assertIn("big blind with pocket sevens".lower(), source.lower())
        self.assertIn("button calls with A-T offsuit", source)
        self.assertIn("15,000 / 30,000 / 30,000", source)
        self.assertIn("About 585,000", source)
        self.assertIn("four-way deal", source)
        self.assertIn("$2,900", source)
        self.assertIn("$5,100", source)

    def test_source_and_published_hand_link_to_new_review_only_once(self):
        self.assertIn(self.episode, self.episode_public)
        for p in (self.episode, self.episode_public):
            self.assertEqual(p.count('href="' + SEVENS + '"'), 1)
            self.assertEqual(p.count('id="hand-77-review"'), 1)
            self.assertIn("The guide is a framework, not a solved range", p)

    def test_private_blank_and_three_worked_example_links(self):
        self.assertEqual(len(re.findall(r"(?m)^## [1-7]\. ", self.blank)), 7)
        self.assertIn("A private, editable record", self.blank)
        self.assertIn("Keep other people's identifying information", self.blank)
        for route in (AK, BUBBLE, SEVENS):
            self.assertIn(route, self.blank)
        for private_fact in ("Nolan", "585,000", "61,000", "A-T offsuit"):
            self.assertNotIn(private_fact, self.blank)

    def test_general_guide_preserves_fictional_hand_reading_time_and_search_prose(self):
        self.assertEqual(self.guide.count(NAV), 1)
        self.assertEqual(self.public.count(NAV), 1)
        self.assertIn(self.guide, self.public)
        self.assertIn("Fictional example / No-limit hold'em", self.guide)
        self.assertIn("The button faces 5 BB more to call, not 7 BB", self.guide)
        stripped = self.guide.replace(NAV, "")
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

    def test_site_download_targets_and_article_dates_stay_consistent(self):
        endpoints = check_live.targets()
        for route in (BLANK, AK, BUBBLE, SEVENS):
            with self.subTest(route=route):
                self.assertEqual(endpoints[route],
                                 (200, (ROOT / route.lstrip("/")).read_bytes()))
        metadata = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        guide = next(p for p in metadata if p["path"] == GUIDE)
        self.assertEqual(guide["date"], "2026-10-05")
        self.assertEqual(guide["updated"], "2026-11-16")
        self.assertIn('"dateModified": "2026-11-16"', self.public)
        self.assertIn('"dateModified": "2026-11-20"', self.episode_public)

        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        lastmods = {item.findtext(ns + "loc"): item.findtext(ns + "lastmod") for item in sitemap}
        self.assertEqual(lastmods["https://nolankido.com" + GUIDE], "2026-11-16")
        self.assertEqual(lastmods["https://nolankido.com/poker/episodes/portland-meadows-ep1/"],
                         "2026-11-20")

    def test_hindsight_and_invalid_range_assumptions_are_caught(self):
        variants = (
            self.sample.replace("## 6. Result and later tournament outcome, kept separate",
                                "## 6. Result scattered across decisions", 1),
            self.sample.replace("No contemporaneous at-table thought record",
                                "Verified written notes from the table", 1),
            self.sample.replace("opening range is not its calling range",
                                "opening range is identical to its calling range", 1),
            self.sample.replace("no defensible numeric chip-EV or ICM verdict",
                                "guaranteed profitable", 1),
            self.sample.replace("585,000 / 30,000 = 19.5 BB",
                                "585,000 / 30,000 = 12 BB", 1),
            self.sample.replace("/poker/episodes/portland-meadows-ep1/#hand-77-record",
                                "/poker/episodes/invalid/#hand-77-record", 1),
            self.sample.replace("The button's opening range is not its calling range.",
                                "A-T offsuit was known in advance. The button's opening range is not its calling range.", 1),
        )
        for idx, sample in enumerate(variants):
            with self.subTest(idx=idx):
                self.assertTrue(review_problems(sample))


if __name__ == "__main__":
    unittest.main()
