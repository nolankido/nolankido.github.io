"""A few source-approved acronyms improve Find without open-ended guesses.

Run locally with python -m unittest discover -s _tests -p test_turn131_find_acronyms.py -v.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import unittest

from test_site import ROOT, Page, build
import player_find
import site_find


EXPECTED = {
    '/poker/tournament-trip-budget/': ['WSOPC'],
    '/poker/thunder-valley-poker-guide/': ['WSOPC'],
    '/technology/ai-website-visibility/': ['SEO', 'GEO'],
}


class FindAcronymTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.entries = site_find.entries(ROOT, cls.pages)
        cls.output = build.build_outputs()[Path('find/index.html')]

    def test_aliases_are_only_on_three_existing_public_pages(self):
        aliases = {entry['path']: entry['aliases'] for entry in self.entries if entry['aliases']}
        self.assertEqual(aliases, EXPECTED)
        for entry in self.entries:
            self.assertEqual(entry['title'], next(p['title'] for p in self.pages if p['path'] == entry['path']))
        self.assertEqual(len(self.entries), len({entry['path'] for entry in self.entries}))

    def test_visible_labels_explain_why_result_matched(self):
        cards = [li for li in Page(self.output).tags('li') if 'data-find-aliases' in li]
        self.assertEqual(len(cards), 3)
        self.assertEqual(sorted(c['data-find-aliases'] for c in cards), ['SEO GEO', 'WSOPC', 'WSOPC'])
        for acronyms in ('Related search terms: SEO · GEO', 'Related search terms: WSOPC'):
            self.assertIn(acronyms, self.output)
        self.assertEqual(self.output, (ROOT / 'find/index.html').read_text(encoding='utf-8'))
        self.assertIn('a few explicitly labeled topic acronyms', self.output)
        self.assertIn('Filtering happens on this page.', self.output)

    def test_actual_query_scoring_works_and_has_no_topic_invention(self):
        records = player_find.add(ROOT, self.entries)
        script = r'''
const assert=require('node:assert/strict');
const {score,matchingSections}=require('./assets/site-find.js');
const data=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const rows=data.map(row=>({...row,searchTitle:row.search_title,aliases:(row.aliases||[]).join(' '),subjects:row.interests.join(' ')}));
const paths=q=>rows.filter(row=>score(row,q)>=0).map(row=>row.path).sort();
assert.deepEqual(paths('WSOPC'),['/poker/thunder-valley-poker-guide/','/poker/tournament-trip-budget/']);
assert.deepEqual(paths('SEO'),['/technology/ai-website-visibility/']);
assert.deepEqual(paths('GEO'),['/technology/ai-website-visibility/']);
assert.deepEqual(paths('WSOPC hotel'),['/poker/tournament-trip-budget/']);
assert(paths('wine').includes('/living-well/wine-tasting-notes/'));
for(const query of ['chess','SEO poker','WSOPC oncology','<script>alert(1)</script>']) assert.deepEqual(paths(query),[],query);
assert(paths('NolanPoker').includes('/poker/nolan-kido/'));
const example={title:'A trip',description:'Other planning',subjects:'Poker',aliases:'WSOPC',sections:[['hotel','Hotel and travel costs']]};
assert.deepEqual(matchingSections(example,'WSOPC hotel'),[['hotel','Hotel and travel costs']]);
assert.equal(score({...example,aliases:''},'WSOPC'),-1);
'''
        result = subprocess.run(['node', '-e', script], cwd=ROOT, input=json.dumps(records),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bad_or_nonpublic_aliases_fail_closed(self):
        target = next(i for i, p in enumerate(self.pages) if p['path'] == '/poker/tournament-trip-budget/')
        for invalid in ([], 'WSOPC', None, ['WSOPC', 'WSOPC'], ['wsopc'], ['WSOP C'],
                        ['WSOPC!'], ['TOOLONGACRONYM'], [12], ['A', 'B', 'C', 'D', 'E']):
            changed = deepcopy(self.pages)
            changed[target]['find_aliases'] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                site_find.entries(ROOT, changed)
        changed = deepcopy(self.pages)
        next(p for p in changed if p['id'] == 'home')['find_aliases'] = ['SEO']
        with self.assertRaises(ValueError):
            site_find.entries(ROOT, changed)

    def test_search_stays_browser_local(self):
        js = (ROOT / 'assets/site-find.js').read_text(encoding='utf-8')
        self.assertNotRegex(js, r'\b(fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage|WebSocket)\b')
        self.assertNotRegex(js, r'(document\.cookie|location\.[A-Za-z]|history\.[A-Za-z]|innerHTML|insertAdjacentHTML)')
        self.assertNotIn('name="query"', self.output)
        self.assertEqual(len(re.findall(r'data-find-aliases=', self.output)), 3)


if __name__ == '__main__':
    unittest.main()
