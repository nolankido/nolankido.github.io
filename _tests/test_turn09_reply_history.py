"""The reply audit history is anchored to its exact original Git release."""

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from reviewed_release import read as reviewed_bytes
import turn09_reply_history as history


# The original article, offline audit and page were published together.
# The turn report's final bytes were recorded in a later receipt commit.
# Pin both, since neither historical revision is today's website tree.
RELEASE = "39147029a88ec3e48a6a245f6fd0defda9ded918"
RELEASE_TREE = "9365f8b24bbe9ffb0393408896c237f8c2ed24be"
PARENT_TREE = "8027763f346b80f3d2c81ffcdc50efa22d3d072e"
RECEIPT = "e7072a370184a6750fa1da640d13d8b5b47d73f5"
RECEIPT_TREE = "196a4ee0035dfcb60c40e24afd04095b68309b53"
REPORT_PATH = "_reports/visibility-sprint/sprint50-turn09-2026-11-03.md"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT).decode("ascii").strip()


class Turn09ReplyHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.added = {path: reviewed_bytes(RECEIPT if path == REPORT_PATH else RELEASE,
                                          path, digest)
                     for path, digest in history.ADDED.items()}
        # Current files are relevant only to prove unknown edits are retained.
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_original_reply_release_and_later_receipt_are_exact_snapshots(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(git_revision(RECEIPT + "^{tree}"), RECEIPT_TREE)
        self.assertEqual(set(self.released), set(history.BLOBS))
        self.assertEqual(set(self.added), set(history.ADDED))
        for path, (old_sha, published_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), published_sha)
                self.assertEqual(history.blob(self.parents[path]), old_sha)
        for path, digest in history.ADDED.items():
            with self.subTest(added=path):
                self.assertEqual(history.blob(self.added[path]), digest)

    def test_exact_successors_restore_the_original_parent_bytes(self):
        for path, (old_sha, published_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(history.blob(released), published_sha)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_only_the_original_added_files_leave_the_old_inventory(self):
        for path, digest in history.ADDED.items():
            with self.subTest(path=path):
                released = self.added[path]
                self.assertEqual(history.blob(released), digest)
                self.assertEqual(history.source_records({path: released}), {})
                changed = released + b"unknown"
                self.assertEqual(history.source_records({path: changed}), {path: changed})
                with TemporaryDirectory() as temporary:
                    copied_root = Path(temporary)
                    copied_path = copied_root / path
                    copied_path.parent.mkdir(parents=True, exist_ok=True)
                    copied_path.write_bytes(released)
                    with patch.object(history, "ROOT", copied_root):
                        self.assertEqual(history.files([path, "unreviewed.txt"]),
                                         ["unreviewed.txt"])
                        self.assertEqual(history.files((path, "unreviewed.txt")),
                                         ("unreviewed.txt",))
                        copied_path.write_bytes(changed)
                        self.assertEqual(history.files([path, "unreviewed.txt"]),
                                         [path, "unreviewed.txt"])

    def test_live_routes_rewind_only_exact_successful_published_bytes(self):
        for route, path in history.ROUTES.items():
            with self.subTest(route=route):
                released = self.released[path]
                self.assertEqual(history.live_targets({route: (200, released)}),
                                 {route: (200, history.before(path, released))})
                self.assertEqual(history.live_targets({route: (404, released)}),
                                 {route: (404, released)})
                altered = released + b"unknown"
                self.assertEqual(history.live_targets({route: (200, altered)}),
                                 {route: (200, altered)})
        for route, path in history.NEW_ROUTES.items():
            with self.subTest(route=route):
                released = self.added[path]
                self.assertEqual(history.live_targets({route: (200, released)}), {})
                self.assertEqual(history.live_targets({route: (404, released)}),
                                 {route: (404, released)})
                altered = released + b"unknown"
                self.assertEqual(history.live_targets({route: (200, altered)}),
                                 {route: (200, altered)})

    def test_unknown_bytes_and_unrelated_paths_stay_unchanged(self):
        for revision, records in (("release", self.released), ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"unknown", b"unknown" + raw, raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                text = raw.decode("utf-8") + "unknown"
                self.assertEqual(history.before(path, text), text)
                self.assertEqual(history.before("misc/" + path, raw), raw)
        self.assertEqual(history.before("private.bin", b"\xff\x00"), b"\xff\x00")


if __name__ == "__main__":
    unittest.main()
