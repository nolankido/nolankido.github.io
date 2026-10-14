"""Section discovery must find real destinations without indexing hidden answers."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import beginner_history
import build,search_sections,site_find
import search_sections_history as history
import time_examples_history
import poker_titles_history
from test_site import Page

class SearchSectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.baseline=json.loads((ROOT/'_tests/search-sections-baseline.json').read_text())
        cls.index=search_sections.index(cls.outputs,cls.pages)

    def test_only_search_and_frozen_native_anchor_spacing_change(self):
        historical_outputs = {p:time_examples_history.before(p,d) for p,d in beginner_history.outputs(self.outputs).items()}
        b=self.baseline
        self.assertEqual(poker_titles_history.pages(beginner_history.pages(self.pages)),b['pages'])
        self.assertEqual(set(map(str,historical_outputs)),set(b['outputs']))
        changed=[]
        for p,digest in b['outputs'].items():
            raw=historical_outputs[Path(p)]
            if sha256(raw.encode()).hexdigest()!=digest:changed.append(p)
            self.assertEqual(sha256(history.before(p,raw).encode()).hexdigest(),digest,p)
        self.assertCountEqual(changed,[p for p in b['outputs'] if p.endswith('.html')]+['assets/site-core.css'])
        paths=beginner_history.files({p.relative_to(ROOT).as_posix() for d in ['_source','assets','downloads'] for p in (ROOT/d).rglob('*') if p.is_file()})
        self.assertEqual(paths,set(b['files']));self.assertEqual(len(paths),343)
        changed=[]
        for p,digest in b['files'].items():
            raw=time_examples_history.before(p,(ROOT/p).read_bytes())
            if sha256(raw).hexdigest()!=digest:changed.append(p)
            self.assertEqual(sha256(history.before(p,raw)).hexdigest(),digest,p)
        self.assertCountEqual(changed,['_source/find.html','assets/site-find.js','assets/site-find.css','assets/site.css','assets/site-core.css'])

    def test_index_reuses_real_public_anchors_with_bounded_payload(self):
        self.assertEqual(len(self.index),155)
        self.assertEqual(sum(map(len,self.index.values())),958)
        excluded={p['path'] for p in self.pages if p.get('noindex') or p.get('living_well_kind')=='experiment'}
        self.assertFalse(excluded.intersection(self.index))
        self.assertNotIn('/contact/',self.index)
        for path,rows in self.index.items():
            document=Page(self.outputs[build.output_path(path)])
            all_ids=[a['id'] for _,a in document.elements if 'id' in a]
            for anchor,label in rows:
                self.assertEqual(all_ids.count(anchor),1,(path,anchor))
                self.assertTrue(label.strip())
        doc=self.outputs[search_sections.PAGE]
        payload=re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>',doc,re.S)[1]
        self.assertEqual(json.loads(payload),self.index)
        self.assertLess(len(payload.encode()),60000)
        # Preserve this release's original budget after the later reviewed
        # title metadata and beginner entry are reversed. Current growth has
        # its own independent bound in test_beginner_decisions.
        self.assertLess(len(time_examples_history.before(search_sections.PAGE,doc).encode()),145000)
        self.assertIn(['part-5','Keep access and recovery simple'],self.index['/living-well/find-the-document-you-need/'])

    def test_only_visible_major_headings_inside_main_are_indexed(self):
        doc='''<h2 id="outside">Outside</h2><main>
        <h2 id="intro">Visible <em>heading</em><span hidden>secret</span></h2>
        <h2 id="bad id">Invalid destination</h2><h3 id="minor">Not a major section</h3>
        <details open><summary>Exercise</summary><h2 id="answer">Hidden answer</h2></details>
        <nav><h2 id="navigation">Navigation</h2></nav><div hidden><h2 id="private">Hidden</h2></div>
        <div aria-hidden="true"><h2 id="decoration">Decoration</h2></div>
        <h2 id="next">Next<br>section</h2></main><h2 id="footer">Footer</h2>'''
        self.assertEqual(search_sections.headings(doc),[['intro','Visible heading'],['next','Next section']])
        for doc in ['<main><h2 id="same">One</h2><h2 id="same">Two</h2></main>','<main></main><main></main>','<h2>No main</h2>']:
            with self.assertRaises(ValueError):search_sections.headings(doc)

    def test_safe_data_cannot_break_out_of_the_json_element(self):
        p={'id':'example','path':'/notes/example/','note':True}
        text='</script><script>alert(1)</script>&'
        from html import escape
        outputs={search_sections.PAGE:'<main>Search</main>',Path('notes/example/index.html'):'<main><h2 id="safe">'+escape(text)+'</h2></main>'}
        rendered=search_sections.apply(outputs,[p])[search_sections.PAGE]
        self.assertNotIn(text,rendered)
        self.assertEqual(len(Page(rendered).tags('script')),1)
        payload=re.search(r'id="find-section-data">(.*?)</script>',rendered)[1]
        self.assertEqual(json.loads(payload)[p['path']],[['safe',text]])
        with self.assertRaises(ValueError):search_sections.apply(outputs,[p])

    def test_real_missed_queries_ranking_and_section_specificity(self):
        rows=[dict(r,subjects=' '.join(r['interests']),sections=self.index[r['path']]) for r in site_find.entries(ROOT,self.pages)]
        old=history.before('assets/site-find.js',(ROOT/'assets/site-find.js').read_text())
        code=r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const {rows,old}=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const current=require('./assets/site-find.js');const context={module:{exports:{}}};vm.runInNewContext(old,context);
const cases=[['recovery','/living-well/find-the-document-you-need/','part-5'],['bounded job','/notes/keep-the-judgment/','delegate-a-bounded-job'],['commitments','/technology/check-ai-answers/','review-writing'],['manageable shape','/creative/','creative-brief-title'],['practical needs','/poker/poker-rules-and-fair-play/','access-and-support']];
for(const [query,path,anchor] of cases){const r=rows.find(r=>r.path===path);assert.equal(context.module.exports.score(r,query),-1,path);assert(current.score(r,query)>=0,path);assert(current.matchingSections(r,query).some(s=>s[0]===anchor),path);}
const r={title:'Guide',description:'',subjects:'',sections:[['a','Alpha'],['b','Beta']]};
assert.equal(current.score(r,'alpha beta'),-1);assert.equal(current.matchingSections(r,'').length,0);
assert(current.score({...r,title:'Alpha'},'alpha')>current.score(r,'alpha'));
assert.equal(current.matchingSections({...r,sections:[1,2,3,4].map(i=>['s'+i,'Alpha '+i])},'alpha').length,3);
assert.equal(current.score(r,'???'),-1);assert.equal(current.score(r,'the and'),-1);
assert.equal(current.score({...r,sections:[['chair','A chair']]},'AI'),-1);
assert(current.score({...r,sections:[['cafe','Café recovery']]},'cafe recov')>=0);
'''
        run=subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps({'rows':rows,'old':old}),text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_adapter_cannot_hide_unreviewed_search_code_or_index_changes(self):
        for path,old,new in [('assets/site-find.js','const stops =','const surprise = 1; const stops ='),('assets/site-find.css','.find-intro {','.find-intro { color: red;'),('_source/find.html','Across my interests','Unexpected heading'),('find/index.html','Keep access and recovery simple','Unreviewed section label'),('assets/site.css','scroll-padding-top: 180px','scroll-padding-top: 181px'),('assets/site-core.css','scroll-padding-top: 180px','scroll-padding-top: 181px'),('about/index.html','<body','<!-- unreviewed --><body')]:
            data=(ROOT/path).read_text();modified=data.replace(old,new,1)
            self.assertNotEqual(data,modified,path)
            self.assertNotEqual(history.before(path,data),history.before(path,modified),path)
        self.assertEqual(history.before('about/index.html','unchanged'),'unchanged')

if __name__=='__main__':unittest.main()
