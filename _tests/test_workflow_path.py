"""Four stages, exact downloads, scoped changes and independent original history."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
import json,re,shutil,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,workflow_path,check_live,workflow_history

class WorkflowPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages();cls.outputs=build.build_outputs()
        cls.base=json.loads((ROOT/'_tests/workflow-path-baseline.json').read_text())
    def test_all_original_bodies_preserved_except_explicit_workflow_navigation(self):
        self.assertEqual(len(self.base['bodies']),170)
        for path,digest in self.base['bodies'].items():
            text=workflow_history.before(path,self.outputs[Path(path)])
            body=re.search(r'<body\b[^>]*>(.*?)</body>',text,re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(),digest,path)
    def test_original_sources_scripts_downloads_feeds_and_identity_preserved(self):
        for path,digest in self.base['files'].items():
            raw=workflow_history.before(path,(ROOT/path).read_bytes())
            self.assertEqual(sha256(raw).hexdigest(),digest,path)
        self.assertEqual(workflow_history.original_pages(json.loads((ROOT/'_source/pages.json').read_text())),self.base['manifest'])
    def test_four_ordered_stages_have_distinct_outputs_and_limits(self):
        self.assertEqual([s['label'] for s in workflow_path.STEPS],['Decide','Brief','Check','Measure'])
        html=self.outputs[Path('technology/index.html')]
        self.assertEqual(html.count('class="workflow-stage"'),4)
        positions=[html.index('href="'+s['route']+'"',html.index('id="ai-workflow-path"')) for s in workflow_path.STEPS]
        self.assertEqual(positions,sorted(positions))
        for s in workflow_path.STEPS:self.assertIn(s['output'],unescape(html))
        for phrase in ['fictional','do not run AI','Other outputs need their own independent tests','pause or a simpler method']:self.assertIn(phrase,html)
    def test_destinations_have_one_current_stage_and_native_sibling_routes(self):
        for n,s in enumerate(workflow_path.STEPS,1):
            html=self.outputs[build.output_path(s['route'])]
            self.assertEqual(html.count('aria-current="step"'),1)
            self.assertEqual(html.count('Practical AI workflow stages'),1)
            self.assertIn(str(n)+'. '+s['label']+'<span class="workflow-here">',html)
            for other in workflow_path.STEPS:
                if other!=s:self.assertIn('href="'+other['route']+'"',html)
            self.assertIn('These links do not save progress.',html)
    def test_workbook_keeps_every_original_once_and_matches_complete_preview(self):
        text=self.outputs[workflow_path.SHEET]
        self.assertEqual(text,(ROOT/workflow_path.SHEET).read_text())
        for s in workflow_path.STEPS:self.assertEqual(text.count((ROOT/s['sheet']).read_text()),1)
        preview=re.search(r'<details><summary>Preview the complete blank workbook</summary><pre>(.*?)</pre>',self.outputs[Path('technology/index.html')],re.S)[1]
        self.assertEqual(unescape(preview),text)
        for phrase in ['Keep completed copies private','not a course, validated assessment','other outputs','permission','not a personal result']:self.assertIn(phrase,text)
    def test_collection_metadata_matches_visible_stages_and_does_not_mutate(self):
        html=self.outputs[Path('technology/index.html')]
        data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)[1])
        self.assertEqual(data['@type'],'CollectionPage')
        items=data['mainEntity']['itemListElement'];self.assertEqual(len(items),4)
        for n,(item,s) in enumerate(zip(items,workflow_path.STEPS),1):
            self.assertEqual(item['position'],n);self.assertEqual(item['url'],'https://nolankido.com'+s['route']);self.assertEqual(item['name'],s['title'])
        self.assertIn('Practical AI Workflow, Tools &amp; Checklists | Nolan Kido',html)
        before={'@type':'WebPage'};copy=deepcopy(before);workflow_path.schema(before,{'id':'technology'},'https://nolankido.com');self.assertEqual(before,copy)
    def test_new_entrances_scoped_css_and_no_new_scripts_or_tracking(self):
        for path in ['start-here/index.html','resources/index.html']:self.assertIn('href="'+workflow_path.HUB+'"',self.outputs[Path(path)])
        for p in self.pages:
            html=self.outputs[build.output_path(p['path'])]
            self.assertEqual(workflow_path.BEGIN in html,p['id'] in workflow_path.IDS|{'technology','resources','start-here'},p['path'])
            self.assertEqual('/assets/workflow-path.css?v=' in html,p['id'] in workflow_path.IDS|{'technology','resources'},p['path'])
        for code in [workflow_path.hub(ROOT),workflow_path.stage_navigation(self.pages[0])]:
            for bad in ['<script','<form','data-umami','iframe','localStorage']:self.assertNotIn(bad,code)
    def test_invalid_destinations_and_empty_worksheets_fail_closed(self):
        for variant in ['missing','noindex','route']:
            pages=deepcopy(self.pages)
            if variant=='missing':pages=[p for p in pages if p['id']!='task-brief']
            elif variant=='route':next(p for p in pages if p['id']=='task-brief')['path']='https://bad.invalid/'
            else:next(p for p in pages if p['id']=='task-brief')['noindex']=True
            with self.assertRaises(ValueError):workflow_path.validate(pages,ROOT)
        with TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(ROOT/'downloads',root/'downloads');(root/workflow_path.STEPS[0]['sheet']).write_text('')
            with self.assertRaises(ValueError):workflow_path.validate(self.pages,root)
            with self.assertRaises(ValueError):workflow_path.workbook(root)
        with self.assertRaises(ValueError):workflow_path.decorate(workflow_path.BEGIN,{'id':'technology'},ROOT)
        with self.assertRaises(ValueError):workflow_path.decorate('missing',{'id':'technology'},ROOT)
    def test_negative_control_adapter_does_not_hide_article_text_changes(self):
        path='technology/task-brief/index.html'
        raw=self.outputs[Path(path)]
        original=re.search(r'<body\b[^>]*>(.*?)</body>',raw,re.S)[1]
        self.assertIn('Build a clearer AI task brief.',original)
        changed=raw.replace('Build a clearer AI task brief.','Invented credential and guaranteed result.')
        restored=workflow_history.before(path,changed)
        body=re.search(r'<body\b[^>]*>(.*?)</body>',restored,re.S)[1]
        self.assertNotEqual(sha256(body.encode()).hexdigest(),self.base['bodies'][path])
    def test_only_revised_hub_dates_change_and_live_inventory_is_complete(self):
        old={p['id']:p for p in self.base['manifest']}
        for p in json.loads((ROOT/'_source/pages.json').read_text()):
            if p['id'] in {'technology','start-here','resources'}:self.assertEqual(p['updated'],'2026-10-12')
            else:self.assertEqual(p,old[p['id']])
        targets=check_live.targets()
        for p in [workflow_path.SHEET,workflow_path.CSS]:self.assertEqual(targets['/'+str(p)],(200,(ROOT/p).read_bytes()))
        self.assertEqual(len(self.pages),170);self.assertEqual(sum(not p.get('noindex') for p in self.pages),165)

if __name__=='__main__':unittest.main(verbosity=2)
