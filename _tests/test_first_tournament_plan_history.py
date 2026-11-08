"""The first-event plan preserves only its exact published predecessor."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import first_tournament_plan_history as history
from reviewed_release import read as reviewed_bytes


# This is the complete merged tournament-planning release, not a view of
# today's site after additional independently reviewed revisions.
FIRST_TOURNAMENT_RELEASE = 'dfdcdc64dd096f7bdcab0569f19d6cc466c5584b'
RELEASE_BLOBS = {
    '_source/pages.json': 'fe24d32ba4499e02bbbc96a700ae95b53bc00317',
    '_source/poker/first-live-tournament.html': '28a4aba01f1dd40b16007c5fe6039be1f579ab5d',
    '_source/poker/tournament-checklists.html': '1c9ae0308be1605d2af48092501aee002377defc',
    'downloads/poker-event-planner.md': 'b0a3b47f0671df6437b3d3ce6db5327f587d4480',
    'find/index.html': 'dac1446e9678fa919cfa8ba24f392dc6b8f9a7d8',
    'poker/find/index.html': 'e7e0dbb41b456a26de0c74a2e91240e03be3ed39',
    'poker/first-live-tournament/index.html': '4131614d0d600cf39151ee818f55fea26d025f3a',
    'poker/library/index.html': '2ecb757993805a6f9b5b96e1dbe0379f2d9a7995',
    'poker/poker-access-and-protection/index.html': 'ad5721d76e81ca2143eb04d08ce743f74f32daf7',
    'poker/poker-rules-and-fair-play/index.html': 'c3c21390f1895eaa7f52320f4d432d2c08658ae0',
    'poker/thunder-valley-poker-guide/index.html': '781264cfc099a85577800460c6f13ab7f4a61dbf',
    'poker/topics/places-to-play/index.html': 'f2946154fe25225f92b4f0b3623a6273a1affd73',
    'poker/topics/tournaments/index.html': '2f0aa0a64c7c628ae8ff101ad1220fb0575827b2',
    'poker/tournament-checklists/index.html': 'c26f0b7aa186be3f1a9ed1a046aae04058ba3659',
    'sitemap.xml': '83e8d53254828106b2dfc7068f89ed1ae39bf464',
}


class FirstTournamentPlanHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = deepcopy(history.change())
        cls.raw = {name: reviewed_bytes(FIRST_TOURNAMENT_RELEASE, name, RELEASE_BLOBS[name])
                   for name in history.PATHS}
        cls.pages = json.loads(cls.raw['_source/pages.json'])

    def test_actual_merged_release_has_the_ledger_parent_and_fifteen_exact_predecessors(self):
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', FIRST_TOURNAMENT_RELEASE + '^'],
            cwd=ROOT).decode().strip(), self.record['parent_commit'])
        self.assertEqual(subprocess.check_output(
            ['git', 'rev-parse', self.record['parent_commit'] + '^{tree}'],
            cwd=ROOT).decode().strip(), self.record['parent_tree'])
        self.assertEqual(set(RELEASE_BLOBS), history.PATHS)
        for name, item in self.record['paths'].items():
            with self.subTest(path=name):
                actual_parent = subprocess.check_output(
                    ['git', 'show', self.record['parent_commit'] + ':' + name], cwd=ROOT)
                self.assertEqual(history.digest(actual_parent), item['parent_sha256'])
                self.assertEqual(history.before(name, self.raw[name]), actual_parent)

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
