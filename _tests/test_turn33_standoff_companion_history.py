"""Turn 33 replays only exact predecessor Git files, not arbitrary new content."""
from pathlib import Path
import subprocess
import unittest

import turn33_standoff_companion_history as history


class StandOffCompanionHistoryTests(unittest.TestCase):
    def test_complete_changed_files_rewind_to_reviewed_parent(self):
        self.assertGreaterEqual(len(history.BLOBS), 18)
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertEqual(history.blob(current), current_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT
                ))
                self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                                 previous.decode("utf-8"))
                self.assertEqual(history.before(path, previous), previous)

    def test_unknown_mutations_and_wrong_destinations_are_not_masked(self):
        for path in history.BLOBS:
            current = (history.ROOT / path).read_bytes()
            for changed in (current + b"EXTRA", b"EXTRA" + current, current[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, current), current)
        self.assertEqual(history.before("unknown.bin", b"\xff\x00"), b"\xff\x00")

    def test_only_complete_approved_new_public_files_are_recognized(self):
        required = {
            "_source/poker/portland-meadows-standoff.html",
            "poker/episodes/portland-meadows-standoff/index.html",
            "_scripts/build_standoff_episode.py",
            "_scripts/poker_standoff_episode.py",
        }
        self.assertTrue(required <= set(history.ADDED))
        for path in history.ADDED:
            with self.subTest(path=path):
                current = (history.ROOT / path).read_bytes()
                self.assertTrue(history.is_added_file(path, current))
                self.assertFalse(history.is_added_file(path, current + b"unreviewed"))
                self.assertFalse(history.is_added_file("other/" + path, current))


if __name__ == "__main__":
    unittest.main()
