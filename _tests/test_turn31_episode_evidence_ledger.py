"""Turn 31: a checkable proposed overlay ledger for a public poker episode.

The public video is not parsed by these tests. Synthetic error cases are
deliberately constructed. Publication dates and user provenance stay distinct.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

from test_site import ROOT, build
import build_poker_episode
import poker_episode
import turn32_standoff_source_history as turn32


SOURCE = ROOT / "_source/poker/portland-meadows-ep1.html"
PUBLIC = ROOT / poker_episode.OUTPUT
LEDGER = ROOT / "downloads/portland-meadows-ep1-scene-claims.json"
GATE = ROOT / "downloads/poker-vlog-fact-gate.py"
SHEET = ROOT / "downloads/poker-vlog-truth-to-screen-qa.md"
LEDGER_ID = "episode-evidence-ledger"
BASE = "0906e6ae2d51b062dd6d3bf34b86d6be6e432657"


def section(body):
    mark = '<section id="' + LEDGER_ID + '" aria-labelledby="episode-evidence-ledger-title">'
    if body.count(mark) != 1:
        raise AssertionError("Episode source needs one evidence-ledger section")
    first = body.index(mark)
    return body[first:body.index("</section>", first) + len("</section>")]


class Tags(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unbalanced ledger markup at " + tag)


def run_gate(*args):
    return subprocess.run([sys.executable, str(GATE), *map(str, args)],
                          capture_output=True, text=True)


class EpisodeEvidenceLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.html = PUBLIC.read_text(encoding="utf-8")
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_same_readable_ledger_in_manual_source_and_published_page(self):
        html = section(self.html)
        self.assertEqual(html, section(self.source))
        self.assertEqual(self.html.count('id="' + LEDGER_ID + '"'), 1)
        self.assertEqual(html.count("<dt>"), 3)
        self.assertEqual(html.count("</dd>"), 3)
        self.assertIn('href="/downloads/portland-meadows-ep1-scene-claims.json" download', html)
        self.assertIn('href="/downloads/poker-vlog-fact-gate.py" download', html)
        self.assertIn('href="/downloads/poker-vlog-truth-to-screen-qa.md" download', html)
        self.assertIn("not a claim that the currently published YouTube cut", html)
        self.assertIn("not", html.lower())
        self.assertNotIn("\u2014", html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("<iframe", html.lower())
        self.assertNotIn("<form", html.lower())
        tag_parser = Tags()
        tag_parser.feed(html)
        self.assertEqual(tag_parser.stack, [])
        for frag in ("hand-64o-record", "hand-77-record", "event-numbers"):
            self.assertEqual(self.html.count('id="' + frag + '"'), 1)
            self.assertIn('href="#' + frag + '"', html)

    def test_download_is_a_proposal_and_facts_are_bounded_by_existing_hands(self):
        doc = self.ledger
        self.assertEqual(doc["schema_version"], 1)
        self.assertEqual(doc["video_url"], poker_episode.VIDEO)
        self.assertEqual(doc["companion_url"], poker_episode.URL)
        self.assertEqual(doc["published_companion_date"], poker_episode.PUBLISHED)
        self.assertEqual(doc["reviewed_record_date"], poker_episode.MODIFIED)
        self.assertEqual(doc["human_release_approval"], False)
        self.assertFalse(doc["current_public_cut_timestamps_checked"])
        self.assertFalse(doc["current_public_cut_graphics_checked"])
        self.assertFalse(doc["event_calendar_date_independently_verified"])
        self.assertFalse(doc["confirmed_board_runouts"])
        self.assertIn("not an audit of the current audiovisual cut", doc["record_kind"])
        scenes = doc["scenes"]
        self.assertEqual([s["case"] for s in scenes],
                         ["hand_64o", "hand_77", "event_payout"])
        self.assertEqual(scenes[0]["stack_bb_display"], 9.87)
        self.assertAlmostEqual(scenes[0]["reported_stack_chips"] / scenes[0]["big_blind_chips"], 9.87, delta=0.01)
        self.assertEqual(scenes[1]["reported_stack_chips"] / scenes[1]["big_blind_chips"], 19.5)
        self.assertEqual(scenes[1]["button_open_to_chips"] / scenes[1]["big_blind_chips"], 2.5)
        self.assertEqual(scenes[2]["advertised_first_usd"], 5100)
        self.assertEqual(scenes[2]["received_after_deal_usd"], 2900)
        self.assertFalse(scenes[2]["net_profit_claimed"])
        for hand in scenes[:2]:
            self.assertTrue(hand["stack_marked_approximate"])
            for field in ("individual_suits_displayed", "full_board_displayed",
                          "solver_verdict_claimed_verified",
                          "archived_v7_timecode_reused_for_current_cut"):
                self.assertIs(hand[field], False)

    def test_existing_public_fact_gate_accepts_only_scoped_proposals(self):
        self.assertTrue(SHEET.is_file())
        accepted = run_gate("--check", LEDGER)
        self.assertEqual(accepted.returncode, 0, accepted.stderr + accepted.stdout)
        data = json.loads(accepted.stdout)
        self.assertEqual(data["result"], "no_targeted_flags")
        self.assertEqual(data["findings"], 0)
        self.assertEqual([s["case"] for s in data["scenes"]],
                         ["hand_64o", "hand_77", "event_payout"])
        self.assertIn("Human review is required", data["limit"])
        demo = run_gate("--self-test")
        self.assertEqual(demo.returncode, 0, demo.stderr + demo.stdout)
        self.assertTrue(json.loads(demo.stdout)["self_test_passed"])
        self.assertIn("not model outputs", json.loads(demo.stdout)["demo"])

    def test_wrong_visuals_stack_payout_and_stale_offsets_are_flagged(self):
        changes = [
            ("invented suits", "hand_64o", "individual_suits_displayed", True, "UNVERIFIED_SUITS"),
            ("wrong BB", "hand_77", "stack_bb_display", 16.0, "STACK_BB_MISMATCH"),
            ("fake precision", "hand_77", "stack_marked_approximate", False, "STACK_PRECISION"),
            ("stale v7 offset", "hand_64o", "archived_v7_timecode_reused_for_current_cut", True, "STALE_TIMECODE"),
            ("paid prize substituted", "event_payout", "received_after_deal_usd", 5100, "FACT_CONFLICT"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "scene.json"
            for label, case, key, value, expected in changes:
                with self.subTest(label=label):
                    data = json.loads(LEDGER.read_text(encoding="utf-8"))
                    scene = next(s for s in data["scenes"] if s["case"] == case)
                    scene[key] = value
                    file.write_text(json.dumps(data), encoding="utf-8")
                    result = run_gate("--check", file)
                    self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                    codes = {f["code"] for s in json.loads(result.stdout)["scenes"]
                             for f in s["findings"]}
                    self.assertIn(expected, codes)
            file.write_text("{bad json", encoding="utf-8")
            invalid = run_gate("--check", file)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("Input error", invalid.stderr)

    def test_manual_builder_article_identity_and_revision_metadata(self):
        self.assertEqual(self.html, build_poker_episode.render())
        info = poker_episode.record(ROOT)
        self.assertEqual(info["route"], poker_episode.ROUTE)
        self.assertEqual(info["date"], "2026-11-02")
        self.assertEqual(info["modified"], "2026-11-04")
        self.assertIn('property="article:published_time" content="2026-11-02"', self.html)
        self.assertIn('property="article:modified_time" content="2026-11-04"', self.html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                          self.html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema["datePublished"], "2026-11-02")
        self.assertEqual(schema["dateModified"], "2026-11-04")
        self.assertEqual(schema["author"]["@id"], poker_episode.PERSON_ID)
        self.assertIn('rel="canonical" href="' + poker_episode.URL + '"', self.html)
        self.assertNotIn("JToB7upHqEM", self.html)

    def test_only_episode_lastmod_changes_and_rss_publication_is_preserved(self):
        older = subprocess.check_output(
            ["git", "show", BASE + ":sitemap.xml"], cwd=ROOT
        ).decode("utf-8")
        current = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        def rows(text):
            return {
                node.findtext(ns + "loc"): node.findtext(ns + "lastmod")
                for node in ET.fromstring(text)
            }
        before, after = rows(older), rows(turn32.before("sitemap.xml", current))
        self.assertEqual(set(before), set(after))
        self.assertEqual({url for url in before if before[url] != after[url]},
                         {poker_episode.URL})
        self.assertEqual(after[poker_episode.URL], "2026-11-04")
        self.assertEqual(build.build_outputs()[Path("sitemap.xml")], current)
        for feed in ("poker/feed.xml", "writing.xml"):
            xml = ET.fromstring((ROOT / feed).read_text(encoding="utf-8"))
            episodes = [item for item in xml.findall("./channel/item")
                        if item.findtext("link") == poker_episode.URL]
            self.assertEqual(len(episodes), 1)
            self.assertEqual(episodes[0].findtext("pubDate"),
                             "Mon, 02 Nov 2026 00:00:00 GMT")

    def test_manual_live_check_includes_all_three_public_downloads(self):
        import check_live
        targets = check_live.targets()
        for file in (LEDGER, GATE, SHEET):
            with self.subTest(path=file.name):
                route = "/" + file.relative_to(ROOT).as_posix()
                self.assertEqual(targets[route], (200, file.read_bytes()))


if __name__ == "__main__":
    unittest.main()
