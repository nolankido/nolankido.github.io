"""The new local-AI article cannot erase old reviewed release history."""
from pathlib import Path
import subprocess
import unittest

import turn08_laptop_history as history
import turn09_reply_history


class Turn08HistoryTests(unittest.TestCase):
    def test_exact_successor_restores_original_parent_bytes(self):
        for path, (old_sha, published_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = turn09_reply_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(current), published_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=history.ROOT))
                self.assertEqual(history.before(path, previous), previous)

    def test_only_complete_known_new_files_are_excluded(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                raw = turn09_reply_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(raw), sha)
                self.assertEqual(history.source_records({path: raw}), {})
                altered = raw + b"unknown"
                self.assertEqual(history.source_records({path: altered}), {path: altered})
                self.assertEqual(history.files([path, "unreviewed.txt"]), ["unreviewed.txt"])

    def test_live_published_bytes_rewind_only_when_exact(self):
        for route, path in history.ROUTES.items():
            with self.subTest(route=route):
                raw = turn09_reply_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.live_targets({route: (200, raw)}),
                                 {route: (200, history.before(path, raw))})
                self.assertEqual(history.live_targets({route: (200, raw + b"unknown")}),
                                 {route: (200, raw + b"unknown")})
        for route, path in history.ADDED_ROUTES.items():
            with self.subTest(route=route):
                raw = turn09_reply_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.live_targets({route: (200, raw)}), {})
                self.assertEqual(history.live_targets({route: (404, raw)}), {route: (404, raw)})

    def test_unreviewed_bytes_and_incorrect_paths_survive(self):
        for path in history.BLOBS:
            current = turn09_reply_history.before(path, (history.ROOT / path).read_bytes())
            for altered in (current + b"unknown", b"unknown" + current, current[1:]):
                self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before("misc/" + path, current), current)
        self.assertEqual(history.before("private.bin", bytes([255, 0])), bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
