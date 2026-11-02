"""Manual Poker episode RSS uses only the reviewed public source and date."""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import shutil
import unittest

from test_site import ROOT, build
import follow
import manual_poker_feed
import poker_content
import poker_episode


class PublishedEpisodeFeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()

    def test_approved_portland_video_is_one_real_rss_item(self):
        original = poker_content.feed(self.pages, "https://nolankido.com")
        actual = self.outputs[Path("poker/feed.xml")]
        self.assertEqual(manual_poker_feed.add(original, ROOT), actual)
        self.assertEqual((ROOT / "poker/feed.xml").read_text(encoding="utf-8"), actual)
        items = ET.fromstring(actual).findall("./channel/item")
        relevant = [item for item in items if item.findtext("link") == poker_episode.URL]
        self.assertEqual(len(relevant), 1)
        self.assertEqual(items[0].findtext("link"), poker_episode.URL)
        self.assertEqual(relevant[0].findtext("guid"), poker_episode.URL)
        self.assertEqual(relevant[0].findtext("pubDate"), "Mon, 02 Nov 2026 00:00:00 GMT")
        self.assertIn("6-4 versus A-K", relevant[0].findtext("description"))

    def test_combined_writing_feed_copies_episode_once_with_source_provenance(self):
        combined = follow.combined(self.outputs, self.pages, "https://nolankido.com", ROOT)
        self.assertEqual(combined, self.outputs[follow.OUTPUT])
        self.assertEqual(combined, (ROOT / "writing.xml").read_text(encoding="utf-8"))
        channel = ET.fromstring(combined).find("channel")
        self.assertEqual(channel.findtext("pubDate"), "Mon, 02 Nov 2026 00:00:00 GMT")
        items = channel.findall("item")
        relevant = [item for item in items if item.findtext("link") == poker_episode.URL]
        self.assertEqual(len(relevant), 1)
        self.assertEqual(relevant[0].find("source").get("url"), "https://nolankido.com/poker/feed.xml")
        self.assertEqual(relevant[0].find("source").text, "Nolan Kido Poker")

    def test_unpublished_episode_is_never_injected_and_duplicate_rejected(self):
        old = poker_content.feed(self.pages, "https://nolankido.com")
        with TemporaryDirectory() as directory:
            self.assertEqual(manual_poker_feed.add(old, Path(directory)), old)
            root = Path(directory)
            for path in (poker_episode.SOURCE, poker_episode.OUTPUT):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertEqual(manual_poker_feed.add(old, root), self.outputs[Path("poker/feed.xml")])
            with self.assertRaisesRegex(ValueError, "twice"):
                manual_poker_feed.add(self.outputs[Path("poker/feed.xml")], root)
            (root / poker_episode.SOURCE).unlink()
            with self.assertRaises(ValueError):
                manual_poker_feed.add(old, root)


if __name__ == "__main__":
    unittest.main()
