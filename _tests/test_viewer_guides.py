"""Verify reader paths and fictional examples independently of the prose authoring.
The small evaluator below is a test oracle for these fixtures, not a public solver.
"""
from collections import Counter
from fractions import Fraction
from html.parser import HTMLParser
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import check_live

GUIDES = ['holdem-basics','hand-rankings','betting-and-pots','tournaments','poker-math','glossary','viewer-questions']

class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.items=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.items.append((tag,dict(attrs)))

def five(cards):
    ranks = sorted(('23456789TJQKA'.index(c[0])+2 for c in cards),reverse=True)
    counts = Counter(ranks)
    ordered = sorted(counts, key=lambda r:(counts[r],r), reverse=True)
    flush = len({c[1] for c in cards}) == 1
    unique = sorted(counts)
    straight = (5 if unique == [2,3,4,5,14] else unique[-1] if len(unique)==5 and unique[-1]-unique[0]==4 else 0)
    groups = sorted(counts.values(),reverse=True)
    if flush and straight: return (8,straight)
    if groups == [4,1]: return (7,*ordered)
    if groups == [3,2]: return (6,*ordered)
    if flush: return (5,*ranks)
    if straight: return (4,straight)
    if groups == [3,1,1]: return (3,*ordered)
    if groups == [2,2,1]: return (2,*ordered)
    if groups == [2,1,1,1]: return (1,*ordered)
    return (0,*ranks)

def best(cards):
    return max(map(five, combinations(cards,5)))

class ViewerGuidesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.outputs=build.build_outputs()

    def test_seven_guides_are_reachable_dated_and_sourced(self):
        manifest=build.public_pages()
        hub=self.outputs[Path('poker/start-here/index.html')]
        targets=check_live.targets()
        feed=ET.fromstring(self.outputs[Path('poker/feed.xml')])
        links={item.findtext('link') for item in feed.findall('./channel/item')}
        for slug in GUIDES:
            route='/poker/'+slug+'/'
            page=next(p for p in manifest if p['path']==route)
            text=self.outputs[build.output_path(route)]
            self.assertIn(route,hub)
            self.assertIn(route,targets)
            self.assertIn('https://nolankido.com'+route,links)
            self.assertIn(route,self.outputs[Path('sitemap.xml')])
            self.assertIn('References and limits',text)
            self.assertIn('fictional',text.lower())
            self.assertIn('Prepared with AI assistance.',text)
            self.assertIn('/poker/start-here/#viewer-library',text)
            self.assertIn('class="viewer-sources"',text)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S).group(1))
            self.assertEqual(schema['@type'],'Article')
            self.assertEqual(schema['datePublished'],page['date'])
            self.assertIn('property="article:published_time"',text)
            self.assertNotIn('<form',text)
            self.assertNotIn('<iframe',text)
            self.assertNotIn('<script src=',text)

    def test_old_viewer_anchors_and_48_glossary_entries(self):
        text=self.outputs[Path('poker/start-here/index.html')]
        for anchor in ['situation','action','terms','interpretation','term-pot','term-check','term-call','term-raise','term-range','term-ante','term-bubble','term-effective']:
            self.assertIn('id="'+anchor+'"',text)
        glossary=self.outputs[Path('poker/glossary/index.html')]
        self.assertEqual(glossary.count('<dt>'),48)
        self.assertIn('id="effective-stack"',glossary)
        self.assertIn('id="reconstruction"',glossary)

    def test_rank_examples_follow_the_correct_order(self):
        text=self.outputs[Path('poker/hand-rankings/index.html')]
        samples=[a['data-rank-cards'].split() for _,a in Tags(text).items if 'data-rank-cards' in a]
        self.assertEqual(len(samples),10)
        for cs in samples: self.assertEqual(len(set(cs)),5)
        scores=[five(cs) for cs in samples]
        self.assertEqual([s[0] for s in scores],[8,8,7,6,5,4,3,2,1,0])
        self.assertEqual(scores,sorted(scores,reverse=True))
        self.assertEqual(five('As 2d 3h 4s 5c'.split()),(4,5))
        self.assertEqual(five('Qs Kd Ah 2s 3c'.split())[0],0)

    def test_four_showdown_answers_are_independently_correct(self):
        cases=[a for _,a in Tags(self.outputs[Path('poker/hand-rankings/index.html')]).items if 'data-winner' in a]
        self.assertEqual(len(cases),4)
        for a in cases:
            first=a['data-a'].split(); second=a['data-b'].split(); board=a['data-board'].split()
            self.assertEqual(len(set(first+second+board)),9)
            one,two=best(first+board),best(second+board)
            winner='a' if one>two else 'b' if two>one else 'tie'
            self.assertEqual(winner,a['data-winner'])
        names=[a for _,a in Tags(self.outputs[Path('poker/hand-rankings/index.html')]).items if a.get('role')=='img']
        self.assertEqual(len(names),86)
        self.assertTrue(all(' of ' in a.get('aria-label','') for a in names))

    def test_full_hand_bookkeeping_matches_published_totals(self):
        text=self.outputs[Path('poker/holdem-basics/index.html')]
        invested=500+400+600
        totals=[500*2+100,500*2+100+400*2,500*2+100+400*2+600*2]
        self.assertEqual(totals,[1100,1900,3100])
        self.assertEqual(totals[-1]-invested,1600)
        for phrase in ['1,100 = 500 + 500 + 100','1,900 = 1,100 + 400 + 400','3,100 = 1,900 + 600 + 600','1,600']:
            self.assertIn(phrase,text)
        board='Qd 7c 2s 9h 3d'.split()
        self.assertGreater(best('As Qs'.split()+board),best('Qh Jh'.split()+board))

    def test_side_pots_call_and_tournament_arithmetic(self):
        main=1000*3; side=(2500-1000)*2; refund=4000-2500
        self.assertEqual(main+side+refund,1000+2500+4000)
        bets=self.outputs[Path('poker/betting-and-pots/index.html')]
        for phrase in ['3,000 = 1,000 × 3','3,000 = (2,500 − 1,000) × 2','7,500','3,000 = 1,200 + 400 + 1,400','4,000']:
            self.assertIn(phrase,bets)
        self.assertEqual(500+(500-200),800)
        self.assertEqual(1400-400,1000)
        tour=self.outputs[Path('poker/tournaments/index.html')]
        self.assertEqual(24000//1000,24); self.assertEqual(24000//1500,16)
        self.assertEqual(1200000//40,30000); self.assertEqual(450-300*2,-150)
        for phrase in ['24 BB','16 BB','30,000','$450 − $600 = −$150']:
            self.assertIn(phrase,tour)

    def test_probability_examples_match_exact_counts(self):
        text=self.outputs[Path('poker/poker-math/index.html')]
        self.assertEqual(Fraction(10,20+10+10),Fraction(1,4))
        self.assertEqual(Fraction(3,10)*30-Fraction(7,10)*10,2)
        self.assertEqual(Fraction(3,10)**2,Fraction(9,100))
        hit=1-Fraction(38,47)*Fraction(37,46)
        # Count ordered turn/river outcomes using nine marked cards.
        hits=sum(a<9 or b<9 for a in range(47) for b in range(47) if a!=b)
        self.assertEqual(hit,Fraction(hits,47*46))
        for value in [9/47, float(hit),9/46]: self.assertIn(f'{value*100:.1f}%',text)
        for phrase in ['10 ÷ 40 = 25%','0.30 × 30 − 0.70 × 10 = +2','0.30 × 0.30 = 9%']:
            self.assertIn(phrase,text)

    def test_reference_and_no_account_practice(self):
        text=(ROOT/'downloads/poker-viewer-reference.md').read_text()
        self.assertIn('call 10: final pot 40',text)
        self.assertIn('/downloads/poker-viewer-reference.md',check_live.targets())
        total=sum(s.count('class="poker-details viewer-question"') for p,s in self.outputs.items() if p in {Path('poker') / slug / 'index.html' for slug in GUIDES})
        self.assertEqual(total,26)
        for p,s in self.outputs.items():
            if str(p).startswith('poker/') and p.suffix=='.html':
                self.assertNotIn('class="poker-details viewer-question" open',s)

if __name__=='__main__': unittest.main(verbosity=2)
