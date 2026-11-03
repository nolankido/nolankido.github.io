"""Turn 9 independent audit cannot invalidate earlier reviewed release snapshots."""
from pathlib import Path
import subprocess
import unittest
import turn09_reply_history as history
import turn11_video_discovery_history
import turn12_cross_platform_history


class Turn09ReplyHistoryTests(unittest.TestCase):
    def test_reviewed_changes_restore_exact_previous_source_and_generated_bytes(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = turn11_video_discovery_history.before(path, turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes()))
                self.assertEqual(history.blob(current), new_sha)
                previous = history.before(path, current)
                self.assertEqual(history.blob(previous), old_sha)
                self.assertEqual(previous, subprocess.check_output(
                    ['git', 'show', history.PARENT + ':' + path], cwd=history.ROOT))
                self.assertEqual(history.before(path, previous), previous)

    def test_unreviewed_edits_and_paths_survive_without_faking_history(self):
        for path in history.BLOBS:
            raw = turn11_video_discovery_history.before(path, turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes()))
            for altered in (raw + b'unknown', b'unknown' + raw, raw[1:]):
                self.assertEqual(history.before(path, altered), altered)
            self.assertEqual(history.before('another/' + path, raw), raw)
        self.assertEqual(history.before('private.bin', bytes([255, 0])), bytes([255, 0]))

    def test_only_reviewed_new_files_are_excluded_from_older_inventories(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                raw = turn11_video_discovery_history.before(path, turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes()))
                self.assertEqual(history.blob(raw), sha)
                self.assertEqual(history.source_records({path: raw}), {})
                self.assertEqual(history.source_records({path: raw + b'unknown'}),
                                 {path: raw + b'unknown'})
                self.assertEqual(history.files([path, 'other.txt']), ['other.txt'])

    def test_only_exact_addition_and_release_bytes_are_rewound(self):
        for route, path in history.NEW_ROUTES.items():
            raw = turn11_video_discovery_history.before(path, turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes()))
            self.assertEqual(history.live_targets({route: (200, raw)}), {})
            self.assertEqual(history.live_targets({route: (200, raw + b'unknown')}),
                             {route: (200, raw + b'unknown')})
        for route, path in history.ROUTES.items():
            raw = turn11_video_discovery_history.before(path, turn12_cross_platform_history.before(path, (history.ROOT / path).read_bytes()))
            self.assertEqual(history.live_targets({route: (200, raw)}),
                             {route: (200, history.before(path, raw))})


if __name__ == '__main__':
    unittest.main()
