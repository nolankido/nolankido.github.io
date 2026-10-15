"""Independent numerical checks and exact predecessor preservation."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import importlib.util,json,re,sys,unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,search_sections
import uncertainty_history as history
import getting_started_history
from test_viewer_guides import best
ROUTE='/poker/poker-under-uncertainty/'
spec=importlib.util.spec_from_file_location('uncertainty',ROOT/'downloads/poker-under-uncertainty-reproduce.py')
calculator=importlib.util.module_from_spec(spec)
# Loading the downloadable source must not create an untracked published file.
exec(compile(Path(spec.origin).read_text(),spec.origin,'exec'),calculator.__dict__)

class UncertaintyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(cls.main.itertext())
        cls.evidence=json.loads((ROOT/'downloads/poker-under-uncertainty-evidence.json').read_text())

    def test_predecessor_and_mutation_guards(self):
        b=json.loads((ROOT/'_tests/uncertainty-baseline.json').read_text())
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('b8f812dda7b0e6ce472fe443246ae028e1483fbd',180,207,416))
        self.assertEqual(history.pages(self.pages),b['pages'])
        previous=history.outputs(self.outputs);self.assertEqual(set(map(str,previous)),set(b['outputs']))
        for p,v in previous.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in b['files'].items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        modified=deepcopy(self.pages);next(p for p in modified if p['path']==ROUTE)['description']='Unreviewed claim'
        self.assertNotEqual(history.pages(modified),b['pages'])
        changed=dict(self.outputs);changed[build.output_path(ROUTE)]=self.html.replace('131.5','999.5')
        self.assertIn(build.output_path(ROUTE),history.outputs(changed))
        p='poker/poker-math-reference/index.html';bad=self.outputs[Path(p)]+'unreviewed'
        self.assertEqual(history.before(p,bad),bad)

    def test_exact_range_against_independent_evaluator(self):
        known=set(calculator.HERO+calculator.BOARD);weighted=F(0);mass=F(0)
        for row in self.evidence['cards']['legal_combinations']:
            label=row['holding'];hands=[h for h in combinations(calculator.DECK,2) if not set(h)&known and sorted(c[0] for c in h)==sorted(label[:2]) and (len(label)==2 or h[0][1]==h[1][1])]
            self.assertEqual(len(hands),row['combos']);wins=F(0)
            for hand in hands:
                rivers=[c for c in calculator.DECK if c not in known and c not in hand];self.assertEqual(len(rivers),44)
                for river in rivers:
                    hero=best(list(calculator.HERO+calculator.BOARD+(river,)));opponent=best(list(hand+calculator.BOARD+(river,)))
                    wins+=F(1) if hero>opponent else F(1,2) if hero==opponent else F(0)
            self.assertEqual(wins/(len(hands)*44),F(row['river_equity']))
            weight=F(row['weight']);mass+=weight*len(hands);weighted+=weight*wins/44
        self.assertEqual(mass,F(45,2));self.assertEqual(weighted/mass,F(181,440))

    def test_river_boundary_and_stack_ledger(self):
        board=calculator.BOARD+('Kd',);known=set(calculator.HERO+board);masses=[F(0)]*3
        for label,weight in calculator.RANGE:
            for hand in calculator.legal_hands(label,known):
                hero=best(list(calculator.HERO+board));opp=best(list(hand+board));self.assertNotEqual(hero,opp)
                index=0 if hero<opp else 1 if best(list(hand+board))[0]==1 else 2
                masses[index]+=weight
        self.assertEqual(masses,[F(21,2),F(9,2),F(27,4)])
        x=F(303,610);equity=(F(27,40)+F(27,4)*x)/(F(189,20)+F(27,40)+F(27,4)*x)
        self.assertEqual(equity,F(26,87));self.assertEqual(equity*F(435,2)-65,0)
        pots=[2*11+.5,2*(11+7.5)+.5,2*(11+7.5+25)+.5,2*(11+7.5+25+65)+.5]
        self.assertEqual(pots,self.evidence['ledger']['pots'])
        self.assertEqual(150-11-7.5,131.5);self.assertEqual(150-108.5,41.5)
        self.assertIn('131.5 bb behind before the turn bet',self.text)
        self.assertNotIn('106.5 bb behind before the turn bet',self.text)

    def test_reproduction_manifest_and_inference(self):
        exact=calculator.exact_results();recorded={k:v for k,v in self.evidence.items() if k!='monte_carlo'}
        self.assertEqual(json.loads(json.dumps(exact)),recorded)
        self.assertEqual(sum(F(v) for v in exact['bayes']['posterior']),1)
        self.assertEqual(F(exact['icm']['break_even_q']),F(17,28))
        self.assertEqual(sum(F(v) for v in exact['icm']['before']),100)
        low,high=exact['frequency']['wilson_95'];self.assertAlmostEqual(low,.0889417,places=6);self.assertAlmostEqual(high,.5323053,places=6)
        mc=self.evidence['monte_carlo'];self.assertEqual((mc['seed'],mc['n'],mc['numpy']),(20261014,1000000,'2.3.5'))
        self.assertEqual(mc['estimate'],.349986);self.assertLess(mc['normal_95'][0],float(F(378,1081)));self.assertGreater(mc['normal_95'][1],float(F(378,1081)))

    def test_native_math_sources_delivery_and_privacy(self):
        math=[e for e in self.main.iter() if e.tag=='{http://www.w3.org/1998/Math/MathML}math']
        self.assertEqual(len(math),190)
        # The converter must not treat unbraced "42" as one binomial argument.
        fractions=[e for e in self.main.iter() if e.tag=='{http://www.w3.org/1998/Math/MathML}mfrac']
        arguments=[tuple(''.join(child.itertext()) for child in e) for e in fractions]
        self.assertIn(('4','2'),arguments)
        self.assertNotIn(('42','='),arguments)
        self.assertNotRegex(self.html,r'|\\\[|\\\(|```|Proposed figure|eP-eC\+C\?')
        self.assertEqual(len(list(self.main.iter('table'))),11)
        self.assertEqual(len([e for e in self.main.iter('img') if '/uncertainty-' in e.get('src','')]),3)
        self.assertIn('Koomen',self.text);self.assertIn('1806–1821',self.text)
        self.assertIn('13',self.text);self.assertIn('795–818',self.text)
        self.assertIn('not a peer-reviewed research paper',self.text)
        self.assertNotRegex(self.html,r'<script[^>]+(?:mathjax|katex)|<iframe|<form')
        idx=search_sections.index(getting_started_history.outputs(self.outputs),getting_started_history.pages(self.pages))
        before=json.loads((ROOT/'_tests/uncertainty-baseline.json').read_text())
        old=search_sections.index(history.outputs(self.outputs),before['pages'])
        # The existing library heading accurately changes its inventory to 56.
        old['/poker/library/']=[[a,label.replace('55 free guides','56 free guides')] for a,label in old['/poker/library/']]
        self.assertEqual({k:v for k,v in idx.items() if k!=ROUTE},old)
        packed=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[Path('find/index.html')],re.S)[1]
        self.assertLessEqual(len(packed.encode()),60000)
        self.assertEqual(len(check_live.targets()),432)
        for path in ['/assets/poker-uncertainty.css','/downloads/poker-under-uncertainty-reproduce.py','/downloads/poker-under-uncertainty-evidence.json','/assets/poker/uncertainty-bayes.png']:
            self.assertIn(path,check_live.targets())

if __name__=='__main__':unittest.main()
