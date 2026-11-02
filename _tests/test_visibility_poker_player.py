"""Turn 5 verifies independently sourced player identity without profit claims."""
from pathlib import Path
import unittest

from test_site import ROOT, build

SOURCES = (
    "https://www.wsop.com/players/448066374/nolan-kido/",
    "https://www.globalpokerindex.com/poker-players/nolan-kido-1314580/",
    "https://www.globalpokerindex.com/tournaments/2026/united-states/lucky-300-no-limit-hold-em-1590392/",
)


class PokerPlayerEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/poker/home.html").read_text(encoding="utf-8")
        cls.outputs = build.build_outputs()
        cls.published = cls.outputs[Path("poker/index.html")]

    def test_verified_player_record_appears_in_source_and_published_hub(self):
        start = '<section class="poker-player-evidence"'
        end = "</section>"
        for document in (self.source, self.published):
            self.assertEqual(document.count(start), 1)
            section = document[document.index(start):]
            section = section[:section.index(end) + len(end)]
            self.assertIn('id="nolan-tournament-record-title"', section)
            self.assertIn('June 25, 2026', section)
            self.assertIn('1,652-entry', section)
            self.assertIn('Fifth place', section)
            self.assertIn('13th', section)
            self.assertIn('35th', section)
            for url in SOURCES:
                self.assertIn('href="' + url + '"', section)
            self.assertIn("gross event payouts, not net profit", section)
            self.assertNotIn("profitability", section)
            self.assertNotIn("Circuit ring winner", section)
            self.assertNotIn("homeLocation", section)
        src = self.source.split(start, 1)[1].split(end, 1)[0]
        pub = self.published.split(start, 1)[1].split(end, 1)[0]
        self.assertEqual(src, pub)

    def test_existing_poker_course_and_unpublished_vlog_boundary_remain(self):
        self.assertIn('id="free-course"', self.published)
        self.assertIn('id="watch"', self.published)
        self.assertIn('href="/poker/episodes/portland-meadows-ep1/"', self.published)
        self.assertIn("later tournament episodes are not published here yet.", self.published)
        self.assertIn('href="/poker/reviewing-a-hand/"', self.published)
        self.assertNotIn("\u2014", self.source)


if __name__ == "__main__":
    unittest.main()
