"""Public title discovery, unchanged answers and a separate release snapshot."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import re
import subprocess
import unittest
from test_site import ROOT, build
import poker_search_titles_history as history
import poker_study_list_history as study_history
import poker_progress_history as progress_history
import poker_school_history as school


def load(name, path):
    spec = spec_from_file_location(name, ROOT / path)
    module = module_from_spec(spec); spec.loader.exec_module(module)
    return module


evaluation = load('title_evaluation', '_reports/poker-search-intent/evaluate.py')
capture = load('title_capture', '_reports/poker-search-titles/capture_history.py')


class PokerSearchTitlesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()

    def test_same_declared_targets_improve_without_losing_any_prior_pass(self):
        old = evaluation.evaluate(prior_release=True)
        current = evaluation.evaluate(titles_release=True)
        self.assertEqual(current, json.loads((ROOT / '_reports/poker-search-titles/results.json').read_text()))
        self.assertEqual((old['target_hits_top_three'], current['target_hits_top_three']), (29, 30))
        self.assertEqual(old['query_sha256'], current['query_sha256'])
        self.assertEqual([x['id'] for x in old['results']], [x['id'] for x in current['results']])
        for a, b in zip(old['results'], current['results']):
            if a['hit_top_three']: self.assertTrue(b['hit_top_three'], a['id'])
        icm = next(x for x in current['results'] if x['id'] == 'Q20')
        self.assertEqual(icm['top_three'][0]['url'], '/poker/tournament-equity/')

    def test_titles_come_from_public_manifest_and_existing_card_content_is_identical(self):
        page = study_history.before('poker/find/index.html', (ROOT / 'poker/find/index.html').read_text())
        old = history.before('poker/find/index.html', page)
        rows = evaluation.Cards(page).rows
        pages = {p['path']: p for p in build.public_pages()}
        titled = [r for r in rows if 'searchTitle' in r]
        self.assertEqual(len(titled), 90)
        for row in titled:
            p = pages[row['url']]
            self.assertEqual(row['searchTitle'], p.get('seo_title', p['title']))
            self.assertEqual(row['title'], p['title'])
            self.assertEqual(row['kind'], 'guide')
        self.assertEqual([{k: v for k, v in r.items() if k != 'searchTitle'} for r in rows], evaluation.Cards(old).rows)
        body = lambda text: text[text.index('<body'):]
        self.assertEqual(re.sub(r'data-search-title="[^"]*" ', '', body(page)), body(old))

    def test_related_wording_unrelated_words_and_route_independence(self):
        rows = evaluation.Cards((ROOT / 'poker/find/index.html').read_text()).rows
        code = r'''
const assert=require('node:assert/strict'),e=require('./assets/poker-finder.js');
const rows=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const rank=(q,source=rows)=>source.map(e.prepare).map(c=>({c,s:e.score(c,e.plan(q))})).filter(x=>x.s>=0).sort((a,b)=>b.s-a.s||a.c.index-b.c.index).map(x=>x.c);
for(const q of ['ICM','what is ICM','tournament equity','prize equity'])assert.equal(rank(q)[0].url,'/poker/tournament-equity/',q);
assert(rank('independent chip model').slice(0,3).some(c=>c.url==='/poker/tournament-equity/'));
for(const q of ['ICM football','tournament equity football','prize equity football'])assert.equal(rank(q).length,0,q);
assert.equal(rank('what does BB mean')[0].url,'/poker/glossary/#big-blind');
assert.equal(rank('why did my two pair lose')[0].url,'/poker/hand-rankings/');
const changed=rows.map((r,i)=>({...r,url:'/arbitrary/'+i+'/',id:'renamed-'+i}));
assert.deepEqual(rank('ICM',changed).map(c=>c.title),rank('ICM').map(c=>c.title));
const untitled=rows.map(({searchTitle,...r})=>r);
assert.notEqual(rank('ICM',untitled)[0].url,'/poker/tournament-equity/');
assert.equal(rank('',changed)[0].index,0);
'''
        result = subprocess.run(['node', '-e', code], input=json.dumps(rows), cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_exact_release_preservation_and_mutation_rejection(self):
        b = json.loads((ROOT / '_tests/poker-search-titles-baseline.json').read_text())
        self.assertEqual(b['commit'], '9bb91ac660de26eb91aa43b1aae2b3486a1691d6')
        sources = {p.relative_to(ROOT).as_posix(): p.read_bytes() for d in capture.PREFIXES
                   for p in (ROOT / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        sources = progress_history.source_records(sources)
        outputs = {str(p): s.encode() for p, s in school.outputs(self.outputs).items()}
        self.assertEqual((len(sources), len(outputs)), (b['source_count'], b['output_count']))
        self.assertEqual(capture.fingerprint({p: history.before(p, s) for p, s in sources.items()}), b['source_fingerprint'])
        self.assertEqual(capture.fingerprint({p: history.before(p, s) for p, s in outputs.items()}), b['output_fingerprint'])
        self.assertEqual(set(history.change()['paths']), capture.ALLOWED)
        for path, item in history.change()['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), item['old_sha256'])
            self.assertEqual(history.before(path, raw + b'Unreviewed'), raw + b'Unreviewed')
        self.assertEqual(history.before('unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__': unittest.main()
