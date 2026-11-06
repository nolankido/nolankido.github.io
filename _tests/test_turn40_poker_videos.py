"""New published poker video routes are sourced, bounded and discoverable."""
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
import build_player_profile
import check_live
import player_sitemap
import turn40_poker_video_history as history

VIDEOS = (
    "qABaiIcvvpU", "I75GOBVXij4", "bxpaM_1mWPE",
    "HE7VDvO9gDU", "edNSD5BjIV8",
)
NEW = VIDEOS[2:4]
HUB = re.compile(r'<div class="poker-content-grid">(.*?)</div>\s*<p class="small-copy">', re.S)
PROFILE = re.compile(r'<h2 id="player-vlog-title">.*?<ul>(.*?)</ul>', re.S)


def video_errors(source: str, pattern: re.Pattern) -> list[str]:
    section = pattern.search(source)
    if section is None:
        return ["video gallery is missing"]
    block = section.group(1)
    found = re.findall(r'href="https://www.youtube.com/watch\?v=([A-Za-z0-9_-]+)"', block)
    errors = []
    if tuple(found) != VIDEOS:
        errors.append("gallery video order, number or destinations changed")
    if "youtube.com/embed/" in block or "<iframe" in block or "onclick=" in block:
        errors.append("gallery is not link-only")
    for marker in ("Portland Meadows", "Episode 3", "Day 4"):
        if marker not in block:
            errors.append("missing truthful episode label: " + marker)
    return errors


class CurrentPokerVideosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub_source = (ROOT / "_source/poker/home.html").read_text(encoding="utf-8")
        cls.hub = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        cls.player_source = (ROOT / "_source/poker/nolan-kido-profile.html").read_text(encoding="utf-8")
        cls.player = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")

    def test_five_user_supplied_published_video_links_on_both_entry_points(self):
        for value, selector in ((self.hub_source, HUB), (self.hub, HUB),
                                (self.player_source, PROFILE), (self.player, PROFILE)):
            with self.subTest(page=value[:45]):
                self.assertEqual(video_errors(value, selector), [])
                for video in NEW:
                    self.assertEqual(value.count('https://www.youtube.com/watch?v=' + video), 1)
                self.assertNotIn("\u2014", value)
        self.assertIn("Five public video links", self.hub)
        self.assertIn("five linked tournament videos", self.player)

    def test_first_two_companions_remain_separate_from_unchecked_later_cuts(self):
        for value in (self.hub_source, self.player_source):
            self.assertIn("/poker/episodes/portland-meadows-ep1/", value)
            self.assertIn("/poker/episodes/portland-meadows-standoff/", value)
            self.assertIn("not independently", value)
            self.assertNotIn('start=', value)
        self.assertIn("their current titles, cuts and chapter times have not been independently verified", self.hub_source)
        self.assertIn("external metadata and availability were not independently verified", self.player_source)
        self.assertNotIn('WSOP media credential', self.player_source)

    def test_builder_sitemap_and_exact_public_byte_inventory_agree(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.hub)
        self.assertEqual(build_player_profile.render(), self.player)
        self.assertIn(self.player_source, self.player)
        self.assertEqual(player_sitemap.record(ROOT), (player_sitemap.URL, player_sitemap.MODIFIED))
        self.assertEqual(check_live.targets()["/poker/"], (200, self.hub.encode()))
        self.assertEqual(check_live.targets()["/poker/nolan-kido/"], (200, self.player.encode()))
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        hub_modified = next(x["updated"] for x in pages if x["path"] == "/poker/")
        self.assertEqual(self.hub.count('"dateModified": "' + hub_modified + '"'), 1)
        self.assertEqual(self.player.count('"dateModified": "' + player_sitemap.MODIFIED + '"'), 1)
        tree = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        records = {}
        for entry in tree:
            url = next((x.text for x in entry if x.tag.endswith('}loc')), None)
            date = next((x.text for x in entry if x.tag.endswith('}lastmod')), None)
            records[url] = date
        self.assertEqual(records['https://nolankido.com/poker/'], hub_modified)
        self.assertEqual(records[player_sitemap.URL], player_sitemap.MODIFIED)

    def test_broken_duplicate_or_wrong_destination_fails_closed(self):
        for value, selector in ((self.hub_source, HUB), (self.player_source, PROFILE)):
            for version in (
                value.replace("bxpaM_1mWPE", "unverified-id", 1),
                value.replace("HE7VDvO9gDU", "", 1),
                value.replace("https://www.youtube.com/watch?v=bxpaM_1mWPE", "https://invalid.example/video", 1),
                value.replace('Episode 3', 'Unlabeled video'),
            ):
                with self.subTest(sample=version[-130:]):
                    self.assertTrue(video_errors(version, selector))


class CurrentPokerVideoHistoryTests(unittest.TestCase):
    def test_all_reviewed_predecessors_can_be_restored_exactly(self):
        # Turn 41 revises these four pages. Verify the exact historical Turn 40
        # release, not the subsequently edited working copy, against its ledger.
        turn40_release = "be2325c8c539302ed8a55edf63f7314ec696d48e"
        for path, (old_hash, new_hash) in history.records()["files"].items():
            with self.subTest(path=path):
                current = (ROOT / path).read_bytes()
                turn40 = subprocess.check_output(["git", "show", turn40_release + ":" + path], cwd=ROOT)
                prior = subprocess.check_output(["git", "show", history.PARENT + ":" + path], cwd=ROOT)
                self.assertEqual(history.blob(turn40), new_hash)
                self.assertEqual(history.blob(prior), old_hash)
                self.assertEqual(history.before(path, turn40), prior)
                if current != turn40:
                    self.assertEqual(history.before(path, current), prior)

    def test_an_unknown_change_cannot_be_hidden_by_history(self):
        for path in history.records()["files"]:
            current = (ROOT / path).read_bytes()
            self.assertEqual(history.before(path, current + b"UNREVIEWED"), current + b"UNREVIEWED")
            self.assertEqual(history.before("other/" + path, current), current)


if __name__ == "__main__":
    unittest.main()
