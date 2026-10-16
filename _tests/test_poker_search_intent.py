"""A real failed lookup, bounded query recovery and exact release preservation."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from test_site import ROOT, build
import poker_search_history as history

FOLDER = ROOT / '_reports/poker-search-intent'
spec = spec_from_file_location('poker_search_evaluation', FOLDER / 'evaluate.py')
evaluation = module_from_spec(spec); spec.loader.exec_module(evaluation)
spec = spec_from_file_location('poker_search_capture', FOLDER / 'capture_history.py')
capture = module_from_spec(spec); spec.loader.exec_module(capture)


class PokerSearchIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/poker-search-baseline.json').read_text())

    def test_declared_regressions_reproduce_and_known_failure_has_an_honest_section(self):
        baseline = evaluation.evaluate(baseline=True)
        current = evaluation.evaluate()
        self.assertEqual(baseline, json.loads((FOLDER / 'baseline.json').read_text()))
        self.assertEqual(current, json.loads((FOLDER / 'results.json').read_text()))
        self.assertEqual(baseline['target_hits_top_three'], 18)
        self.assertGreaterEqual(current['target_hits_top_three'], 29)
        for old, new in zip(baseline['results'], current['results']):
            if old['hit_top_three']: self.assertTrue(new['hit_top_three'], old['id'])
        self.assertEqual((baseline['results'][0]['matches'], baseline['results'][0]['hit_top_three']), (6, False))
        first = current['results'][0]['top_three'][0]
        self.assertEqual((first['url'], first['section']), ('/poker/hand-rankings/', '/poker/hand-rankings/#ties'))
        self.assertIn('Two pair compares the higher pair', first['excerpt'])
        self.assertEqual(current['query_sha256'], baseline['query_sha256'])
        self.assertEqual([r['id'] for r in current['results']], [r['id'] for r in baseline['results']])

    def test_extra_wording_precision_and_literal_hostile_queries(self):
        rows = evaluation.Cards((ROOT / 'poker/find/index.html').read_text()).rows
        code = r'''
const assert=require('node:assert/strict'),e=require('./assets/poker-finder.js');
const cards=JSON.parse(require('node:fs').readFileSync(0,'utf8')).map(e.prepare);
const ranked=q=>cards.map(c=>({c,s:e.score(c,e.plan(q))})).filter(x=>x.s>=0).sort((a,b)=>b.s-a.s||a.c.index-b.c.index).map(x=>x.c.url);
for(const q of ['Why did my 2pair lose?','TWO PAIRS LOST','why did my two-pair lose'])assert.equal(ranked(q)[0],'/poker/hand-rankings/',q);
for(const q of ['two pair football','pot ods football','constructor','__proto__','toString','???','the and','<img src=x onerror=alert(1)>'])assert.equal(ranked(q).length,0,q);
assert.equal(ranked('what does BB mean')[0],'/poker/glossary/#big-blind');
assert(!ranked('learn poker free').includes('/poker/glossary/#freezeout'));
assert.equal(ranked('kicer')[0],'/poker/glossary/#kicker');
assert.equal(ranked('ods').length,0); // Correct this spelling only in a pot-odds context.
assert.equal(ranked('')[0],cards[0].url); // Unfiltered browsing retains its original order.
const original=JSON.stringify(cards);ranked('two pair lose');assert.equal(JSON.stringify(cards),original);
'''
        result = subprocess.run(['node', '-e', code], input=json.dumps(rows), cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_frozen_baseline_is_reproducible_without_parent_git_objects(self):
        missing = subprocess.CalledProcessError(128, ['git', 'show'])
        with patch.object(evaluation.subprocess, 'check_output', side_effect=missing):
            self.assertEqual(evaluation.evaluate(baseline=True), json.loads((FOLDER / 'baseline.json').read_text()))
            with patch.object(evaluation.Path, 'read_bytes', return_value=b'Unreviewed bytes'):
                with self.assertRaisesRegex(ValueError, 'changed bytes'):
                    evaluation.snapshot_text(ROOT, 'assets/poker-finder.js')

    def test_all_prior_source_and_output_bytes_are_preserved_except_reviewed_delta(self):
        b = self.baseline
        self.assertEqual(b['commit'], evaluation.BASE)
        files = {p.relative_to(ROOT).as_posix(): p.read_bytes() for d in capture.PREFIXES
                 for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        outputs = {str(p): raw.encode() for p, raw in self.outputs.items()}
        self.assertEqual((len(files), len(outputs)), (b['source_count'], b['output_count']))
        self.assertEqual(capture.fingerprint({p: history.before(p, raw) for p, raw in files.items()}), b['source_fingerprint'])
        self.assertEqual(capture.fingerprint({p: history.before(p, raw) for p, raw in outputs.items()}), b['output_fingerprint'])
        self.assertEqual(set(history.change()['paths']), capture.ALLOWED)

    def test_history_never_accepts_an_unreviewed_mutation(self):
        for path, record in history.change()['paths'].items():
            current = (ROOT / path).read_bytes()
            self.assertEqual(sha256(history.before(path, current)).hexdigest(), record['old_sha256'])
            mutated = current + b'Unreviewed change'
            self.assertEqual(history.before(path, mutated), mutated)
        self.assertEqual(history.before('unrelated.bin', b'\xff\x00'), b'\xff\x00')

    def test_searchable_sources_and_closed_answer_exclusions_are_unchanged(self):
        page = (ROOT / 'poker/find/index.html').read_text()
        old = history.before('poker/find/index.html', page)
        self.assertEqual(evaluation.Cards(page).rows, evaluation.Cards(old).rows)
        start = '<body'
        self.assertEqual(page[page.index(start):], old[old.index(start):])


if __name__ == '__main__': unittest.main()
