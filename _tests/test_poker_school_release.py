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

    def test_historical_manifest_is_frozen_not_a_future_site_lock(self):
        frozen = json.loads((ROOT / gate.FROZEN).read_text())
        self.assertEqual(frozen["base_commit"], gate.BASE)
        self.assertEqual(len(frozen["tracked_base_blobs"]), 1207)
        self.assertEqual(frozen["tracked_base_blobs"]["assets/contact.js"],
                         "65663ddee4a515c63a9f1d7e35e7ef47b3d21f8a")
        # The exact current-branch audit is invoked separately for PR #110.
        # Future site improvements should not be frozen to these 2026 bytes.


if __name__ == "__main__":
    unittest.main()
