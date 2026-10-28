"""The first-event plan preserves only its exact published predecessor."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import first_tournament_plan_history as history
import build


class FirstTournamentPlanHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.raw = {name: (ROOT / name).read_bytes() for name in history.PATHS}
        cls.pages = build.public_pages()

    def test_fifteen_current_files_are_bound_to_the_published_parent(self):
        self.assertEqual(set(self.record['paths']), {
            '_source/pages.json', '_source/poker/first-live-tournament.html',
            '_source/poker/tournament-checklists.html', 'downloads/poker-event-planner.md',
            'find/index.html', 'poker/find/index.html',
            'poker/first-live-tournament/index.html', 'poker/library/index.html',
            'poker/poker-access-and-protection/index.html',
            'poker/poker-rules-and-fair-play/index.html',
            'poker/thunder-valley-poker-guide/index.html',
            'poker/topics/places-to-play/index.html',
            'poker/topics/tournaments/index.html',
            'poker/tournament-checklists/index.html', 'sitemap.xml',
        })
        self.assertEqual(self.record['parent_commit'], '74e064631e59e7659826144390dc77d49d2022ed')
        self.assertEqual(self.record['parent_tree'], '24495e6156dd0d5abf71c707fb7bbd0f195e4983')
        for name, item in self.record['paths'].items():
            with self.subTest(path=name):
                self.assertEqual(set(item), {'current_sha256', 'parent_sha256', 'edits'})
                self.assertEqual(history.digest(self.raw[name]), item['current_sha256'])
                self.assertNotEqual(item['current_sha256'], item['parent_sha256'])

    def test_exact_reversal_preserves_types_paths_and_idempotence(self):
        for name, item in self.record['paths'].items():
            raw = self.raw[name]
            old = history.before(name, raw)
            with self.subTest(path=name):
                self.assertIsInstance(old, bytes)
                self.assertEqual(history.digest(old), item['parent_sha256'])
                for path in (name, Path(name), ROOT / name):
                    self.assertEqual(history.before(path, raw), old)
                    text = history.before(path, raw.decode('utf-8'))
                    self.assertIsInstance(text, str)
                    self.assertEqual(text.encode('utf-8'), old)
                    self.assertEqual(history.before(path, old), old)
                    self.assertEqual(history.before(path, text), text)

    def test_unknown_bytes_and_unrelated_paths_never_activate_a_reversal(self):
        for name, raw in self.raw.items():
            midpoint = len(raw) // 2
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:],
                            raw[:midpoint] + b'UNREVIEWED' + raw[midpoint:], b'\xff\x00'):
                with self.subTest(path=name, mutation=history.digest(altered)):
                    self.assertEqual(history.before(name, altered), altered)
            text = raw.decode() + 'UNREVIEWED'
            self.assertEqual(history.before(name, text), text)
        raw = self.raw['downloads/poker-event-planner.md']
        for name in ('downloads/unreviewed.md', ROOT.parent / 'other/downloads/poker-event-planner.md'):
            self.assertEqual(history.before(name, raw), raw)

    def test_successor_hash_is_checked_before_corrupt_edits(self):
        name = '_source/pages.json'
        bad = deepcopy(self.record)
        bad['paths'][name].update(current_sha256='0' * 64, edits=None)
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, self.raw[name]), self.raw[name])
        bad['paths'][name]['current_sha256'] = self.record['paths'][name]['current_sha256']
        changed = self.raw[name] + b'UNREVIEWED'
        with patch.object(history, 'change', return_value=bad):
            self.assertEqual(history.before(name, changed), changed)

    def test_invalid_or_incomplete_reverse_edits_fail_closed(self):
        name = '_source/poker/first-live-tournament.html'
        original = self.record['paths'][name]['edits']
        self.assertGreaterEqual(len(original), 2)
        cases = [[], None, original[1:], [original[0], *original], list(reversed(original))]
        for field, value in (('start', -1), ('start', True),
                             ('end', len(self.raw[name].decode()) + 1),
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
        for field in ('parent_sha256', 'old'):
            bad = deepcopy(self.record)
            if field == 'old':
                bad['paths'][name]['edits'][0]['old'] += 'UNREVIEWED'
            else:
                bad['paths'][name][field] = '0' * 64
            with patch.object(history, 'change', return_value=bad):
                with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                    history.before(name, self.raw[name])

    def test_parent_scope_file_shape_and_metadata_corruption_are_rejected(self):
        cases = []
        for field, value in (('version', True), ('parent_commit', '0' * 40),
                             ('parent_tree', '0' * 40), ('paths', None), ('pages', None)):
            bad = deepcopy(self.record)
            bad[field] = value
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
        for page_id in self.record['pages']:
            for side, field in (('new', 'description'), ('new', 'revision'),
                                ('new', 'path'), ('old', 'updated'), ('old', 'revision')):
                bad = deepcopy(self.record)
                bad['pages'][page_id][side][field] = 'UNREVIEWED'
                cases.append(bad)
            bad = deepcopy(self.record)
            del bad['pages'][page_id]
            cases.append(bad)
            bad = deepcopy(self.record)
            bad['pages'][page_id] = None
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

    def test_complete_metadata_matches_current_and_reconstructed_manifests(self):
        raw_pages = json.loads(self.raw['_source/pages.json'])
        previous = json.loads(history.before('_source/pages.json', self.raw['_source/pages.json']))
        for pages in (raw_pages, self.pages):
            restored = history.pages(pages)
            for new, old in zip(pages, restored):
                pair = self.record['pages'].get(new['id'])
                if pair:
                    self.assertEqual(new, pair['new'])
                    self.assertEqual(old, pair['old'])
                else:
                    self.assertEqual(old, new)
        for page_id, pair in self.record['pages'].items():
            with self.subTest(page=page_id):
                self.assertEqual(next(p for p in previous if p['id'] == page_id), pair['old'])
                self.assertEqual(pair['old']['date'], '2026-10-08')
                self.assertEqual(pair['new']['date'], '2026-10-08')

    def test_partial_or_changed_metadata_stays_visible_and_inputs_are_copied(self):
        for pair in self.record['pages'].values():
            current = pair['new']
            for field in current:
                missing = deepcopy(current)
                del missing[field]
                for altered in ({**current, field: 'UNREVIEWED'}, missing):
                    self.assertEqual(history.pages([altered]), [altered])
            for altered in ({**current, 'noindex': True}, {**current, 'extra_claim': 'UNREVIEWED'}):
                self.assertEqual(history.pages([altered]), [altered])
        saved = deepcopy(self.pages)
        old = history.pages(self.pages)
        self.assertEqual(history.pages(old), old)
        old[0]['title'] = 'Changed only in the returned view'
        self.assertEqual(self.pages, saved)

    def test_new_leaf_composes_through_the_oldest_chain_without_hiding_mutations(self):
        import answer_record_history
        import beginner_history
        for name, raw in self.raw.items():
            parent = history.before(name, raw)
            with self.subTest(path=name):
                self.assertEqual(beginner_history.before(name, raw),
                                 beginner_history.before(name, parent))
                for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw):
                    self.assertEqual(beginner_history.before(name, altered), altered)
        self.assertEqual(answer_record_history.pages(self.pages),
                         answer_record_history.pages(history.pages(self.pages)))
        self.assertEqual(beginner_history.pages(self.pages),
                         beginner_history.pages(history.pages(self.pages)))
        for pair in self.record['pages'].values():
            altered = {**pair['new'], 'description': 'UNREVIEWED'}
            self.assertEqual(answer_record_history.pages([altered]), [altered])
            self.assertEqual(beginner_history.pages([altered])[0]['description'], 'UNREVIEWED')


if __name__ == '__main__':
    unittest.main()
