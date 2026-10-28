"""The practice connection restores only its actual published predecessor."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import ranking_practice_history as history

# Independently captured with git show dfdcdc64:<path>, before generating the
# reverse spans. These are whole files from the published parent, not hashes
# derived from the adapter's reconstruction.
PUBLISHED_PARENT_HASHES = {
    '_source/pages.json':
        'a8054aae31450162f9a21a0bddff1045a9b1fa11d2ecb96a7b59818f73665ee5',
    '_source/poker/hand-rankings.html':
        '12e66e982e63cd7175f38183c2cb51e1f769e6186859d8a86848c7f4f83664e1',
    'assets/poker-hand-lab.css':
        '4799a6fbbda1ffff1211c951cacc91bf5f2c84e25344c18efeda3cd8d420b996',
    'find/index.html':
        '576675c835ad28ff80d12c57dcbb5c374e1ea60dc1baf69fdc4a444d87d10a5f',
    'poker/find/index.html':
        '717a9323fb0528b88a7eb6e79a44164315597093f40ce66185b5ecf9952f8e8c',
    'poker/free-poker-learning-path/index.html':
        '0171191be048092bac27bf1e9504cdaa90f3b166822424ecaa392480b80feb02',
    'poker/hand-rankings/index.html':
        '31fb0b50bf14febb5ac1619f4dd854a077be9d425f331872dc5bbfdb051d2f4b',
    'sitemap.xml':
        'a82c7f44fb8f5bb8ecba0ff02854df3027a0b3b40d691fc5ac29847fcbdf89ff',
}


class RankingPracticeHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.raw = {name: (ROOT / name).read_bytes() for name in history.PATHS}
        cls.pages = json.loads(cls.raw['_source/pages.json'])

    def test_eight_current_files_restore_the_independently_captured_parent(self):
        self.assertEqual(set(self.record['paths']), set(PUBLISHED_PARENT_HASHES))
        self.assertEqual(history.PATHS, set(PUBLISHED_PARENT_HASHES))
        self.assertEqual(self.record['parent_commit'],
                         'dfdcdc64dd096f7bdcab0569f19d6cc466c5584b')
        self.assertEqual(self.record['parent_tree'],
                         'bfce9e3713ff4413450aff2dccb1a0b326f38748')
        for name, expected in PUBLISHED_PARENT_HASHES.items():
            item = self.record['paths'][name]
            with self.subTest(path=name):
                self.assertEqual(sha256(self.raw[name]).hexdigest(), item['current_sha256'])
                self.assertEqual(item['parent_sha256'], expected)
                self.assertNotEqual(item['current_sha256'], expected)
                self.assertEqual(sha256(history.before(name, self.raw[name])).hexdigest(), expected)

    def test_reversal_preserves_types_paths_and_idempotence(self):
        for name, raw in self.raw.items():
            previous = history.before(name, raw)
            with self.subTest(path=name):
                self.assertIsInstance(previous, bytes)
                for path in (name, Path(name), ROOT / name):
                    self.assertEqual(history.before(path, raw), previous)
                    text = history.before(path, raw.decode('utf-8'))
                    self.assertIsInstance(text, str)
                    self.assertEqual(text.encode('utf-8'), previous)
                    self.assertEqual(history.before(path, previous), previous)
                    self.assertEqual(history.before(path, text), text)

    def test_unknown_bytes_and_unrelated_paths_remain_visible(self):
        for name, raw in self.raw.items():
            midpoint = len(raw) // 2
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:],
                            raw[:midpoint] + b'UNREVIEWED' + raw[midpoint:], b'\xff\x00'):
                with self.subTest(path=name, mutation=sha256(altered).hexdigest()):
                    self.assertIs(history.before(name, altered), altered)
            text = raw.decode('utf-8') + 'UNREVIEWED'
            self.assertIs(history.before(name, text), text)
        raw = self.raw['poker/hand-rankings/index.html']
        for path in ('poker/unreviewed/index.html',
                     ROOT.parent / 'other/poker/hand-rankings/index.html'):
            self.assertIs(history.before(path, raw), raw)

    def test_whole_successor_hash_is_checked_before_reverse_spans(self):
        name = '_source/pages.json'
        bad = deepcopy(self.record)
        bad['paths'][name].update(current_sha256='0' * 64, edits=None)
        with patch.object(history, 'change', return_value=bad):
            self.assertIs(history.before(name, self.raw[name]), self.raw[name])
        bad['paths'][name]['current_sha256'] = self.record['paths'][name]['current_sha256']
        altered = self.raw[name] + b'UNREVIEWED'
        with patch.object(history, 'change', return_value=bad):
            self.assertIs(history.before(name, altered), altered)
            with self.assertRaisesRegex(ValueError, 'edits'):
                history.before(name, self.raw[name])

    def test_invalid_incomplete_or_reordered_reverse_spans_fail_closed(self):
        name = '_source/poker/hand-rankings.html'
        original = self.record['paths'][name]['edits']
        self.assertGreaterEqual(len(original), 2)
        cases = [[], None, {}, original[1:], [original[0], *original], list(reversed(original))]
        for field, value in (('start', -1), ('start', True),
                             ('end', len(self.raw[name].decode('utf-8')) + 1),
                             ('end', '1'), ('old', None),
                             ('current_sha256', '0' * 64), ('extra', True)):
            changed = deepcopy(original)
            changed[0][field] = value
            cases.append(changed)
        missing = deepcopy(original)
        del missing[0]['old']
        cases.extend((missing, [None]))
        for index, edits in enumerate(cases):
            bad = deepcopy(self.record)
            bad['paths'][name]['edits'] = edits
            with self.subTest(case=index), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, self.raw[name])

    def test_complete_parent_digest_rejects_wrong_replacements_and_parent_hashes(self):
        name = '_source/poker/hand-rankings.html'
        for field in ('parent_sha256', 'old'):
            bad = deepcopy(self.record)
            if field == 'old':
                bad['paths'][name]['edits'][0]['old'] = 'UNREVIEWED'
            else:
                bad['paths'][name][field] = '0' * 64
            with self.subTest(field=field), patch.object(history, 'change', return_value=bad):
                with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                    history.before(name, self.raw[name])

    def test_parent_scope_file_shape_and_complete_metadata_corruption_are_rejected(self):
        cases = [None, [], {}]
        for field, value in (('version', True), ('parent_commit', '0' * 40),
                             ('parent_tree', '0' * 40), ('paths', None),
                             ('pages', None), ('extra', True)):
            bad = deepcopy(self.record)
            bad[field] = value
            cases.append(bad)
        for field in self.record:
            bad = deepcopy(self.record)
            del bad[field]
            cases.append(bad)
        for remove in (True, False):
            bad = deepcopy(self.record)
            if remove:
                del bad['paths']['sitemap.xml']
            else:
                bad['paths']['unreviewed.js'] = bad['paths']['sitemap.xml']
            cases.append(bad)
        for field, value in (('current_sha256', 'x' * 64), ('parent_sha256', None),
                             ('extra', True)):
            bad = deepcopy(self.record)
            bad['paths']['sitemap.xml'][field] = value
            cases.append(bad)
        bad = deepcopy(self.record)
        bad['paths']['sitemap.xml'] = None
        cases.append(bad)
        for side in ('old', 'new'):
            for field in self.record['pages'][history.PAGE_ID][side]:
                bad = deepcopy(self.record)
                bad['pages'][history.PAGE_ID][side][field] = 'UNREVIEWED'
                cases.append(bad)
            bad = deepcopy(self.record)
            bad['pages'][history.PAGE_ID][side] = None
            cases.append(bad)
        for pair in ({}, None, {'old': {}, 'new': {}, 'extra': True}):
            bad = deepcopy(self.record)
            bad['pages'][history.PAGE_ID] = pair
            cases.append(bad)
        bad = deepcopy(self.record)
        bad['pages']['unreviewed-page'] = bad['pages'].pop(history.PAGE_ID)
        cases.append(bad)
        # Even matching corruption on both sides must not establish a new
        # accepted metadata boundary.
        bad = deepcopy(self.record)
        for side in ('old', 'new'):
            bad['pages'][history.PAGE_ID][side]['description'] = 'UNREVIEWED'
        cases.append(bad)
        for index, bad in enumerate(cases):
            history.change.cache_clear()
            try:
                with self.subTest(case=index), patch.object(history, 'CHANGE') as location:
                    location.read_text.return_value = json.dumps(bad)
                    with self.assertRaises(ValueError):
                        history.change()
            finally:
                history.change.cache_clear()

    def test_complete_page_records_match_both_manifest_versions(self):
        pair = self.record['pages'][history.PAGE_ID]
        previous = json.loads(history.before('_source/pages.json', self.raw['_source/pages.json']))
        self.assertEqual(history.pages(self.pages), previous)
        self.assertEqual(next(p for p in self.pages if p['id'] == history.PAGE_ID), pair['new'])
        self.assertEqual(next(p for p in previous if p['id'] == history.PAGE_ID), pair['old'])
        self.assertEqual(pair['old']['date'], pair['new']['date'])
        changed = {key for key in pair['old'].keys() | pair['new'].keys()
                   if pair['old'].get(key) != pair['new'].get(key)}
        self.assertEqual(changed, {'updated', 'revision'})
        self.assertEqual(history.pages(previous), previous)

    def test_partial_unreviewed_metadata_and_nested_inputs_are_copied(self):
        pair = self.record['pages'][history.PAGE_ID]
        current = pair['new']
        for field in current:
            missing = deepcopy(current)
            del missing[field]
            for altered in ({**current, field: 'UNREVIEWED'}, missing):
                self.assertEqual(history.pages([altered]), [altered])
        for altered in ({**current, 'noindex': True}, {**current, 'extra': 'UNREVIEWED'}):
            self.assertEqual(history.pages([altered]), [altered])
        nested = {'id': 'unrelated', 'notes': [{'value': 'original'}]}
        inputs = [deepcopy(current), nested, deepcopy(current)]
        saved = deepcopy(inputs)
        restored = history.pages(inputs)
        self.assertEqual(restored, [pair['old'], nested, pair['old']])
        restored[0]['title'] = 'Changed copy'
        restored[1]['notes'][0]['value'] = 'Changed nested copy'
        self.assertEqual(inputs, saved)
        self.assertEqual(restored[2], pair['old'])
        self.assertEqual(history.change()['pages'][history.PAGE_ID], pair)

    def test_leaf_composes_first_and_unknown_changes_survive_the_oldest_chain(self):
        import answer_record_history
        import beginner_history
        import first_tournament_plan_history
        for name, raw in self.raw.items():
            parent = history.before(name, raw)
            for adapter in (first_tournament_plan_history, answer_record_history, beginner_history):
                with self.subTest(path=name, adapter=adapter.__name__):
                    self.assertEqual(adapter.before(name, raw), adapter.before(name, parent))
                    for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw):
                        self.assertEqual(adapter.before(name, altered), altered)
        for adapter in (first_tournament_plan_history, answer_record_history, beginner_history):
            self.assertEqual(adapter.pages(self.pages), adapter.pages(history.pages(self.pages)))
            altered = {**self.record['pages'][history.PAGE_ID]['new'],
                       'description': 'UNREVIEWED'}
            self.assertEqual(adapter.pages([altered]), [altered])

    def test_new_leaf_depends_only_on_the_standard_library(self):
        tree = ast.parse(Path(history.__file__).read_text(encoding='utf-8'))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                imports.add(node.module.split('.')[0])
        self.assertFalse(imports - sys.stdlib_module_names)


if __name__ == '__main__':
    unittest.main()
