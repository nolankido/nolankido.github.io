"""Turn 11 public poker-video routes and identity discovery stay source aligned."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import player_sitemap
VIDEOS = ("qABaiIcvvpU", "I75GOBVXij4", "edNSD5BjIV8")
SOURCE = ROOT / "_source/poker/home.html"
PUBLIC = ROOT / "poker/index.html"
PROFILE_SOURCE = ROOT / "_source/poker/nolan-kido-profile.html"
PROFILE = ROOT / "poker/nolan-kido/index.html"


class PokerVideoDiscoveryTests(unittest.TestCase):
    def test_all_three_public_videos_on_both_poker_entry_points(self):
        for source, published in ((SOURCE, PUBLIC), (PROFILE_SOURCE, PROFILE)):
            authored = source.read_text(encoding="utf-8")
            rendered = published.read_text(encoding="utf-8")
            if source == SOURCE:
                authored_links = authored.split('<div class="poker-content-grid">', 1)[1].split('</div>', 1)[0]
                rendered_links = rendered.split('<div class="poker-content-grid">', 1)[1].split('</div>', 1)[0]
            else:
                authored_links = authored.split('id="player-vlog-title"', 1)[1].split('</ul>', 1)[0]
                rendered_links = rendered.split('id="player-vlog-title"', 1)[1].split('</ul>', 1)[0]
            for video in VIDEOS:
                link = "https://www.youtube.com/watch?v=" + video
                with self.subTest(path=source, video=video):
                    self.assertEqual(authored_links.count(link), 1)
                    self.assertEqual(rendered_links.count(link), 1)
            self.assertNotIn("youtube.com/embed/", authored)
            self.assertNotIn("\u2014", authored)
        self.assertEqual(SOURCE.read_text().count('class="poker-public-video-list"'), 1)
        self.assertEqual(PUBLIC.read_text().count('class="poker-public-video-list"'), 1)

    def test_written_companion_is_not_claimed_for_newer_videos(self):
        for path in (SOURCE, PROFILE_SOURCE):
            content = path.read_text(encoding="utf-8")
            self.assertIn("/poker/episodes/portland-meadows-ep1/", content)
            self.assertIn("source-checked", content)
            self.assertNotIn("start=", content)
            if path == SOURCE:
                self.assertIn("/poker/nolan-kido/", content)

    def test_player_metadata_find_and_sitemap_are_consistent(self):
        html = PROFILE.read_text(encoding="utf-8")
        source = PROFILE_SOURCE.read_text(encoding="utf-8")
        self.assertIn(source, html)
        self.assertIn("Results &amp; Videos", html)
        self.assertNotIn("Vlog Plans", html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(data["dateModified"], player_sitemap.MODIFIED)
        self.assertEqual(data["url"], "https://nolankido.com/poker/nolan-kido/")
        find = (ROOT / "find/index.html").read_text(encoding="utf-8")
        self.assertIn('data-search-title="Nolan Kido: Tournament Poker Player | Results &amp; Videos"', find)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertRegex(sitemap, r'<loc>https://nolankido.com/poker/nolan-kido/</loc>\s*<lastmod>' +
                         player_sitemap.MODIFIED + r'</lastmod>')


if __name__ == "__main__":
    unittest.main()
