"""The best-five recap release preserves the complete published predecessor."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import subprocess
import unittest

import best_five_history as history
import time_print_history

ROOT = Path(__file__).resolve().parents[1]


class BestFiveHistoryTests(unittest.TestCase):
    def test_seven_reviewed_files_restore_exact_predecessor_bytes(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name, record in history.change()['paths'].items():
            with self.subTest(path=name):
                raw = (ROOT / name).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(), record['new_sha256'])
                old = history.before(name, raw)
                self.assertEqual(sha256(old).hexdigest(), record['old_sha256'])
                self.assertEqual(history.before(Path(name), raw.decode()).encode(), old)
                self.assertEqual(history.before(name, old), old)
                self.assertEqual(time_print_history.before(name, raw), old)

    def test_complete_production_inventory_restores_the_published_parent(self):
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        rows = sorted((name, sha256(history.before(name, (ROOT / name).read_bytes())).hexdigest())
                      for name in paths if name and not name.startswith(('_tests/', '_reports/')))
        self.assertEqual(len(rows), history.change()['production_count'])
        self.assertEqual(sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(),
                         history.change()['production_fingerprint'])

    def test_unknown_changes_are_not_hidden(self):
        for name in history.PATHS:
            raw = (ROOT / name).read_bytes()
            for altered in (raw + b'!', b'!' + raw, raw[1:]):
                self.assertEqual(history.before(name, altered), altered)
        self.assertEqual(history.before('index.html', b'unrelated'), b'unrelated')

    def test_corrupt_records_cannot_reconstruct_history(self):
        name = 'poker/hand-rankings/index.html'
        raw = (ROOT / name).read_bytes()
        corrupt = deepcopy(history.change())
        corrupt['paths'][name]['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=corrupt), self.assertRaises(ValueError):
            history.before(name, raw)
        for edits in ([[True, 1, '']], [[-1, 0, '']], [[2, 1, '']],
                      [[0, 3, ''], [2, 4, '']], [[0, len(raw) + 1, '']],
                      [[0, 1, 'not base64']], [[0, 1, None]]):
            corrupt = deepcopy(history.change())
            corrupt['paths'][name]['edits'] = edits
            with self.subTest(edits=edits), patch.object(history, 'change', return_value=corrupt):
                with self.assertRaises(ValueError):
                    history.before(name, raw)


if __name__ == '__main__':
    unittest.main()
