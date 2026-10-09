"""Search coverage, private-query architecture and independently verified examples."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree as ET
import copy
import hashlib
import re
import unittest
from test_site import ROOT, Page, build
import poker_finder
import poker_library
import poker_resources
import poker_reference
import check_live

NEW = ('poker-math-reference', 'reading-preflop-charts', 'poker-rules-and-fair-play')

class FinderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.resources = poker_resources.load(ROOT)
        cls.guides = poker_library.load(ROOT, cls.pages)
        cls.items = poker_finder.entries(ROOT, cls.pages, cls.guides, cls.resources)
        cls.outputs = build.build_outputs()
        cls.content = cls.outputs[Path('poker/find/index.html')]

    def test_index_is_exactly_the_published_poker_destinations_and_sources(self):
        pages = {p['path'] for p in self.pages if p['path'].startswith('/poker/') and not p.get('noindex') and p['path'] != '/poker/find/'}
        self.assertEqual({i['url'] for i in self.items if i['kind'] == 'guide'}, pages)
        self.assertEqual({i['url'] for i in self.items if i['kind'] == 'resource'}, {e['url'] for e in self.resources})
        definitions = poker_finder.Glossary((ROOT / '_source/poker/glossary.html').read_text()).entries
        self.assertEqual(len(definitions), 48)
        self.assertEqual({i['url'] for i in self.items if i['kind'] == 'glossary'}, {'/poker/glossary/#' + d['id'] for d in definitions})
        self.assertEqual(len(self.items), len(pages) + len(self.resources) + 48)
        self.assertEqual(len({i['id'] for i in self.items}), len(self.items))

    def test_new_pages_are_not_fictional_personal_accounts(self):
        for slug in NEW:
            route = '/poker/' + slug + '/'
            page = next(p for p in self.pages if p['path'] == route)
            self.assertTrue(page['poker_guide'])
            for output in ['poker/library/index.html','poker/resource-collections/index.html','poker/feed.xml','sitemap.xml']:
                self.assertIn(route, self.outputs[Path(output)])
            body = self.outputs[Path('poker') / slug / 'index.html']
            self.assertIn('fictional', body)
            self.assertIn('Prepared with AI assistance.', body)
            self.assertEqual(body.count('class="poker-details viewer-question"'), 3)
        catalog = build.poker_content.load(ROOT)
        self.assertTrue(set(NEW).isdisjoint(e['slug'] for e in catalog['entries']))
        page = next(p for p in self.pages if p['id'] == 'poker-find')
        self.assertFalse(page.get('poker_guide'))

    def test_retrieval_limits_and_notes_follow_the_real_catalogue(self):
        by_id = {e['id']: e for e in self.resources}
        for e in self.items:
            if e['kind'] != 'resource': continue
            r = by_id[e['id'].removeprefix('external-')]
            for key in ('title','description','notes','access'): self.assertEqual(e[key], r[key])
            self.assertEqual(e['reviewed'], r['reviewed_on'])
            self.assertEqual(e['method'], 'Public page read' if r['review_method'] == 'page' else 'Search index only')
        self.assertIn('Search index only', self.content)

    def test_render_escapes_titles_search_text_and_cautions(self):
        items = copy.deepcopy(self.items[:1])
        for key in ('title','description','keywords','notes','meta'):
            items[0][key] = '<img src=x onerror="bad()"> & text'
        rendered = poker_finder.render(items)['poker_finder_cards']
        self.assertNotIn('<img', rendered)
        self.assertIn('&lt;img', rendered)
        self.assertEqual(len(Page(rendered).tags('article')), 1)
        self.assertFalse(Page(rendered).tags('script'))

    def test_finder_assets_are_page_scoped_and_versioned(self):
        for path, text in self.outputs.items():
            if path.suffix != '.html': continue
            self.assertEqual('/assets/poker-finder.js?v=' in text, path == Path('poker/find/index.html'))
            self.assertEqual('/assets/poker-finder.css?v=' in text, path == Path('poker/find/index.html'))
        for asset in ('poker-finder.js','poker-finder.css'):
            digest = hashlib.sha256((ROOT / 'assets' / asset).read_bytes()).hexdigest()[:12]
            self.assertIn('/assets/' + asset + '?v=' + digest, self.content)
            self.assertIn('/assets/' + asset, check_live.targets())
        self.assertIn('/downloads/poker-math-reference.md', check_live.targets())

    def test_no_query_transport_or_client_storage(self):
        js = (ROOT / 'assets/poker-finder.js').read_text()
        for token in ('fetch(', 'XMLHttpRequest', 'WebSocket', 'sendBeacon', 'localStorage', 'sessionStorage',
                      'document.cookie', 'innerHTML', 'outerHTML', 'insertAdjacentHTML', 'eval(', 'new Function',
                      'umami', 'console.'):
            self.assertNotIn(token, js)
        filter_writer = js.split('function saveFilters() {', 1)[1].split('function filtersChanged()', 1)[0]
        self.assertNotIn('input.value', filter_writer)
        self.assertEqual(set(re.findall(r"params.set\('([^']+)'", filter_writer)), {'topic', 'kind', 'free'})
        self.assertNotIn('<form', self.content)
        self.assertIn('maxlength="160"', self.content)
        self.assertIn('<noscript>', self.content)
        self.assertIn('id="finder-controls" class="reader-controls" hidden', self.content)
        self.assertIn('id="finder-support"', self.content)

    def test_navigation_keeps_resource_discovery_on_every_poker_page_only(self):
        for p in self.pages:
            content = self.outputs[build.output_path(p['path'])]
            if p['path'].startswith('/poker/'):
                nav = re.search(r'<nav class="subsite-links".*?</nav>', content).group(0)
                self.assertIn('href="/poker/find/"', nav)
                self.assertIn('href="/poker/resources/"', nav)
            elif p['path'].startswith('/living-well/'):
                self.assertIn('aria-label="Living Well section"', content)
                nav = re.search(r'<nav class="subsite-links".*?</nav>', content).group(0)
                self.assertNotIn('href="/poker/find/"', nav)
                self.assertNotIn('href="/poker/resources/"', nav)
            else:
                self.assertNotIn('subsite-links', content)
        self.assertIn('id="watch"', self.outputs[Path('poker/index.html')])

    def test_reference_fractions_and_download_are_consistent(self):
        expected = [('Quarter pot', Fraction(50,3), 20), ('One-third pot',20,25), ('Half pot',25,Fraction(100,3)),
                    ('Two-thirds pot',Fraction(200,7),40),('Three-quarters pot',30,Fraction(300,7)),
                    ('Pot',Fraction(100,3),50),('One-and-a-half pot',Fraction(75,2),60),('Twice pot',40,Fraction(200,3))]
        self.assertEqual(poker_reference.rows(), expected)
        content = self.outputs[Path('poker/poker-math-reference/index.html')]
        downloaded = self.outputs[Path('downloads/poker-math-reference.md')]
        self.assertEqual(downloaded,(ROOT / 'downloads/poker-math-reference.md').read_text())
        for label, call, bluff in expected:
            self.assertIn(f'<th scope="row">{label}</th><td>{float(call):.2f}%</td><td>{float(bluff):.2f}%</td>',content)
            self.assertIn(f'| {label} | {float(call):.2f}% | {float(bluff):.2f}% |',downloaded)
        pot, bet = 120, 90
        self.assertEqual(Fraction(bet,pot + 2 * bet), Fraction(3,10))
        max_raise = bet + pot + bet + bet
        self.assertEqual(max_raise,390)
        self.assertEqual(Fraction(max_raise, max_raise+pot+bet),Fraction(13,20))
        self.assertEqual(250 + (250-100),400)
        self.assertLess(340-250,250-100)

    def test_hand_classes_by_physical_enumeration(self):
        deck = [(rank, suit) for rank in range(13) for suit in range(4)]
        counts = Counter()
        for a,b in combinations(deck,2):
            high,low=sorted((a[0],b[0]),reverse=True)
            kind='pair' if high==low else 'suited' if a[1]==b[1] else 'offsuit'
            counts[(kind,high,low)] += 1
        self.assertEqual(len(counts),169)
        self.assertEqual(sum(counts.values()),1326)
        self.assertEqual(Counter(key[0] for key in counts),{'pair':13,'suited':78,'offsuit':78})
        for (kind,_,_),count in counts.items(): self.assertEqual(count,{'pair':6,'suited':4,'offsuit':12}[kind])
        self.assertEqual(Fraction(1,2)*4,2)

    def test_invalid_glossary_cannot_silently_create_bad_links(self):
        for source in ('<dl class="poker-glossary"><div id="../x"><dt>A</dt><dd>B</dd></div></dl>',
                       '<dl class="poker-glossary"><div id="ok"><dt>A</dt></div></dl>', ''):
            with self.assertRaises(ValueError): poker_finder.Glossary(source)

if __name__ == '__main__': unittest.main(verbosity=2)
