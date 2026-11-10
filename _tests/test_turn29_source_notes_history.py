"""Turn 29 public source-note history uses the exact reviewed Git release."""

from pathlib import Path
import subprocess
import unittest

from reviewed_release import read as reviewed_bytes
import turn27_profile_history as turn27
import turn29_source_notes_history as history
import turn30_evidence_index_history as turn30


# Later approved edits changed the live article, Find index, page registry,
# and sitemap. The original Turn 29 successor is immutable Git evidence.
RELEASE = "c259d366176f3411e89777646135262178cc75b3"
RELEASE_TREE = "a88806d384ee754d06a25fb062d63ce0694dbbb8"
PARENT_TREE = "c4f3778afc431f558832432de552a1c773e7ce69"


def git_revision(ref):
    return subprocess.check_output(
        ["git", "rev-parse", ref], cwd=history.ROOT
    ).decode("ascii").strip()


class SourceNotesHistoryTests(unittest.TestCase):
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

    def test_original_source_notes_release_has_exact_git_provenance(self):
        self.assertEqual(git_revision(RELEASE + "^"), history.PARENT)
        self.assertEqual(git_revision(RELEASE + "^{tree}"), RELEASE_TREE)
        self.assertEqual(git_revision(history.PARENT + "^{tree}"), PARENT_TREE)
        self.assertEqual(set(history.BLOBS), {
            "_source/pages.json",
            "_source/technology/organize-public-notes.html",
            "technology/organize-public-notes/index.html",
            "find/index.html",
            "sitemap.xml",
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
                self.assertEqual(history.blob(turn30.before(path, released)), newer)
                previous = history.before(path, released)
                self.assertEqual(history.blob(previous), older)
                self.assertEqual(previous, self.parents[path])
                self.assertEqual(history.before(path, previous), previous)
                for alias in (Path(path), history.ROOT / path):
                    self.assertEqual(history.before(alias, released), previous)
                text = history.before(path, released.decode("utf-8"))
                self.assertIsInstance(text, str)
                self.assertEqual(text, previous.decode("utf-8"))

    def test_page_registry_rewinds_through_biography_release_in_order(self):
        path = "_source/pages.json"
        before_bio = reviewed_bytes(turn27.PARENT, path, turn27.BLOBS[path][0])
        after_bio = self.parents[path]
        self.assertEqual(history.blob(after_bio), turn27.BLOBS[path][1])
        self.assertEqual(history.before(path, self.released[path]), after_bio)
        self.assertEqual(turn27.before(path, after_bio), before_bio)
        self.assertEqual(turn27.before(path, self.released[path]), before_bio)

    def test_unknown_mutations_and_later_edits_remain_visible(self):
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
        self.assertEqual(history.before("unrelated.bin", b"\xff\x00"), b"\xff\x00")

    def test_added_audit_checker_requires_exact_original_public_blob(self):
        name = "downloads/source-notes-audit.py"
        raw = self.added[name]
        self.assertEqual(set(history.ADDED), {name})
        self.assertEqual(history.blob(raw), history.ADDED[name])
        self.assertTrue(history.is_added_file(name, raw))
        self.assertFalse(history.is_added_file(name, raw + b"UNREVIEWED"))
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

    def test_only_approved_complete_page_record_rewinds(self):
        old = dict(history.OLD_PAGE)
        revised = dict(old, updated="2026-11-04")
        self.assertEqual(history.pages([revised]), [old])
        self.assertEqual(history.pages([old]), [old])
        mutant = dict(revised, description="unreviewed change")
        self.assertEqual(history.pages([mutant]), [mutant])
        unrelated = {"id": "other", "updated": "2026-11-04"}
        self.assertEqual(history.pages([unrelated]), [unrelated])


if __name__ == "__main__":
    unittest.main()
