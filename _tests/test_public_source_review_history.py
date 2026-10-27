"""The source-review capsule is exact, reversible and safe in older test views."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import brand_positioning_history as brand_history
import build
import public_source_review_history as history


class PublicSourceReviewHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.raw = {name: (ROOT / name).read_bytes() for name in history.PATHS}
        cls.pages = build.public_pages()

    def test_only_the_four_reviewed_files_and_published_parent_are_recorded(self):
        self.assertEqual(set(self.record['paths']), {
            '_source/pages.json', '_source/technology/home.html',
            'technology/index.html', 'sitemap.xml',
        })
        self.assertEqual(self.record['parent_commit'],
                         'a64bc51b6a39405a1ba59fbc589a9e190fce6229')
        self.assertEqual(self.record['parent_tree'],
                         '3fb7c1bb414db847c972516b5c558ce38712592c')
        for name, item in self.record['paths'].items():
            with self.subTest(path=name):
                self.assertEqual(history.digest(self.raw[name]), item['current_sha256'])
                self.assertNotEqual(item['parent_sha256'], item['current_sha256'])
                self.assertEqual(set(item), {'current_sha256', 'parent_sha256', 'edits'})

    def test_byte_and_text_views_reconstruct_exact_parents_and_are_idempotent(self):
        for name, item in self.record['paths'].items():
            raw = self.raw[name]
            previous = history.before(name, raw)
            with self.subTest(path=name):
                self.assertIsInstance(previous, bytes)
                self.assertEqual(history.digest(previous), item['parent_sha256'])
                self.assertEqual(history.before(name, previous), previous)
                for path in (name, Path(name), ROOT / name):
                    self.assertEqual(history.before(path, raw), previous)
                    text = history.before(path, raw.decode('utf-8'))
                    self.assertIsInstance(text, str)
                    self.assertEqual(text.encode('utf-8'), previous)
                    self.assertEqual(history.before(path, text), text)

    def test_unknown_mutations_and_binary_inputs_remain_visible(self):
        for name, raw in self.raw.items():
            midpoint = len(raw) // 2
            altered = (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:],
                       raw[:midpoint] + b'UNREVIEWED' + raw[midpoint:], b'\xff\x00')
            for value in altered:
                with self.subTest(path=name, mutation=history.digest(value)):
                    self.assertEqual(history.before(name, value), value)
                    self.assertEqual(brand_history.before(name, value), value)
            text = raw.decode('utf-8') + 'UNREVIEWED'
            self.assertEqual(history.before(name, text), text)
            self.assertEqual(brand_history.before(name, text), text)

    def test_known_bytes_at_unknown_or_external_paths_are_not_rewritten(self):
        raw = self.raw['technology/index.html']
        for name in ('other/index.html', 'technology/unreviewed.html',
                     ROOT.parent / 'another-site/technology/index.html'):
            with self.subTest(path=name):
                self.assertEqual(history.before(name, raw), raw)
                self.assertEqual(history.before(name, raw.decode()), raw.decode())

    def test_successor_hash_is_required_before_any_edits_are_considered(self):
        name = '_source/pages.json'
        bad = deepcopy(self.record)
        bad['paths'][name]['current_sha256'] = '0' * 64
        bad['paths'][name]['edits'] = None
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, self.raw[name]), self.raw[name])
        bad['paths'][name]['current_sha256'] = self.record['paths'][name]['current_sha256']
        changed = self.raw[name] + b'UNREVIEWED'
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, changed), changed)

    def test_corrupt_predecessor_and_replacement_content_fail_closed(self):
        name = '_source/pages.json'
        wrong_digest = deepcopy(self.record)
        wrong_digest['paths'][name]['parent_sha256'] = '0' * 64
        wrong_text = deepcopy(self.record)
        wrong_text['paths'][name]['edits'][0]['old'] += 'UNREVIEWED'
        for record in (wrong_digest, wrong_text):
            with patch.object(history, 'change', return_value=record):
                with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                    history.before(name, self.raw[name])

    def test_invalid_offsets_types_span_hashes_and_edit_fields_fail_closed(self):
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
            {**original, 'unexpected': True},
            missing,
            None,
        ]
        for index, edit in enumerate(cases):
            bad = deepcopy(self.record)
            bad['paths'][name]['edits'] = [edit]
            with self.subTest(case=index), patch.object(history, 'change', return_value=bad):
                with self.assertRaisesRegex(ValueError, 'edit span'):
                    history.before(name, self.raw[name])

    def test_missing_overlapping_and_out_of_order_edits_fail_closed(self):
        name = '_source/technology/home.html'
        edits = self.record['paths'][name]['edits']
        cases = ([], None, edits[1:], [edits[0], edits[0], *edits[1:]], list(reversed(edits)))
        for index, changed in enumerate(cases):
            bad = deepcopy(self.record)
            bad['paths'][name]['edits'] = deepcopy(changed)
            with self.subTest(case=index), patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, self.raw[name])

    def test_record_identity_scope_and_metadata_corruption_are_rejected(self):
        bad_records = []
        for field, wrong in (('version', True), ('parent_commit', '0' * 40),
                             ('parent_tree', '0' * 40)):
            bad = deepcopy(self.record)
            bad[field] = wrong
            bad_records.append(bad)
        bad = deepcopy(self.record)
        bad['paths']['unreviewed.html'] = bad['paths']['technology/index.html']
        bad_records.append(bad)
        bad = deepcopy(self.record)
        del bad['paths']['sitemap.xml']
        bad_records.append(bad)
        bad = deepcopy(self.record)
        bad['page']['new']['description'] = 'A changed claim'
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

    def test_metadata_matches_raw_and_rendered_records_and_restored_parent(self):
        raw_records = json.loads(self.raw['_source/pages.json'])
        previous_records = json.loads(history.before('_source/pages.json', self.raw['_source/pages.json']))
        pair = self.record['page']
        for records in (raw_records, self.pages):
            technology = next(page for page in records if page['id'] == 'technology')
            self.assertEqual(technology, pair['new'])
            self.assertEqual(history.pages([technology]), [pair['old']])
            previous = history.pages(records)
            for current, restored in zip(records, previous):
                if current['id'] != 'technology':
                    self.assertEqual(current, restored)
        self.assertEqual(next(page for page in previous_records if page['id'] == 'technology'),
                         pair['old'])
        self.assertEqual(pair['old'], {**pair['new'], 'updated': '2026-10-26'})

    def test_changed_missing_and_additional_metadata_fields_remain_visible(self):
        current = self.record['page']['new']
        cases = []
        for field in current:
            altered = deepcopy(current)
            altered[field] = 'UNREVIEWED'
            cases.append(altered)
            missing = deepcopy(current)
            del missing[field]
            cases.append(missing)
        cases.extend(({**current, 'noindex': True},
                      {**current, 'extra_claim': 'UNREVIEWED'}))
        for index, altered in enumerate(cases):
            with self.subTest(case=index):
                self.assertEqual(history.pages([altered]), [altered])
                self.assertEqual(brand_history.pages([altered]), [altered])

    def test_metadata_reversal_is_idempotent_and_never_mutates_inputs(self):
        current = deepcopy(self.pages)
        saved = deepcopy(current)
        previous = history.pages(current)
        self.assertEqual(current, saved)
        self.assertEqual(history.pages(previous), previous)
        previous[0]['title'] = 'Changed only in the returned view'
        self.assertEqual(current, saved)
        self.assertEqual(history.pages([self.record['page']['new']]), [self.record['page']['old']])

    def test_latest_leaf_composes_with_brand_and_common_output_history(self):
        import beginner_history
        for name, current in self.raw.items():
            parent = history.before(name, current)
            with self.subTest(path=name):
                self.assertEqual(brand_history.before(name, current), brand_history.before(name, parent))
                self.assertEqual(beginner_history.outputs({Path(name): current.decode('utf-8')}),
                                 beginner_history.outputs({Path(name): parent.decode('utf-8')}))
        current = deepcopy(self.pages)
        self.assertEqual(brand_history.pages(current), brand_history.pages(history.pages(current)))

    def test_common_output_chain_preserves_unknown_paths_and_current_mutations(self):
        import beginner_history
        records = {Path(name): raw.decode('utf-8') + 'UNREVIEWED' for name, raw in self.raw.items()}
        records[Path('unreviewed.html')] = self.raw['technology/index.html'].decode('utf-8')
        self.assertEqual(beginner_history.outputs(records), records)


if __name__ == '__main__':
    unittest.main()
