"""Turn 11 video discovery preserves reviewed release history exactly."""
import subprocess
import unittest
from pathlib import Path

import turn11_video_discovery_history as history
import turn12_cross_platform_history


class Turn11VideoDiscoveryHistoryTests(unittest.TestCase):
    def test_only_exact_published_files_restore_the_parent(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(raw), new_sha)
                original = history.before(path, raw)
                self.assertEqual(history.blob(original), old_sha)
                self.assertEqual(original, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT))
                self.assertEqual(history.before(path, original), original)
                self.assertEqual(history.before(Path(path), raw.decode("utf-8")),
                                 original.decode("utf-8"))

    def test_mutations_and_wrong_paths_are_not_hidden(self):
        for path in history.BLOBS:
            raw = turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes())
            for changed in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unrelated.bin", bytes([255, 0])),
                         bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
