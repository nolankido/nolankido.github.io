"""Turn 11 video discovery preserves its exact original Git release."""

import subprocess
import unittest
from pathlib import Path

from reviewed_release import read as reviewed_bytes
import turn11_video_discovery_history as history


# The reviewed public-video discovery was committed before later Poker,
# player-profile, search and test improvements. Today's bytes do not
# represent the Turn 11 successor snapshot.
RELEASE = "0122add1160f88dd3ef48024067f6fbd77cbbf37"
RELEASE_TREE = "2540b122250a2d12bbb03429564cda61580cd2d5"
PARENT_TREE = "95b6a22c12b7a3a7a3b3070d5c6f7e0ad4110aba"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT).decode("ascii").strip()


class Turn11VideoDiscoveryHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_original_video_discovery_release_has_exact_git_tree_and_blobs(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), new_sha)
                self.assertEqual(history.blob(self.parents[path]), old_sha)

    def test_only_exact_published_files_restore_the_parent(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = self.released[path]
                self.assertEqual(history.blob(raw), new_sha)
                original = history.before(path, raw)
                self.assertEqual(history.blob(original), old_sha)
                self.assertEqual(original, self.parents[path])
                self.assertEqual(history.before(path, original), original)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, raw), original)
                text = history.before(path, raw.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, original.decode("utf-8"))

    def test_mutations_and_wrong_paths_are_not_hidden(self):
        for revision, records in (("release", self.released), ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"UNKNOWN", b"UNKNOWN" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                text = raw.decode("utf-8") + "UNKNOWN"
                self.assertEqual(history.before(path, text), text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unrelated.bin", bytes([255, 0])),
                         bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
