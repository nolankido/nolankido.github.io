"""Exact predecessor guard for the player Find enhancement."""
import unittest
from pathlib import Path
import player_find_turn_history as history
import episode_turn06_history
import turn07_hand_history
import turn08_laptop_history


class PlayerFindHistoryTests(unittest.TestCase):
    def test_every_approved_file_restores_its_reviewed_git_predecessor(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = episode_turn06_history.before(path, turn07_hand_history.before(path, turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())))
                self.assertEqual(history.blob(current), new_sha)
                earlier = history.before(path, current)
                self.assertEqual(history.blob(earlier), old_sha)
                self.assertEqual(history.before(path, earlier), earlier)
                self.assertEqual(history.before(Path(path), current.decode('utf-8')),
                                 earlier.decode('utf-8'))

    def test_corruption_wrong_file_and_unknown_content_are_not_hidden(self):
        for path in history.BLOBS:
            current = episode_turn06_history.before(path, turn07_hand_history.before(path, turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())))
            for bad in (current + b'UNREVIEWED', b'UNREVIEWED' + current, current[1:]):
                self.assertEqual(history.before(path, bad), bad)
            self.assertEqual(history.before('other/' + path, current), current)
        self.assertEqual(history.before('unknown.bin', bytes([255, 0])), bytes([255, 0]))

    def test_only_exact_added_files_disappear_from_historical_source_view(self):
        for path, sha in history.ADDED.items():
            with self.subTest(path=path):
                current = episode_turn06_history.before(path, turn07_hand_history.before(path, turn08_laptop_history.before(path, (history.ROOT / path).read_bytes())))
                self.assertEqual(history.blob(current), sha)
                self.assertEqual(history.source_records({path: current}), {})
                changed = current + b'UNREVIEWED'
                self.assertEqual(history.source_records({path: changed}), {path: changed})
                self.assertEqual(history.files([path, 'other.txt']), ['other.txt'])


if __name__ == '__main__':
    unittest.main()
