"""Public discovery is a complete, bounded projection, not another content catalog."""
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import site_find
import check_live
from test_site import Page

class SiteFindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.items = site_find.entries(ROOT, cls.pages)
        cls.outputs = build.build_outputs()

    def test_exact_manifest_projection_once_with_canonical_copy(self):
        expected = {p['path']: p for p in self.pages if site_find.eligible(p)}
        self.assertEqual(len(self.items), len(expected))
        self.assertEqual({e['path'] for e in self.items}, set(expected))
        for entry in self.items:
            page = expected[entry['path']]
            self.assertEqual((entry['title'], entry['description']), (page['title'], page['description']))
        rendered = site_find.render(self.items)
        links = [a['href'] for a in Page(rendered).tags('a')]
        self.assertEqual(len(links), len(set(links)))
        self.assertEqual(set(links), set(expected))
        self.assertIn('/technology/', links)
        self.assertIn('/creative/', links)

    def test_excludes_nonpublic_plans_and_administrative_records(self):
        paths = {e['path'] for e in self.items}
        for p in self.pages:
            if p.get('noindex') or p.get('living_well_kind') == 'experiment':
                self.assertNotIn(p['path'], paths)
        for path in ['/contact/', '/bio/', '/find/', '/living-well/field-notes/', '/poker/find/', '/living-well/find/']:
            self.assertNotIn(path, paths)
        rendered = site_find.render(self.items)
        self.assertNotIn('submit-form.com', rendered)
        self.assertNotIn('turnstile', rendered)
        self.assertNotIn('Proposed experiment:', rendered)

    def test_cross_interest_membership_does_not_duplicate_the_family_story(self):
        record = [e for e in self.items if e['path'] == '/living-well/preserve-family-story/']
        self.assertEqual(len(record), 1)
        self.assertEqual(record[0]['interests'], ['living-well','creative'])
        self.assertEqual(record[0]['home'], 'living-well')
        self.assertEqual(record[0]['kind'], 'guide')
        note = next(e for e in self.items if e['path'] == '/notes/keep-the-judgment/')
        self.assertEqual(note['kind'], 'essay')
        self.assertEqual(note['date'], '2026-10-11')

    def test_search_controls_progressively_enhance_static_links(self):
        content = self.outputs[Path('find/index.html')]
        parsed = Page(content)
        section = next(s for s in parsed.tags('section') if s.get('id') == 'find-controls')
        self.assertIn('hidden', section)
        self.assertEqual(section['role'], 'search')
        self.assertNotIn('<form', content)
        query = next(i for i in parsed.tags('input') if i.get('id') == 'find-query')
        self.assertEqual(query['maxlength'], '180')
        self.assertNotIn('name', query)
        for interest in site_find.INTERESTS:
            self.assertTrue(any(o.get('value') == interest for o in parsed.tags('option')))
        self.assertEqual(len([d for d in parsed.tags('details') if d.get('class') == 'find-group']), 4)
        for page in ['index.html','start-here/index.html','notes/index.html','resources/index.html','404.html']:
            self.assertIn('href="/find/"',self.outputs[Path(page)])
        self.assertIn('class="utility-find" href="/find/" aria-current="page"',content)

    def test_assets_load_only_on_search_and_are_live_targets(self):
        for page in self.pages:
            content = self.outputs[build.output_path(page['path'])]
            for asset in ['site-find.js','site-find.css']:
                self.assertEqual('/assets/'+asset in content, page['id']=='find',page['path'])
        targets = check_live.targets()
        for asset in ['site-find.js','site-find.css']:
            self.assertEqual(targets['/assets/'+asset],(200,(ROOT/'assets'/asset).read_bytes()))
        self.assertIn('/find/',targets)

    def test_never_searches_or_persists_private_input_remotely(self):
        code=(ROOT/'assets/site-find.js').read_text()
        self.assertNotRegex(code,r'\b(fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage|WebSocket)\b')
        self.assertNotRegex(code,r'(document\.cookie|location\.[A-Za-z]|history\.[A-Za-z]|innerHTML|insertAdjacentHTML)')
        self.assertIn("'pagehide'",code)
        self.assertIn("'pageshow'",code)
        self.assertIn('maxlength="180"',(ROOT/'_source/find.html').read_text())

    def test_rendering_escapes_metadata_without_mutation(self):
        items=deepcopy(self.items);items[0]['title']='"><img src=x onerror=alert(1)>'
        items[0]['description']='<script>private()</script>';before=deepcopy(items)
        rendered=site_find.render(items)
        self.assertIn('&lt;img',rendered);self.assertIn('&lt;script&gt;',rendered)
        self.assertNotIn('<script>',rendered);self.assertNotIn('<img',rendered)
        self.assertEqual(items,before)

    def test_config_fails_closed_with_useful_errors(self):
        original=json.loads((ROOT/'_source/discovery.json').read_text())
        cases=[]
        changed=deepcopy(original);changed['note_interests'].pop('keep-the-judgment');cases.append(changed)
        changed=deepcopy(original);changed['also_in']['/not-here/']=['technology'];cases.append(changed)
        changed=deepcopy(original);changed['also_in']['/living-well/notebook-or-ai/']=['technology'];cases.append(changed)
        changed=deepcopy(original);changed['note_interests']['keep-the-judgment']=['unknown'];cases.append(changed)
        changed=deepcopy(original);changed['note_interests']['keep-the-judgment']=[];cases.append(changed)
        changed=deepcopy(original);changed['note_interests']['keep-the-judgment']=['technology','technology'];cases.append(changed)
        for config in cases:
            with TemporaryDirectory() as tmp:
                root=Path(tmp);(root/'_source').mkdir();(root/'_source/discovery.json').write_text(json.dumps(config))
                with self.assertRaises(ValueError):site_find.entries(root,self.pages)
        changed=deepcopy(self.pages);changed.append(changed[0])
        with self.assertRaises(ValueError):site_find.entries(ROOT,changed)

    def test_real_query_matching_and_short_ai_token(self):
        script=r'''
const assert = require('node:assert/strict');
const {score, terms, normalize} = require('./assets/site-find.js');
const records = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const rows=records.map(e=>({...e,subjects:e.interests.join(' ')}));
const result=q=>rows.filter(r=>score(r,q)>=0);
assert(result('family story').some(r=>r.path==='/living-well/preserve-family-story/'));
assert(result('how do I review a hand').some(r=>r.path==='/poker/reviewing-a-hand/'));
assert(result('AI').some(r=>r.path==='/notes/keep-the-judgment/'));
assert(result('pot odds').length>0);
assert(result('Omaha').length>0);
assert.equal(score({title:'Said plainly',description:'A chair',subjects:''},'ai'),-1);
assert(score({title:'Good decisions',description:'',subjects:''},'decision')>=0);
assert.equal(normalize('Café’s ideas'), 'cafes ideas');
assert.equal(result('notarealwordzz').length,0);
assert.equal(result('<script>alert(99)</script>').length,0);
assert.equal(result('???').length,0);
assert.equal(result('the and').length,0);
assert.equal(result('').length,records.length);
assert(score({title:'Family story',description:'',subjects:''},'family story')>
       score({title:'Useful guide',description:'A family story',subjects:''},'family story'));
'''
        run=subprocess.run(['node','-e',script],cwd=ROOT,input=json.dumps(self.items),capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)

if __name__=='__main__': unittest.main()
