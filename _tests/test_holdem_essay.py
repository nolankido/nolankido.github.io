"""Independent card/accounting checks and lossless beginner-guide integration."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,re,subprocess,sys,unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,search_sections,check_live
import holdem_essay_history as history
from test_viewer_guides import best
ROUTE='/poker/no-limit-holdem-guide/'

class HoldemEssayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(cls.main.itertext())
        cls.baseline=json.loads((ROOT/'_tests/holdem-essay-baseline.json').read_text())

    def test_complete_predecessor_survives_only_exact_reviewed_edits(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs'])),('ef9c90473062719f2e751bb286fe360e89e2ad9f',179,206))
        self.assertEqual(history.pages(self.pages),b['pages'])
        previous=history.outputs(self.outputs)
        self.assertEqual(set(map(str,previous)),set(b['outputs']))
        for p,v in previous.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in b['files'].items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        records=deepcopy(self.pages);next(p for p in records if p['path']==ROUTE)['description']='A claim nobody reviewed'
        self.assertNotEqual(history.pages(records),b['pages'])
        changed=dict(self.outputs);changed[build.output_path(ROUTE)]=self.html.replace('+$87','+$887')
        self.assertIn(build.output_path(ROUTE),history.outputs(changed))
        path='poker/holdem-basics/index.html';raw=self.outputs[Path(path)];mutated=raw.replace('broader explanation','guaranteed profitable strategy')
        self.assertNotEqual(raw,mutated);self.assertEqual(history.before(path,mutated),mutated)

    def test_hand_rankings_and_all_supplied_showdowns_are_independent(self):
        cases=[
          ('As Qs','Kc Qc','Qd 7s 4s 2c 9h',1),
          ('Ac Kd','Ah Qh','As 8c 8d 4s 2c',1),
          ('9s 9h','Ac Kc','Ad 9d Kh Ks 2c',-1),
          ('7c 6d','2h 2d','As Kd Qc Jh Ts',0),
          ('Kc Kd','Qc Qd','Ah Jh 8h 5h 2h',0),
          ('Ah Kc','7d 7h','Ks Kd 7c 3h 2c',-1),
          ('As Qd','Kh Kc','Qs 9h 5d Kd 2c',-1)]
        for h,o,b,w in cases:
            cards=(h+' '+o+' '+b).split();self.assertEqual(len(set(cards)),9)
            left=best((h+' '+b).split());right=best((o+' '+b).split())
            self.assertEqual((left>right)-(left<right),w,(h,o,b))
        self.assertEqual(best('As Qd Qs 9h 5d Kd 2c'.split()),(1,12,14,13,9))
        self.assertEqual(best('Kh Kc Qs 9h 5d Kd 2c'.split()),(3,13,12,9))
        ranks=['9c 8c 7c 6c 5c','Ks Kh Kd Kc 3s','Qs Qh Qd 7c 7d','Ac Jc 8c 5c 2c','9s 8d 7c 6h 5s','7s 7h 7d Ac Kc','Js Jd 4c 4h As','9s 9h Ad Kc 7s','As Kd Jc 8h 5c']
        self.assertEqual([best(x.split())[0] for x in ranks],list(range(8,-1,-1)))

    def test_pots_prices_ties_outs_and_bluffs_reconcile(self):
        pots=[6+6+6+1];pots.append(pots[-1]+2*10);pots.append(pots[-1]+2*24);pots.append(pots[-1]+2*40)
        self.assertEqual(pots,[19,39,87,167]);self.assertEqual(167-sum([6,10,24,40]),87)
        self.assertEqual((3*40,2*(100-40),40+100+100),(120,120,240))
        self.assertEqual((25-10,25+15,32+15),(15,40,47))
        self.assertEqual(F(30,60+30+30),F(1,4));self.assertEqual(F(30,90+30+30),F(1,5))
        self.assertEqual(F(40,80+40+40),F(1,4));self.assertEqual(F(20,80+20+20),F(1,6))
        self.assertEqual(F(1,5)+F(1,5)*F(1,2),F(3,10))
        draws=1-F(38,47)*F(37,46)
        # Enumerate the possible unknown-card pairs separately from the formula.
        hit=sum(any(c<9 for c in pair) for pair in combinations(range(47),2))
        self.assertEqual(draws,F(hit,1081));self.assertAlmostEqual(float(draws)*100,34.97,places=2)
        self.assertAlmostEqual(float(F(9,46)*100-F(37,46)*20),3.48,places=2)
        self.assertEqual(F(50,100+50),F(1,3));self.assertEqual(F(1,3)*100-F(2,3)*50,0)
        for value in ['$167 - $80 = +$87','34.97%','19.57%','16.67%','+$3.48','$30 / $120 = 25%','$150','20%']:
            self.assertIn(value,self.text)

    def test_lossless_search_keeps_every_old_heading_under_original_budget(self):
        raw=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[search_sections.PAGE],re.S)[1]
        self.assertLess(len(raw.encode()),60000)
        canonical=search_sections.index(self.outputs,self.pages)
        code="const a=require('node:assert/strict'),s=require('./assets/site-find.js'),d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));a.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(d.packed))),d.canonical);for(const bad of [null,[],{}, {version:2,pages:[]},{version:3,pages:{}}]) a.deepEqual(s.decodeSections(bad),{});a.equal(Object.keys(s.decodeSections({version:2,pages:{'/poker/':['odd']}})).length,0);a.deepEqual(s.decodeSections({version:2,pages:{'/poker/':['bad id','x','safe','</script><img src=x>']}})['/poker/'],[['safe','</script><img src=x>']]);a.equal(Object.keys(s.decodeSections({version:2,pages:{'https://example.com/':['safe','x']}})).length,0);"
        run=subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps({'packed':json.loads(raw),'canonical':canonical}),text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        old=self.baseline['outputs'];restored=history.outputs(self.outputs)
        for p in old:self.assertEqual(sha256(restored[Path(p)].encode()).hexdigest(),old[p],p)

    def test_entry_points_sources_reading_and_privacy(self):
        for route in ['/poker/','/poker/topics/learn/','/poker/library/','/poker/start-here/','/poker/holdem-basics/','/poker/free-poker-learning-path/','/poker/find/','/find/','/notes/']:
            self.assertIn(ROUTE,self.outputs[build.output_path(route)],route)
        for p in ['poker/feed.xml','writing.xml','sitemap.xml']:self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path(p)])
        self.assertEqual(check_live.targets()[ROUTE],(200,self.html.encode()))
        self.assertEqual(len([e for e in self.main.iter('details') if e.get('id','').startswith('guide-check-')]),3)
        self.assertGreater(len(self.text.split()),7000)
        self.assertIn('Gemini Deep Research',self.text);self.assertIn('No reader study or learning outcome is claimed',self.text)
        self.assertIn('it does not establish how quickly a beginner learns',self.text)
        self.assertNotRegex(self.html,'|```|'+chr(8212))
        self.assertNotRegex(self.html,r'<(?:form|input|textarea|iframe)\b')
        ids={e.get('id') for e in self.doc.iter()}
        for a in self.main.iter('a'):
            link=a.get('href','')
            if link.startswith('#'):self.assertIn(link[1:],ids)
        sources=[e for e in self.main.iter('li') if e.get('id','').startswith('source-')]
        self.assertEqual(len(sources),11)
        for source in sources:self.assertEqual(len(list(source.iter('a'))),1)

if __name__=='__main__':unittest.main()
