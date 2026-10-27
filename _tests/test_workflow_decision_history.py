"""The human decision release has one exact predecessor, not a broad exemption."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import build
import answer_record_history
import public_source_review_history as source_history
import workflow_decision_history as history


class WorkflowDecisionHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.current_raw = {name: (ROOT / name).read_bytes() for name in history.PATHS}
        # Compare this archived layer at its own exact successor boundary.
        # Keep the unnormalized current files for unknown-mutation checks.
        cls.raw = {name: answer_record_history.before(name, raw)
                   for name, raw in cls.current_raw.items()}
        cls.pages = answer_record_history.pages(build.public_pages())

    def test_current_files_and_scope_match_the_published_parent_boundary(self):
        self.assertEqual(set(self.record['paths']), {
            '_source/pages.json', '_source/technology/ai-time-savings.html',
            'assets/workflow-time.js', 'technology/ai-time-savings/index.html', 'sitemap.xml',
        })
        self.assertEqual(self.record['parent_commit'], '962e489bb557ee6dfda3a48524a4bc8953f3c8e8')
        self.assertEqual(self.record['parent_tree'], 'c58a229171ec97246111faccc80d411969e42010')
        for name, item in self.record['paths'].items():
            with self.subTest(path=name):
                self.assertEqual(history.digest(self.raw[name]), item['current_sha256'])
                self.assertNotEqual(item['parent_sha256'], item['current_sha256'])
                self.assertEqual(set(item), {'current_sha256', 'parent_sha256', 'edits'})

    def test_exact_reversal_preserves_byte_text_and_path_types_and_is_idempotent(self):
        for name, item in self.record['paths'].items():
            raw = self.raw[name]
            previous = history.before(name, raw)
            with self.subTest(path=name):
                self.assertIsInstance(previous, bytes)
                self.assertEqual(history.digest(previous), item['parent_sha256'])
                for path in (name, Path(name), ROOT / name):
                    self.assertEqual(history.before(path, raw), previous)
                    text = history.before(path, raw.decode('utf-8'))
                    self.assertIsInstance(text, str)
                    self.assertEqual(text.encode('utf-8'), previous)
                    self.assertEqual(history.before(path, previous), previous)
                    self.assertEqual(history.before(path, text), text)

    def test_unknown_whole_file_mutations_and_binary_inputs_pass_through(self):
        for name, raw in self.current_raw.items():
            midpoint = len(raw) // 2
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:],
                            raw[:midpoint] + b'UNREVIEWED' + raw[midpoint:], b'\xff\x00'):
                with self.subTest(path=name, mutation=history.digest(altered)):
                    self.assertEqual(history.before(name, altered), altered)
            changed = raw.decode('utf-8') + 'UNREVIEWED'
            self.assertEqual(history.before(name, changed), changed)

    def test_known_bytes_at_other_paths_never_activate_the_reversal(self):
        raw = self.raw['assets/workflow-time.js']
        for name in ('assets/unreviewed.js', 'technology/other/index.html',
                     ROOT.parent / 'different-site/assets/workflow-time.js'):
            with self.subTest(path=name):
                self.assertEqual(history.before(name, raw), raw)
                self.assertEqual(history.before(name, raw.decode()), raw.decode())

    def test_successor_hash_is_checked_before_reversal_data(self):
        name = '_source/pages.json'
        bad = deepcopy(self.record)
        bad['paths'][name].update(current_sha256='0' * 64, edits=None)
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, self.raw[name]), self.raw[name])
        bad['paths'][name]['current_sha256'] = self.record['paths'][name]['current_sha256']
        altered = self.raw[name] + b'UNREVIEWED'
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, altered), altered)

    def test_corrupt_predecessor_hash_or_replacement_content_fails_closed(self):
        for name in ('assets/workflow-time.js', '_source/pages.json'):
            bad_hash = deepcopy(self.record)
            bad_hash['paths'][name]['parent_sha256'] = '0' * 64
            bad_text = deepcopy(self.record)
            bad_text['paths'][name]['edits'][0]['old'] += 'UNREVIEWED'
            for bad in (bad_hash, bad_text):
                with self.subTest(path=name), patch.object(history, 'change', return_value=bad):
                    with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                        history.before(name, self.raw[name])

    def test_invalid_span_offsets_types_hashes_and_fields_fail_closed(self):
        name = '_source/pages.json'
        original = self.record['paths'][name]['edits'][0]
        missing = deepcopy(original)
        del missing['old']
        cases = [
            {**original, 'start': -1},
            {**original, 'end': len(self.raw[name].decode()) + 1},
            {**original, 'start': original['end'] + 1},
            {**original, 'start': True},
            {**original, 'end': str(original['end'])},
            {**original, 'old': None},
            {**original, 'current_sha256': '0' * 64},
            {**original, 'unexpected': True}, missing, None,
        ]
        for index, edit in enumerate(cases):
            bad = deepcopy(self.record)
            bad['paths'][name]['edits'] = [edit]
            with self.subTest(case=index), patch.object(history, 'change', return_value=bad):
                with self.assertRaisesRegex(ValueError, 'edit span'):
                    history.before(name, self.raw[name])

    def test_missing_overlapping_and_reordered_edits_fail_closed(self):
        name = 'assets/workflow-time.js'
        edits = self.record['paths'][name]['edits']
        cases = ([], None, edits[1:], [edits[0], edits[0], *edits[1:]], list(reversed(edits)))
        for index, changed in enumerate(cases):
            bad = deepcopy(self.record)
            bad['paths'][name]['edits'] = deepcopy(changed)
            with self.subTest(case=index), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, self.raw[name])

    def test_record_parent_scope_and_metadata_corruption_are_rejected(self):
        bad_records = []
        for field, wrong in (('version', True), ('parent_commit', '0' * 40),
                             ('parent_tree', '0' * 40)):
            bad = deepcopy(self.record)
            bad[field] = wrong
            bad_records.append(bad)
        for remove in (False, True):
            bad = deepcopy(self.record)
            if remove:
                del bad['paths']['sitemap.xml']
            else:
                bad['paths']['unreviewed.js'] = bad['paths']['assets/workflow-time.js']
            bad_records.append(bad)
        bad = deepcopy(self.record)
        bad['page']['new']['description'] = 'An unreviewed claim'
        bad_records.append(bad)
        for index, bad in enumerate(bad_records):
            history.change.cache_clear()
            try:
                with self.subTest(case=index), patch.object(history, 'CHANGE') as location:
                    location.read_text.return_value = json.dumps(bad)
                    with self.assertRaises(ValueError):
                        history.change()
            finally:
                history.change.cache_clear()

    def test_complete_calculator_metadata_matches_raw_and_public_manifests(self):
        pair = self.record['page']
        raw_pages = json.loads(self.raw['_source/pages.json'])
        parent_pages = json.loads(history.before('_source/pages.json', self.raw['_source/pages.json']))
        for records in (raw_pages, self.pages):
            current = next(page for page in records if page['id'] == 'ai-time-savings')
            self.assertEqual(current, pair['new'])
            self.assertEqual(history.pages([current]), [pair['old']])
            restored = history.pages(records)
            for old, new in zip(records, restored):
                if old['id'] != 'ai-time-savings':
                    self.assertEqual(old, new)
        self.assertEqual(next(page for page in parent_pages if page['id'] == 'ai-time-savings'),
                         pair['old'])
        self.assertEqual(pair['old'], {**pair['new'], 'updated': '2026-10-11'})

    def test_partial_or_modified_metadata_cannot_match_and_inputs_are_copied(self):
        current = self.record['page']['new']
        for field in current:
            altered = {**current, field: 'UNREVIEWED'}
            missing = deepcopy(current)
            del missing[field]
            for record in (altered, missing):
                with self.subTest(field=field, keys=list(record)):
                    self.assertEqual(history.pages([record]), [record])
                    self.assertEqual(source_history.pages([record]), [record])
        for record in ({**current, 'noindex': True}, {**current, 'extra_claim': 'UNREVIEWED'}):
            self.assertEqual(history.pages([record]), [record])
        saved = deepcopy(self.pages)
        previous = history.pages(self.pages)
        self.assertEqual(history.pages(previous), previous)
        previous[0]['title'] = 'Only changed in the returned view'
        self.assertEqual(self.pages, saved)

    def test_shared_manifest_and_sitemap_reach_the_previous_source_review_boundary(self):
        earlier = source_history.change()['paths']
        for name in ('_source/pages.json', 'sitemap.xml'):
            with self.subTest(path=name):
                self.assertEqual(self.record['paths'][name]['parent_sha256'], earlier[name]['current_sha256'])
                self.assertEqual(history.digest(source_history.before(name, self.raw[name])),
                                 earlier[name]['parent_sha256'])
        self.assertEqual(source_history.pages(self.pages), source_history.pages(history.pages(self.pages)))

    def test_current_raw_files_compose_through_the_oldest_common_history_chain(self):
        import beginner_history
        for name, raw in self.current_raw.items():
            parent = history.before(name, raw)
            with self.subTest(path=name):
                self.assertEqual(beginner_history.before(name, raw), beginner_history.before(name, parent))
                self.assertEqual(beginner_history.outputs({Path(name): raw.decode()}),
                                 beginner_history.outputs({Path(name): parent.decode()}))

    def test_deepest_common_chain_keeps_unknown_changes_detectable(self):
        import beginner_history
        for name, raw in self.current_raw.items():
            previous = beginner_history.before(name, raw)
            for altered in (b'UNREVIEWED' + raw, raw + b'UNREVIEWED'):
                with self.subTest(path=name, prefix=altered.startswith(b'UNREVIEWED')):
                    restored = beginner_history.before(name, altered)
                    self.assertNotEqual(restored, previous)
                    self.assertIn(b'UNREVIEWED', restored)
        unknown = {Path('unreviewed.js'): self.raw['assets/workflow-time.js'].decode()}
        self.assertEqual(beginner_history.outputs(unknown), unknown)


if __name__ == '__main__':
    unittest.main()
