"""Independent budget arithmetic, publication integrity and complete search round trips."""
from copy import deepcopy
from decimal import Decimal as D
from hashlib import sha256
from pathlib import Path
import json,re,subprocess,sys,unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,search_sections,site_find
import tournament_budget_history as history
import thunder_valley_history
ROUTE='/poker/tournament-trip-budget/'

class TournamentBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(cls.main.itertext())
        cls.baseline=json.loads((ROOT/'_tests/tournament-budget-baseline.json').read_text())

    def test_exact_predecessor_inputs_outputs_and_mutation_guards(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('0879bc632d57ac8591206dbe7ff6c99bac96b62f',188,215,440))
        self.assertEqual(history.pages(self.pages),b['pages'])
        old=history.outputs(self.outputs);self.assertEqual(set(map(str,old)),set(b['outputs']))
        for p,v in old.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in {**b['files'],**b['extras']}.items():
            self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        changed=deepcopy(self.pages);next(p for p in changed if p['path']==ROUTE)['description']='Unreviewed profit promise'
        self.assertNotEqual(history.pages(changed),b['pages'])
        changed=dict(self.outputs);changed[build.output_path(ROUTE)]=self.html.replace('$451.50','$401.50')
        self.assertIn(build.output_path(ROUTE),history.outputs(changed))
        for path in ['assets/site-find.js','_scripts/search_sections.py','_source/poker/getting-started.html','find/index.html','_reports/search-audit.json']:
            raw=(ROOT/path).read_bytes();bad=raw+b'Unreviewed'
            self.assertEqual(history.before(path,bad),bad)
            self.assertNotEqual(history.before(path,raw),history.before(path,bad))

    def test_entry_fees_and_fuel_have_the_right_units(self):
        self.assertEqual(D(330)+D(70),D(400))
        self.assertEqual(D(70)/D(400),D('.175'))
        self.assertEqual((D(330)+D(70))*2,D(800))
        fuel=[D(miles)*D('3.50')/D(28) for miles in [60,300,480]]
        self.assertEqual(fuel,[D('7.50'),D('37.50'),D('60')])
        for phrase in ['Do not add $70 again','Each $400 entry already includes its fee','$7.50','$37.50','$60']:
            self.assertIn(phrase,self.text)

    def test_every_budget_reconciles_independently_and_reserves_are_not_losses(self):
        room=D(180)*(1+D('.0875')+D('.05'));self.assertEqual(room,D('204.75'))
        direct=[D('7.50')+32+12,D('37.50')+12+room+65+15,D(60)+18+room*2+105+25]
        self.assertEqual(direct,list(map(D,['51.50','334.25','617.50'])))
        base=[v+entry for v,entry in zip(direct,[400,400,800])]
        self.assertEqual(base,list(map(D,['451.50','734.25','1417.50'])))
        contingency=room+35+10;self.assertEqual(contingency,D('249.75'))
        reserves=[D(50),D(400)+contingency,D(400)+contingency]
        self.assertEqual([a+b for a,b in zip(base,reserves)],list(map(D,['501.50','1384.00','2067.25'])))
        tables=list(self.main.iter('table'))
        for table,planned,funds in zip(tables[2:5],base,[D('501.50'),D('1384.00'),D('2067.25')]):
            text=' '.join(table.itertext())
            self.assertIn('$'+format(planned,',.2f'),text)
            self.assertIn('$'+format(funds,',.2f'),text)
        self.assertIn('Unspent reserves are not expenses or losses',self.text)
        self.assertIn('not a guarantee that every disruption fits',self.text)

    def test_adjustments_sharing_and_payouts_use_all_actual_costs_once(self):
        room=D('204.75');overnight=D('734.25');weekend=D('1417.50')
        self.assertEqual(overnight+400,D('1134.25'))
        self.assertEqual(overnight+room+35+10,D(984))
        self.assertEqual(weekend-room,D('1212.75'))
        self.assertEqual(D(300)+70+2*125,D(620))
        self.assertEqual(weekend+620-(60+18),D('1959.50'))
        self.assertEqual(D(600)-400-D('334.25'),D('-134.25'))
        self.assertEqual(D(600)-800-D('334.25'),D('-534.25'))
        for phrase in ['−$134.25','−$534.25','$1,212.75','$1,959.50','rather than halving everything','pre-tax','not a fare quote']:
            self.assertIn(phrase,self.text)

    def test_dated_primary_sources_assumptions_and_personal_scope_are_explicit(self):
        ids={e.get('id'):e for e in self.main.iter() if e.get('id')}
        self.assertEqual(len([k for k in ids if k.startswith('source-')]),8)
        for e in self.main.iter('a'):
            if e.get('href','').startswith('#source-'):self.assertIn(e.get('href')[1:],ids)
        self.assertIn('PDF pages 2, 12 and 14',self.text)
        self.assertIn('beginning of level 9',self.text)
        self.assertIn('October 15, 2026',self.text)
        self.assertIn('No live hotel or flight quote was obtained',self.text)
        self.assertIn('not a finding that a named hotel charges none',self.text)
        self.assertIn('not Nolan’s travel plans or results',self.text)
        self.assertIn('Oneida city, in Madison County',self.text)
        self.assertNotRegex(self.html,r'||—|publication handoff|turn\d+(?:view|search)\d+')

    def test_explanations_and_download_work_without_a_data_collection_form(self):
        questions=[e for e in self.main.iter('section') if e.get('class')=='budget-check']
        self.assertEqual(len(questions),3)
        for q in questions:
            d=next(q.iter('details'));self.assertNotIn('open',d.attrib)
            self.assertEqual(next(d.iter('summary')).text,'Show the calculation')
        preview=next(e for e in self.main.iter('pre') if 'budget-sheet' in e.get('class',''))
        self.assertEqual(''.join(preview.itertext()),(ROOT/'downloads/poker-tournament-trip-budget.md').read_text())
        self.assertFalse(list(self.main.iter('form'))+list(self.main.iter('input'))+list(self.main.iter('textarea')))
        tables=list(self.main.iter('table'));self.assertEqual(len(tables),6)
        self.assertTrue(all(list(t.iter('caption')) for t in tables))
        region=next(e for e in self.main.iter() if e.get('class')=='budget-comparison')
        self.assertEqual((region.get('role'),region.get('tabindex')),('region','0'))
        self.assertTrue(region.get('aria-label'))

    def test_navigation_archive_feeds_and_live_inventory_include_the_article(self):
        for route in ['/poker/','/poker/library/','/poker/topics/tournaments/','/poker/topics/places-to-play/','/poker/topics/safer-play/','/poker/choosing-a-tournament/','/poker/registration-and-reentry/','/poker/first-live-tournament/','/poker/getting-started/','/poker/tournament-checklists/','/poker/live-tournament-guide/','/notes/']:
            self.assertIn('href="'+ROUTE, self.outputs[build.output_path(route)],route)
        for feed in ['poker/feed.xml','writing.xml','sitemap.xml']:
            self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path(feed)])
        schema=json.loads(re.search(r'type="application/ld\+json">(.*?)</script>',self.html)[1])
        self.assertEqual((schema['@type'],schema['datePublished']),('Article','2026-10-15'))
        self.assertEqual(len(check_live.targets()),470)
        for asset in ['assets/poker-budget.css','downloads/poker-tournament-trip-budget.md','assets/social/reader-poker-tournament-trip-budget.png']:
            self.assertEqual(check_live.targets()['/'+asset],(200,(ROOT/asset).read_bytes()))
        for p,v in self.outputs.items():
            if p.suffix=='.html':self.assertEqual('/assets/poker-budget.css?' in v,p==build.output_path(ROUTE))

    def test_every_prior_search_heading_survives_and_pooled_labels_round_trip(self):
        canonical=search_sections.index(self.outputs,self.pages)
        current=search_sections.index(thunder_valley_history.outputs(self.outputs),thunder_valley_history.pages(self.pages))
        old=search_sections.index(history.outputs(self.outputs),self.baseline['pages'])
        old['/poker/library/']=[[a,label.replace('57 free guides','58 free guides')] for a,label in old['/poker/library/']]
        self.assertEqual({p:v for p,v in current.items() if p not in {ROUTE,'/poker/comics/good-decision-bad-river/'}},old)
        raw=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[search_sections.PAGE],re.S)[1]
        self.assertLess(len(raw.encode()),60000)
        entry=next(e for e in site_find.entries(ROOT,self.pages) if e['path']==ROUTE)
        code=r'''const assert=require('node:assert/strict'),s=require('./assets/site-find.js');
const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
assert(s.score(d.entry,'tournament budget')>=1000);
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(d.packed))),d.canonical);
for(const version of [2,3]){
 const pages=version===2?{'/poker/':['safe','Old label']}:{poker:{'':['safe','Old label']}};
 assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections({version,pages}))),{'/poker/':[['safe','Old label']]});
}
for(const bad of [null,{}, {version:4,pages:{}},{version:4,labels:[''],pages:{}},{version:4,labels:[null],pages:{}},{version:4,labels:[],pages:{'https://evil':{'':['safe','x']}}},{version:4,labels:[],pages:{poker:{'../':['safe','x']}}}])assert.equal(Object.keys(s.decodeSections(bad)).length,0);
const mixed={version:4,labels:['Repeated <label> & café'],pages:{poker:{'':['a',0,'b','Unique label','c',-1,'d',5,'bad id',0,'e',null]}}};
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(mixed))),{'/poker/':[['a','Repeated <label> & café'],['b','Unique label']]});
'''
        data={'entry':dict(entry,subjects=' '.join(entry['interests'])),'packed':json.loads(raw),'canonical':canonical}
        subprocess.run(['node','-e',code],input=json.dumps(data),text=True,check=True,cwd=ROOT)

    def test_new_card_has_its_own_bound_and_all_previous_cards_keep_their_bytes(self):
        cards=json.loads(thunder_valley_history.before('_source/reader-previews.json',(ROOT/'_source/reader-previews.json').read_text()))['pages']
        new=cards['poker-tournament-trip-budget'];raw=(ROOT/new['src'].lstrip('/')).read_bytes()
        self.assertLess(len(raw),25000)
        self.assertEqual(sha256(raw).hexdigest(),new['sha256'])
        previous={p:d for p,d in self.baseline['files'].items() if p.startswith('assets/social/')}
        for p,d in previous.items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        old_total=sum(len(thunder_valley_history.before(v['src'].lstrip('/'),(ROOT/v['src'].lstrip('/')).read_bytes())) for k,v in cards.items() if k!='poker-tournament-trip-budget')
        self.assertLess(old_total,1000000)

if __name__=='__main__':unittest.main()
