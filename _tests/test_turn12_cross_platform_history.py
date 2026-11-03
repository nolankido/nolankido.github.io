"""Turn 12 history only rewinds reviewed, SHA-checked complete files."""
import subprocess
import unittest
from pathlib import Path

import turn14_freshness_history

import turn12_cross_platform_history as history


class Turn12CrossPlatformHistoryTests(unittest.TestCase):
    def test_exact_current_blobs_restore_committed_parent(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = turn14_freshness_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(current), new_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT))
                self.assertEqual(history.before(path, previous), previous)
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 previous.decode("utf-8"))

    def test_unknown_mutations_and_wrong_paths_survive(self):
        for path in history.BLOBS:
            raw = (history.ROOT / path).read_bytes()
            for changed in (raw + b"UNREVIEWED", b"UNREVIEWED" + raw, raw[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("unreviewed/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", bytes([255, 0])),
                         bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
