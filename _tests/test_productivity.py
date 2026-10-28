"""Research status, fair accounting, source navigation and independent preservation."""
from copy import deepcopy
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re
import shutil
import sys
import tempfile
import unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import living_well as lw
import check_live
import productivity_history as history
import holdem_essay_history as essay_history
import uncertainty_history
import living_well_case_links_history as subsequent_changes
SLUG='ai-and-personal-productivity'
ROUTE='/living-well/'+SLUG+'/'
class ProductivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages();cls.entries=lw.load(ROOT)
        cls.previous_entries=subsequent_changes.entries(cls.entries)
        cls.entry=next(e for e in cls.entries if e['slug']==SLUG)
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.article=next(cls.doc.iter('article'));cls.text=' '.join(cls.article.itertext())
        cls.baseline=json.loads((ROOT/'_tests/productivity-baseline.json').read_text())
    def test_every_prior_input_record_and_output_survives_exact_reviewed_changes(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs'])),('4c8818e1a5bac173fe9445132098315cd1c64a45',178,205))
        self.assertEqual(history.pages(self.pages),b['pages']);self.assertEqual(history.entries(self.entries),b['entries'])
        old=history.outputs(self.outputs);self.assertEqual(set(map(str,old)),set(b['outputs']))
        for path,value in old.items():self.assertEqual(sha256(value.encode()).hexdigest(),b['outputs'][str(path)],str(path))
        mutable={'_source/living-well/discovery.json','_source/reader-previews.json','_scripts/living_well.py'}
        for path,digest in b['files'].items():
            raw=uncertainty_history.before(path,(ROOT/path).read_bytes())
            if path not in mutable | set(essay_history.change()['paths']):self.assertEqual(sha256(raw).hexdigest(),digest,path)
            self.assertEqual(sha256(history.before(path,raw)).hexdigest(),digest,path)
    def test_unreviewed_claims_and_records_are_not_hidden_by_history(self):
        records=deepcopy(self.pages);page=next(p for p in records if p['path']==ROUTE);page['description']='A claim nobody reviewed'
        self.assertNotEqual(history.pages(records),self.baseline['pages'])
        path=build.output_path(ROUTE);altered=dict(self.outputs);altered[path]=altered[path].replace('19 percentage points','90 percentage points')
        self.assertIn(path,history.outputs(altered))
        path=Path('living-well/did-the-tool-actually-help/index.html');raw=self.outputs[path]
        previous=subsequent_changes.before(path,raw)
        changed=previous.replace('Added a related research essay','Claimed a completed personal trial')
        self.assertNotEqual(changed,previous)
        self.assertEqual(history.before(path,changed),changed)
        revision=next(e['revision'] for e in self.entries if e['slug']=='did-the-tool-actually-help')
        changed=raw.replace(escape(revision),'Claimed a completed personal trial')
        self.assertNotEqual(changed,raw)
        self.assertEqual(history.before(path,changed),changed)
    def test_time_example_counts_all_steps_and_evidence_has_the_right_scope(self):
        baseline=sum([18,20,16]);assisted=12+sum([9,11,10])
        self.assertEqual((baseline,assisted,baseline-assisted),(54,42,12))
        for phrase in ['54 minutes','12 + 9 + 11 + 10 = 42','54 - 42 = 12','non-AI baseline does not have zero checking time','Fictional example, not measured savings','19 percentage points','453','758','319','1,222','2026 preprint','Self-reported','Gemini Deep Research']:
            self.assertIn(phrase,self.text)
        self.assertNotIn(chr(8212),self.html)
        self.assertGreater(len(self.text.split()),2500)
        self.assertNotRegex(self.html,r'<(?:form|input|textarea|iframe)\b')
    def test_incoming_reading_routes_and_source_links_match_the_public_article(self):
        self.assertEqual(self.entry['kind'],'essay');self.assertEqual(self.entry['published'],'2026-10-14')
        for route in ['/living-well/ideas/','/living-well/topics/everyday-ai/','/living-well/technology-for-real-life/','/living-well/did-the-tool-actually-help/','/notes/','/find/']:
            self.assertIn(ROUTE,self.outputs[build.output_path(route)],route)
        self.assertEqual(check_live.targets()[ROUTE],(200,self.html.encode()))
        ids={e.get('id') for e in self.doc.iter()};links=[e.get('href') for e in self.article.iter('a')]
        subs=self.entry['sections'][2]['subsections'];self.assertEqual(len(subs),8)
        for sub in subs:
            self.assertIn(sub['id'],ids);self.assertIn('#'+sub['id'],links)
        for s in self.entry['sources']:
            self.assertIn(s['url'],links);self.assertEqual(s['checked'],'2026-10-14')
        for e in self.previous_entries:
            if e['slug'] in ['technology-for-real-life','did-the-tool-actually-help']:
                self.assertEqual((e['published'],e['updated']),('2026-10-10','2026-10-14'))
        self.assertEqual(self.entry['updated'],'2026-10-28')
        self.assertTrue(self.entry['revision'])
        revision_notes=[''.join(p.itertext()) for p in self.doc.iter('p')
                        if 'editorial-note' in p.get('class','').split()]
        self.assertTrue(any(self.entry['revision'] in note for note in revision_notes))
        reviewed=next(e for e in self.entries if e['slug']=='did-the-tool-actually-help')
        self.assertEqual(reviewed['updated'],'2026-10-28')
        self.assertIn('/technology/check-ai-answers/',links)
    def test_subsection_navigation_fails_closed_and_titles_are_plain_text(self):
        variants=[]
        for field,value in [('id','part-1'),('id','use-x" onclick="oops'),('heading',None),('paragraphs','a string')]:
            e=deepcopy(self.entry);e['sections'][2]['subsections'][0][field]=value;variants.append(e)
        e=deepcopy(self.entry);e['sections'][2]['subsections'].append(deepcopy(e['sections'][2]['subsections'][0]));variants.append(e)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);shutil.copytree(ROOT/'_source/living-well',root/'_source/living-well')
            for e in variants:
                (root/'_source/living-well/productivity.json').write_text(json.dumps({'entries':[e]}))
                with self.assertRaises(ValueError):lw.load(root)
        e=deepcopy(self.entry);e['sections'][2]['subsections'][0]['heading']='<b>Plain title</b>'
        rendered=lw.article(e,[e]+[p for p in self.entries if p['slug']!=SLUG])
        self.assertIn('&lt;b&gt;Plain title&lt;/b&gt;',rendered);self.assertNotIn('<b>Plain title</b>',rendered)
        stripped=deepcopy(e);stripped['sections'][2]['subsections']=[]
        self.assertGreater(lw.minutes(e),lw.minutes(stripped))
if __name__=='__main__':unittest.main()
