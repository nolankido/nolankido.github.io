"""Turn 29 exact historical blobs, added checker, and old dated case record."""
from pathlib import Path
import subprocess
import unittest
import turn29_source_notes_history as history
import turn30_evidence_index_history as turn30


class SourceNotesHistoryTests(unittest.TestCase):
    def test_exact_new_blobs_restore_the_recorded_parent(self):
        for path, (previous_hash, current_hash) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(turn30.before(path, current)), current_hash)
                old = history.before(path, current)
                self.assertEqual(history.blob(old), previous_hash)
                self.assertEqual(old, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 old.decode("utf-8"))
                self.assertEqual(history.before(path, old), old)

    def test_unrecognized_edits_are_not_disguised_as_history(self):
        for path in history.BLOBS:
            current = (history.ROOT / path).read_bytes()
            for mutation in (current + b"EXTRA", b"EXTRA" + current, current[1:]):
                self.assertEqual(history.before(path, mutation), mutation)
            self.assertEqual(history.before("other/" + path, current), current)
        self.assertEqual(history.before("unrelated.bin", b"\xff\x00"), b"\xff\x00")

    def test_new_checker_has_one_exact_public_blob(self):
        name = "downloads/source-notes-audit.py"
        raw = (history.ROOT / name).read_bytes()
        self.assertEqual(set(history.ADDED), {name})
        self.assertTrue(history.is_added_file(name, raw))
        self.assertFalse(history.is_added_file(name, raw + b"edited"))
        self.assertFalse(history.is_added_file("other/" + name, raw))

    def test_only_approved_complete_page_record_rewinds(self):
        old = dict(history.OLD_PAGE)
        revised = dict(old, updated="2026-11-04")
        self.assertEqual(history.pages([revised]), [old])
        self.assertEqual(history.pages([old]), [old])
        mutant = dict(revised, description="unreviewed change")
        self.assertEqual(history.pages([mutant]), [mutant])


if __name__ == "__main__":
    unittest.main()
