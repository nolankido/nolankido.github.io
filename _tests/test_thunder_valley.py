"""Thunder Valley: dated source boundaries, event arithmetic and complete publication integrity."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,re,subprocess,sys,unittest
import html5lib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,search_sections,site_find
import thunder_valley_history as history
import multiway_history
ROUTE='/poker/thunder-valley-poker-guide/'

class ThunderValleyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs();cls.pages=build.public_pages()
        cls.html=cls.outputs[build.output_path(ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.main=next(cls.doc.iter('main'));cls.text=' '.join(' '.join(cls.main.itertext()).split())
        cls.baseline=json.loads((ROOT/'_tests/thunder-valley-baseline.json').read_text())

    def test_exact_predecessor_and_unreviewed_mutation_guards(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('94e77791899b57a91c43da7e1744846bccfa43b5',190,217,446))
        self.assertEqual(history.pages(self.pages),b['pages'])
        old=history.outputs(self.outputs);self.assertEqual(set(map(str,old)),set(b['outputs']))
        for p,v in old.items():self.assertEqual(sha256(v.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,d in {**b['files'],**b['extras']}.items():
            self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),d,p)
        changed=deepcopy(self.pages);next(p for p in changed if p['path']==ROUTE)['description']='Unreviewed endorsement'
        self.assertNotEqual(history.pages(changed),b['pages'])
        changed=dict(self.outputs);changed[build.output_path(ROUTE)]=self.html.replace('$5,100','$3,400')
        self.assertIn(build.output_path(ROUTE),history.outputs(changed))
        for path in ['_scripts/build.py','_source/poker/tournament-trip-budget.html','find/index.html','_reports/search-audit.json']:
            raw=(ROOT/path).read_bytes();bad=raw+b'Unreviewed'
            self.assertEqual(history.before(path,bad),bad)
            self.assertNotEqual(history.before(path,raw),history.before(path,bad))

    def test_official_facts_dates_and_unresolved_procedures_are_distinct(self):
        ids={e.get('id'):e for e in self.main.iter() if e.get('id')}
        self.assertEqual(len([k for k in ids if k.startswith('source-')]),7)
        for a in self.main.iter('a'):
            href=a.get('href','')
            if href.startswith('#source-'):self.assertIn(href[1:],ids)
        for value in ['1200 Athens Avenue','916-408-9095','21 or older','24 hours a day','28 tables','non-smoking','4 p.m.','11 a.m.','October 15, 2026']:
            self.assertIn(value,self.text)
        for phrase in ['completed events','does not establish that a particular entry can be purchased online','did not settle all of these details','did not establish a poker-room-specific filming policy','Entertainment','The Venue','No staff interview, timed route, current room quote or personal trip report']:
            self.assertIn(phrase,self.text)
        self.assertNotRegex(self.html,r'||—|\[Internal link:|turn\d+(?:view|search)\d+')
        self.assertFalse(list(self.main.iter('iframe'))+list(self.main.iter('video'))+list(self.main.iter('img')))

    def test_historical_eligibility_reentries_and_included_fees_are_correct(self):
        self.assertEqual(330+70,400);self.assertEqual(1515+185,1700)
        attempts=1+2;self.assertEqual(attempts*1700,5100)
        self.assertEqual(9*40/60,6)
        for phrase in ['50 or older','Two re-entries per flight','Beginning of level 9','Beginning of level 13','75-minute dinner break after level 9','15% remaining','Three paid attempts: 3 × $1,700 = $5,100','six hours of scheduled play','PDF page 1','page 13']:
            self.assertIn(phrase,self.text)
        table=next(self.main.iter('table'));self.assertEqual(len(list(table.iter('tr'))),8)
        self.assertIn('not future event terms',next(table.iter('caption')).text)
        self.assertIn('a ceiling under event rules, not a recommendation',self.text)

    def test_explained_checks_and_private_sheet_work_as_native_html(self):
        questions=[e for e in self.main.iter('section') if e.get('class')=='venue-check']
        self.assertEqual(len(questions),3)
        for q in questions:
            d=next(q.iter('details'));self.assertNotIn('open',d.attrib)
            self.assertTrue(next(d.iter('summary')).text.startswith('Show the '))
        preview=next(e for e in self.main.iter('pre') if 'venue-sheet' in e.get('class',''))
        self.assertEqual(''.join(preview.itertext()),(ROOT/'downloads/thunder-valley-first-visit.md').read_text())
        self.assertFalse(list(self.main.iter('form'))+list(self.main.iter('input'))+list(self.main.iter('textarea')))
        region=next(e for e in self.main.iter() if e.get('class')=='venue-table')
        self.assertEqual((region.get('role'),region.get('tabindex')),('region','0'))
        self.assertTrue(region.get('aria-label'))
        self.assertIn('tel:+19164089095',self.html)

    def test_navigation_archive_feeds_and_live_inventory_reach_the_guide(self):
        for route in ['/poker/','/poker/library/','/poker/topics/places-to-play/','/poker/topics/tournaments/','/poker/topics/cash-games/','/poker/topics/safer-play/','/poker/first-live-tournament/','/poker/first-live-cash-game/','/poker/choosing-a-tournament/','/poker/registration-and-reentry/','/poker/tournament-trip-budget/','/poker/tournament-checklists/','/poker/live-tournament-guide/','/notes/']:
            self.assertIn('href="'+ROUTE,self.outputs[build.output_path(route)],route)
        for name in ['poker/feed.xml','writing.xml','sitemap.xml']:
            self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path(name)])
        schema=json.loads(re.search(r'type="application/ld\+json">(.*?)</script>',self.html)[1])
        self.assertEqual((schema['@type'],schema['datePublished']),('Article','2026-10-15'))
        targets=check_live.targets();self.assertEqual(len(targets),463)
        for asset in ['assets/poker-venue.css','downloads/thunder-valley-first-visit.md','assets/social/reader-poker-thunder-valley-poker-guide.png']:
            self.assertEqual(targets['/'+asset],(200,(ROOT/asset).read_bytes()))
        for p,v in self.outputs.items():
            if p.suffix=='.html':self.assertEqual('/assets/poker-venue.css?' in v,p==build.output_path(ROUTE))

    def test_all_old_search_headings_survive_and_real_queries_reach_the_guide(self):
        canonical=search_sections.index(self.outputs,self.pages)
        current=search_sections.index(multiway_history.outputs(self.outputs),multiway_history.pages(self.pages))
        old=search_sections.index(history.outputs(self.outputs),self.baseline['pages'])
        old['/poker/library/']=[[a,label.replace('58 free guides','59 free guides')] for a,label in old['/poker/library/']]
        self.assertEqual({p:v for p,v in current.items() if p!=ROUTE},old)
        raw=re.search(r'id="find-section-data">(.*?)</script>',self.outputs[search_sections.PAGE],re.S)[1]
        self.assertLess(len(raw.encode()),60000)
        entry=next(e for e in site_find.entries(ROOT,self.pages) if e['path']==ROUTE)
        code=r'''const assert=require('node:assert/strict'),s=require('./assets/site-find.js');
const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
for(const q of ['Thunder Valley','Thunder Valley poker','Thunder Valley registration'])assert(s.score(d.entry,q)>=1000);
assert.deepEqual(JSON.parse(JSON.stringify(s.decodeSections(d.packed))),d.canonical);
'''
        subprocess.run(['node','-e',code],cwd=ROOT,input=json.dumps({'entry':dict(entry,subjects=' '.join(entry['interests'])),'packed':json.loads(raw),'canonical':canonical}),text=True,check=True)

    def test_every_previous_card_is_unchanged_and_new_card_is_bounded(self):
        for p,d in self.baseline['files'].items():
            if p.startswith('assets/social/'):self.assertEqual(sha256((ROOT/p).read_bytes()).hexdigest(),d,p)
        cards=json.loads((ROOT/'_source/reader-previews.json').read_text())['pages']
        record=cards['poker-thunder-valley-poker-guide'];raw=(ROOT/record['src'].lstrip('/')).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(),record['sha256']);self.assertLess(len(raw),25000)
        self.assertEqual(' '.join(record['layout']['lines']),next(p for p in self.pages if p['path']==ROUTE)['title'])

if __name__=='__main__':unittest.main()
