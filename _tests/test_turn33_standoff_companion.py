"""Turn 33: one honest standalone Stand Off companion, native discovery and feeds.

These tests inspect source, generated pages and record boundaries. They do not
listen to or compare the currently public YouTube video with the archived v9 cut.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import re
import shutil
import subprocess
import sys
import unittest

from test_site import ROOT, build
import build_poker_episode
import build_standoff_episode
import poker_episode
import poker_standoff_episode
import poker_content
import manual_poker_feed
import follow
import player_sitemap
import player_find
import site_find
import check_live


class StandOffCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / poker_standoff_episode.SOURCE).read_text(encoding="utf-8")
        cls.html = (ROOT / poker_standoff_episode.OUTPUT).read_text(encoding="utf-8")
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()

    def test_manual_page_rebuild_matches_source_and_shared_poker_shell(self):
        self.assertEqual(self.html, build_standoff_episode.render())
        self.assertIn(self.source, self.html)
        self.assertEqual(self.html.count('<h1 '), 1)
        self.assertEqual(self.html.count('aria-label="Breadcrumb"'), 1)
        self.assertNotIn(build.MARKER, self.html)
        self.assertIn("Stand Off companion: edit _source/poker/portland-meadows-standoff.html",
                      self.html)
        self.assertNotIn("\u2014", self.html)
        self.assertNotIn("<iframe", self.html)
        self.assertNotIn("<form", self.html)
        self.assertNotIn("JToB7upHqEM", self.html)
        self.assertIn('href="' + poker_standoff_episode.VIDEO + '"', self.html)
        self.assertIn('href="/poker/episodes/portland-meadows-ep1/"', self.html)

    def test_article_metadata_is_named_canonical_and_truthfully_dated(self):
        record = poker_standoff_episode.record(ROOT)
        self.assertEqual(record["route"], poker_standoff_episode.ROUTE)
        self.assertEqual(record["date"], "2026-11-04")
        self.assertEqual(record["modified"], "2026-11-04")
        self.assertEqual(record["video_url"], poker_standoff_episode.VIDEO)
        self.assertEqual(self.html.count('<link rel="canonical" href="' +
                                         poker_standoff_episode.URL + '">'), 1)
        self.assertIn('property="article:published_time" content="2026-11-04"',
                      self.html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                          self.html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema["@type"], "Article")
        self.assertEqual(schema["@id"], poker_standoff_episode.URL + "#article")
        self.assertEqual(schema["url"], poker_standoff_episode.URL)
        self.assertEqual(schema["datePublished"], "2026-11-04")
        self.assertEqual(schema["dateModified"], "2026-11-04")
        self.assertEqual(schema["author"]["@id"], poker_standoff_episode.PERSON_ID)
        self.assertEqual(schema["mainEntityOfPage"]["breadcrumb"]["itemListElement"][-1]["item"],
                         poker_standoff_episode.URL)

    def test_hand_facts_and_two_separate_decisions_have_explicit_limits(self):
        for anchor in (
            "standoff-intro", "standoff-format", "standoff-first-decision",
            "standoff-second-decision", "standoff-showdown",
            "standoff-hotel-review", "standoff-provenance",
        ):
            self.assertEqual(self.source.count('id="' + anchor + '"'), 1)
        for token in ("15,000", "46,000", "9,000", "61,000", "17 players",
                      "78 entries", "K-K", "Q-Q", "A-K", "Round 10",
                      "not a solver output", "not independently compared"):
            self.assertIn(token.lower(), self.source.lower())
        self.assertIn("The big blind then shoved", self.source)
        self.assertIn("This was the first decision", self.source)
        self.assertIn("This is a different decision", self.source.lower().replace("was a different", "is a different"))
        self.assertIn("current publicly served", self.source.replace("currently public", "current publicly served"))
        self.assertIn("not asserted as current public-video chapter offsets", self.source)
        self.assertNotIn("v=I75GOBVXij4&amp;t=", self.source)
        self.assertNotRegex(self.source, r"youtube\.com/watch\?v=I75GOBVXij4[&?]t=")
        self.assertNotIn("solver proved", self.source)
        self.assertNotIn("net profit", self.source.lower().replace("claim of net poker profit", ""))
        self.assertNotIn("full board was", self.source)

    def test_archived_source_gate_links_are_public_without_private_originals(self):
        for path in (
            "downloads/portland-meadows-standoff-ak-source-ledger.json",
            "downloads/portland-meadows-standoff-ak-gate.py",
            "downloads/poker-vlog-truth-to-screen-qa.md",
        ):
            self.assertTrue((ROOT / path).is_file(), path)
            self.assertIn('href="/' + path + '" download', self.source)
        self.assertNotIn("IMG_2197", self.source)
        self.assertNotIn("Louisiana_Ave", self.source)
        self.assertNotIn(".mp4", self.source.lower())
        self.assertNotIn("<script", self.source)
        self.assertNotIn("<iframe", self.source)
        self.assertNotIn("<form", self.source)

    def test_canonical_is_only_a_manual_publication_not_a_manifest_or_catalog_draft(self):
        self.assertNotIn(poker_standoff_episode.ROUTE, {p["path"] for p in self.pages})
        catalog = poker_content.load(ROOT)
        self.assertEqual(catalog["entries"], [])
        self.assertEqual(poker_standoff_episode.record(ROOT)["url"],
                         poker_standoff_episode.URL)
        with TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertIsNone(poker_standoff_episode.record(root))
            for path in (poker_standoff_episode.SOURCE,
                         poker_standoff_episode.OUTPUT):
                output = root / path
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, output)
            self.assertIsNotNone(poker_standoff_episode.record(root))
            page = root / poker_standoff_episode.OUTPUT
            good = page.read_text(encoding="utf-8")
            variants = (
                good.replace('<link rel="canonical" href="' +
                             poker_standoff_episode.URL + '">',
                             '<link rel="canonical" href="https://example.invalid/">', 1),
                good.replace("<head>", '<head><meta name="robots" content="noindex">', 1),
                good.replace("I have not independently compared",
                             "I have independently compared", 1),
            )
            for modified in variants:
                with self.subTest(change=modified[:45]):
                    self.assertNotEqual(good, modified)
                    page.write_text(modified, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        poker_standoff_episode.record(root)
            page.write_text(good, encoding="utf-8")
            (root / poker_standoff_episode.SOURCE).unlink()
            with self.assertRaises(ValueError):
                poker_standoff_episode.record(root)

    def test_poker_hub_player_and_find_include_new_authored_route(self):
        hub = self.outputs[Path("poker/index.html")]
        player = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")
        find = self.outputs[Path("find/index.html")]
        for page in (hub, player, find):
            self.assertIn('href="' + poker_standoff_episode.ROUTE + '"', page)
        self.assertIn("archived v9", hub)
        self.assertIn("Reserve Day 1 does not yet have a written hand companion", player)
        entries = player_find.add(ROOT, site_find.entries(ROOT, self.pages))
        manual = [e for e in entries if e["path"] == poker_standoff_episode.ROUTE]
        self.assertEqual(len(manual), 1)
        self.assertEqual(manual[0]["kind"], "episode")
        self.assertEqual(manual[0]["interests"], ["poker"])
        self.assertEqual(manual[0]["date"], "2026-11-04")
        self.assertIn('id="browse-poker"><summary>Poker <span class="find-group-count" hidden>(95)</span>', find)
        self.assertEqual(find, (ROOT / "find/index.html").read_text(encoding="utf-8"))

    def test_sitemap_live_targets_and_feeds_have_one_public_article_each(self):
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        sitemap = self.outputs[Path("sitemap.xml")]
        items = ET.fromstring(sitemap)
        records = {x.findtext(ns + "loc"): x.findtext(ns + "lastmod")
                   for x in items}
        self.assertEqual(records[poker_standoff_episode.URL], "2026-11-04")
        self.assertEqual(list(records).count(poker_standoff_episode.URL), 1)
        self.assertEqual(sitemap, (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual(records[player_sitemap.URL], player_sitemap.MODIFIED)
        targets = check_live.targets()
        self.assertEqual(targets[poker_standoff_episode.ROUTE],
                         (200, (ROOT / poker_standoff_episode.OUTPUT).read_bytes()))
        for name in ("poker/feed.xml", "writing.xml"):
            feed = ET.fromstring(self.outputs[Path(name)])
            matches = [item for item in feed.findall("./channel/item")
                       if item.findtext("link") == poker_standoff_episode.URL]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].findtext("pubDate"),
                             "Wed, 04 Nov 2026 00:00:00 GMT")
            self.assertEqual(self.outputs[Path(name)],
                             (ROOT / name).read_text(encoding="utf-8"))
        first = ET.fromstring(self.outputs[Path("poker/feed.xml")]).find("./channel/item")
        self.assertEqual(first.findtext("link"), poker_standoff_episode.URL)
        combined = follow.combined(self.outputs, self.pages,
                                   "https://nolankido.com", ROOT)
        self.assertEqual(combined, self.outputs[Path("writing.xml")])

    def test_public_builder_never_claims_video_av_certification(self):
        self.assertIn("not a frame-by-frame audit", self.source)
        self.assertIn("A-K", self.source)
        self.assertNotIn("Chapter 1: 0:21", self.source)
        self.assertNotIn("v=I75GOBVXij4&t=", self.source)
        self.assertEqual(build_standoff_episode.render(), self.html)


if __name__ == "__main__":
    unittest.main()
