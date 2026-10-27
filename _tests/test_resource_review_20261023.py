"""Bound the recorded manual review; tests do not establish remote availability."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_resources
import resource_review_history as history
import later_release_history as later_history
import resource_followup_history as followup
import first_tournament_plan_history as subsequent_changes


class ResourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = followup.before('_source/poker/resources.json', (ROOT / '_source/poker/resources.json').read_text())
        cls.current = json.loads(cls.raw)['entries']
        cls.previous = json.loads(history.before('_source/poker/resources.json', cls.raw))['entries']
        cls.entries = followup.resources(poker_resources.load(ROOT))
        cls.outputs = build.build_outputs()

    def test_only_twelve_reviewed_records_change_with_one_scope_correction(self):
        self.assertEqual(len(self.current), 146)
        self.assertEqual([r['id'] for r in self.current], [r['id'] for r in self.previous])
        changed = set()
        for old, new in zip(self.previous, self.current):
            if old == new:
                continue
            changed.add(new['id'])
            keys = {k for k in new if old[k] != new[k]}
            expected = {'reviewed_on', 'review_method', 'notes'} if new['id'] == 'tda-rule-downloads' else {'reviewed_on'}
            self.assertEqual(keys, expected)
            self.assertEqual(new['reviewed_on'], '2026-10-23')
            self.assertEqual(new['review_method'], 'page')
        self.assertEqual(changed, history.IDS)

    def test_blocked_destinations_keep_their_complete_prior_records(self):
        old = {r['id']: r for r in self.previous}
        new = {r['id']: r for r in self.current}
        for ident in ['nj-dge-information', 'wynn-poker']:
            self.assertEqual(new[ident], old[ident])
        self.assertEqual(new['nj-dge-information']['review_method'], 'index')

    def test_tda_scope_is_precise_without_recertifying_the_rules(self):
        entry = next(r for r in self.entries if r['id'] == 'tda-rule-downloads')
        self.assertIn('translation index inspected', entry['notes'])
        self.assertIn('individual translations were not reviewed', entry['notes'])
        self.assertNotIn('timed out', entry['notes'])
        old = next(r for r in self.previous if r['id'] == 'tda-rules')
        new = next(r for r in self.current if r['id'] == 'tda-rules')
        self.assertEqual(old, new)

    def test_dated_queue_keeps_both_unresolved_destinations(self):
        queue = poker_resources.review_queue(self.entries, date(2026, 10, 23))
        self.assertEqual({r['id'] for r in queue}, {'nj-dge-information', 'wynn-poker'})
        previous = poker_resources.review_queue(history.resources(self.entries), date(2026, 10, 23))
        self.assertEqual(len(previous), 14)
        later = poker_resources.review_queue(self.entries, date(2026, 11, 6))
        self.assertTrue((history.IDS - {'tda-rule-downloads'}) <= {r['id'] for r in later})

    def test_all_generated_copies_use_the_current_single_catalogue(self):
        payload = json.loads(followup.before('downloads/poker-resource-directory.json', self.outputs[Path('downloads/poker-resource-directory.json')]))
        self.assertEqual({r['id']: r for r in payload['entries']}, {r['id']: r for r in self.entries})
        entry = next(r for r in self.entries if r['id'] == 'tda-rule-downloads')
        for name in ['downloads/poker-resource-directory.md', 'poker/find/index.html', 'poker/resources/index.html']:
            self.assertIn('2026-10-23', self.outputs[Path(name)])
        card = poker_resources.card(entry)
        self.assertIn('Page read', card)
        self.assertNotIn('Search index only', card)

    def test_current_search_preserves_all_declared_results_without_rewriting_history(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location('review_current_search', ROOT / '_reports/poker-search-intent/evaluate.py')
        evaluation = module_from_spec(spec); spec.loader.exec_module(evaluation)
        current = evaluation.evaluate()
        previous = json.loads((ROOT / '_reports/poker-school/search-results.json').read_text())
        index_path = ROOT / 'poker/find/index.html'
        index_text = index_path.read_text()
        self.assertEqual(current['index_sha256'], sha256(index_path.read_bytes()).hexdigest())
        self.assertNotEqual(current['index_sha256'], previous['index_sha256'])

        # Keep the full recorded result comparison at its reviewed content
        # boundary. Only the exact approved later index bytes can be reversed;
        # the current evaluation above always reads the actual current index.
        predecessor = subsequent_changes.before('poker/find/index.html', index_text)
        self.assertNotEqual(predecessor, index_text)
        read_text = Path.read_text
        def predecessor_text(path, *args, **kwargs):
            return predecessor if path == index_path else read_text(path, *args, **kwargs)
        with patch.object(evaluation.Path, 'read_text', predecessor_text):
            archived = evaluation.evaluate()
        self.assertEqual(archived['index_sha256'], sha256(predecessor.encode()).hexdigest())
        self.assertEqual({k: v for k, v in archived.items() if k != 'index_sha256'},
                         {k: v for k, v in previous.items() if k != 'index_sha256'})

        # New public prose may change ranks, scores and excerpts. It must keep
        # the same declared questions, scorer and successful relevance targets.
        for key in ('scope', 'baseline_commit', 'query_sha256', 'script_sha256',
                    'entries', 'total_queries', 'target_hits_top_three'):
            self.assertEqual(current[key], previous[key], key)
        self.assertEqual([(r['id'], r['query']) for r in current['results']],
                         [(r['id'], r['query']) for r in previous['results']])
        cards = evaluation.Cards(index_text).rows
        for old, new in zip(previous['results'], current['results']):
            with self.subTest(query=new['id']):
                if old['hit_top_three']:
                    self.assertTrue(new['hit_top_three'])
                for found in new['top_three']:
                    candidates = [card for card in cards if card['url'] == found['url']]
                    self.assertTrue(candidates, found['url'])
                    if found['excerpt'] is None:
                        self.assertIsNone(found['section'])
                    else:
                        passages = [(card['url'] + '#' + p['anchor'] if p['anchor'] else None,
                                     p['text'][:320])
                                    for card in candidates for p in card['passages']]
                        self.assertIn((found['section'], found['excerpt']), passages)
        first_visit = next(r for r in current['results'] if r['id'] == 'Q26')
        self.assertEqual(first_visit['top_three'][0]['url'], '/poker/first-live-tournament/')

    def test_complete_production_inventory_reconstructs_verified_release(self):
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        paths = later_history.files([p for p in paths if p])
        rows = sorted((p, sha256(history.before(p, later_history.before(p, (ROOT / p).read_bytes()))).hexdigest())
                      for p in paths if not p.startswith(('_tests/', '_reports/')))
        self.assertEqual(len(rows), 714)
        self.assertEqual(sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(),
                         history.change()['production_fingerprint'])

    def test_byte_reversal_preserves_types_and_unknown_changes_remain_visible(self):
        for name, item in history.change()['paths'].items():
            raw = followup.before(name, (ROOT / name).read_bytes())
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
            old = history.before(name, raw)
            self.assertEqual(sha256(old).hexdigest(), item['old_sha256'])
            self.assertEqual(history.before(Path(name), raw.decode()).encode(), old)
            self.assertEqual(history.before(name, old), old)
            for mutated in [raw + b'!', b'!' + raw, raw[1:]]:
                self.assertEqual(history.before(name, mutated), mutated)

    def test_record_reversal_does_not_erase_unreviewed_changes(self):
        self.assertEqual(history.resources(self.current), self.previous)
        changed = deepcopy(self.current)
        item = next(r for r in changed if r['id'] == 'wsop-schedule')
        item['notes'] += ' Unreviewed edit'
        self.assertIn(item, history.resources(changed))
        original = deepcopy(changed)
        history.resources(changed)[0]['notes'] += ' Mutated copy'
        self.assertEqual(changed, original)

    def test_corrupt_predecessor_hash_and_offsets_fail_closed(self):
        name = '_source/poker/resources.json'
        raw = (ROOT / name).read_bytes()
        record = deepcopy(history.change()); record['paths'][name]['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=record), self.assertRaises(ValueError):
            history.before(name, raw)
        for edits in [[[True, 1, '']], [[-1, 0, '']], [[2, 1, '']], [[0, 3, ''], [2, 4, '']]]:
            record = deepcopy(history.change()); record['paths'][name]['edits'] = edits
            with self.subTest(edits=edits), patch.object(history, 'change', return_value=record), self.assertRaises(ValueError):
                history.before(name, raw)


if __name__ == '__main__':
    unittest.main()
