"""Release scope must preserve every undeclared file and protected source."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import poker_school_release as gate


class PokerSchoolReleaseTests(unittest.TestCase):
    def test_sha_is_the_actual_git_blob_sha(self):
        self.assertEqual(gate.git_blob_sha(b"hello\n"),
                         "ce013625030ba8dba906f756967f9e9ca394464a")
        self.assertNotEqual(gate.git_blob_sha(b"hello"), gate.git_blob_sha(b"hello\n"))

    def test_manifest_rejects_unknown_change_file_and_deletion(self):
        base = {"keep": "a" * 40}
        current = {**base, **{p: "b" * 40 for p in gate.ADDED},
                   **{p: "c" * 40 for p in gate.MODIFIED}}
        for path in gate.MODIFIED:
            base[path] = "d" * 40
        for path in gate.PROTECTED:
            base[path] = "e" * 40
            current[path] = "e" * 40
        self.assertFalse(gate.verify(base, current)["release_authorized"])
        for bad in ({**current, "keep": "changed"},
                    {**current, "unexpected.txt": "x"},
                    {k: v for k, v in current.items() if k != "keep"},
                    {**current, "assets/contact.js": "bad"}):
            with self.assertRaises(ValueError):
                gate.verify(base, bad)

    def test_unmodified_sensitive_files_match_pinned_base(self):
        base = json.loads((ROOT / gate.FROZEN).read_text())["tracked_base_blobs"]
        self.assertEqual(len(base), 1207)
        for path in gate.PROTECTED:
            with self.subTest(path=path):
                self.assertEqual(gate.git_blob_sha((ROOT / path).read_bytes()), base[path])

    def test_repo_changes_are_bounded(self):
        result = gate.audit()
        self.assertEqual(result["status"], "source_delta_checked")
        self.assertEqual(result["deleted"], 0)


if __name__ == "__main__":
    unittest.main()
