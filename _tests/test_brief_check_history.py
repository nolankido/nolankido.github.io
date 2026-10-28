"""The answer-check handoff restores only its actual published predecessor."""
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
import brief_check_history as history

# Independently captured with git show 427f258a:<path>, before generating the
# reverse spans. These are whole files from the published parent, not hashes
# derived from the adapter's reconstruction.
PUBLISHED_PARENT_HASHES = {
    '_source/pages.json':
        'a7cbb3b93806e87fac0efcbb4b07ca803240909cc28e77489ecf206f19889b09',
    '_source/technology/task-brief.html':
        '037275484fcd3e44015634932718cd16f81edcb43b92c95eb510cc0b309b0614',
    'find/index.html':
        '7e4b493da15d88f32329e2faa6812d39450b6056f1e4b301ea90601ad8a1f15e',
    'sitemap.xml':
        '76a07cd983941c43dabe1aad3aadba58a6450cdeb3cbf579457fac1817a14103',
    'technology/task-brief/index.html':
        '54a63337a2cc037eec8f8a0ba05c84a80dfe25ba2d903b44829a59e95d4db5b9',
}


class BriefCheckHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.raw = {name: (ROOT / name).read_bytes() for name in history.PATHS}
        cls.pages = json.loads(cls.raw['_source/pages.json'])

    def test_five_current_files_restore_the_independently_captured_parent(self):
        self.assertEqual(set(self.record['paths']), set(PUBLISHED_PARENT_HASHES))
        self.assertEqual(history.PATHS, set(PUBLISHED_PARENT_HASHES))
        self.assertEqual(self.record['parent_commit'],
                         '427f258ad895cfc736d3d29944347ea584f04826')
        self.assertEqual(self.record['parent_tree'],
                         'f51ffdb98ccb618896e25d6d729cc7919536a92d')
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
        raw = self.raw['technology/task-brief/index.html']
        for path in ('poker/unreviewed/index.html',
                     ROOT.parent / 'other/technology/task-brief/index.html'):
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
        name = '_source/technology/task-brief.html'
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
        name = '_source/technology/task-brief.html'
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
        self.assertNotIn('date', pair['old'])
        self.assertNotIn('date', pair['new'])
        self.assertNotIn('revision', pair['new'])
        changed = {key for key in pair['old'].keys() | pair['new'].keys()
                   if pair['old'].get(key) != pair['new'].get(key)}
        self.assertEqual(changed, {'updated'})
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
        import ranking_practice_history
        import task_brief_walkthrough_history
        for name, raw in self.raw.items():
            parent = history.before(name, raw)
            for adapter in (ranking_practice_history, first_tournament_plan_history,
                            answer_record_history, task_brief_walkthrough_history, beginner_history):
                with self.subTest(path=name, adapter=adapter.__name__):
                    self.assertEqual(adapter.before(name, raw), adapter.before(name, parent))
                    for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw):
                        self.assertEqual(adapter.before(name, altered), altered)
        for adapter in (ranking_practice_history, first_tournament_plan_history,
                        answer_record_history, task_brief_walkthrough_history, beginner_history):
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
