"""Exact predecessor verification for the identity evidence reconciliation."""
from pathlib import Path
import subprocess
import unittest

import turn24_identity_claims_history as history


class IdentityClaimsHistoryTests(unittest.TestCase):
    def test_exact_predecessor_and_idempotence(self):
        self.assertEqual(set(history.BLOBS), {
            "_source/person-schema.jsonld",
            "assets/nolan-kido-identity.jsonld",
            "_tests/test_identity_jsonld.py",
        })
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(current), new_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(path, previous), previous)
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 previous.decode("utf-8"))

    def test_unreviewed_changes_are_never_rewritten(self):
        for path in history.BLOBS:
            current = (history.ROOT / path).read_bytes()
            for changed in (current + b"UNREVIEWED", b"UNREVIEWED" + current, current[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, current), current)

    def test_unknown_binary_input_is_unchanged(self):
        raw = b"\xff\x00"
        self.assertEqual(history.before("other.bin", raw), raw)


if __name__ == "__main__":
    unittest.main()
