"""Only exact Turn 25 bytes can be treated as later than archival releases."""
from pathlib import Path
import subprocess
import unittest

import turn25_identity_evidence_history as history
import turn26_technology_entry_history as turn26_history


class IdentityEvidencePredecessorTests(unittest.TestCase):
    def test_reviewed_public_files_recover_exact_main_parent(self):
        self.assertEqual(set(history.BLOBS), {
            "_source/technology/home.html", "technology/index.html",
            "_source/about.html", "about/index.html",
            "_source/home.html", "index.html", "find/index.html",
        })
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                reviewed = turn26_history.before(path, current)
                self.assertEqual(history.blob(reviewed), new_sha)
                old = history.before(path, current)
                self.assertEqual(history.blob(old), old_sha)
                self.assertEqual(old, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(path, old), old)
                self.assertEqual(
                    history.before(Path(path), current.decode("utf-8")),
                    old.decode("utf-8")
                )

    def test_new_downloads_have_pinned_bytes_not_a_filename_exemption(self):
        self.assertEqual(set(history.ADDED), {
            "downloads/identity-evidence-gate.py",
            "downloads/identity-evidence-case-workbook.md",
        })
        for path, expected in history.ADDED.items():
            with self.subTest(path=path):
                raw = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(raw), expected)
                self.assertTrue(history.is_added_file(path, raw))
                self.assertFalse(history.is_added_file(path, raw + b"UNREVIEWED"))
                self.assertFalse(history.is_added_file("other/" + path, raw))

    def test_unknown_mutations_and_wrong_paths_are_not_rewritten(self):
        for path in history.BLOBS:
            raw = (history.ROOT / path).read_bytes()
            for mutated in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw, raw[1:]):
                self.assertEqual(history.before(path, mutated), mutated)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")


if __name__ == "__main__":
    unittest.main()
