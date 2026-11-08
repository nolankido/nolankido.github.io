"""Release checks for the source-bounded AI-and-poker cross-interest case."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import practical_discovery
from reviewed_release import read as reviewed_bytes
import turn35_cross_interest_history as history

RELEASE = "da8de1e4022490c851a618778c564cedaf70f03c"

ROUTE = "/technology/ai-poker-video-evidence/"
SOURCE = ROOT / "_source/technology/ai-poker-video-evidence.html"
OUTPUT = ROOT / "technology/ai-poker-video-evidence/index.html"


class CrossInterestArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.page = next(p for p in cls.pages if p["id"] == "ai-poker-video-evidence")
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.output = OUTPUT.read_text(encoding="utf-8")
        cls.episode = (ROOT / "_source/poker/portland-meadows-ep1.html").read_text(encoding="utf-8")

    def test_explicit_publication_and_single_canonical_identity(self):
        self.assertEqual(sum(p["path"] == ROUTE for p in self.pages), 1)
        self.assertEqual(self.page["date"], "2026-11-04")
        self.assertTrue(self.page["worked_guide"])
        self.assertEqual(practical_discovery.publication_label(self.page), "Worked guide")
        self.assertEqual(self.page["section"], "technology")
        self.assertEqual(self.page["source"], SOURCE.relative_to(ROOT / "_source").as_posix())
        self.assertEqual(sum(p["path"] == ROUTE for p in practical_discovery.articles(self.pages)), 1)
        self.assertIn('<link rel="canonical" href="https://nolankido.com' + ROUTE + '">', self.output)
        self.assertIn('"datePublished": "2026-11-04"', self.output)
        self.assertIn('"@type": "Article"', self.output)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.output)

    def test_real_hand_source_and_arithmetic_before_conclusions(self):
        for text in ("13 players remain with 10 paid", "148,000", "15,000",
                     "585,000", "30,000", "75,000", "6-4 offsuit", "A-K suited",
                     "A-T offsuit", "$5,100", "$2,900"):
            with self.subTest(text=text):
                self.assertIn(text, self.episode)
        self.assertAlmostEqual(148000 / 15000, 9.87, places=2)
        self.assertEqual(585000 / 30000, 19.5)
        self.assertEqual(75000 / 30000, 2.5)
        for fragment in ("≈ 9.87 big blinds", "= 19.5 big blinds", "2.5 big blinds",
                         "gross reported payout, not profit", "solver recommendation"):
            self.assertIn(fragment, self.source)

    def test_three_proposed_captions_have_public_source_links(self):
        self.assertEqual(re.findall(r'data-poker-ai-caption="([^"]+)"', self.source),
                         ["64o", "77", "payout"])
        for anchor in ("hand-64o-record", "hand-77-record", "event-numbers"):
            self.assertIn('/poker/episodes/portland-meadows-ep1/#' + anchor, self.source)
            self.assertIn('id="' + anchor + '"', self.episode)
        self.assertIn("not transcriptions of overlays in the existing video", self.source)
        self.assertIn("not a recovered transcript from a previous model service", self.source)

    def test_evidence_gaps_and_human_approval_remain_visible(self):
        for phrase in ("not</strong> been independently reviewed", "not a parser for the prose captions",
                       "not accepted final graphics", "before any video-edit approval",
                       "constructed examples for this article", "No new poker solver run",
                       "no targeted flags", "does not open YouTube", "human release approval"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.source)
        self.assertNotIn("\u2014", self.source)
        self.assertNotIn("data:text/html", self.source)
        self.assertNotIn("<script", self.source)
        self.assertEqual(self.source.count("<details"), 3)
        self.assertEqual(self.source.count("</details>"), 3)

    def test_source_record_is_explicitly_unapproved(self):
        record = json.loads((ROOT / "downloads/portland-meadows-ep1-scene-claims.json").read_text())
        self.assertEqual(len(record["scenes"]), 3)
        for field in ("current_public_cut_timestamps_checked", "current_public_cut_graphics_checked",
                      "human_release_approval", "confirmed_board_runouts"):
            self.assertIs(record[field], False, field)
        self.assertEqual(record["published_companion_date"], "2026-11-02")
        self.assertIn('datetime="2026-11-02"', self.episode)

    def test_original_readers_have_natural_cross_interest_routes(self):
        for relative, published in (
            ("_source/technology/home.html", "technology/index.html"),
            ("_source/poker/home.html", "poker/index.html"),
            ("_source/about.html", "about/index.html"),
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertEqual(source.count('href="' + ROUTE + '"'), 1, relative)
            self.assertIn('href="' + ROUTE + '"', (ROOT / published).read_text(encoding="utf-8"))

    def test_generated_article_and_discovery_files_are_deterministic(self):
        expected = build.build_outputs()
        self.assertEqual(expected[Path(ROUTE.lstrip("/") + "index.html")], self.output)
        for relative in ("technology/index.html", "poker/index.html", "about/index.html", "find/index.html",
                         "technology/feed.xml", "writing.xml", "sitemap.xml"):
            path = Path(relative)
            self.assertEqual(expected[path], (ROOT / path).read_text(encoding="utf-8"), relative)
        for feed in ("technology/feed.xml", "writing.xml"):
            rss = ET.fromstring((ROOT / feed).read_text(encoding="utf-8"))
            links = [item.text for item in rss.findall("./channel/item/link")]
            self.assertEqual(links.count("https://nolankido.com" + ROUTE), 1)
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        urls = [e.text for e in sitemap.findall("{*}url/{*}loc")]
        self.assertEqual(urls.count("https://nolankido.com" + ROUTE), 1)

    def test_local_fact_gate_reproduces_bounded_result(self):
        tool = "downloads/poker-vlog-fact-gate.py"
        record = "downloads/portland-meadows-ep1-scene-claims.json"
        for args in (("--check", record), ("--self-test",)):
            with self.subTest(args=args):
                command = [sys.executable, tool, *args]
                proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=15)
                self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
                data = json.loads(proc.stdout)
                if args[0] == "--check":
                    self.assertEqual(data["result"], "no_targeted_flags")
                    self.assertEqual(data["findings"], 0)
                    self.assertEqual(len(data["scenes"]), 3)
                else:
                    self.assertTrue(data["self_test_passed"])
                    self.assertEqual(data["flags_before"], 7)
                    self.assertEqual(data["flags_after"], 0)


class CrossInterestHistoryTests(unittest.TestCase):
    def test_every_rewound_file_has_a_verified_git_predecessor(self):
        for name, (older, newer) in history.records()["files"].items():
            with self.subTest(path=name):
                release = reviewed_bytes(RELEASE, name, newer)
                previous = reviewed_bytes(history.PARENT, name, older)
                self.assertEqual(history.before(name, release), previous)
                self.assertEqual(history.before(Path(name), release.decode("utf-8")),
                                 previous.decode("utf-8"))
                self.assertEqual(history.before(name, previous), previous)

    def test_unknown_edits_or_paths_are_never_hidden(self):
        for name in history.records()["files"]:
            current = (ROOT / name).read_bytes()
            for changed in (current + b"UNREVIEWED", current[1:], b"UNREVIEWED" + current):
                self.assertEqual(history.before(name, changed), changed)
            self.assertEqual(history.before("unknown/" + name, current), current)

    def test_added_files_and_page_require_exact_records(self):
        for name, digest in history.records()["added"].items():
            release = reviewed_bytes(RELEASE, name, digest)
            self.assertTrue(history.is_added_file(name, release))
            self.assertFalse(history.is_added_file(name, release + b"UNREVIEWED"))
            self.assertFalse(history.is_added_file("other/" + name, release))
        page = next(p for p in build.public_pages() if p["id"] == "ai-poker-video-evidence")
        self.assertEqual(page, history.records()["page"])
        self.assertEqual(history.pages([page]), [])
        changed = dict(page, title="Unreviewed change")
        self.assertEqual(history.pages([changed]), [changed])

    def test_only_exact_new_live_response_is_removed_from_old_inventory(self):
        name = OUTPUT.relative_to(ROOT).as_posix()
        body = reviewed_bytes(RELEASE, name, history.records()["added"][name])
        self.assertEqual(history.live_targets({ROUTE: (200, body)}), {})
        for altered in ((404, body), (200, body + b"EXTRA"), (200, "text")):
            self.assertEqual(history.live_targets({ROUTE: altered}), {ROUTE: altered})
        self.assertEqual(history.live_targets({"/unknown/": (200, body)}),
                         {"/unknown/": (200, body)})


if __name__ == "__main__":
    unittest.main()
