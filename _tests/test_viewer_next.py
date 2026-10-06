"""Independent checks for the new viewer explanations and unchanged public baseline."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from html import unescape
import hashlib
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET
from test_viewer_guides import Tags, best

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import check_live
GUIDES=['position-and-stacks','reading-the-board','ranges-and-bets','tournament-formats','table-etiquette','follow-along']
PROTECTED={'_source/poker/holdem-basics.html': 'a36851883f9398fa2e0e18fccf52aa1f0734e63f2f4e55d5ae7cc10a2b65684d', '_source/poker/hand-rankings.html': 'fb6be2d273a470e0be78defd14e46a7e8c4bed1a162bd70fb05d24bd57fcc1a5', '_source/poker/betting-and-pots.html': '9841e0e5121022a04b84cf2f1ef2005f670315a745b257b40efc24f7f717b95e', '_source/poker/tournaments.html': '15244efca170a8c0f954aba553465385a05f7fce2b9f871eb8c1546acfebeb00', '_source/poker/poker-math.html': '0ee78cede40c4b1c6f807dea051099f2660ffc4f6cddb86d57b5bfe016ed31bb', '_source/poker/glossary.html': '9cb6e49e10fc5bacade6a01f42b8d20acc380c8479259ad50a76cc66ad6daebd', '_source/poker/viewer-questions.html': 'c14b14bf74960cc067aa45a09d22c80f4a1ed625e5f302523a3c12a5ee10f6f5', 'index.html': '8de9ffa71f89981ce94ead6ea8743c1c2ef9c5a8a12f15f5533ead462d9c8690', 'technology/index.html': 'bad1290cc58638ab9e00187c9322dc86493aefa1b84835f18881210c255f2ef8', 'creative/index.html': '861519815edc48b8cc18d1e9d2ced9dd27855d453909df1d0748e64407f60cea', 'assets/contact.js': '65b6fc99c23c947f4bcc9b427bc04b08dfabd6333c8c26e9ad6c506adc370858', 'styles.css': '44be94f4cc9dc8ff7af79d975ceae280ae2c01d7ef755db28effbeb6fbfeb4ef', 'assets/site.css': '784f0d0fb3faeefc953712470a5b86dde775e9c9991e7b22fbc0241ccc69acf6', 'assets/hubs.css': 'aab63ac0f415d1d6ff99e2c141979aaceeef8d77af0edeae33533c2ec9c5fb66', '_source/poker/catalog.json': '7c1051f6e2bc3943b7c1dbe4da229694455681b8875a346c99279e555edb733f', 'feed.xml': '9b3e05a7e14db5b1e751d18a7ff0c8cbaf47b7d60453c1e9c43424e8d57e223a'}

class ViewerNextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.outputs=build.build_outputs()

    def output(self,slug): return self.outputs[Path('poker')/slug/'index.html']

    def attrs(self,slug,key):
        return [a for _,a in Tags(self.output(slug)).items if key in a]

    def test_all_six_guides_are_dated_sourced_and_discoverable(self):
        hub=self.output('start-here')
        targets=check_live.targets()
        feed=ET.fromstring(self.outputs[Path('poker/feed.xml')])
        feed_links={i.findtext('link') for i in feed.findall('./channel/item')}
        for slug in GUIDES:
            with self.subTest(slug=slug):
                route='/poker/'+slug+'/'
                source=self.output(slug)
                self.assertIn(route,hub)
                self.assertIn(route,targets)
                self.assertIn('https://nolankido.com'+route,feed_links)
                self.assertIn(route,self.outputs[Path('sitemap.xml')])
                self.assertIn('References and limits',source)
                self.assertIn('fictional',source)
                self.assertIn('Prepared with AI assistance.',source)
                self.assertIn('class="viewer-sources"',source)
                self.assertIn('href="/poker/start-here/#viewer-library"',source)
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S).group(1))
                self.assertEqual(schema['@type'],'Article')
                self.assertEqual(schema['datePublished'],'2026-10-05')
                for forbidden in ['<form','<iframe','<script src=','\u2014']:
                    self.assertNotIn(forbidden,source)

    def test_previous_content_and_design_are_unchanged(self):
        for path,digest in PROTECTED.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertEqual(self.outputs[Path('index.html')],(ROOT/'index.html').read_text())

    def test_twenty_four_new_disclosures_are_closed(self):
        total=0
        for slug in GUIDES:
            entries=[a for tag,a in Tags(self.output(slug)).items if tag=='details' and 'viewer-question' in a.get('class','')]
            total+=len(entries)
            self.assertEqual(len(entries),9 if slug=='follow-along' else 3)
            self.assertTrue(all('open' not in a for a in entries))
        self.assertEqual(total,24)

    def test_draw_overlap_by_enumerating_physical_cards(self):
        a=self.attrs('reading-the-board','data-draw-hole')[0]
        known=(a['data-draw-hole']+' '+a['data-draw-board']).split()
        self.assertEqual(len(set(known)),5)
        deck={r+s for r in '23456789TJQKA' for s in 'shdc'}
        remaining=deck-set(known)
        hits={c for c in remaining if best(known+[c])[0] in [4,5,8]}
        self.assertEqual(len(remaining),47)
        self.assertEqual(len(hits),int(a['data-improving-cards']))
        flush={c for c in remaining if c[1]=='s'}
        straight={c for c in remaining if c[0] in 'Q7'}
        self.assertEqual(len(flush),9);self.assertEqual(len(straight),8)
        self.assertEqual(flush & straight,{'Qs','7s'})
        self.assertEqual(hits,flush|straight)
        self.assertIn('9 + 8 − 2 = 15',unescape(self.output('reading-the-board')))

    def test_winner_changes_on_each_street(self):
        for slug,prefix in [('reading-the-board','data-runout-'),('follow-along','data-showdown-')]:
            a=self.attrs(slug,prefix+'a')[0]
            first,second,board=(a[prefix+k].split() for k in ['a','b','board'])
            self.assertEqual(len(set(first+second+board)),9)
            scores=[(best(first+board[:n]),best(second+board[:n])) for n in [3,4,5]]
            self.assertEqual([x>y for x,y in scores],[True,False,True])
            self.assertEqual([scores[0][0][0],scores[1][1][0],scores[2][0][0]],[3,5,6])
            self.assertEqual(scores[2][0],(6,13,2))

    def test_combinations_with_blockers(self):
        a=self.attrs('ranges-and-bets','data-combo-known')[0]
        deck=[r+s for r in '23456789TJQKA' for s in 'shdc']
        known=set(a['data-combo-known'].split())
        def counts(blocked):
            result=[0,0,0]
            for x,y in combinations([c for c in deck if c not in blocked],2):
                if x[0]==y[0]=='Q':result[0]+=1
                elif {x[0],y[0]}=={'A','K'}:result[1 if x[1]==y[1] else 2]+=1
            return result
        self.assertEqual(counts(set()),[6,4,12]);self.assertEqual(counts(known),[3,3,9])
        self.assertEqual(sum(counts(set())),int(a['data-combo-before']))
        self.assertEqual(sum(counts(known)),int(a['data-combo-after']))
        self.assertIn('6 + 4 + 12 = 22',self.output('ranges-and-bets'))
        self.assertIn('15 total',self.output('ranges-and-bets'))

    def test_raise_pot_and_remaining_stack_conserve_chips(self):
        a=self.attrs('follow-along','data-snapshot-pot')[0]
        pot,bet,raise_to,call,final=(int(a[k]) for k in ['data-snapshot-pot','data-bet','data-raise-to','data-call','data-final-pot'])
        self.assertEqual(call,raise_to-bet)
        self.assertEqual(final,pot+bet+raise_to+call)
        self.assertEqual(final,100+500*2+1200*2)
        remaining_a=6000-500-bet-call;remaining_b=9000-500-raise_to
        self.assertEqual(remaining_a,4300);self.assertEqual(remaining_b,7300)
        self.assertEqual(remaining_a+remaining_b+final,6000+9000+100)
        for value in ['2,700','3,500','4,300','7,300']:
            self.assertIn(value,self.output('follow-along'))

    def test_river_price_and_conditional_expectations(self):
        a=self.attrs('follow-along','data-river-pot')[0]
        pot,bet=int(a['data-river-pot']),int(a['data-river-bet'])
        final=pot+2*bet
        self.assertEqual(Fraction(bet,final),Fraction(a['data-threshold']))
        self.assertEqual(Fraction(20,100)*final-bet,-400)
        self.assertEqual(Fraction(35,100)*final-bet,800)
        for phrase in ['2,000 ÷ 8,000 = 25%','0.20 × 8,000 − 2,000 = −400','0.35 × 8,000 − 2,000 = +800','Both percentages are invented assumptions']:
            self.assertIn(phrase,self.output('follow-along'))

    def test_stack_and_bounty_examples(self):
        a=self.attrs('position-and-stacks','data-stack')[0]
        self.assertEqual(int(a['data-stack'])//int(a['data-blind']),30)
        self.assertEqual([int(a['data-stack'])//int(p) for p in a['data-pots'].split()],[4,2])
        b=self.attrs('tournament-formats','data-bounty')[0]
        self.assertEqual(int(b['data-bounty']),int(b['data-now'])+int(b['data-added']))
        self.assertIn('four identical $500 tickets',self.output('tournament-formats'))
        self.assertIn('100 + 200 + 200',self.output('tournament-formats'))

    def test_cards_are_named_and_printed_with_suits(self):
        total=0
        for slug in GUIDES:
            for _,a in Tags(self.output(slug)).items:
                if 'viewer-card' in a.get('class','').split():
                    total+=1
                    self.assertEqual(a.get('role'),'img')
                    self.assertRegex(a.get('aria-label',''),r'^(ace|king|queen|jack|ten|[a-z]+) of (spades|hearts|diamonds|clubs)$')
        self.assertGreater(total,40)

    def test_guide_directory_and_topic_paths_are_explicit(self):
        hub=self.output('start-here')
        for marker in ['viewer-essentials','viewer-next','heard-it','quick-start']:
            self.assertIn('id="'+marker+'"',hub)
        self.assertEqual(hub.count('/ Viewer guide</p>'),13)
        self.assertIn('aria-label="Commentary phrase shortcuts"',hub)
        self.assertIn('three suggested reading routes',hub)
        self.assertIn('/poker/follow-along/',self.outputs[Path('poker/index.html')])

    def test_new_download_and_deployment_exclusion(self):
        self.assertEqual(check_live.targets()['/downloads/poker-watch-along.md'],(200,(ROOT/'downloads/poker-watch-along.md').read_bytes()))
        download=(ROOT/'downloads/poker-watch-along.md').read_text()
        for slug in GUIDES:self.assertIn('/poker/'+slug+'/',download)
        config=(ROOT/'_config.yml').read_text()
        exclusion=config.split('exclude:',1)[1].split('optional_front_matter:',1)[0]
        self.assertIn('  - VIEWER_NEXT_RELEASE.md',exclusion)
        self.assertEqual(config.split('optional_front_matter:',1)[1].strip(),'enabled: false')

if __name__=='__main__': unittest.main(verbosity=2)
