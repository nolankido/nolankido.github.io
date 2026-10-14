"""Public page titles repair real missed searches without a second content source."""
from copy import deepcopy
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import build, site_find
import search_public_titles_history as history
from test_site import Page


class SearchPublicTitlesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.items = site_find.entries(ROOT, cls.pages)
        cls.baseline = json.loads((ROOT / '_tests/search-public-titles-baseline.json').read_text())

    def test_only_search_metadata_and_runtime_change_against_production(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        b = self.baseline
        self.assertEqual(beginner_history.pages(self.pages), b['pages'])
        self.assertEqual((len(b['outputs']), len(b['files']), len(b['bodies'])), (198, 343, 171))
        self.assertEqual(set(map(str, historical_outputs)), set(b['outputs']))
        changed = []
        for path, expected in b['outputs'].items():
            raw = historical_outputs[Path(path)]
            if sha256(raw.encode()).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw).encode()).hexdigest(), expected, path)
        self.assertEqual(changed, ['find/index.html'])
        # Every other current page body is checked directly, without adapters.
        for path, expected in b['bodies'].items():
            if path == 'find/index.html':
                continue
            body = re.search(r'<body\b[^>]*>.*?</body>', historical_outputs[Path(path)], re.S)[0]
            self.assertEqual(sha256(body.encode()).hexdigest(), expected, path)
        files = beginner_history.files({p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file()})
        self.assertEqual(files, set(b['files']))
        changed = []
        for path, expected in b['files'].items():
            raw = beginner_history.before(path, (ROOT / path).read_bytes())
            if sha256(raw).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), expected, path)
        self.assertEqual(changed, ['assets/site-find.js'])

    def test_exact_public_titles_are_escaped_and_invalid_metadata_fails_closed(self):
        expected = {p['path']: p for p in self.pages if site_find.eligible(p)}
        cards = Page(site_find.render(self.items)).tags('li')
        self.assertEqual(len(cards), 154)
        for item, card in zip(self.items, cards):
            self.assertEqual(item['search_title'], expected[item['path']]['seo_title'])
            self.assertEqual(card['data-search-title'], item['search_title'])
        items = deepcopy(self.items)
        items[0]['search_title'] = '\"><img src=x onerror=alert(1)> & title'
        before = deepcopy(items)
        raw = site_find.render(items)
        self.assertIn('data-search-title="' + escape(items[0]['search_title'], quote=True) + '"', raw)
        self.assertNotIn('<img', raw)
        self.assertEqual(items, before)
        for value in [None, '', '  ', [], 17]:
            pages = deepcopy(self.pages)
            next(p for p in pages if site_find.eligible(p))['seo_title'] = value
            with self.assertRaisesRegex(ValueError, 'public search title'):
                site_find.entries(ROOT, pages)

    def test_real_missed_queries_ranking_sections_and_old_match_preservation(self):
        sections = json.loads(re.search(r'id="find-section-data">(.*?)</script>', self.outputs[Path('find/index.html')], re.S)[1])
        rows = [dict(r, searchTitle=r['search_title'], subjects=' '.join(r['interests']), sections=sections[r['path']]) for r in self.items]
        old = history.before('assets/site-find.js', (ROOT / 'assets/site-find.js').read_text())
        code = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const {rows,old}=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const current=require('./assets/site-find.js'),context={module:{exports:{}}};vm.runInNewContext(old,context);
const cases=[['pot odds calculator','/poker/study-calculators/'],['Texas Holdem rules','/poker/holdem-basics/'],['AI assisted reflection prompts','/living-well/reflection-with-your-judgment-intact/']];
for(const [query,path] of cases){const row=rows.find(r=>r.path===path);assert.equal(context.module.exports.score(row,query),-1,path);assert(current.score(row,query)>=750,path);}
for(const row of rows)for(const query of ['AI','family story','recovery','pot odds','weekly reset','AI time savings','poker hand rankings','task brief']){
 const prior=context.module.exports.score(row,query);if(prior>=500)assert.equal(current.score(row,query),prior);if(prior>=0)assert(current.score(row,query)>=0);
}
const base={title:'Guide',description:'',subjects:'',path:'/guide/',sections:[]};
const viaTitle={...base,searchTitle:'Pot Odds Calculator | Nolan Kido'};
assert(current.score({...base,title:'Pot odds calculator'},'pot odds calculator')>current.score(viaTitle,'pot odds calculator'));
assert(current.score(viaTitle,'pot odds calculator')>current.score({...base,path:'/pot-odds-calculator/'},'pot odds calculator'));
for(const searchTitle of [undefined,null,[],{private:'secret'},17])assert.equal(current.score({...base,searchTitle},'secret'),-1);
for(const query of ['the and','???','notarealwordzz','pot odds calculator football'])assert.equal(current.score(viaTitle,query),-1);
assert.equal(current.score({...base,searchTitle:'Chair'},'AI'),-1);
assert.equal(current.matchingSections({...viaTitle,sections:[['call','Compare a call']]},'pot odds calculator call')[0][0],'call');
assert.equal(current.score({...viaTitle,sections:[['alpha','Alpha'],['beta','Beta']]},'calculator alpha beta'),-1);
'''
        result = subprocess.run(['node', '-e', code], cwd=ROOT, input=json.dumps({'rows': rows, 'old': old}), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_frozen_adapter_keeps_unreviewed_metadata_copy_and_logic_visible(self):
        for path, old, new in [('find/index.html', 'data-search-title="', 'data-search-title="Unreviewed '),
                               ('find/index.html', 'Keep access and recovery simple', 'An invented achievement'),
                               ('find/index.html', 'href="/technology/"', 'href="https://other.example/"'),
                               ('assets/site-find.js', 'searchTitleMatch ? 750', 'searchTitleMatch ? 1750'),
                               ('assets/site-find.js', 'const stops =', 'const unknown = 1; const stops =')]:
            raw = self.outputs[Path(path)] if path.endswith('.html') else (ROOT / path).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertNotEqual(history.before(path, changed), history.before(path, raw))
        self.assertEqual(history.before('about/index.html', 'untouched'), 'untouched')
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
