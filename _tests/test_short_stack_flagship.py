"""Short stacks: independent prize arithmetic and an integrated existing lesson."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json,re,runpy,subprocess,sys,unittest
from types import SimpleNamespace
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,search_sections,site_find
import short_stack_history as history
import poker_routes_history
ROUTE='/poker/short-stack-decisions/'
ARRIVALS=['/poker/','/poker/library/','/poker/topics/tournaments/','/poker/topics/strategy/','/poker/tournaments/','/poker/reading-preflop-charts/','/poker/position-and-stacks/','/poker/first-live-tournament/','/poker/tournament-equity/','/poker/limped-multiway-pots/','/poker/study/','/notes/']

def finish_orders(stacks):
    """Independent full permutation method; the public script uses recursion."""
    result=[[F(0) for _ in stacks] for _ in stacks]
    for order in permutations(range(len(stacks))):
        remaining=sum(stacks);chance=F(1)
        for i in order:
            chance*=F(stacks[i],remaining);remaining-=stacks[i]
        for rank,i in enumerate(order):result[i][rank]+=chance
    return result

class ShortStackFlagshipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(' '.join(cls.main.itertext()).split())
        cls.baseline=json.loads((ROOT/'_tests/short-stack-baseline.json').read_text())
        cls.example=SimpleNamespace(**runpy.run_path(str(ROOT/'downloads/short-stack-icm-example.py')))

    def test_complete_predecessor_and_mutation_guards(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('e8fa70161bfd574d1d7a9ff6a41b53baed7d12be',192,219,454))
        self.assertEqual(history.pages(self.pages),b['pages'])
        old=history.outputs(self.outputs);self.assertEqual(set(map(str,old)),set(b['outputs']))
        for p,v in old.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in {**b['files'],**b['extras']}.items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        changed=deepcopy(self.pages);next(p for p in changed if p['path']==ROUTE)['description']='Unreviewed range claim'
        self.assertNotEqual(history.pages(changed),b['pages'])
        for p in ['_scripts/build.py','_source/poker/short-stack-decisions.html','find/index.html','_reports/search-audit.json']:
            raw=(ROOT/p).read_bytes();bad=raw+b'Unreviewed'
            self.assertEqual(history.before(p,bad),bad)
            self.assertNotEqual(history.before(p,raw),history.before(p,bad))
        for p,d in b['files'].items():
            if p.startswith('assets/social/') or '/comics/' in p:self.assertEqual(sha256((ROOT/p).read_bytes()).hexdigest(),d,p)

    def test_forced_posts_and_coverage_are_accounted_for(self):
        self.assertEqual(8000-1000-1000,6000)
        self.assertEqual(F(1,2)+1+1,F(5,2))
        self.assertEqual(F(1,2)+1+6*F(1,10),F(21,10))
        self.assertEqual(F(1,2)+1+9*F(1,10),F(12,5))
        # A 16.5 BB opponent can cover a 17 BB hero whose dead BBA leaves
        # only 16 BB in live chips. Pre-hand stack order alone is insufficient.
        self.assertGreater(F(33,2),17-1)
        for value in ['6,000 chips remain behind','2.5 BB','2.1 BB','2.4 BB','after you pay a big-blind ante','The ante does not','before posting']:
            self.assertIn(value,self.text)

    def test_zero_equity_boundaries_are_not_hand_recommendations(self):
        for risk,reward,display in [(2,F(5,2),'44.44%'),(20,F(5,2),'88.89%'),(15,F(3,2),'90.91%'),(15,F(5,2),'85.71%')]:
            threshold=F(risk)/(risk+reward)
            self.assertEqual(threshold*reward-(1-threshold)*risk,0)
            self.assertEqual(f'{100*float(threshold):.2f}%',display)
            self.assertIn(display,self.text)
        for value in ['all opponents start with at least 21 BB','zero-equity model','joint fold probability','not a model of how either action actually plays','do not select a preferred action','conditional on earlier actions']:
            self.assertIn(value,self.text)

    def test_four_player_icm_by_independent_finish_orders(self):
        m=self.example;self.assertEqual(m.START,(40,30,20,10))
        self.assertEqual((m.FOLD,m.WIN,m.LOSE),((41,30,19,10),(20,30,40,10),(60,30,0,10)))
        values={}
        for label,stacks in [('fold',m.FOLD),('win',m.WIN)]:
            finish=finish_orders(stacks);equities=[]
            for player in range(4):
                self.assertEqual(tuple(finish[player]),m.finish_probabilities(stacks,player))
                equity=sum(p*prize for p,prize in zip(finish[player],m.PRIZES));equities.append(equity)
                self.assertEqual(equity,m.prize_value(stacks,player))
                self.assertEqual(m.prize_value(stacks,player,(100,0,0,0)),stacks[player])
            self.assertEqual(sum(equities),100);values[label]=equities[m.HERO]
        self.assertEqual(values['fold'],F(86570194,3772755))
        self.assertEqual(values['win'],F(2117,63))
        threshold=values['fold']/values['win']
        self.assertEqual(threshold,F(86570194,126776545))
        self.assertGreater(F(3,5),F(19,40));self.assertLess(F(3,5)*values['win'],values['fold'])
        result=json.loads(subprocess.check_output([sys.executable,str(ROOT/'downloads/short-stack-icm-example.py')],text=True))
        self.assertEqual(result,json.loads(json.dumps(m.example())))
        self.assertEqual(result['classic_icm_threshold_exact'],str(threshold))
        self.assertEqual((result['assumptions']['hero_additional_call_bb'],result['assumptions']['contested_pot_bb'],result['assumptions']['uncalled_SB_refund_bb']),(19,40,20))
        for value in ['$22.946148','$33.603175','47.5%','68.2857%','All branches conserve 100 BB','no ties','uncalled and returned']:
            self.assertIn(value,self.text)

    def test_sources_action_models_and_revision_are_unambiguous(self):
        ids={e.get('id'):e for e in self.main.iter() if e.get('id')}
        self.assertEqual(len([k for k in ids if k.startswith('source-')]),7)
        for a in self.main.iter('a'):
            if a.get('href','').startswith('#source-'):self.assertIn(a.get('href')[1:],ids)
        for value in ['push-or-fold calculation','does not restore omitted actions','provider-reported examples','not new solves','not a complete export','deal allocations also differ','not Nolan’s hand','no personal hand','Prepared with AI assistance.']:
            self.assertIn(value.lower(),self.text.lower())
        self.assertNotRegex(self.html,r'||—|turn\d+(?:view|search)\d+|33,478')
        schema=json.loads(re.search(r'type="application/ld\+json">(.*?)</script>',self.html)[1])
        self.assertEqual((schema['datePublished'],schema['dateModified']),('2026-10-06','2026-10-15'))
        self.assertIn(next(p for p in self.pages if p['path']==ROUTE)['revision'],self.text)
        self.assertIn('Originally published October 6, 2026',self.text)
        self.assertIn('Substantially expanded October 15, 2026',self.text)

    def test_native_checks_and_private_download_parity(self):
        questions=[e for e in self.main.iter('section') if e.get('class')=='short-stack-check']
        self.assertEqual(len(questions),3)
        for q in questions:
            d=next(q.iter('details'));self.assertNotIn('open',d.attrib);self.assertTrue(next(d.iter('summary')).text.startswith('Show the '))
        preview=next(e for e in self.main.iter('pre') if 'short-stack-sheet' in e.get('class',''))
        self.assertEqual(''.join(preview.itertext()),(ROOT/'downloads/poker-short-stack-record.md').read_text())
        self.assertFalse(list(self.main.iter('form'))+list(self.main.iter('input'))+list(self.main.iter('textarea'))+list(self.main.iter('iframe')))
        css=(ROOT/'assets/poker-short-stack.css').read_text()
        for value in ['pre-wrap','overflow-wrap: anywhere','@media print','content-visibility: visible','overflow-x: auto',':focus-visible']:self.assertIn(value,css)
        source=(ROOT/'downloads/short-stack-icm-example.py').read_text()
        for forbidden in ['input(', 'requests.', 'urllib.', 'open(', 'socket', 'subprocess']:self.assertNotIn(forbidden,source)

    def test_routes_search_old_anchors_and_live_inventory(self):
        for route in ARRIVALS:self.assertIn('href="'+ROUTE,self.outputs[build.output_path(route)],route)
        for name in ['poker/feed.xml','writing.xml','sitemap.xml']:self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path(name)])
        canonical=search_sections.index(self.outputs,self.pages)
        current=search_sections.index(poker_routes_history.outputs(self.outputs),poker_routes_history.pages(self.pages));old=search_sections.index(history.outputs(self.outputs),self.baseline['pages'])
        self.assertEqual({p:v for p,v in current.items() if p!=ROUTE},{p:v for p,v in old.items() if p!=ROUTE})
        self.assertTrue({v[0] for v in old[ROUTE]} <= {v[0] for v in current[ROUTE]})
        raw=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[search_sections.PAGE],re.S)[1];self.assertLess(len(raw.encode()),60000)
        entry=next(e for e in site_find.entries(ROOT,self.pages) if e['path']==ROUTE)
        code=r'''const assert=require('node:assert/strict'),s=require('./assets/site-find.js');const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));for(const q of ['15BB','short stack','10–20 BB'])assert(s.score(d.entry,q)>0);assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(d.packed))),d.canonical);'''
        subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps({'entry':dict(entry,subjects=' '.join(entry['interests'])),'packed':json.loads(raw),'canonical':canonical}),text=True,check=True)
        targets=check_live.targets();self.assertEqual(len(targets),468)
        for asset in ['assets/poker-short-stack.css','downloads/short-stack-icm-example.py','downloads/poker-short-stack-record.md']:self.assertEqual(targets['/'+asset],(200,(ROOT/asset).read_bytes()))
        for p,v in self.outputs.items():
            if p.suffix=='.html':self.assertEqual('/assets/poker-short-stack.css?' in v,p==build.output_path(ROUTE))

if __name__=='__main__':unittest.main()
