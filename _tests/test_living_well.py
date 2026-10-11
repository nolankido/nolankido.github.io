"""Living Well publishing, reachability, privacy, and editorial-status regressions."""
from html import escape
from pathlib import Path
import json
import hashlib
import re
import sys
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import living_well as lw
import check_live

class LivingWellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = lw.load(ROOT)
        cls.pages = lw.manifest(ROOT)
        cls.outputs = build.build_outputs()

    def test_full_launch_scope_and_substance(self):
        self.assertEqual(len(self.pages), 75)
        self.assertEqual(sum(e['kind'] != 'experiment' for e in self.entries), 31)
        self.assertEqual(sum(e['kind'] == 'experiment' for e in self.entries), 3)
        self.assertEqual({e['topic'] for e in self.entries}, {t[0] for t in lw.TOPICS})
        for e in self.entries:
            text = e['lead'] + ' '.join(' '.join(s['paragraphs']) for s in e['sections']) + e.get('practice', '') + e['question']
            with self.subTest(slug=e['slug']):
                short = e.get('format') == 'short-read'
                self.assertGreaterEqual(len(re.findall(r'\b[\w\'-]+\b', re.sub('<[^>]+>', ' ', text))), 250 if short else 390)
                self.assertGreaterEqual(len(e['sections']), 2 if short else 5)
                self.assertEqual(len(e['related']), 2)

    def test_every_article_reachable_through_kind_and_topic(self):
        for e in self.entries:
            route = lw.PREFIX + e['slug'] + '/'
            hub = {'essay': 'ideas', 'guide': 'guides', 'experiment': 'field-notes'}[e['kind']]
            self.assertIn('href="' + route + '"', self.outputs[Path('living-well/' + hub + '/index.html')])
            self.assertIn('href="' + route + '"', self.outputs[Path('living-well/topics/' + e['topic'] + '/index.html')])
        for p in self.pages:
            self.assertIn(build.output_path(p['path']), self.outputs)
            self.assertIn(p['path'], check_live.targets())

    def test_no_fabricated_results_and_no_new_collection_surface(self):
        field = self.outputs[Path('living-well/field-notes/index.html')]
        self.assertIn('No completed personal field notes are published here yet', field)
        for p in self.pages:
            content = self.outputs[build.output_path(p['path'])]
            self.assertNotRegex(content, r'<(?:form|textarea|iframe)\b')
            scripts = re.findall(r'<script[^>]+src="([^"]+)"', content)
            expected = ['https://cloud.umami.is/script.js']
            if p['path'] == '/living-well/find/':
                expected.insert(0, '/assets/living-well-directory.js?v=' + hashlib.sha256((ROOT / 'assets/living-well-directory.js').read_bytes()).hexdigest()[:12])
                self.assertEqual(len(re.findall('<input ', content)), 1)
                self.assertIn('type="search"', content)
            else:
                self.assertNotIn('<input', content)
            self.assertEqual(scripts, expected)
            if p.get('living_well_entry'):
                self.assertIn('Prepared with AI assistance', content)
                self.assertIn('aria-label="On this page"', content)
        for e in self.entries:
            if e['kind'] == 'experiment':
                self.assertIn('Status: proposed experiment.', self.outputs[Path('living-well/' + e['slug'] + '/index.html')])

    def test_feed_has_only_published_essays_and_guides(self):
        feed = ET.fromstring(self.outputs[Path('living-well/feed.xml')])
        links = [e.findtext('link') for e in feed.findall('./channel/item')]
        expected = {'https://nolankido.com/living-well/' + e['slug'] + '/' for e in self.entries if e['kind'] != 'experiment'}
        self.assertEqual(set(links), expected)
        self.assertEqual(len(links), len(expected))
        self.assertIn('rel="self"', self.outputs[Path('living-well/feed.xml')])

    def test_worksheet_previews_are_exact_and_downloads_checked_live(self):
        body = self.outputs[Path('living-well/worksheets/index.html')]
        for path, content in lw.worksheet_exports().items():
            self.assertIn('<pre>' + escape(content) + '</pre>', body)
            self.assertEqual(self.outputs[path], content)
            self.assertEqual((ROOT / path).read_text(), content)
            self.assertIn('/' + str(path), check_live.targets())
        self.assertEqual(len(re.findall('<pre>', body)), 5)

    def test_article_metadata_and_section_state(self):
        for p in self.pages:
            content = self.outputs[build.output_path(p['path'])]
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.S).group(1))
            self.assertIn('href="/living-well/" aria-current=', content)
            self.assertIn('aria-label="Living Well section"', content)
            if p.get('living_well_entry'):
                self.assertEqual(schema['@type'], 'Article')
                self.assertEqual(schema['datePublished'], p['date'])
                self.assertIn('property="article:published_time"', content)
            self.assertNotIn(chr(0x2014), content)

    def test_four_home_destinations_and_cross_section_links(self):
        home = self.outputs[Path('index.html')]
        markers = ['destination-technology', 'destination-living-well', 'destination-poker', 'destination-creative']
        self.assertEqual([home.index(m) for m in markers], sorted(home.index(m) for m in markers))
        for path in ['technology/index.html', 'notes/index.html', 'resources/index.html']:
            self.assertIn('href="/living-well/', self.outputs[Path(path)])

if __name__ == '__main__':
    unittest.main(verbosity=2)
