"""No snapshot rewrite: exact player sitemap predecessors and unknown changes."""
from pathlib import Path
import unittest

import profile_sitemap_turn_history as history
import episode_turn06_history
import turn07_hand_history
import turn08_laptop_history


class PlayerSitemapHistoryTests(unittest.TestCase):
    def test_only_exact_published_successor_blobs_can_be_restored(self):
        for name, item in history.REVISIONS.items():
            with self.subTest(path=name):
                current = episode_turn06_history.before(name, turn07_hand_history.before(name, turn08_laptop_history.before(name, (history.ROOT / name).read_bytes())))
                self.assertEqual(history.blob(current), item['new'])
                previous = history.before(name, current)
                self.assertEqual(history.blob(previous), item['old'])
                self.assertEqual(history.before(name, previous), previous)
                self.assertEqual(history.before(Path(name), current.decode('utf-8')),
                                 previous.decode('utf-8'))
                for corrupt in (current + b'UNKNOWN', b'UNKNOWN' + current, current[1:]):
                    self.assertEqual(history.before(name, corrupt), corrupt)

    def test_only_exact_added_files_are_hidden_from_old_inventories(self):
        for name, reviewed_sha in history.ADDED_FILES.items():
            with self.subTest(path=name):
                original = episode_turn06_history.before(name, turn07_hand_history.before(name, turn08_laptop_history.before(name, (history.ROOT / name).read_bytes())))
                self.assertEqual(history.blob(original), reviewed_sha)
                self.assertEqual(history.source_records({name: original}), {})
                self.assertEqual(history.source_records({name: original + b'unknown'}),
                                 {name: original + b'unknown'})
                self.assertEqual(history.files([name, 'unrelated.txt']), ['unrelated.txt'])
        self.assertEqual(history.source_records({'other.bin': b'hello'}),
                         {'other.bin': b'hello'})

    def test_live_record_removed_from_old_targets_only_for_exact_bytes(self):
        name = history.PROFILE_ROUTE
        public = episode_turn06_history.before('poker/nolan-kido/index.html', turn07_hand_history.before('poker/nolan-kido/index.html', (history.ROOT / 'poker/nolan-kido/index.html').read_bytes()))
        self.assertEqual(history.blob(public), history.PLAYER_BLOB)
        self.assertEqual(history.live_targets({name: (200, public)}), {})
        for data in ((404, public), (200, public + b'unknown'), (200, 'wrong')):
            self.assertEqual(history.live_targets({name: data}), {name: data})


if __name__ == '__main__':
    unittest.main()
