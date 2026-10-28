"""The visibility sprint cannot erase unreviewed changes from old contracts."""
import ast
import base64
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
sys.path.insert(0, str(ROOT / '_scripts'))
import visibility_sprint_history as history


class VisibilitySprintHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())

    def test_capsule_is_bound_to_the_actual_parent_and_complete_render_inventory(self):
        import build
        self.assertEqual(self.record['parent_commit'], '2aae4923318c0028d98266d78f6e4aabea295387')
        self.assertEqual(self.record['parent_tree'], '5cb303f7aec831e6f02f152455dbb2306e83fb37')
        tree = subprocess.check_output(['git', 'rev-parse', history.PARENT + '^{tree}'], cwd=ROOT).decode().strip()
        self.assertEqual(self.record['parent_tree'], tree)
        self.assertEqual(len(self.record['parent_outputs']), 223)
        current = build.build_outputs()
        restored = history.outputs(current)
        actual = {str(path): history.digest(value) for path, value in restored.items()}
        self.assertEqual(actual, self.record['parent_outputs'])
        self.assertEqual(history.outputs(restored), restored)

    def test_changed_files_restore_independently_captured_git_parent_bytes(self):
        for name, item in self.record['paths'].items():
            raw = (ROOT / name).read_bytes()
            original = subprocess.check_output(['git', 'show', history.PARENT + ':' + name], cwd=ROOT)
            with self.subTest(path=name):
                self.assertEqual(history.digest(raw), item['current_sha256'])
                self.assertEqual(history.digest(original), item['parent_sha256'])
                for path in [name, Path(name), ROOT / name]:
                    self.assertEqual(history.before(path, raw), original)
                    self.assertEqual(history.before(path, original), original)
                try:
                    text = raw.decode('utf-8')
                except UnicodeDecodeError:
                    continue
                self.assertEqual(history.before(name, text), original.decode('utf-8'))

    def test_unknown_mutations_and_wrong_paths_remain_visible(self):
        for name in self.record['paths']:
            raw = (ROOT / name).read_bytes()
            middle = len(raw) // 2
            for altered in [raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:],
                            raw[:middle] + b'UNREVIEWED' + raw[middle:], b'\xff\x00']:
                with self.subTest(path=name):
                    self.assertIs(history.before(name, altered), altered)
            self.assertIs(history.before('unreviewed/' + name, raw), raw)
            self.assertIs(history.before(ROOT.parent / 'other' / name, raw), raw)

    def test_corrupt_capsule_and_predecessor_bytes_fail_closed(self):
        raw = history.CHANGE.read_bytes()
        with TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'changed.json'
            changed.write_bytes(raw + b' ')
            history.change.cache_clear()
            with patch.object(history, 'CHANGE', changed):
                with self.assertRaisesRegex(ValueError, 'capsule digest'):
                    history.change()
            history.change.cache_clear()
        name = next(iter(self.record['paths']))
        current = (ROOT / name).read_bytes()
        for field, value in [('parent_sha256', '0' * 64), ('parent_size', -1),
                             ('parent_zlib_base64', base64.b64encode(zlib.compress(b'wrong')).decode()),
                             ('parent_zlib_base64', 'not base64!')]:
            bad = deepcopy(self.record)
            bad['paths'][name][field] = value
            with self.subTest(field=field), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, current)
        bad['paths'][name]['current_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=bad):
            self.assertIs(history.before(name, current), current)

    def test_only_exact_additions_are_removed_and_input_types_are_preserved(self):
        for name, expected in self.record['added_files'].items():
            raw = (ROOT / name).read_bytes()
            with self.subTest(path=name):
                self.assertEqual(history.digest(raw), expected)
                self.assertEqual(history.source_records({name: raw}), {})
                altered = raw + b'UNREVIEWED'
                self.assertEqual(history.source_records({name: altered}), {name: altered})
                for values in [[name, 'unreviewed.txt'], {name, 'unreviewed.txt'},
                               (ROOT / name, ROOT / 'unreviewed.txt')]:
                    result = history.files(values)
                    self.assertIsInstance(result, type(values))
                    self.assertEqual([history.key(p) for p in result], ['unreviewed.txt'])
                with patch.object(Path, 'read_bytes', return_value=altered):
                    self.assertEqual(history.files([name]), [name])
                if name not in self.record['added_outputs']:
                    self.assertEqual(history.outputs({name: raw}), {name: raw})
        unknown = {'unreviewed.txt': b'new material'}
        self.assertEqual(history.source_records(unknown), unknown)
        self.assertEqual(history.outputs(unknown), unknown)

    def test_complete_metadata_only_and_duplicate_additions_remain_detectable(self):
        for pair in self.record['pages']:
            current = pair['new']
            original = deepcopy(current)
            expected = [] if pair['old'] is None else [pair['old']]
            self.assertEqual(history.pages([current]), expected)
            self.assertEqual(current, original)
            for field in current:
                altered = {**current, field: 'UNREVIEWED'}
                if altered != current:
                    self.assertEqual(history.pages([altered]), [altered])
                if isinstance(current[field], bool):
                    for value in [int(current[field]), float(current[field])]:
                        altered = {**current, field: value}
                        self.assertEqual(history.pages([altered]), [altered])
            altered = {**current, 'unexpected': 'UNREVIEWED'}
            self.assertEqual(history.pages([altered]), [altered])
            if pair['old'] is None:
                self.assertEqual(history.pages([current, current]), [current])
        nested = {'id': 'unrelated', 'notes': [{'value': 'original'}]}
        result = history.pages([nested])
        result[0]['notes'][0]['value'] = 'changed'
        self.assertEqual(nested['notes'][0]['value'], 'original')

    def test_only_exact_successful_new_live_targets_are_filtered(self):
        import check_live
        current = check_live.targets()
        for route, item in self.record['added_targets'].items():
            response = current[route]
            self.assertEqual(response[0], 200)
            self.assertEqual(history.digest(response[1]), item['sha256'])
            self.assertEqual(history.live_targets({route: response}), {})
            for altered in [(404, response[1]), (200, response[1] + b'UNREVIEWED'),
                            [200, response[1]], (200, ''), (True, response[1])]:
                records = {route: altered}
                self.assertEqual(history.live_targets(records), records)
        unknown = {'/unreviewed/': (200, b'content')}
        self.assertEqual(history.live_targets(unknown), unknown)

    def test_older_golden_capsules_and_baselines_are_unchanged(self):
        names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', history.PARENT, '_tests'], cwd=ROOT).decode().splitlines()
        snapshots = [name for name in names if name.endswith(('-baseline.json', '-change.json'))]
        self.assertGreater(len(snapshots), 50)
        for name in snapshots:
            old = subprocess.check_output(['git', 'show', history.PARENT + ':' + name], cwd=ROOT)
            self.assertEqual((ROOT / name).read_bytes(), old, name)

    def test_new_leaf_has_no_runtime_or_older_history_dependency(self):
        tree = ast.parse(Path(history.__file__).read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                imports.add(node.module.split('.')[0])
        self.assertFalse(imports - sys.stdlib_module_names)
        for path in (ROOT / '_scripts').rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or '', *(alias.name for alias in node.names)]
                else:
                    continue
                self.assertFalse(any('visibility_sprint_history' in name.split('.') for name in names), str(path))


if __name__ == '__main__':
    unittest.main()
