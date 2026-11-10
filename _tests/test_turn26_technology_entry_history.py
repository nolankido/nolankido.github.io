"""Turn 26 Technology entrance history uses its original reviewed release."""

import subprocess
import unittest
from pathlib import Path

from reviewed_release import read as reviewed_bytes
import turn26_technology_entry_history as history


# The Technology first-screen revision preceded later notes, project and
# navigation work. Today's pages are not the original Turn 26 successor.
RELEASE = "f2ce3bd71474bc0cec1ad39cf6feb7feb357ce43"
RELEASE_TREE = "f2723f9996008dec5e5fab97ba63090c8a9de84d"
PARENT_TREE = "64f894d5cc96e535b96aed61cd24a53db6fbbf67"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class TechnologyFirstScreenHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.released = {path: reviewed_bytes(RELEASE, path, pair[1])
                        for path, pair in history.BLOBS.items()}
        cls.parents = {path: reviewed_bytes(history.PARENT, path, pair[0])
                       for path, pair in history.BLOBS.items()}
        cls.current = {path: (history.ROOT / path).read_bytes()
                       for path in history.BLOBS}

    def test_original_technology_entrance_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(history.BLOBS), {
            "_source/technology/home.html",
            "technology/index.html",
            "find/index.html",
        })
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), new_sha)
                self.assertEqual(history.blob(self.parents[path]), old_sha)

    def test_only_original_successors_restore_the_exact_parent(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(history.blob(released), new_sha)
                earlier = history.before(path, released)
                self.assertEqual(history.blob(earlier), old_sha)
                self.assertEqual(earlier, self.parents[path])
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), earlier)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, earlier.decode("utf-8"))
                self.assertEqual(history.before(path, earlier), earlier)

    def test_mutations_and_unrelated_paths_are_not_rewritten(self):
        for revision, records in (("release", self.released),
                                  ("today", self.current)):
            for path, raw in records.items():
                for changed in (raw + b"UNKNOWN", b"UNKNOWN" + raw,
                                raw[1:], b"\xff\x00"):
                    with self.subTest(revision=revision, path=path,
                                      mutation=history.blob(changed)):
                        self.assertEqual(history.before(path, changed), changed)
                changed_text = raw.decode("utf-8") + "UNKNOWN"
                self.assertEqual(history.before(path, changed_text), changed_text)
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("other.bin", b"\xff\x00"), b"\xff\x00")


if __name__ == "__main__":
    unittest.main()
