"""The new local-AI article cannot erase old reviewed release history."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import turn08_laptop_history as history
from reviewed_release import read as reviewed_bytes


# The November 2 local-AI laptop guide belongs to this immutable Git tree.
# Later Technology, Find and RSS improvements must never be partly reversed
# to manufacture these old successor files from the modern repository.
RELEASE = "fa6a2f7429df991bcea0ef4f204b6e1ec95238da"
RELEASE_TREE = "8027763f346b80f3d2c81ffcdc50efa22d3d072e"
PARENT_TREE = "35d0fc7d2b7651d2ea6c3d47658c4487c26490d8"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT).decode("ascii").strip()


class Turn08HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.added = {path: reviewed_bytes(RELEASE, path, digest)
                     for path, digest in history.ADDED.items()}
        # Use today's files only to check that unknown mutations survive.
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_original_laptop_release_and_parent_are_exact_git_snapshots(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(self.released), set(history.BLOBS))
        self.assertEqual(set(self.added), set(history.ADDED))
        for path, (old_sha, published_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), published_sha)
                self.assertEqual(history.blob(self.parents[path]), old_sha)
        for path, digest in history.ADDED.items():
            with self.subTest(added=path):
                self.assertEqual(history.blob(self.added[path]), digest)

    def test_exact_successor_restores_original_parent_bytes(self):
        for path, (old_sha, published_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = self.released[path]
                self.assertEqual(history.blob(current), published_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, current), previous)
                text = history.before(path, current.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_only_complete_known_new_files_are_excluded(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                raw = self.added[path]
                self.assertEqual(history.blob(raw), sha)
                self.assertEqual(history.source_records({path: raw}), {})
                altered = raw + b"unknown"
                self.assertEqual(history.source_records({path: altered}), {path: altered})
                # File inventory operates on the filesystem. Use a temporary
                # copy of the original release, not the current edited file.
                with TemporaryDirectory() as temporary:
                    copied_root = Path(temporary)
                    copied_path = copied_root / path
                    copied_path.parent.mkdir(parents=True, exist_ok=True)
                    copied_path.write_bytes(raw)
                    with patch.object(history, "ROOT", copied_root):
                        self.assertEqual(history.files([path, "unreviewed.txt"]),
                                         ["unreviewed.txt"])
                        self.assertEqual(history.files((path, "unreviewed.txt")),
                                         ("unreviewed.txt",))
                        copied_path.write_bytes(altered)
                        self.assertEqual(history.files([path, "unreviewed.txt"]),
                                         [path, "unreviewed.txt"])

    def test_live_published_bytes_rewind_only_when_exact(self):
        for route, path in history.ROUTES.items():
            with self.subTest(route=route):
                raw = self.released[path]
                self.assertEqual(history.live_targets({route: (200, raw)}),
                                 {route: (200, history.before(path, raw))})
                self.assertEqual(history.live_targets({route: (200, raw + b"unknown")}),
                                 {route: (200, raw + b"unknown")})
        for route, path in history.ADDED_ROUTES.items():
            with self.subTest(route=route):
                raw = self.added[path]
                self.assertEqual(history.live_targets({route: (200, raw)}), {})
                self.assertEqual(history.live_targets({route: (404, raw)}), {route: (404, raw)})
                self.assertEqual(history.live_targets({route: (200, raw + b"unknown")}),
                                 {route: (200, raw + b"unknown")})

    def test_unreviewed_bytes_and_incorrect_paths_survive(self):
        for label, records in (("release", self.released), ("today", self.current)):
            for path, current in records.items():
                for altered in (current + b"unknown", b"unknown" + current,
                                current[1:], b"\xff\x00"):
                    with self.subTest(revision=label, path=path,
                                      mutation=history.blob(altered)):
                        self.assertEqual(history.before(path, altered), altered)
                text = current.decode("utf-8") + "unknown"
                self.assertEqual(history.before(path, text), text)
                self.assertEqual(history.before("misc/" + path, current), current)
        self.assertEqual(history.before("private.bin", bytes([255, 0])), bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
