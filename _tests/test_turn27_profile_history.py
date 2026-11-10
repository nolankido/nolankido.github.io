"""Turn 27 public profile history uses the exact original Git release."""

import subprocess
import unittest
from pathlib import Path

from reviewed_release import read as reviewed_bytes
import turn27_profile_history as history


# The public profile kit preceded later Bio, sitemap, Find and date edits.
# Current files must never be mistaken for the original Turn 27 successor.
RELEASE = "b2e1587ed0040d700f237804d75dce102dfcda63"
RELEASE_TREE = "14f61828b3fe12a2667ac034f6a23a81ca4451d3"
PARENT_TREE = "f2723f9996008dec5e5fab97ba63090c8a9de84d"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class ProfileKitHistoryTests(unittest.TestCase):
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

    def test_original_profile_release_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(history.BLOBS), {
            "_source/bio.html", "bio/index.html", "_source/pages.json", "sitemap.xml"
        })
        self.assertEqual(set(self.released), set(history.BLOBS))
        for path, (older, newer) in history.BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(history.blob(self.released[path]), newer)
                self.assertEqual(history.blob(self.parents[path]), older)

    def test_only_exact_original_successors_restore_the_parent(self):
        for path, (older, newer) in history.BLOBS.items():
            with self.subTest(path=path):
                released = self.released[path]
                self.assertEqual(history.blob(released), newer)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), older)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_unknown_mutations_and_wrong_paths_remain_visible(self):
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
                self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_profile_kit_is_only_excluded_with_its_exact_new_bytes(self):
        name = "downloads/nolan-kido-public-profile-kit.md"
        raw = self.added[name]
        self.assertEqual(set(history.ADDED), {name})
        self.assertEqual(history.blob(raw), history.ADDED[name])
        self.assertTrue(history.is_added_file(name, raw))
        self.assertFalse(history.is_added_file(name, raw + b"EXTRA"))
        self.assertFalse(history.is_added_file("other/" + name, raw))
        absent = subprocess.run(
            ["git", "cat-file", "-e", history.PARENT + ":" + name],
            cwd=history.ROOT, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, check=False
        )
        self.assertNotEqual(absent.returncode, 0)
        today = (history.ROOT / name).read_bytes()
        self.assertEqual(history.is_added_file(name, today),
                         history.blob(today) == history.ADDED[name])

    def test_only_complete_bio_record_reverts_to_previous_date(self):
        before = dict(history.OLD_BIO)
        after = dict(before, updated="2026-11-04")
        self.assertEqual(history.pages([after]), [before])
        self.assertEqual(history.pages([before]), [before])
        changed = {**after, "description": "UNREVIEWED"}
        self.assertEqual(history.pages([changed]), [changed])
        self.assertEqual(history.pages([{"id": "other", "updated": "2026-11-04"}]),
                         [{"id": "other", "updated": "2026-11-04"}])


if __name__ == "__main__":
    unittest.main()
