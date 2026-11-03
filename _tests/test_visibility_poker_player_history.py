"""Exact, type-safe historical boundary for the sourced Poker player evidence."""
import unittest
from pathlib import Path

import poker_player_turn05_history as history
import profile_links_turn05_history
import episode_turn06_history
import turn07_hand_history
import turn11_video_discovery_history


class Turn05PokerHistoryTests(unittest.TestCase):
    def test_reviewed_successors_restore_exact_main_predecessors(self):
        for name, (old_digest, new_digest) in history.BLOBS.items():
            with self.subTest(path=name):
                current = profile_links_turn05_history.before(name, episode_turn06_history.before(name, turn07_hand_history.before(name, turn11_video_discovery_history.before(name, (history.ROOT / name).read_bytes()))))
                self.assertEqual(history.git_blob(current), new_digest)
                previous = history.before(name, current)
                self.assertEqual(history.git_blob(previous), old_digest)
                self.assertNotIn(b"poker-player-evidence", previous)
                self.assertEqual(history.before(name, previous), previous)
                self.assertEqual(history.before(Path(name), current.decode("utf-8")),
                                 previous.decode("utf-8"))

    def test_unknown_edits_and_wrong_paths_are_never_hidden(self):
        for name in history.BLOBS:
            current = turn11_video_discovery_history.before(name, (history.ROOT / name).read_bytes())
            for changed in (current + b"UNKNOWN", b"UNKNOWN" + current, current[1:]):
                self.assertEqual(history.before(name, changed), changed)
            self.assertEqual(history.before("other/" + name, current), current)
        self.assertEqual(history.before("misc.bin", bytes([255, 1])), bytes([255, 1]))


if __name__ == "__main__":
    unittest.main()
