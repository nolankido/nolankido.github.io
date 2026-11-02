"""Exact predecessor tests for Portland Meadows Episode 1 with no CI service."""
from pathlib import Path
import subprocess
import unittest

import episode_turn06_history as history
import turn07_hand_history


class Turn06HistoryTests(unittest.TestCase):
    def test_all_reviewed_changes_restore_exact_published_parent(self):
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = turn07_hand_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(current), current_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                parent = subprocess.check_output(["git", "show", history.PARENT + ":" + path],
                                                 cwd=history.ROOT)
                self.assertEqual(previous, parent)
                self.assertEqual(history.before(path, previous), previous)

    def test_unknown_edits_never_collapse_into_older_release(self):
        for path in history.BLOBS:
            raw = turn07_hand_history.before(path, (history.ROOT / path).read_bytes())
            for altered in (raw + b"UNKNOWN", b"UNKNOWN" + raw, raw[1:]):
                self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before("unreviewed/" + path, raw), raw)

    def test_new_public_sources_removed_only_from_old_inventories(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                current = turn07_hand_history.before(path, (history.ROOT / path).read_bytes())
                self.assertEqual(history.blob(current), sha)
                self.assertEqual(history.source_records({path: current}), {})
                mutated = current + b"UNREVIEWED"
                self.assertEqual(history.source_records({path: mutated}), {path: mutated})
                self.assertEqual(history.files([path, "unreviewed.txt"]), ["unreviewed.txt"])

    def test_live_video_route_is_removed_only_when_public_bytes_are_exact(self):
        raw = turn07_hand_history.before('poker/episodes/portland-meadows-ep1/index.html', (history.ROOT / history.EPISODE_ROUTE.lstrip('/') / "index.html").read_bytes())
        self.assertEqual(history.live_targets({history.EPISODE_ROUTE: (200, raw)}), {})
        for value in ((404, raw), (200, raw + b"UNKNOWN"), (200, "")):
            self.assertEqual(history.live_targets({history.EPISODE_ROUTE: value}),
                             {history.EPISODE_ROUTE: value})


if __name__ == "__main__":
    unittest.main()
