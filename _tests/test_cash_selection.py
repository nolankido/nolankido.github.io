"""Cash reader journeys, task-fit validation and independent accounting checks."""
from copy import deepcopy
from datetime import date
from fractions import Fraction
from hashlib import sha256
from html import escape, unescape
from html.parser import HTMLParser
from itertools import combinations
import json
from pathlib import Path
import tempfile
import unittest
from test_site import ROOT, Page, build
import check_live
import poker_selection

SLUGS = ('first-live-cash-game', 'cash-game-costs', 'cash-game-study-path')

class TableRows(HTMLParser):
    def __init__(self, content):
        super().__init__(); self.rows = []; self.row = None; self.cell = None; self.feed(content)
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        if tag in ('td', 'th'): self.cell = []
    def handle_data(self, value):
        if self.cell is not None: self.cell.append(value)
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(''.join(self.cell)); self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None

class CashSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = build.poker_resources.load(ROOT)
        cls.by_id = {r['id']: r for r in cls.resources}
        cls.data = poker_selection.load(ROOT, cls.resources)
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()

    def check_invalid(self, mutate, *, resource_mutate=None):
        data = deepcopy(self.data); resources = deepcopy(self.resources)
        mutate(data)
        if resource_mutate: resource_mutate(resources)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); target = root / '_source/poker/resource-selection.json'
            target.parent.mkdir(parents=True); target.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                poker_selection.load(root, resources, as_of=date(2026, 10, 8))

    def test_selection_rejects_bad_schema_and_references(self):
        cases = [lambda d: d.update(version=True), lambda d: d.update(edited_on='2027-01-01'),
                 lambda d: d.update(edited_on='2026-02-30'), lambda d: d.update(edited_on='October 8'),
                 lambda d: d.update(entries=[]), lambda d: d['entries'].append(deepcopy(d['entries'][0])),
                 lambda d: d['entries'][0].update(resource_id='missing'),
                 lambda d: d['entries'][0].update(alternative_id='missing'),
                 lambda d: d['entries'][0].update(alternative_id=d['entries'][0]['resource_id']),
                 lambda d: d['entries'][0].update(fits=''), lambda d: d['entries'][0].update(why='x'*241),
                 lambda d: d['entries'][0].update(first_step='line\nbreak'),
                 lambda d: d['entries'][0].update(choose_other='no' + chr(0x2014) + 'dash'),
                 lambda d: d['entries'][0].update(extra='unexpected'), lambda d: d['entries'].pop(0)]
        for mutate in cases:
            with self.subTest(mutate=mutate): self.check_invalid(mutate)

    def test_free_shortlists_cannot_silently_become_paid(self):
        self.check_invalid(lambda d: None, resource_mutate=lambda rs: next(r for r in rs if r['id']=='pot-odds').update(access='Paid'))
        self.assertEqual(len(self.data['entries']), 20)
        for key in ('cash','free'):
            self.assertTrue(all(self.by_id[i]['access']=='Free' for i in poker_selection.SHORTLISTS[key]))

    def test_existing_resource_identity_access_and_reviews_are_unchanged(self):
        # Snapshot of the 145 approved records at baseline 2a625ce, not a new review claim.
        original = [r for r in self.resources if r['id'] != 'stars-live-cash-rules']
        self.assertEqual(len(original),145)
        self.assertEqual(sha256(json.dumps(original,sort_keys=True,ensure_ascii=False).encode()).hexdigest(), 'b80e3f91b32bef0e250dac5bbc362a8032283f244f5ab6a9915e3fbd53164948')
        added=self.by_id['stars-live-cash-rules']
        self.assertEqual(added['url'],'https://www.pokerstarslive.com/poker/cashgamerules/')
        self.assertEqual(added['review_method'],'page')
        self.assertIn('operator',added['notes'])

    def test_shortlists_reuse_canonical_access_cautions_and_review_method(self):
        values=poker_selection.supplement(self.data,self.resources)
        for key,ids in poker_selection.SHORTLISTS.items():
            markup=values['selection_'+key]
            self.assertEqual(len(Page(markup).tags('article')),len(ids))
            for ident in ids:
                r=self.by_id[ident]
                for value in (r['title'],r['url'],r['access'],r['notes'],r['reviewed_on']):
                    self.assertIn(escape(value,quote=True),markup)
        changed=deepcopy(self.resources);next(r for r in changed if r['id']=='equilab').update(review_method='index')
        self.assertIn('Search index only',poker_selection.supplement(self.data,changed)['selection_ranges'])

    def test_plain_text_is_escaped_in_every_editorial_surface(self):
        data=deepcopy(self.data);data['entries'][0]['fits']='<img src=x onerror="attack()">'
        item=data['entries'][0]
        panel=poker_selection.details(item,self.by_id)
        self.assertIn(escape(item['fits']),panel)
        self.assertEqual(Page(panel).tags('img'),[])
        markup=poker_selection.supplement(data,self.resources)['selection_free']
        self.assertEqual(Page(markup).tags('img'),[])

    def test_native_directory_panels_do_not_add_external_destinations(self):
        content=self.outputs[Path('poker/resources/index.html')];page=Page(content)
        panels=[a for a in page.tags('details') if 'resource-selection' in a.get('class','').split()]
        self.assertEqual(len(panels),20)
        self.assertTrue(all('open' not in a for a in panels))
        self.assertCountEqual([a['href'] for a in page.tags('a') if a.get('rel')=='external'],[r['url'] for r in self.resources])
        self.assertIn('listings include task-fit guidance',content)

    def test_finder_enrichment_is_nonmutating_and_source_scoped(self):
        items=[{'id':'external-equilab','kind':'resource','keywords':'ORIGINAL','url':'/unchanged/', 'notes':'same'},
               {'id':'term-equilab','kind':'glossary','keywords':'TERM'},
               {'id':'unrelated','kind':'guide','keywords':'GUIDE'}]
        before=deepcopy(items);out=poker_selection.annotate(items,self.data)
        self.assertEqual(items,before)
        self.assertEqual(out[1:],items[1:]);self.assertEqual(out[0]['notes'],'same')
        self.assertEqual(out[0]['url'],'/unchanged/');self.assertGreater(len(out[0]['keywords']),len('ORIGINAL'))
        finder=self.outputs[Path('poker/find/index.html')]
        note=next(n for n in self.data['entries'] if n['resource_id']=='pio-quick-start')
        self.assertIn(escape(note['first_step'],quote=True),finder)

    def test_all_three_guides_are_in_every_required_discovery_surface(self):
        library=build.poker_library.load(ROOT,self.pages)
        topics=build.poker_topics.load(ROOT,self.pages,library,self.resources)
        cash=next(t for t in topics if t['id']=='cash-games')
        for slug in SLUGS:
            route='/poker/'+slug+'/'
            self.assertIn(slug,cash['primary_guides'])
            self.assertIn(route,check_live.targets())
            for path in ('poker/library/index.html','poker/find/index.html','poker/topics/cash-games/index.html','poker/feed.xml','sitemap.xml'):
                self.assertIn(route,self.outputs[Path(path)],(slug,path))
            page=next(p for p in self.pages if p['path']==route)
            self.assertTrue(page['poker_guide'])
            source=(ROOT/'_source'/page['source']).read_text()
            self.assertGreater(len(source.split()),450)
            self.assertIn('fictional',source.lower());self.assertIn('Prepared with AI assistance',source)
            self.assertNotIn(chr(0x2014),source);self.assertEqual(Page(source).tags('form'),[])

    def test_fee_table_matches_independent_exact_arithmetic(self):
        source=(ROOT/'_source/poker/cash-game-costs.html').read_text()
        rows=TableRows(source).rows[1:]
        self.assertEqual(len(rows),3)
        for row in rows:
            pot=int(row[0]);rake=min(Fraction(pot,20),6);total=rake+1
            self.assertEqual(row[1],f'{rake} + 1 = {total}')
            self.assertEqual(int(row[2]),pot-total)
            self.assertEqual(int(row[3]),5);self.assertEqual(int(row[4]),pot-5)
        self.assertEqual(min(Fraction(120,20),6)+1,7)
        self.assertIn('7 removed, 113 awarded',source)
        self.assertEqual(7*6,42);self.assertEqual(7*2*8,112)
        self.assertIn('<strong>112 per hour</strong>', source)
        for number in (42,-40,-68,-80):self.assertIn(f'<strong>{number}</strong>',source)
        self.assertEqual(260-200-100,-40)
        self.assertEqual(260-200-100-28,-68)
        self.assertEqual(260-200-100-28-12,-80)
        self.assertIn('already reflected',source)

    def test_study_prices_and_blockers_are_independently_correct(self):
        source=(ROOT/'_source/poker/cash-game-study-path.html').read_text()
        self.assertEqual(Fraction(30,60+30+30),Fraction(1,4))
        self.assertIn('25%',source)
        self.assertEqual(round(float(Fraction(30,114))*100,2),26.32)
        self.assertIn('26.32%',source)
        aces=[a for a in ('As','Ah','Ac','Ad') if a not in ('As','Kd')]
        self.assertEqual(len(list(combinations(aces,2))),3)
        self.assertIn('3',source)
        for n in ('one','two','three','four','five'):self.assertIn('id="session-'+n+'"',source)

    def test_worksheet_preview_and_download_are_the_same_blank_file(self):
        sheet=(ROOT/'downloads/poker-cash-study.md').read_text()
        guide=self.outputs[Path('poker/cash-game-study-path/index.html')]
        self.assertIn('<pre>'+escape(sheet)+'</pre>',guide)
        self.assertIn('/downloads/poker-cash-study.md',check_live.targets())
        self.assertNotIn('<form',guide)

    def test_reading_estimates_include_generated_selection_panels(self):
        values=poker_selection.supplement(self.data,self.resources)
        values['poker_cash_study_sheet']=escape((ROOT/'downloads/poker-cash-study.md').read_text())
        for slug in ('choosing-study-tools','cash-game-study-path'):
            source=(ROOT/f'_source/poker/{slug}.html').read_text()
            estimate=build.poker_library.minutes(build.fill(source,values))
            self.assertGreater(estimate,build.poker_library.minutes(source))
            self.assertIn(f'About {estimate} min read',self.outputs[Path('poker')/slug/'index.html'])

    def test_guide_navigation_uses_shared_topics_not_tournament_only_context(self):
        tools=(ROOT/'_source/poker/choosing-study-tools.html').read_text()
        self.assertIn('href="/poker/topics/study/"',tools)
        self.assertNotIn('>Live tournament field guide</a>',tools)
        self.assertIn('id="task-shortlists"',tools)
        self.assertIn('/poker/cash-game-study-path/',self.outputs[Path('poker/index.html')])

if __name__=='__main__': unittest.main()
