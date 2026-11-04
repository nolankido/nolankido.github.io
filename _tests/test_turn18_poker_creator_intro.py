"""Turn 18: the event-ready poker introduction is factual and source-compiled."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build_player_profile as profile
import turn18_poker_creator_history as history

SOURCE = ROOT / "_source/poker/nolan-kido-profile.html"
PUBLISHED = ROOT / "poker/nolan-kido/index.html"

class Turn18PokerCreatorTests(unittest.TestCase):
    def test_compiled_page_preserves_exact_authored_section(self):
        source = SOURCE.read_text(encoding="utf-8")
        html = PUBLISHED.read_text(encoding="utf-8")
        self.assertEqual(profile.render(), html)
        self.assertIn(source, html)
        self.assertEqual(source.count('id="creator-introduction"'), 1)
        self.assertEqual(html.count('id="creator-introduction"'), 1)
        self.assertEqual(source.count(history.INSERTION), 1)
        self.assertEqual(html.count(history.INSERTION), 1)
        self.assertNotIn("\u2014", source)
        self.assertNotIn("<form", source.lower())
        self.assertNotIn("<script", source.lower())
        self.assertIn('"dateModified": "2026-11-03"', html)
        self.assertIn('<link rel="canonical" href="' + profile.URL + '">', html)

    def test_independent_records_stay_separate_from_media(self):
        section = history.INSERTION
        urls = (
            "https://pokerdb.thehendonmob.com/event.php?a=r&amp;n=1399113",
            "https://www.wsop.com/tournaments/result/17989/",
            "https://www.wsop.com/tournaments/result/18650/",
        )
        for url in urls:
            self.assertEqual(section.count('href="' + url + '"'), 1)
        for phrase in ("fifth place", "13th", "20th", "independent event listings",
                       "self-published media", "net profit", "official media credentials",
                       "/contact/", "/poker/episodes/portland-meadows-ep1/"):
            self.assertIn(phrase, section)
        self.assertNotIn("Circuit ring winner", section)
        self.assertIn("not an affiliation with or endorsement by WSOP", section)

    def test_existing_videos_and_sources_are_unchanged(self):
        source = SOURCE.read_text(encoding="utf-8")
        for video_id in ("qABaiIcvvpU", "I75GOBVXij4", "edNSD5BjIV8"):
            self.assertEqual(source.count("watch?v=" + video_id), 1)
        self.assertNotIn("youtube.com/embed/", source)
        self.assertIn('id="player-record-title"', source)
        self.assertIn('id="player-sources-title"', source)
        self.assertIn("gross payout, not net profit", source)
        self.assertIn("no source-checked companion here yet", source)
        self.assertEqual(len(re.findall(r'<h1\b', PUBLISHED.read_text(encoding="utf-8"))), 1)

    def test_predecessor_is_exact_and_mutations_are_visible(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            current = (ROOT / path).read_bytes()
            self.assertEqual(history.blob(current), new_sha)
            previous = history.before(path, current)
            self.assertEqual(history.blob(previous), old_sha)
            self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                             previous.decode("utf-8"))
            self.assertEqual(history.before(path, previous), previous)
            for altered in (current + b"UNREVIEWED", b"UNREVIEWED" + current, current[1:]):
                self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before("other/" + path, current), current)

if __name__ == "__main__":
    unittest.main()
