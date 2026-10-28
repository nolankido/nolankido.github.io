"""Independently recompute the public time model and keep historical claims bounded."""
import choice_history
from fractions import Fraction
from pathlib import Path
from copy import deepcopy
import hashlib,json,random,re,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,check_search,site_find
KEYS=['manual','assisted','review','count','setup','upkeep']
BASE=dict(zip(KEYS,['30','8','7','6','60','15']))

def node(payload,script):
    program="const api=require("+json.dumps(str(ROOT/'assets/workflow-time.js'))+");const x=JSON.parse(require('fs').readFileSync(0,'utf8'));"+script
    return json.loads(subprocess.run(['node','-e',program],input=json.dumps(payload),text=True,capture_output=True,check=True).stdout)

class WorkflowEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages();cls.outputs=build.build_outputs()
    def test_exact_fraction_reference_for_250_models(self):
        rng=random.Random(2817)
        inputs=[BASE,{**BASE,'count':'1','upkeep':'0'},{**BASE,'manual':'20','assisted':'5','review':'18','count':'10','setup':'10','upkeep':'5'}, {**BASE,'manual':'0.3','assisted':'0.1','review':'0.1','setup':'0.2','upkeep':'0','count':'2'}]
        for _ in range(250):
            values={k:f'{rng.randrange(1 if k=="manual" else 0,1000000)/100:.2f}' for k in KEYS if k!='count'}
            values['count']=str(rng.randrange(1,1000));inputs.append(values)
        answers=node(inputs,"console.log(JSON.stringify(x.map(v=>api.calculate(v))));")
        for raw,out in zip(inputs,answers):
            v={k:Fraction(t) for k,t in raw.items()};g=v['manual']-v['assisted']-v['review'];h=v['setup']+v['upkeep'];n=int(v['count'])
            expected={'usual':n*v['manual']*100,'changed':(h+n*(v['assisted']+v['review']))*100,'net':(n*g-h)*100,'perRun':g*100,'overhead':h*100}
            for k,z in expected.items(): self.assertEqual(out[k],int(z),(raw,k))
            if g>0:
                ratio=h/g;ceil=-(-ratio.numerator//ratio.denominator);floor=ratio.numerator//ratio.denominator
                self.assertEqual(out['breakEven'],max(1,ceil));self.assertEqual(out['firstSaving'],floor+1)
            else:self.assertIsNone(out['breakEven']);self.assertIsNone(out['firstSaving'])
        self.assertEqual([x['net'] for x in answers[:4]],[1500,-4500,-4500,0])
    def test_bad_values_fail_without_silent_zero_or_rounding(self):
        bad=['',' ','1e3','NaN','Infinity','-1','1,000','.5','1.001','100000.01','0x12','<script>']
        cases=[{**BASE,'review':v} for v in bad]+[{**BASE,'count':v} for v in ['0','1.1','100001']]+[{**BASE,'manual':'0'}]
        result=node(cases,"console.log(JSON.stringify(x.map(v=>{try{api.calculate(v);return false;}catch(e){return true;}})));")
        self.assertTrue(all(result))
    def test_large_limits_and_equal_methods_remain_finite(self):
        cases=[{k:'100000' for k in KEYS},{**BASE,'manual':'15','assisted':'8','review':'7','setup':'0','upkeep':'0'},{**BASE,'setup':'0','upkeep':'0'}]
        ans=node(cases,"console.log(JSON.stringify(x.map(v=>api.calculate(v))));")
        self.assertEqual(ans[0]['net'],-1000020000000);self.assertEqual(ans[1]['net'],0);self.assertIsNone(ans[1]['firstSaving']);self.assertEqual(ans[2]['breakEven'],1)
    def test_no_network_storage_or_html_execution(self):
        js=(ROOT/'assets/workflow-time.js').read_text()
        for forbidden in ['fetch(', 'XMLHttpRequest','sendBeacon','localStorage','sessionStorage','innerHTML','eval(', 'location.search','console.log']:
            self.assertNotIn(forbidden,js)
        self.assertIn('pagehide',js);self.assertIn('pageshow',js)
    def test_assets_are_scoped_and_live_checked(self):
        for p in self.pages:
            html=self.outputs[build.output_path(p['path'])]
            self.assertEqual('/assets/workflow-time.js?' in html,p['id']=='ai-time-savings')
            self.assertEqual('/assets/workflow-evidence.css?' in html,p['id'] in {
                'ai-time-savings','ai-website-verification',
                'local-ai-review-replies','ai-book-continuity-checker','dinner-on-time',
                'ai-weekly-reset','organize-public-notes','local-ai-test-record',
            })
        targets=check_live.targets()
        for name in ['assets/workflow-time.js','assets/workflow-evidence.css','downloads/workflow-time-review.txt','downloads/website-check-reproduction.py','downloads/website-check-evidence.json']:
            self.assertEqual(targets['/'+name],(200,(ROOT/name).read_bytes()))
    def test_new_pages_have_metadata_and_discovery(self):
        items=site_find.entries(ROOT,self.pages)
        for ident in ['ai-time-savings','ai-website-verification']:
            p=next(p for p in self.pages if p['id']==ident)
            self.assertEqual(sum(e['path']==p['path'] for e in items),1)
            for parent in ['technology/index.html','resources/index.html','about/index.html']:
                self.assertIn('href="'+p['path']+'"',self.outputs[Path(parent)])
            self.assertIn(p['path'],self.outputs[Path('sitemap.xml')])
        case=check_search.Document(self.outputs[Path('technology/checking-ai-website-changes/index.html')]).schemas[0]
        self.assertEqual(case['@type'],'Article');self.assertEqual(case['datePublished'],'2026-10-11')
        app=check_search.Document(self.outputs[Path('technology/ai-time-savings/index.html')]).schemas[0]['mainEntity']
        self.assertEqual(app['@type'],'WebApplication');self.assertNotIn('aggregateRating',app)
    def test_worksheet_preview_exact_and_examples_honest(self):
        from html import unescape
        html=self.outputs[Path('technology/ai-time-savings/index.html')]
        self.assertIn((ROOT/'downloads/workflow-time-review.txt').read_text(),unescape(html))
        for text in ['fictional teaching examples','165 minutes','75 minutes','245 minutes','quality','not a controlled experiment']:
            self.assertIn(text,html)
        self.assertNotIn('<form',html)
    def test_historical_receipt_not_a_new_performance_claim(self):
        rec=json.loads((ROOT/'downloads/website-check-evidence.json').read_text())
        self.assertEqual(rec['pre_repair']['unit_content_tests_passed'],347)
        self.assertEqual(rec['pre_repair']['html5_error']['code'],'end-tag-too-early')
        self.assertEqual(rec['published']['matched_targets'],235)
        self.assertEqual(rec['published']['commit'],'6832b5e1edc85c50a3e6eb39a447cd67d9f0f80c')
        text=self.outputs[Path('technology/checking-ai-website-changes/index.html')]
        for limit in ['not a measured productivity study','color-contrast','reduced teaching example','No reliable time comparison']:
            self.assertIn(limit,text)
    def test_home_feeds_contact_and_original_articles_are_unchanged(self):
        baseline=json.loads((ROOT/'_tests/workflow-evidence-baseline.json').read_text())
        for p,h in baseline.items():self.assertEqual(hashlib.sha256(choice_history.read(p)).hexdigest(),h,p)
    def test_css_uses_existing_tokens(self):
        css=(ROOT/'assets/workflow-evidence.css').read_text()
        available=set(re.findall(r'(--[a-z-]+)\s*:',(ROOT/'styles.css').read_text()+(ROOT/'assets/site.css').read_text()))
        self.assertTrue(set(re.findall(r'var\((--[a-z-]+)',css)).issubset(available))
if __name__=='__main__':unittest.main()
