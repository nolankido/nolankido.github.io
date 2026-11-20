"""Turn 154: direct, source-bounded study links inside both published companions.

Both pages have separate builders. Their original article publication dates and
historical source-ledger review dates must not be reset by this navigation edit.
This test does not review current video cuts or solve any live hand.
"""
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build_poker_episode
import build_standoff_episode
import poker_episode
import poker_standoff_episode

EP1_SOURCE = ROOT / "_source/poker/portland-meadows-ep1.html"
STANDOFF_SOURCE = ROOT / "_source/poker/portland-meadows-standoff.html"
HOME = ROOT / "poker/index.html"
STUDY = "/poker/#nolanpoker-hand-study"

LINKS = (
    ("hand-64o-record", "/poker/six-to-ten-bb-tournament-decisions/"),
    ("hand-77-record", "/poker/short-stack-decisions/"),
    ("standoff-second-decision", "/poker/short-stack-decisions/"),
)


def section(html: str, anchor: str) -> str:
    match = re.search(
        r'<section id="' + re.escape(anchor) + r'"[^>]*>(.*?)</section>',
        html, re.S
    )
    if match is None:
        raise AssertionError("Missing hand section: " + anchor)
    return match.group(1)


def direct_links_ok(ep1: str, standoff: str) -> bool:
    if ep1.count('href="' + STUDY + '"') != 2:
        return False
    if standoff.count('href="' + STUDY + '"') != 1:
        return False
    for index, (anchor, url) in enumerate(LINKS):
        body = section(ep1 if index < 2 else standoff, anchor)
        if body.count('href="' + url + '"') != 1:
            return False
        if body.count('href="' + STUDY + '"') != 1:
            return False
    if 'The worked guide does not solve this actual hand.' not in ep1:
        return False
    if 'not a solved range for these opponents.' not in ep1:
        return False
    if 'before flat-calling 15,000, not the stack left facing two shoves' not in standoff:
        return False
    if 'does not prove whether the later call or a fold was best' not in standoff:
        return False
    if any(text in ep1 + standoff for text in ("\u2014", "<iframe", "onclick=", "utm_")):
        return False
    return True


class CompanionStudyRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ep1 = EP1_SOURCE.read_text(encoding="utf-8")
        cls.standoff = STANDOFF_SOURCE.read_text(encoding="utf-8")
        cls.ep1page = (ROOT / poker_episode.OUTPUT).read_text(encoding="utf-8")
        cls.standoffpage = (ROOT / poker_standoff_episode.OUTPUT).read_text(encoding="utf-8")

    def test_three_hand_sections_have_matching_guides_and_return_link(self):
        self.assertTrue(direct_links_ok(self.ep1, self.standoff))
        self.assertTrue(direct_links_ok(self.ep1page, self.standoffpage))
        for index, (anchor, guide) in enumerate(LINKS):
            with self.subTest(anchor=anchor):
                body = section(self.ep1 if index < 2 else self.standoff, anchor)
                self.assertIn('href="' + guide + '"', body)
                self.assertTrue((ROOT / guide.strip("/") / "index.html").is_file())
        self.assertEqual(HOME.read_text(encoding="utf-8").count('id="nolanpoker-hand-study"'), 1)

    def test_manual_renderers_match_committed_pages(self):
        self.assertEqual(build_poker_episode.render(), self.ep1page)
        self.assertEqual(build_standoff_episode.render(), self.standoffpage)
        self.assertEqual(self.ep1page.count(self.ep1), 1)
        self.assertEqual(self.standoffpage.count(self.standoff), 1)

    def test_dates_and_source_provenance_remain_separate(self):
        for registry, page, published in (
            (poker_episode, self.ep1page, "2026-11-02"),
            (poker_standoff_episode, self.standoffpage, "2026-11-04"),
        ):
            with self.subTest(route=registry.ROUTE):
                info = registry.record(ROOT)
                self.assertEqual(info["date"], published)
                self.assertEqual(info["modified"], registry.MODIFIED)
                meta = f'property="article:modified_time" content="{registry.MODIFIED}"'
                self.assertIn(meta, page)
                match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                self.assertIsNotNone(match)
                schema = json.loads(match.group(1))
                self.assertEqual(schema["datePublished"], published)
                self.assertEqual(schema["dateModified"], registry.MODIFIED)
                self.assertEqual(schema["url"], registry.URL)
                self.assertEqual(schema["author"]["@id"],
                                 "https://nolankido.com/about/#nolan-kido")
        self.assertIn('datetime="2026-11-02">November 2, 2026', self.ep1)
        self.assertIn('datetime="2026-11-04">November 4, 2026', self.standoff)
        self.assertIn('datetime="2026-11-20">November 20, 2026', self.ep1)
        self.assertIn('datetime="2026-11-16">November 16, 2026', self.standoff)
        ledger = json.loads((ROOT / "downloads/portland-meadows-ep1-scene-claims.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["reviewed_record_date"], "2026-11-04")

    def test_sitemap_updated_while_original_rss_publication_dates_survive(self):
        xml = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        sitemap = {row.findtext(ns + "loc"): row.findtext(ns + "lastmod") for row in xml}
        for registry in (poker_episode, poker_standoff_episode):
            self.assertEqual(sitemap[registry.URL], registry.MODIFIED)
        for path in ("poker/feed.xml", "writing.xml"):
            rss = ET.fromstring((ROOT / path).read_text(encoding="utf-8"))
            for registry, stamp in (
                (poker_episode, "Mon, 02 Nov 2026 00:00:00 GMT"),
                (poker_standoff_episode, "Wed, 04 Nov 2026 00:00:00 GMT"),
            ):
                items = [row for row in rss.findall("./channel/item")
                         if row.findtext("link") == registry.URL]
                self.assertEqual(len(items), 1)
                self.assertEqual(items[0].findtext("pubDate"), stamp)

    def test_known_false_or_broken_study_routes_are_detected(self):
        mutations = (
            (self.ep1.replace('href="/poker/six-to-ten-bb-tournament-decisions/"',
                              'href="/poker/missing/"', 1), self.standoff),
            (self.ep1.replace('href="/poker/short-stack-decisions/"',
                              'href="/poker/three-to-five-bb-tournament-decisions/"', 1),
             self.standoff),
            (self.ep1.replace('href="' + STUDY + '"', 'href="/poker/"', 1),
             self.standoff),
            (self.ep1, self.standoff.replace('before flat-calling 15,000, not the stack left facing two shoves',
                                             'when facing two shoves', 1)),
        )
        for index, (ep1, standoff) in enumerate(mutations):
            with self.subTest(index=index):
                self.assertFalse(direct_links_ok(ep1, standoff))


if __name__ == "__main__":
    unittest.main()
