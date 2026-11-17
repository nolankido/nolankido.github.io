"""Turn 161: connect the hand-review method to actual source-bounded exercises.

The original K-Q hand and all of its pot math remain fictional. Three links
point to separately documented outcomes and review prompts, not solved ranges.
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
import poker_finder
import poker_library
import poker_reading

GUIDE = "/poker/reviewing-a-hand/"
NAV_LABEL = "Source-documented hand-review exercises"
HAND_LINKS = (
    "/poker/episodes/portland-meadows-ep1/#hand-64o-review",
    "/poker/episodes/portland-meadows-ep1/#hand-77-review",
    "/poker/episodes/portland-meadows-standoff/#standoff-second-review",
)


def route_nav(markup: str) -> str:
    pattern = (r'<nav class="poker-jump" aria-label="' + re.escape(NAV_LABEL) +
               r'">([\s\S]*?)</nav>')
    found = re.findall(pattern, markup)
    if len(found) != 1:
        raise ValueError("Missing or duplicate documented-hand navigation")
    return found[0]


def route_errors(markup: str) -> list[str]:
    problems = []
    try:
        nav = route_nav(markup)
    except ValueError as exc:
        return [str(exc)]
    if "Recorded hands, not solved strategy:" not in nav:
        problems.append("Real accounts and solved outcomes must be distinguished")
    destinations = re.findall(r'<a href="([^"]+)">([^<]+)</a>', nav)
    if tuple(url for url, label in destinations) != HAND_LINKS:
        problems.append("The three exact documented-hand review routes must be present")
    if any(len(label.strip()) < 8 for url, label in destinations):
        problems.append("All three hand links need distinguishing visible labels")
    if any(x in nav for x in ("<script", "<form", "<iframe", "onclick=", "utm_", "t=6:08")):
        problems.append("The navigation must be static, privacy-preserving and cut-independent")
    if "\u2014" in nav:
        problems.append("No em dashes in new navigation")
    return problems


class DocumentedHandReviewRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/poker/reviewing-a-hand.html").read_text(encoding="utf-8")
        cls.html = (ROOT / "poker/reviewing-a-hand/index.html").read_text(encoding="utf-8")
        cls.pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))

    def test_sources_and_public_page_have_same_three_honest_links(self):
        self.assertEqual(route_errors(self.source), [])
        self.assertEqual(route_errors(self.html), [])
        self.assertEqual(route_nav(self.source), route_nav(self.html))
        self.assertIn(self.source, self.html)
        self.assertIn("Fictional example / No-limit hold'em", self.source)
        self.assertIn("The K-Q example and pot ledger here remain fictional", self.source)
        self.assertIn("Linked tournament accounts report outcomes", self.source)
        self.assertIn("The button faces 5 BB more to call, not 7 BB", self.source)
        self.assertEqual(self.source.count('id="pot-ledger"'), 1)
        self.assertEqual(self.html.count('class="reader-outline-count">6 sections'), 1)

    def test_review_links_resolve_to_original_hand_exercises(self):
        for url in HAND_LINKS:
            with self.subTest(url=url):
                route, anchor = url.split("#")
                original = (ROOT / route.lstrip("/") / "index.html").read_text(encoding="utf-8")
                self.assertEqual(original.count(f'id="{anchor}"'), 1)
                self.assertIn("Reveal the evidence check, not a solver answer",
                              original)
                self.assertIn('href="' + GUIDE + '"', original)

    def test_no_finder_text_or_outline_regression(self):
        s = self.source
        nav = '<nav class="poker-jump" aria-label="' + NAV_LABEL + '">' + route_nav(s) + '</nav>'
        self.assertEqual(s.count(nav), 1)
        stripped = s.replace(nav, "")
        self.assertEqual(poker_finder.GuideText(s).sections,
                         poker_finder.GuideText(stripped).sections)
        self.assertEqual(poker_reading.VisibleHeadings(s).headings,
                         poker_reading.VisibleHeadings(stripped).headings)
        self.assertEqual(len(poker_reading.VisibleHeadings(s).headings), 6)
        self.assertEqual(poker_library.minutes(s), 4)
        css = (ROOT / "assets/poker.css").read_text(encoding="utf-8")
        self.assertIn(".poker-jump a { display:inline-flex; align-items:center; min-height:44px; }", css)

    def test_modification_and_publication_dates_remain_consistent(self):
        page = next(p for p in self.pages if p["path"] == GUIDE)
        self.assertEqual(page["date"], "2026-10-05")
        self.assertEqual(page["updated"], "2026-11-16")
        schema = json.loads(re.search(
            r'<script type="application/ld\+json">([\s\S]*?)</script>', self.html
        ).group(1))
        self.assertEqual(schema["url"], "https://nolankido.com" + GUIDE)
        self.assertEqual(schema["dateModified"], "2026-11-16")
        self.assertIn('Updated <time datetime="2026-11-16">November 16, 2026</time>', self.html)
        self.assertIn("Published October 5, 2026", self.source)
        self.assertIn("Updated October 7", self.source)
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        dates = {item.findtext(ns + "loc"): item.findtext(ns + "lastmod")
                 for item in sitemap}
        self.assertEqual(dates["https://nolankido.com" + GUIDE], "2026-11-16")

    def test_main_generator_reproduces_the_published_page(self):
        built = build.build_outputs()
        self.assertEqual(built[Path("poker/reviewing-a-hand/index.html")], self.html)

    def test_broken_routes_and_dropped_caveats_fail(self):
        source = self.source
        for altered in (
            source.replace(HAND_LINKS[0], "/poker/episodes/none/#hand-64o-review", 1),
            source.replace(HAND_LINKS[2], HAND_LINKS[0], 1),
            source.replace("Recorded hands, not solved strategy:", "Guaranteed best shoves:", 1),
            source.replace('aria-label="' + NAV_LABEL + '"',
                           'aria-label="Unknown hands"', 1),
        ):
            with self.subTest(content=altered[:70]):
                self.assertTrue(route_errors(altered))


if __name__ == "__main__":
    unittest.main()
