"""Turn 12 cross-platform identity history uses its exact reviewed Git release."""

import subprocess
import unittest
from pathlib import Path

from reviewed_release import read as reviewed_bytes
import turn12_cross_platform_history as history


# The Substack and NolanPoker identity links were released before later
# About, homepage, profile and historical-test improvements. Today's site
# bytes are not the Turn 12 successor snapshot.
RELEASE = "3f53b3aacd43a4be0e3fd71d8bae6faa87d40532"
RELEASE_TREE = "a775d2be5992bae9de675f289dd18f67de7d63ac"
PARENT_TREE = "b45acb1f0dc897abf1f66bcf967ad5be6e4ee3f6"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class Turn12CrossPlatformHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_original_identity_release_matches_parent_and_git_blobs(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), new_sha)
                self.assertEqual(history.blob(self.parents[path]), old_sha)

    def test_only_original_successor_blobs_restore_the_committed_parent(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(history.blob(released), new_sha)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_unknown_mutations_and_wrong_paths_survive(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                changed_text = raw.decode("utf-8") + "UNREVIEWED"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("unreviewed/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", bytes([255, 0])),
                         bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
