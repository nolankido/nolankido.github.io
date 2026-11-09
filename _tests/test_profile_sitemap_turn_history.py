"""Verify the original player-sitemap release and today's independent route."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

import profile_sitemap_turn_history as history
from reviewed_release import read as reviewed_bytes


# The November 1 sitemap integration predates later edits to builders,
# checkers, tests, the generated sitemap and the standalone player page.
# Its strict predecessor adapter requires these immutable Git release bytes.
SITEMAP_RELEASE = "86018bb5245684c153e26ec94a4131537d6264a7"
SITEMAP_PARENT = "de5d684a5f74b251ccf9520760fe5d8ac8b66fbe"
RELEASE_TREE = "a7e5bdb67299f1e803cf7aaf5f47457453ce35ea"
PARENT_TREE = "7c6c6e3d7b3dec577b3a833756bc2656a6e17244"
PROFILE_FILE = "poker/nolan-kido/index.html"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT).decode("ascii").strip()


class PlayerSitemapHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {
            path: reviewed_bytes(SITEMAP_RELEASE, path, item["new"])
            for path, item in history.REVISIONS.items()
        }
        cls.predecessors = {
            path: reviewed_bytes(SITEMAP_PARENT, path, item["old"])
            for path, item in history.REVISIONS.items()
        }
        cls.added = {
            path: reviewed_bytes(SITEMAP_RELEASE, path, expected)
            for path, expected in history.ADDED_FILES.items()
        }
        cls.player = reviewed_bytes(
            SITEMAP_RELEASE, PROFILE_FILE, history.PLAYER_BLOB)

    def test_exact_release_parent_and_added_file_inventory(self):
        self.assertEqual(git_revision(SITEMAP_RELEASE + "^"), SITEMAP_PARENT)
        self.assertEqual(git_revision(SITEMAP_RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(SITEMAP_PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(len(history.REVISIONS), 6)
        self.assertEqual(set(history.ADDED_FILES), {
            "_scripts/player_sitemap.py", "_tests/test_player_sitemap.py",
        })
        self.assertEqual(reviewed_bytes(
            SITEMAP_PARENT, PROFILE_FILE, history.PLAYER_BLOB), self.player)
        for name in history.ADDED_FILES:
            with self.subTest(added=name):
                self.assertEqual(subprocess.check_output(
                    ["git", "ls-tree", SITEMAP_PARENT, "--", name],
                    cwd=history.ROOT), b"")

    def test_only_exact_published_successor_blobs_can_be_restored(self):
        for name, item in history.REVISIONS.items():
            with self.subTest(path=name):
                current = self.released[name]
                self.assertEqual(history.blob(current), item["new"])
                previous = history.before(name, current)
                self.assertEqual(history.blob(previous), item["old"])
                self.assertEqual(previous, self.predecessors[name])
                self.assertEqual(history.before(name, previous), previous)
                self.assertEqual(history.before(Path(name), current.decode("utf-8")),
                                 previous.decode("utf-8"))
                for corrupt in (current + b"UNKNOWN", b"UNKNOWN" + current, current[1:]):
                    self.assertEqual(history.before(name, corrupt), corrupt)
                self.assertEqual(history.before("unrelated/" + name, current), current)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_only_exact_added_files_are_hidden_from_old_inventories(self):
        for name, reviewed_sha in history.ADDED_FILES.items():
            with self.subTest(path=name):
                original = self.added[name]
                self.assertEqual(history.blob(original), reviewed_sha)
                self.assertEqual(history.source_records({name: original}), {})
                changed = original + b"unknown"
                self.assertEqual(history.source_records({name: changed}),
                                 {name: changed})
                # The real files have legitimate later edits. Test the file
                # filtering against temporary copies of the reviewed blobs.
                with TemporaryDirectory() as tmp:
                    target = Path(tmp) / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(original)
                    with patch.object(history, "ROOT", Path(tmp)):
                        self.assertEqual(history.files([name, "unrelated.txt"]),
                                         ["unrelated.txt"])
                        target.write_bytes(changed)
                        self.assertEqual(history.files([name, "unrelated.txt"]),
                                         [name, "unrelated.txt"])
        self.assertEqual(history.source_records({"other.bin": b"hello"}),
                         {"other.bin": b"hello"})

    def test_live_record_removed_from_old_targets_only_for_exact_bytes(self):
        name = history.PROFILE_ROUTE
        public = self.player
        self.assertEqual(history.blob(public), history.PLAYER_BLOB)
        self.assertEqual(history.live_targets({name: (200, public)}), {})
        for response in ((404, public), (200, public + b"unknown"),
                         (200, "wrong"), (200, None)):
            self.assertEqual(history.live_targets({name: response}),
                             {name: response})
        self.assertEqual(history.live_targets({"/unrelated/": (200, public)}),
                         {"/unrelated/": (200, public)})

    def test_current_sitemap_and_public_pages_still_link_player(self):
        url = "https://nolankido.com" + history.PROFILE_ROUTE
        sitemap = ET.fromstring((history.ROOT / "sitemap.xml").read_bytes())
        urls = [node.text for node in sitemap.iter()
                if node.tag.endswith("}loc")]
        self.assertEqual(urls.count(url), 1)
        self.assertTrue((history.ROOT / PROFILE_FILE).is_file())
        for page in ("poker/index.html", "about/index.html"):
            with self.subTest(page=page):
                self.assertIn('href="' + history.PROFILE_ROUTE + '"',
                              (history.ROOT / page).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
