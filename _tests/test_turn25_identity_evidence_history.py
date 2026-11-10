"""Turn 25 identity evidence history uses its original reviewed Git release."""

import subprocess
import unittest
from pathlib import Path

from reviewed_release import read as reviewed_bytes
import turn25_identity_evidence_history as history


# The identity-claim audit was published before later About, homepage,
# Technology and Find revisions. Those current files are not its successor
# snapshot, and predecessor adapters must not rewrite unknown later bytes.
RELEASE = "e7d9fdb8ab000e996734a02af83cf65132411a58"
RELEASE_TREE = "64f894d5cc96e535b96aed61cd24a53db6fbbf67"
PARENT_TREE = "2783476629164f50d68e2360b1c8a9e1459e5516"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class IdentityEvidencePredecessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}
        cls.added = {path: reviewed_bytes(RELEASE, path, expected)
                     for path, expected in history.ADDED.items()}

    def test_original_identity_evidence_release_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(history.BLOBS), {
            "_source/technology/home.html", "technology/index.html",
            "_source/about.html", "about/index.html",
            "_source/home.html", "index.html", "find/index.html",
        })
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), new_sha)
                self.assertEqual(history.blob(self.parents[path]), old_sha)

    def test_only_original_successors_restore_their_git_predecessors(self):
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

    def test_new_downloads_have_pinned_bytes_not_a_filename_exemption(self):
        self.assertEqual(set(history.ADDED), {
            "downloads/identity-evidence-gate.py",
            "downloads/identity-evidence-case-workbook.md",
        })
        for path, expected in history.ADDED.items():
            with self.subTest(path=path):
                raw = self.added[path]
                self.assertEqual(history.blob(raw), expected)
                self.assertTrue(history.is_added_file(path, raw))
                self.assertFalse(history.is_added_file(path, raw + b"UNREVIEWED"))
                self.assertFalse(history.is_added_file("other/" + path, raw))
                absent = subprocess.run(
                    ["git", "cat-file", "-e", history.PARENT + ":" + path],
                    cwd=history.ROOT, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=False
                )
                self.assertNotEqual(absent.returncode, 0)
                today = (history.ROOT / path).read_bytes()
                self.assertEqual(history.is_added_file(path, today),
                                 history.blob(today) == expected)

    def test_unknown_mutations_and_wrong_paths_are_not_rewritten(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, raw in records.items():
                for mutated in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(mutated)):
                        self.assertEqual(history.before(path, mutated), mutated)
                changed_text = raw.decode("utf-8") + "UNREVIEWED"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")


if __name__ == "__main__":
    unittest.main()
