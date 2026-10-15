"""Limped pots: accounting, model boundaries and complete publication integrity."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json,re,subprocess,sys,unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,search_sections,site_find
import multiway_history as history
import short_stack_history
ROUTE='/poker/limped-multiway-pots/'
ARRIVALS=['/poker/','/poker/library/','/poker/topics/cash-games/','/poker/topics/strategy/','/poker/topics/tournaments/','/poker/multiway-pot-workshop/','/poker/cash-game-study/','/poker/cash-game-study-path/','/poker/first-flop-decisions/','/poker/betting-with-a-purpose/','/poker/poker-under-uncertainty/','/notes/']

class MultiwayEssayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(' '.join(cls.main.itertext()).split())
        cls.baseline=json.loads((ROOT/'_tests/multiway-baseline.json').read_text())

    def test_complete_predecessor_survives_and_unreviewed_changes_fail_closed(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('35f071b6641797e9a04da28085513bf18ab30054',191,218,450))
        self.assertEqual(history.pages(self.pages),b['pages'])
        old=history.outputs(self.outputs);self.assertEqual(set(map(str,old)),set(b['outputs']))
        for p,v in old.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in {**b['files'],**b['extras']}.items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        changed=deepcopy(self.pages);next(p for p in changed if p['path']==ROUTE)['description']='Unreviewed solver endorsement'
        self.assertNotEqual(history.pages(changed),b['pages'])
        changed=dict(self.outputs);changed[build.output_path(ROUTE)]=self.html.replace('$253','$278')
        self.assertIn(build.output_path(ROUTE),history.outputs(changed))
        for path in ['_scripts/build.py','_source/poker/multiway-pot-workshop.html','find/index.html','_reports/search-audit.json']:
            raw=(ROOT/path).read_bytes();bad=raw+b'Unreviewed'
            self.assertEqual(history.before(path,bad),bad)
            self.assertNotEqual(history.before(path,raw),history.before(path,bad))

    def test_pot_conservation_call_increment_and_blockers_are_consistent(self):
        preflop=[18,18,18,18,1];pot=sum(preflop)
        self.assertEqual(pot,73);self.assertEqual(450-18,432)
        self.assertAlmostEqual(float(F(432,73)),5.9178082,places=6)
        before_call=pot+25+90;call=90-25;after_call=before_call+call
        self.assertEqual((before_call,call,after_call),(188,65,253))
        self.assertAlmostEqual(100*float(F(call,after_call)),25.6917,places=4)
        known={'As','Qs','Qd','9s','6s'};self.assertEqual(len(known),5)
        deck={rank+suit for rank in '23456789TJQKA' for suit in 'shdc'}-known
        spades=[c for c in deck if c.endswith('s')]
        self.assertEqual(len(spades),9)
        self.assertFalse(any(c.startswith('A') for c in spades));self.assertIn('Ts',spades)
        for value in ['4 × $18 + $1 = $73','$432 behind','$188','$65','$253','25.69%','to $90 total','heads-up against the check-raiser','removes ace-high spade draws','It does not remove every other spade draw','fictional']:
            self.assertIn(value,self.text)
        self.assertIn('The turn can bring another bet',self.text)

    def test_bluff_math_is_joint_conditional_and_model_limited(self):
        p=F(55,100);self.assertEqual(p*p,F(121,400))
        threshold=F(50,100+50);ev=p*p*100-(1-p*p)*50
        self.assertLess(p*p,threshold);self.assertEqual(ev,F(-37,8))
        table=next(self.main.iter('table'))
        self.assertEqual(len(list(table.iter('tr'))),5)
        for value in ['55.0%','30.3%','16.6%','9.2%','30.25%','33.33%','−$4.625','conditional probabilities','assume independence','zero-equity model','not an observed live-game frequency']:
            self.assertIn(value,self.text)
        self.assertIn('heads-up minimum-defense figure is not a quota',self.text)

    def test_sources_distinguish_live_reads_studies_and_current_tool_boundaries(self):
        ids={e.get('id'):e for e in self.main.iter() if e.get('id')}
        self.assertEqual(len([k for k in ids if k.startswith('source-')]),7)
        for a in self.main.iter('a'):
            if a.get('href','').startswith('#source-'):self.assertIn(a.get('href')[1:],ids)
        for value in ['20-flop subset','11 percentage points','18% to 1.3%','chip expected value','three players to reach the flop','fourth overcaller or overlimper is not supported','Nodelocking','25bb middle stack','40bb','16bb','not Nolan’s sessions','October 15, 2026','does not claim a new solver run','one opponent’s','For study away from play']:
            self.assertIn(value.lower(),self.text.lower())
        self.assertNotRegex(self.html,r'||—|turn\d+(?:view|search)\d+|Caribbean Cardroom|Hero had roughly')
        self.assertFalse(list(self.main.iter('iframe'))+list(self.main.iter('video'))+list(self.main.iter('img')))

    def test_explanations_and_download_are_native_and_private(self):
        questions=[e for e in self.main.iter('section') if e.get('class')=='multiway-check']
        self.assertEqual(len(questions),3)
        for q in questions:
            d=next(q.iter('details'));self.assertNotIn('open',d.attrib);self.assertTrue(next(d.iter('summary')).text.startswith('Show the '))
        preview=next(e for e in self.main.iter('pre') if 'multiway-sheet' in e.get('class',''))
        self.assertEqual(''.join(preview.itertext()),(ROOT/'downloads/poker-multiway-review.md').read_text())
        self.assertFalse(list(self.main.iter('form'))+list(self.main.iter('input'))+list(self.main.iter('textarea')))
        css=(ROOT/'assets/poker-multiway.css').read_text();self.assertIn('pre-wrap',css);self.assertIn('overflow-wrap: anywhere',css);self.assertIn('@media print',css)
        self.assertIn('content-visibility: visible',css)

    def test_public_routes_feeds_search_and_all_old_headings_remain_reachable(self):
        for route in ARRIVALS:self.assertIn('href="'+ROUTE,self.outputs[build.output_path(route)],route)
        for name in ['poker/feed.xml','writing.xml','sitemap.xml']:self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path(name)])
        schema=json.loads(re.search(r'type="application/ld\+json">(.*?)</script>',self.html)[1]);self.assertEqual((schema['@type'],schema['datePublished']),('Article','2026-10-15'))
        canonical=search_sections.index(self.outputs,self.pages);current=search_sections.index(short_stack_history.outputs(self.outputs),short_stack_history.pages(self.pages));old=search_sections.index(history.outputs(self.outputs),self.baseline['pages'])
        old['/poker/library/']=[[a,label.replace('59 free guides','60 free guides')] for a,label in old['/poker/library/']]
        self.assertEqual({p:v for p,v in current.items() if p!=ROUTE},old)
        raw=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[search_sections.PAGE],re.S)[1];self.assertLess(len(raw.encode()),60000)
        entry=next(e for e in site_find.entries(ROOT,self.pages) if e['path']==ROUTE)
        code=r'''const assert=require('node:assert/strict'),s=require('./assets/site-find.js');
const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
for(const q of ['limped multiway pots','limpers','isolation'])assert(s.score(d.entry,q)>0);
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(d.packed))),d.canonical);'''
        subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps({'entry':dict(entry,subjects=' '.join(entry['interests'])),'packed':json.loads(raw),'canonical':canonical}),text=True,check=True)
        targets=check_live.targets();self.assertEqual(len(targets),470)
        for asset in ['assets/poker-multiway.css','downloads/poker-multiway-review.md','assets/social/reader-poker-limped-multiway-pots.png']:self.assertEqual(targets['/'+asset],(200,(ROOT/asset).read_bytes()))
        for p,v in self.outputs.items():
            if p.suffix=='.html':self.assertEqual('/assets/poker-multiway.css?' in v,p==build.output_path(ROUTE))

    def test_old_images_are_immutable_and_new_title_card_is_bounded(self):
        for p,d in self.baseline['files'].items():
            if p.startswith('assets/social/'):self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        record=json.loads((ROOT/'_source/reader-previews.json').read_text())['pages']['poker-limped-multiway-pots']
        raw=(ROOT/record['src'].lstrip('/')).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(),record['sha256']);self.assertLess(len(raw),25000)
        self.assertEqual(' '.join(record['layout']['lines']),next(p for p in self.pages if p['path']==ROUTE)['title'])

if __name__=='__main__':unittest.main()
