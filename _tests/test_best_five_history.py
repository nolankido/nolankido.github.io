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
import answer_review_print_history as subsequent_changes
from reviewed_release import read as reviewed_bytes

ROOT = Path(__file__).resolve().parents[1]
BEST_FIVE_RELEASE = '2809bbf4a234331ab6413323f3d100ccc823bd0f'
LIBRARY_FILE = 'poker/library/index.html'
LIBRARY_RELEASE_BLOB = '216646fe471c57d356d3120307b055c48847a3db'


class BestFiveHistoryTests(unittest.TestCase):
    def test_seven_reviewed_files_restore_exact_predecessor_bytes(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name, record in history.change()['paths'].items():
            with self.subTest(path=name):
                # The library page changed in later releases. Recover this
                # exact successor from the reviewed original Git release.
                if name == LIBRARY_FILE:
                    raw = reviewed_bytes(BEST_FIVE_RELEASE, name, LIBRARY_RELEASE_BLOB)
                else:
                    raw = subsequent_changes.before(name, (ROOT / name).read_bytes())
                self.assertEqual(sha256(raw).hexdigest(), record['new_sha256'])
                old = history.before(name, raw)
                self.assertEqual(sha256(old).hexdigest(), record['old_sha256'])
                self.assertEqual(history.before(Path(name), raw.decode()).encode(), old)
                self.assertEqual(history.before(name, old), old)
                self.assertEqual(time_print_history.before(name, raw), old)

    def test_complete_production_inventory_restores_the_published_parent(self):
        # This is a frozen release fingerprint, not today's live inventory.
        # Include its original paths even when a later site change removes
        # them (including the intentionally removed GitHub Actions workflow).
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', BEST_FIVE_RELEASE + '^'], cwd=ROOT).decode().strip(),
            history.BASE)
        paths = subprocess.check_output(
            ['git', 'ls-tree', '-r', '-z', '--name-only', history.BASE],
            cwd=ROOT).decode().split('\0')
        rows = sorted((name, sha256(subprocess.check_output(
            ['git', 'show', history.BASE + ':' + name], cwd=ROOT)).hexdigest())
            for name in paths if name and not name.startswith(('_tests/', '_reports/')))
        self.assertEqual(len(rows), history.change()['production_count'])
        self.assertEqual(sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(),
                         history.change()['production_fingerprint'])

    def test_archived_inventory_is_checked_without_restoring_active_workflows(self):
        self.assertFalse((ROOT / '.github/workflows/site-checks.yml').exists())
        archived = subprocess.check_output(
            ['git', 'show', history.BASE + ':.github/workflows/site-checks.yml'],
            cwd=ROOT)
        self.assertTrue(archived)

    def test_unknown_changes_are_not_hidden(self):
        for name in history.PATHS:
            raw = (ROOT / name).read_bytes()
            for altered in (raw + b'!', b'!' + raw, raw[1:]):
                self.assertEqual(history.before(name, altered), altered)
        self.assertEqual(history.before('index.html', b'unrelated'), b'unrelated')

    def test_corrupt_records_cannot_reconstruct_history(self):
        name = 'poker/hand-rankings/index.html'
        raw = subsequent_changes.before(name, (ROOT / name).read_bytes())
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
