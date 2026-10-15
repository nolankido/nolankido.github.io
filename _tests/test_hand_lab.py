"""Independent card oracles, constructive practice and exact release preservation."""
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import re
import shutil
import subprocess
import unittest
import html5lib
from test_site import ROOT, build
from test_viewer_guides import best, five
import check_live
import poker_finder
import poker_hand_lab as lab
import hand_lab_history as history


def node(code, data=None):
    result = subprocess.run(['node','-e',code], cwd=ROOT, input=json.dumps(data), text=True, capture_output=True, timeout=120)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class HandLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = lab.load(ROOT)
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/hand-lab-baseline.json').read_text())

    def test_current_release_is_preserved_through_only_the_reviewed_delta(self):
        b = self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])), ('dd80b250369b61da19220f23c58324c2936dfd8f',193,221,468))
        self.assertEqual(history.pages(self.pages), b['pages'])
        self.assertEqual(len(self.pages),193)
        previous = history.outputs(self.outputs)
        self.assertEqual(set(map(str, previous)),set(b['outputs']))
        for path,text in previous.items():
            self.assertEqual(sha256(text.encode()).hexdigest(),b['outputs'][str(path)],str(path))
        for path,digest in {**b['files'],**b['extras']}.items():
            self.assertEqual(sha256(history.before(path,(ROOT/path).read_bytes())).hexdigest(),digest,path)
        for path,digest in b['files'].items():
            if path.startswith('_source/poker/') and path.endswith('.html') and path not in {'_source/poker/free-poker-learning-path.html','_source/poker/beginner-learning-path.html','_source/poker/beginner-practice.html'}:
                self.assertEqual(sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        self.assertEqual(set(history.change()['new_files']),{lab.DATA,lab.CSS,lab.SCRIPT,'_scripts/poker_hand_lab.py'})
        self.assertEqual(history.change()['new_outputs'],{})
        actual={p.relative_to(ROOT).as_posix() for d in ['_source','_scripts','assets','downloads'] for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(history.files(actual),set(b['files']))
        for path in ['poker/feed.xml','writing.xml']:
            identity=lambda text:[(x.findtext('guid'),x.findtext('pubDate'),x.findtext('title')) for x in ET.fromstring(text).findall('./channel/item')]
            self.assertEqual(identity(previous[Path(path)]),identity(self.outputs[Path(path)]))

    def test_mutations_outside_the_frozen_review_are_not_hidden(self):
        for path in ['_scripts/build.py','_scripts/poker_course.py','_source/pages.json','poker/free-poker-learning-path/index.html','find/index.html']:
            changed=(ROOT/path).read_bytes()+b'Unreviewed change'
            self.assertEqual(history.before(path,changed),changed)
        records=deepcopy(self.pages);next(p for p in records if p['path']==lab.ROUTE)['description']+='Unreviewed'
        self.assertNotEqual(history.pages(records),self.baseline['pages'])
        outputs=dict(self.outputs);outputs[build.output_path(lab.ROUTE)]+='Unreviewed'
        self.assertNotEqual(history.outputs(outputs),history.outputs(self.outputs))

    def test_each_reviewed_solution_and_category_uses_an_independent_evaluator(self):
        categories=set();private_counts=set();equivalent=False
        for record in [self.data['example'],*self.data['cases']]:
            available=record['hero']+record['board'];score=best(available)
            self.assertEqual(five(record['solution']),score)
            solutions=[cards for cards in combinations(available,5) if five(cards)==score]
            private_counts.update(len(set(cards)&set(record['hero'])) for cards in solutions)
            equivalent |= len(solutions)>1
            if 'category' in record:
                self.assertEqual(record['category'],score[0]);categories.add(score[0])
        self.assertEqual(categories,set(range(9)))
        self.assertEqual(private_counts,{0,1,2})
        self.assertTrue(equivalent)
        wheel=next(c for c in self.data['cases'] if c['id']=='ace-low')
        self.assertEqual(best(wheel['hero']+wheel['board']),(4,5))
        # The visual chart is reused from the published reference, not copied.
        original=(ROOT/'_source/poker/hand-rankings.html').read_text()
        chart=re.search(r'<ol class="viewer-rankings">.*?</ol>',original,re.S)[0]
        self.assertIn(chart,lab.render(ROOT))
        self.assertEqual([five(x.split())[0] for x in re.findall(r'data-rank-cards="([^"]+)"',chart)],[8,8,7,6,5,4,3,2,1,0])

    def test_javascript_values_match_independent_five_and_seven_card_oracles(self):
        deck=[r+s for r in '23456789TJQKA' for s in 'shdc'];rng=Random(20261015)
        fives=[list(cs) for item in self.data['cases'] for cs in combinations(item['hero']+item['board'],5)]
        fives += [rng.sample(deck,5) for _ in range(1500)]
        sevens=[c['hero']+c['board'] for c in self.data['cases']] + [rng.sample(deck,7) for _ in range(1000)]
        result=node("const h=require('./assets/poker-hand-lab.js'),d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify({fives:d.fives.map(h.scoreFive),sevens:d.sevens.map(c=>h.bestFive(c).score)}));",{'fives':fives,'sevens':sevens})
        self.assertEqual(result['fives'],[list(five(c)) for c in fives])
        self.assertEqual(result['sevens'],[list(best(c)) for c in sevens])
        pair=next(c for c in self.data['cases'] if c['id']=='two-pair')
        selections=node("const h=require('./assets/poker-hand-lab.js'),c=JSON.parse(require('node:fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(h.bestFive(c).selections));",pair['hero']+pair['board'])
        self.assertEqual(len(selections),2)
        self.assertEqual({frozenset(c) for c in selections},{frozenset(['Ac','Ad','Kc','Kd','Ts']),frozenset(['Ac','Ad','Kc','Kd','Th'])})

    def test_all_possible_five_card_categories_match_independent_combinatorics(self):
        # Enumerate all 2,598,960 five-card hands in the production JS evaluator.
        # Expected counts are derived separately from combinations of ranks/suits.
        counts=node("""const h=require('./assets/poker-hand-lab.js'),d=[...'23456789TJQKA'].flatMap(r=>[...'shdc'].map(s=>r+s)),n=Array(9).fill(0);for(let a=0;a<48;a++)for(let b=a+1;b<49;b++)for(let c=b+1;c<50;c++)for(let e=c+1;e<51;e++)for(let f=e+1;f<52;f++)n[h.scoreFive([d[a],d[b],d[c],d[e],d[f]])[0]]++;process.stdout.write(JSON.stringify(n));""")
        expected=[(comb(13,5)-10)*(4**5-4),13*comb(4,2)*comb(12,3)*4**3,comb(13,2)*comb(4,2)**2*11*4,13*comb(4,3)*comb(12,2)*4**2,10*(4**5-4),4*comb(13,5)-40,13*comb(4,3)*12*comb(4,2),13*12*4,4*10]
        self.assertEqual(counts,expected)
        self.assertEqual(sum(counts),comb(52,5))

    def test_invalid_card_inputs_and_evaluator_inputs_fail_closed(self):
        bad=[]
        item=deepcopy(self.data);item['cases'][0]['hero'][0]=item['cases'][0]['board'][0];bad.append(item)
        item=deepcopy(self.data);item['cases'][0]['solution'][0]='2h';bad.append(item)
        item=deepcopy(self.data);item['cases'][0]['solution'].pop();bad.append(item)
        item=deepcopy(self.data);item['cases'][0]['category']=True;bad.append(item)
        item=deepcopy(self.data);item['cases'][0]['repair']='/poker/hand-rankings/#missing';bad.append(item)
        item=deepcopy(self.data);item['cases'].reverse();bad.append(item)
        with TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(ROOT/'_source/poker',root/'_source/poker')
            for value in bad:
                (root/lab.DATA).write_text(json.dumps(value))
                with self.assertRaises(ValueError):lab.load(root)
        result=node("const h=require('./assets/poker-hand-lab.js');let rejected=0;for(const c of [null,[],['As','As','Kh','Qh','Jh'],['1s','2s','3s','4s','5s'],['As','Ks','Qs','Js','Ts','9s'],['as','Ks','Qs','Js','Ts']]){try{h.scoreFive(c);}catch(e){rejected++;}}process.stdout.write(JSON.stringify(rejected));")
        self.assertEqual(result,6)

    def test_new_foundations_precede_the_hand_and_connect_to_existing_stages(self):
        html=self.outputs[build.output_path(lab.ROUTE)]
        doc=html5lib.parse(html,namespaceHTMLElements=False)
        ids=[e.get('id') for e in doc.iter() if e.get('id')]
        self.assertLess(ids.index('card-basics'),ids.index('first-hand-practice'))
        self.assertLess(ids.index('first-hand-practice'),ids.index('beginner-practice'))
        self.assertEqual(len([e for e in doc.iter('input') if e.get('type')=='checkbox']),70)
        self.assertEqual(len([e for e in doc.iter('article') if 'data-lab-case' in e.attrib]),10)
        for slug,case in [('first-decisions','pair'),('first-flop-decisions','three-kind'),('turn-and-river-decisions','two-pair')]:
            self.assertIn('href="'+lab.ROUTE+'#hand-lab-'+case+'"',self.outputs[build.output_path('/poker/'+slug+'/')])
        self.assertIn(lab.ROUTE+'#card-basics',self.outputs[Path('poker/beginner-practice/index.html')])
        text=' '.join(doc.itertext())
        for phrase in ['zero, one or two private cards','Suits do not outrank','A-2-3-4-5','ten fixed fictional hands','not a score or proof of learning']:
            self.assertIn(phrase,text)

    def test_precise_search_reaches_questions_without_hint_or_solution_spoilers(self):
        page=next(p for p in self.pages if p['path']==lab.ROUTE)
        sections={s['anchor']:s['text'] for s in poker_finder.guide_sections(ROOT,page,build.poker_content.load(ROOT))}
        for item in self.data['cases']:
            text=sections['hand-lab-'+item['id']]
            self.assertIn(item['prompt'],text)
            self.assertNotIn(item['hint'],text)
            self.assertNotIn(item['reason'],text)
        self.assertNotIn(self.data['example']['reason'],' '.join(sections.values()))

    def test_optional_assets_are_scoped_private_printable_and_verified_live(self):
        for path,text in self.outputs.items():
            if path.suffix=='.html':
                for asset in [lab.CSS,lab.SCRIPT]:self.assertEqual('/'+asset+'?v=' in text,path==build.output_path(lab.ROUTE),str(path))
        js=(ROOT/lab.SCRIPT).read_text()
        for token in ['fetch(', 'XMLHttpRequest','localStorage','sessionStorage','document.cookie','innerHTML','eval(','pushState','replaceState','Math.random']:
            self.assertNotIn(token,js)
        targets=check_live.targets();self.assertEqual(len(targets),468)
        for asset in [lab.CSS,lab.SCRIPT]:self.assertEqual(targets['/'+asset],(200,(ROOT/asset).read_bytes()))
        css=(ROOT/lab.CSS).read_text()
        self.assertIn('@media print',css)
        self.assertIn('[data-lab-case][hidden]',css)
        self.assertIn(':focus-visible',css)


if __name__=='__main__':unittest.main()
