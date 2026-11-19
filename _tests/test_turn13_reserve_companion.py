"""Turn 13: source-bounded WSOP Circuit Reserve Day 1 companion contracts.

The archived v8 production notes were reviewed editorially; these local tests
do not establish that the current YouTube footage matches the older source.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import re
import unittest

from test_site import ROOT, build
import build_reserve_day1_episode
import poker_reserve_day1_episode as reserve
import check_live
import player_find
import player_sitemap


class ReserveCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = (ROOT / reserve.SOURCE).read_text(encoding="utf-8")
        cls.html = (ROOT / reserve.OUTPUT).read_text(encoding="utf-8")
        cls.ledger = json.loads((ROOT / reserve.LEDGER).read_text(encoding="utf-8"))

    def test_same_standalone_source_and_no_unsafe_embedding(self):
        self.assertEqual(self.html, build_reserve_day1_episode.render())
        self.assertEqual(self.html.count(self.body), 1)
        self.assertEqual(self.html.count('<h1 '), 1)
        self.assertIn("Reserve Day 1 companion: edit _source/poker/reserve-day-1.html", self.html)
        self.assertNotIn(build.MARKER, self.html)
        self.assertNotIn("\u2014", self.html)
        self.assertNotRegex(self.body.lower(), r"<iframe|<script|<form")
        self.assertEqual(self.body.count('href="' + reserve.VIDEO + '"'), 1)
        self.assertNotIn("youtube.com/watch?v=edNSD5BjIV8&t=", self.body)

    def test_canonical_person_dates_and_breadcrumb(self):
        info = reserve.record(ROOT)
        self.assertEqual(info["route"], reserve.ROUTE)
        self.assertEqual(info["date"], "2026-11-18")
        self.assertEqual(info["modified"], "2026-11-18")
        self.assertEqual(self.html.count('<link rel="canonical" href="' + reserve.URL + '">'), 1)
        self.assertIn('property="article:published_time" content="2026-11-18"', self.html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema["@type"], "Article")
        self.assertEqual(schema["@id"], reserve.URL + "#article")
        self.assertEqual(schema["url"], reserve.URL)
        self.assertEqual(schema["datePublished"], reserve.PUBLISHED)
        self.assertEqual(schema["dateModified"], reserve.MODIFIED)
        self.assertEqual(schema["author"]["@id"], reserve.PERSON_ID)
        self.assertEqual(schema["mainEntityOfPage"]["breadcrumb"]["itemListElement"][-1]["item"], reserve.URL)

    def test_independent_finish_is_gross_and_matches_public_ledger(self):
        event, finish = self.ledger["event"], self.ledger["finish"]
        self.assertEqual((event["buy_in_usd"], event["entries"], event["paid_places"]),
                         (400, 527, 80))
        self.assertEqual((finish["place"], finish["gross_cash_usd"]), (63, 800))
        self.assertIsNone(finish["net_profit_usd"])
        self.assertIsNone(finish["total_entries_purchased"])
        for url in [event["official_url"], *finish["sources"]]:
            self.assertIn('href="' + url.replace("&", "&amp;") + '"', self.body)
        self.assertIn("gross payout", self.body)
        self.assertIn("not an independently audited count of purchases", self.body)

    def test_hand_boundary_and_matched_layers_are_consistent(self):
        video = self.ledger["video"]
        self.assertFalse(video["current_youtube_cut_compared_with_archive"])
        self.assertFalse(video["current_youtube_chapter_offsets_verified"])
        self.assertIn("have not independently compared", self.body)
        self.assertIn("not asserted as current public-video chapter", self.body)
        for anchor in ("reserve-intro", "reserve-event", "reserve-bubble",
                       "reserve-ak-action", "reserve-pots", "reserve-last-hand",
                       "reserve-questions", "reserve-evidence"):
            self.assertEqual(self.body.count('id="' + anchor + '"'), 1)
        hands = {hand["id"]: hand for hand in self.ledger["narrated_decisions"]}
        self.assertIsNone(hands["small_blind_j9"]["reported_action"])
        self.assertIsNone(hands["three_way_ak"]["solver_verdict"])
        self.assertFalse(hands["three_way_ak"]["complete_board_known"])
        self.assertFalse(hands["three_way_ak"]["opponent_suit_combinations_known"])
        layers = hands["three_way_ak"]["illustrative_layer_bb"]
        self.assertEqual(layers["three_way_matched_per_player"], 7)
        self.assertEqual(layers["two_way_extra_matched_per_larger_player"], 18 - 7)
        self.assertEqual(layers["hero_uncalled_return"], 28 - 18)
        self.assertEqual(94 - 80, 14)
        self.assertIn("Q-J offsuit", self.body)
        self.assertIn("A♣K♥", self.body)
        self.assertIn("9♦10♦", self.body)
        self.assertNotIn("a solver proved", self.body.lower())

    def test_native_hub_profile_search_and_archive_entries(self):
        hub = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        profile = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")
        for html in (hub, profile):
            self.assertIn('href="' + reserve.ROUTE + '"', html)
        entry = player_find.reserve_day1_entry(ROOT)
        self.assertEqual(entry["path"], reserve.ROUTE)
        self.assertEqual(entry["kind"], "episode")
        self.assertEqual(entry["date"], reserve.PUBLISHED)
        self.assertIn(reserve.ROUTE, {e["path"] for e in player_find.add(ROOT, [])})
        self.assertIn(reserve.ROUTE, check_live.targets())
        self.assertIn("/" + reserve.LEDGER.as_posix(), check_live.targets())

    def test_sitemap_and_feeds_have_one_canonical_item(self):
        sitemap = ET.parse(ROOT / "sitemap.xml")
        ns = {"x": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [e.text for e in sitemap.findall("./x:url/x:loc", ns)]
        self.assertEqual(urls.count(reserve.URL), 1)
        self.assertEqual(player_sitemap.MODIFIED, "2026-11-18")
        for name in ("poker/feed.xml", "writing.xml"):
            rss = ET.parse(ROOT / name)
            items = rss.findall("./channel/item")
            self.assertEqual([e.findtext("link") for e in items].count(reserve.URL), 1)
            item = next(e for e in items if e.findtext("link") == reserve.URL)
            self.assertIn("18 Nov 2026", item.findtext("pubDate"))

    def test_incomplete_public_record_is_rejected(self):
        with TemporaryDirectory() as location:
            root = Path(location)
            for relative in (reserve.SOURCE, reserve.OUTPUT, reserve.LEDGER):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            self.assertIsNotNone(reserve.record(root))
            source = root / reserve.SOURCE
            source.write_text(self.body.replace("have not independently compared", "did verify the video"), encoding="utf-8")
            with self.assertRaises(ValueError):
                reserve.record(root)
            source.write_text(self.body, encoding="utf-8")
            data = json.loads((root / reserve.LEDGER).read_text(encoding="utf-8"))
            data["video"]["current_youtube_cut_compared_with_archive"] = True
            (root / reserve.LEDGER).write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                reserve.record(root)


if __name__ == "__main__":
    unittest.main()
