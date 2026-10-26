from pathlib import Path
from hashlib import sha256
import base64
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '501990c1079b89738aa19d9c48def5f1346bc09d'
PATHS = [
    '_source/poker/hand-rankings.html',
    'poker/hand-rankings/index.html',
    'poker/holdem-basics/index.html',
    'poker/library/index.html',
    'poker/omaha-and-mixed-games/index.html',
    'poker/topics/learn/index.html',
    'poker/topics/variants/index.html',
]


def old_bytes(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def compact_edit(new, old):
    start = 0
    limit = min(len(new), len(old))
    while start < limit and new[start] == old[start]:
        start += 1
    suffix = 0
    max_suffix = min(len(new) - start, len(old) - start)
    while suffix < max_suffix and new[len(new) - 1 - suffix] == old[len(old) - 1 - suffix]:
        suffix += 1
    new_end = len(new) - suffix
    old_end = len(old) - suffix
    replacement = base64.b64encode(old[start:old_end]).decode('ascii')
    return [[start, new_end, replacement]]


record = {'version': 1, 'base_commit': BASE, 'paths': {}}
for name in PATHS:
    current = (ROOT / name).read_bytes()
    previous = old_bytes(name)
    if current == previous:
        raise RuntimeError('Expected changed path: ' + name)
    record['paths'][name] = {
        'new_sha256': sha256(current).hexdigest(),
        'old_sha256': sha256(previous).hexdigest(),
        'edits': compact_edit(current, previous),
    }

names = subprocess.check_output(
    ['git', 'ls-tree', '-r', '--name-only', '-z', BASE], cwd=ROOT
).decode().split('\0')
rows = []
for name in names:
    if not name or name.startswith(('_tests/', '_reports/')):
        continue
    rows.append((name, sha256(old_bytes(name)).hexdigest()))
rows.sort()
record['production_count'] = len(rows)
record['production_fingerprint'] = sha256(
    json.dumps(rows, separators=(',', ':')).encode()
).hexdigest()
(ROOT / '_tests/best-five-change.json').write_text(
    json.dumps(record, indent=2) + '\n', encoding='utf-8'
)

history = '''"""Restore only the exact predecessor of the best-five showdown recaps.

Complete reviewed hashes gate every reversal. Unknown changes pass through,
and reconstructed bytes must match the independently captured parent hash.
This adapter is test-only and never runs in the published website.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = '501990c1079b89738aa19d9c48def5f1346bc09d'
PATHS = {
    '_source/poker/hand-rankings.html',
    'poker/hand-rankings/index.html',
    'poker/holdem-basics/index.html',
    'poker/library/index.html',
    'poker/omaha-and-mixed-games/index.html',
    'poker/topics/learn/index.html',
    'poker/topics/variants/index.html',
}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/best-five-change.json').read_text(encoding='utf-8'))
    if (type(record.get('version')) is not int or record['version'] != 1
            or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown best-five predecessor')
    return record


def before(path, data):
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    parts, offset = [], 0
    for start, end, replacement in item['edits']:
        if (type(start) is not int or type(end) is not int
                or not offset <= start <= end <= len(raw)
                or not isinstance(replacement, str)):
            raise ValueError('Invalid best-five predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    previous = b''.join(parts)
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt best-five predecessor: ' + str(path))
    return previous if binary else previous.decode('utf-8')
'''
(ROOT / '_tests/best_five_history.py').write_text(history, encoding='utf-8')

suite = '''"""The best-five recap release preserves the complete published predecessor."""
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
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\\0')
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
'''
(ROOT / '_tests/test_best_five_history.py').write_text(suite, encoding='utf-8')

chain_path = ROOT / '_tests/time_print_history.py'
chain = chain_path.read_text(encoding='utf-8')
old = "def before(path, data):\n    item = change()['paths'].get(str(path))"
new = "def before(path, data):\n    import best_five_history\n    data = best_five_history.before(path, data)\n    item = change()['paths'].get(str(path))"
if chain.count(old) != 1:
    raise RuntimeError('Unexpected workflow print history shape')
chain_path.write_text(chain.replace(old, new, 1), encoding='utf-8')

report_path = ROOT / '_reports/website-growth/turn-22-hand-ranking-best-five.md'
report = report_path.read_text(encoding='utf-8')
report += '''

## Release-integrity binding

Seven production paths are bound to the exact published parent at commit `501990c1079b89738aa19d9c48def5f1346bc09d`: the source guide, its generated page and five generated reading-time references. A hash-gated, test-only adapter reconstructs the complete predecessor only when every changed file matches its reviewed new hash. Unknown edits pass through unchanged, and corrupt records fail closed. The production inventory fingerprint confirms that no unrelated public path is hidden by this release history.
'''
report_path.write_text(report, encoding='utf-8')
