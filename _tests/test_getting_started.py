"""Independent checks for the first-session examples and lossless site integration."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,re,subprocess,sys,unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,search_sections,site_find
import getting_started_history as history
from test_viewer_guides import best
ROUTE='/poker/getting-started/'

class GettingStartedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(cls.main.itertext())
        cls.baseline=json.loads((ROOT/'_tests/getting-started-baseline.json').read_text())

    def test_exact_predecessor_and_unreviewed_mutation_guards(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('5993b164a2f7972744cd733332041f1b07edd029',185,212,432))
        self.assertEqual(history.pages(self.pages),b['pages'])
        original=history.outputs(self.outputs);self.assertEqual(set(map(str,original)),set(b['outputs']))
        for p,v in original.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in b['files'].items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        for p,d in b['extras'].items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        records=deepcopy(self.pages);next(p for p in records if p['path']==ROUTE)['description']='Unreviewed promise'
        self.assertNotEqual(history.pages(records),b['pages'])
        changed=dict(self.outputs);changed[build.output_path(ROUTE)]=self.html.replace('63 BB','99 BB')
        self.assertIn(build.output_path(ROUTE),history.outputs(changed))
        for path in ['assets/site-find.js','_scripts/search_sections.py','poker/no-limit-holdem-guide/index.html','find/index.html','_reports/search-audit.json']:
            raw=(ROOT/path).read_bytes();bad=raw+b'Unreviewed'
            self.assertEqual(history.before(path,bad),bad)
            self.assertNotEqual(history.before(path,raw),history.before(path,bad))

    def test_hand_comparisons_use_the_best_five_and_first_different_kicker(self):
        cases=[('Ad 9d','Ah 7h','As Jd 8c 4h 2s',(1,14,11,9,8),(1,14,11,8,7)),
               ('8s 7s','6c 5c','Ks Kd Qc Qh Ac',(2,13,12,14),(2,13,12,14)),
               ('As Ks','Kc Qc','Kd 8c 3h 6s 2d',(1,13,14,8,6),(1,13,12,8,6)),
               ('Ks Jc','Ad 8h','Qd Qh 9s 5c 2d',(1,12,13,11,9),(1,12,14,9,8))]
        for h,o,b,a,c in cases:
            self.assertEqual(len(set((h+' '+o+' '+b).split())),9)
            self.assertEqual(best((h+' '+b).split()),a);self.assertEqual(best((o+' '+b).split()),c)
        self.assertIn('The next comparison is nine against eight',self.text)
        self.assertIn('You stop at the first difference',self.text)
        self.assertNotIn('beats Morgan’s seven',self.text)

    def test_counted_hand_side_pots_raise_increments_and_costs_conserve_money(self):
        pot=F(3)+F(1,2)+F(5,2)+1;self.assertEqual(pot,7)
        pot+=2*4;self.assertEqual(pot,15);pot+=2*10;self.assertEqual(pot,35)
        investment=3+4+10;self.assertEqual(investment,17);self.assertEqual(100-investment+pot,118)
        contributions=[40,100,150];main=3*min(contributions);side=2*(100-40);uncalled=150-100
        self.assertEqual((main,side,uncalled),(120,120,50));self.assertEqual(main+side+uncalled,sum(contributions))
        self.assertEqual(main+side,240)
        increment=55-20;self.assertEqual((increment,55+increment,90+increment),(35,90,125))
        self.assertLess(35-20,20)
        self.assertEqual((2*110,2*110+15+10,2*200),(220,245,400))
        self.assertEqual((2*55,2*55+12+8),(110,130));self.assertEqual(F(126,2),63)
        for value in ['$118','net gain of $18','$240, not $290','$245','63 BB','110','130']:
            self.assertIn(value,self.text)

    def test_call_prices_and_draw_probability_are_independently_correct(self):
        self.assertEqual(F(20,60+20+20),F(1,5));self.assertEqual(F(1,4)*100-20,5)
        self.assertEqual(F(12,48+12+12),F(1,6));self.assertEqual(F(1,5)*72-12,F(12,5))
        probability=1-F(38,47)*F(37,46)
        hit=sum(any(c<9 for c in pair) for pair in combinations(range(47),2))
        self.assertEqual(probability,F(hit,1081));self.assertAlmostEqual(float(probability),.3496762,places=6)
        self.assertAlmostEqual(float(F(9,47)),.1914894,places=6)
        self.assertAlmostEqual(float(F(9,46)),.1956522,places=6)
        self.assertIn('after a non-club turn',self.text)
        self.assertIn('an opponent’s known cards or information in their actions could change',self.text)
        self.assertIn('16.67%',self.text);self.assertIn('+$2.40',self.text)

    def test_all_old_heading_destinations_and_labels_survive_within_original_budget(self):
        current=search_sections.index(self.outputs,self.pages)
        previous=search_sections.index(history.outputs(self.outputs),self.baseline['pages'])
        previous['/poker/library/']=[[a,label.replace('56 free guides','57 free guides')] for a,label in previous['/poker/library/']]
        self.assertEqual({p:v for p,v in current.items() if p not in {ROUTE,'/poker/comics/best-five-cards-win/'}},previous)
        raw=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[search_sections.PAGE],re.S)[1]
        self.assertLess(len(raw.encode()),60000)
        code=r'''const assert=require('node:assert/strict'),s=require('./assets/site-find.js');
const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
assert(s.score(d.entry,'beginner poker')>=1000);
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(d.packed))),d.canonical);
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections({version:2,pages:{'/poker/':['safe','Old label']}}))),{'/poker/':[['safe','Old label']]});
for(const bad of [null,{}, {version:99,pages:{}},{version:3,pages:[]},{version:3,pages:{'https://evil':{'':['safe','x']}}},{version:3,pages:{poker:{'../':['safe','x']}}},{version:3,pages:{poker:{'x?y/':['safe','x']}}}])assert.equal(Object.keys(s.decodeSections(bad)).length,0);
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections({version:3,pages:{poker:{'':['bad id','x','safe','</script><img src=x>']}}}))),{'/poker/':[['safe','</script><img src=x>']]});
assert.equal(Object.keys(s.decodeSections({version:3,pages:{poker:{'':['odd']}}})).length,0);
assert.equal(Object.getPrototypeOf(s.decodeSections(d.packed)),null);
'''
        entry=next(e for e in site_find.entries(ROOT,self.pages) if e['path']==ROUTE)
        entry.update(subjects=' '.join(entry['interests']),searchTitle=entry['search_title'],sections=current[ROUTE])
        run=subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps({'packed':json.loads(raw),'canonical':current,'entry':entry}),text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_learning_routes_native_explanations_source_scope_and_private_sheet(self):
        arrivals=['/poker/','/poker/topics/learn/','/poker/topics/cash-games/','/poker/topics/tournaments/','/poker/topics/study/','/poker/library/','/poker/free-poker-learning-path/','/poker/start-here/','/poker/no-limit-holdem-guide/','/poker/first-live-cash-game/','/poker/first-live-tournament/','/poker/comics/','/notes/','/find/','/poker/find/']
        for route in arrivals:self.assertIn(ROUTE,self.outputs[build.output_path(route)],route)
        for p in ['writing.xml','poker/feed.xml','sitemap.xml']:self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path(p)])
        self.assertEqual(len(search_sections.headings(self.html)),16)
        questions=[e for e in self.main.iter('section') if e.get('class')=='session-check'];self.assertEqual(len(questions),5)
        for question in questions:
            details=next(question.iter('details'));self.assertNotIn('open',details.attrib)
            self.assertGreater(len(list(details.iter('a'))),0)
        self.assertEqual(len(list(self.main.iter('table'))),2)
        stages=next(e for e in self.main.iter('ol') if e.get('class')=='session-stages')
        self.assertEqual(len(list(stages)),4)
        for stage in stages:
            self.assertIn('Explain a fresh situation:', ''.join(stage.itertext()))
            self.assertEqual(len(list(stage.iter('a'))),1)
        sources=[e for e in self.main.iter('li') if e.get('id','').startswith('source-')];self.assertEqual(len(sources),13)
        self.assertIn('Saying only “raise” is not permission to add chips',self.text)
        self.assertIn('not validated standards of readiness or profitability',self.text)
        self.assertIn('They have not been validated as a teaching curriculum with actual beginners',self.text)
        self.assertNotIn('Correctly rank 20',self.text)
        self.assertNotRegex(self.html,r'|```|'+chr(8212)+r'|<form|<input|<textarea|<iframe')
        self.assertEqual(len(check_live.targets()),442)
        for p in [ROUTE,'/assets/poker-session.css','/downloads/poker-first-session.md']:
            self.assertIn(p,check_live.targets())
        worksheet=(ROOT/'downloads/poker-first-session.md').read_text()
        for value in ['zero is valid','No answers are submitted','Facts I cannot remember','not a validated readiness test']:
            self.assertIn(value,worksheet)

if __name__=='__main__':unittest.main()
