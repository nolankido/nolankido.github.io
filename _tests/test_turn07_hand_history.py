"""Turn 7 preserves released historical bytes and rejects unreviewed changes."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import turn07_hand_history as history
from reviewed_release import read as reviewed_bytes


# The original Turn 7 content was approved in this Git release. The sprint
# report received a separate follow-up receipt, and its digest was updated
# in the frozen inventory adapter to match that exact published receipt.
RELEASE = "5ce3774e762a8217ac5c41e4c64f70745763c6f4"
RELEASE_TREE = "4c77a80833e23f4ecd70f69c60303204a786897e"
PARENT_TREE = "f247ea9b9cceed2a1da2cabe44c9545073986ff9"
RECEIPT = "9e7bd9a090c8a67a07bc6da8eebc94025e47529b"
RECEIPT_TREE = "eed875411e03bc2a6d085a6ec346f94f24df6e82"
REPORT_PATH = "_reports/visibility-sprint/sprint50-turn07-2026-11-02.md"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT).decode("ascii").strip()


class Turn07HandHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.added = {path: reviewed_bytes(RECEIPT if path == REPORT_PATH else RELEASE,
                                          path, blob)
                     for path, blob in history.ADDED.items()}
        # Present-day content is used only for unreviewed-change controls.
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_published_release_and_receipt_have_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(git_revision(RECEIPT + "^"), RELEASE)
        self.assertEqual(git_revision(RECEIPT + "^{tree}"), RECEIPT_TREE)
        self.assertEqual(set(self.released), set(history.BLOBS))
        self.assertEqual(set(self.added), set(history.ADDED))
        for path, (before_sha, after_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), after_sha)
                self.assertEqual(history.blob(self.parents[path]), before_sha)
        for path, blob in history.ADDED.items():
            with self.subTest(added=path):
                self.assertEqual(history.blob(self.added[path]), blob)
        # Turn 7's original report was amended after the release merged.
        original_report = subprocess.check_output(
            ["git", "show", RELEASE + ":" + REPORT_PATH], cwd=history.ROOT)
        self.assertNotEqual(history.blob(original_report), history.ADDED[REPORT_PATH])

    def test_every_scoped_changed_file_matches_its_parent_git_blob(self):
        for path, (before_sha, after_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                content = self.released[path]
                self.assertEqual(history.blob(content), after_sha)
                previous = history.before(path, content)
                self.assertEqual(history.blob(previous), before_sha)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, content), previous)
                self.assertEqual(history.before(path, content.decode("utf-8")),
                                 previous.decode("utf-8"))

    def test_unknown_edits_and_other_pathnames_survive(self):
        for revision, records in (("release", self.released), ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:],
                                b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                text = raw.decode("utf-8") + "UNKNOWN"
                self.assertEqual(history.before(path, text), text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("private.bin", bytes([255, 0])), bytes([255, 0]))

    def test_source_additions_only_disappear_when_exact(self):
        for path, digest in history.ADDED.items():
            with self.subTest(path=path):
                raw = self.added[path]
                self.assertEqual(history.blob(raw), digest)
                self.assertEqual(history.source_records({path: raw}), {})
                altered = raw + b"UNREVIEWED"
                self.assertEqual(history.source_records({path: altered}), {path: altered})
                # Inventory removal must run against an archived exact file,
                # never today's independently edited repository copy.
                with TemporaryDirectory() as temporary:
                    copied_root = Path(temporary)
                    copied_path = copied_root / path
                    copied_path.parent.mkdir(parents=True, exist_ok=True)
                    copied_path.write_bytes(raw)
                    with patch.object(history, "ROOT", copied_root):
                        self.assertEqual(history.files([path, "unrelated.txt"]),
                                         ["unrelated.txt"])
                        self.assertEqual(history.files((path, "unrelated.txt")),
                                         ("unrelated.txt",))
                        copied_path.write_bytes(altered)
                        self.assertEqual(history.files([path, "unrelated.txt"]),
                                         [path, "unrelated.txt"])

    def test_later_live_bytes_rewind_only_when_exact(self):
        for route, path in history.ROUTES.items():
            with self.subTest(route=route):
                raw = self.released[path]
                restored = history.live_targets({route: (200, raw)})
                self.assertEqual(restored[route], (200, history.before(path, raw)))
                for bad in ((200, raw + b"UNKNOWN"), (404, raw), (200, "")):
                    self.assertEqual(history.live_targets({route: bad}), {route: bad})


if __name__ == "__main__":
    unittest.main()
