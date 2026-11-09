"""The Turn 10 video-link repair rewinds only its reviewed Git release."""

from pathlib import Path
import subprocess
import unittest

from reviewed_release import read as reviewed_bytes
import turn10_video_history as history


# The original accessible-video repair predates later hand ledger updates.
# Current Episode 1 pages cannot be partially rewound into that release.
RELEASE = "78ab6414091bbaa6a46d71e2f1100277513819e2"
RELEASE_TREE = "db0bb1ec0691ebea5b84a5f5f3ac0ca1ba91f654"
PARENT_TREE = "196a4ee0035dfcb60c40e24afd04095b68309b53"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT).decode("ascii").strip()


class Turn10VideoHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_release_commit_and_parent_have_exact_git_trees(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (old_sha, published_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.parents[path]), old_sha)
                self.assertEqual(history.blob(self.released[path]), published_sha)

    def test_exact_release_bytes_restore_predecessor(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = self.released[path]
                self.assertEqual(history.blob(raw), new_sha)
                previous = history.before(path, raw)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, raw), previous)
                text = history.before(path, raw.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_mutations_current_content_and_unrelated_files_are_not_rewritten(self):
        for revision, records in (("release", self.released), ("today", self.current)):
            for path, raw in records.items():
                for altered in (raw + b"unexpected", b"unexpected" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(altered)):
                        self.assertEqual(history.before(path, altered), altered)
                text = raw.decode("utf-8") + "unexpected"
                self.assertEqual(history.before(path, text), text)
                self.assertEqual(history.before("other/" + path, raw), raw)


if __name__ == "__main__":
    unittest.main()
