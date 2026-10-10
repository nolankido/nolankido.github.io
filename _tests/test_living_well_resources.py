"""Discovery catalog, explicit access, preservation, and reader-route regressions."""
from copy import deepcopy
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import living_well as lw
import living_well_resources as resources

class ResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = resources.load(ROOT)
        cls.entries = {e['slug']: e for e in lw.load(ROOT)}
        cls.outputs = build.build_outputs()
        cls.page = cls.outputs[Path('living-well/free-resources/index.html')]

    def test_sixtysix_selections_twelve_complete_collections(self):
        self.assertEqual(len(self.catalog['resources']), 98)
        self.assertEqual(len(self.catalog['shelves']), 16)
        for shelf in self.catalog['shelves']:
            entries = [e for e in self.catalog['resources'] if e['shelf'] == shelf['id']]
            self.assertGreaterEqual(len(entries), 4)
            self.assertIn(shelf['start_id'], {e['id'] for e in entries})
            self.assertIn('id="shelf-' + shelf['id'] + '"', self.page)
        for e in self.catalog['resources']:
            self.assertIn(e['companion'], self.entries)
            self.assertIn('id="' + e['id'] + '"', self.page)
            self.assertIn('href="' + escape(e['entry_url'], quote=True) + '"', self.page)
            original_ids = {item['id'] for item in json.loads((ROOT / '_source/living-well/resources.json').read_text())['resources']}
            self.assertEqual(e['reviewed_on'], '2026-10-09' if e['id'] in original_ids else '2026-10-10')
            self.assertTrue(e['review_scope'])

    def test_access_and_limitations_are_not_hidden_behind_registration(self):
        entries = {e['id']: e for e in self.catalog['resources']}
        self.assertEqual(entries['openai-academy']['access'], 'account')
        self.assertEqual(entries['libby']['access'], 'library')
        self.assertEqual(entries['seek']['access'], 'app')
        self.assertIn('Apps have not been installed', self.page)
        self.assertIn('courses have not been completed', self.page)
        for e in entries.values():
            card = resources.resource_card(e)
            self.assertLess(card.index(escape(e['requirements'])), card.index('<details'))
            self.assertNotIn('<iframe', card)
            self.assertNotIn('target="_blank"', card)
            self.assertIn('Provider details', card)

    def test_four_primary_choices_and_preserved_secondary_routes(self):
        for p in lw.manifest(ROOT):
            nav = lw.section_navigation(p)
            primary = re.search(r'<nav class="subsite-links".*?</nav>', nav).group(0)
            links = re.findall(r'href="([^"]+)"', primary)
            self.assertEqual(links, ['/living-well/what-i-mean-by-living-well/', '/living-well/ideas/', '/living-well/free-resources/', '/living-well/guides/'])
            self.assertIn('aria-label="More Living Well"', nav)
            for route in ['topics', 'worksheets', 'field-notes']:
                self.assertIn('href="/living-well/' + route + '/"', nav)
            self.assertLessEqual(primary.count('aria-current='), 1)

    def test_new_publication_and_honest_revision_dates(self):
        new = {e['slug'] for e in json.loads((ROOT / '_source/living-well/discovery.json').read_text())['entries']} | {e['slug'] for e in json.loads((ROOT / '_source/living-well/expansion.json').read_text())['entries']}
        revised = {'what-i-mean-by-living-well', 'weekly-reset', 'preserve-family-story', 'free-afternoon'}
        for slug, e in self.entries.items():
            expected = '2026-10-10' if e.get('series') == 'technology-for-real-life' else ('2026-10-09' if slug in new else '2026-10-08')
            self.assertEqual(e['published'], expected)
            if slug in revised:
                self.assertEqual(e['updated'], '2026-10-09')
                self.assertTrue(e['revision'])
        self.assertEqual(lw.entry_label(self.entries['spiritual-curiosity-reading-path']), 'Reading path')
        body = self.outputs[Path('living-well/weekly-reset/index.html')]
        self.assertIn('id="part-7"', body)
        self.assertIn('fictional example', body)
        self.assertIn('not a claim about what a particular AI system returned', body)
        for n in range(1, 7):
            self.assertIn('id="part-' + str(n) + '"', body)

    def test_feed_order_and_no_experiment_results(self):
        feed = ET.fromstring(self.outputs[Path('living-well/feed.xml')])
        items = feed.findall('./channel/item')
        dates = [parsedate_to_datetime(e.findtext('pubDate')) for e in items]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertEqual(len(items), 31)
        self.assertEqual(len({e.findtext('guid') for e in items}), 31)
        self.assertIn('No completed personal field notes', self.outputs[Path('living-well/field-notes/index.html')])

    def test_worksheets_readable_without_download_or_javascript(self):
        html = self.outputs[Path('living-well/worksheets/index.html')]
        self.assertEqual(html.count('class="lw-preview" open'), 5)
        self.assertEqual(html.count('Download editable text (.md)'), 5)
        self.assertIn('lw-worksheet-intro', html)
        self.assertEqual(html.count('lw-worksheet-first'), 1)
        self.assertNotIn('<form', html)

    def test_malformed_and_unreviewed_resources_fail_closed(self):
        def bad_catalog(change):
            data = deepcopy(self.catalog)
            change(data)
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                target = root / '_source/living-well/resources.json'
                target.parent.mkdir(parents=True)
                target.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    resources.load(root)
        bad_catalog(lambda d: d['resources'][0].update(entry_url='javascript:alert(1)'))
        bad_catalog(lambda d: d['resources'][0].update(entry_url='https://name:pass@example.com/'))
        bad_catalog(lambda d: d['resources'][0].update(status='candidate'))
        bad_catalog(lambda d: d['resources'][0].update(access='trial'))
        bad_catalog(lambda d: d['resources'][0].update(shelf='absent'))
        bad_catalog(lambda d: d['resources'][1].update(id=d['resources'][0]['id']))
        bad_catalog(lambda d: d['resources'][1].update(entry_url=d['resources'][0]['entry_url']))
        bad_catalog(lambda d: d['shelves'][0].update(start_id='absent'))

    def test_living_well_styles_use_defined_design_tokens(self):
        shared = '\n'.join((ROOT / p).read_text() for p in ['styles.css', 'assets/site.css', 'assets/hubs.css', 'assets/living-well.css'])
        declared = set(re.findall(r'(--[a-zA-Z0-9-]+)\s*:', shared))
        used = set(re.findall(r'var\((--[a-zA-Z0-9-]+)\)', (ROOT / 'assets/living-well.css').read_text()))
        self.assertEqual(used - declared, set())

    def test_resource_text_escaped(self):
        e = deepcopy(self.catalog['resources'][0])
        e['why'] = '<script>alert("not markup")</script>'
        e['title'] = '<b>not markup</b>'
        card = resources.resource_card(e)
        self.assertIn('&lt;script&gt;', card)
        self.assertNotIn('<script>', card)
        self.assertNotIn('<b>not markup</b>', card)

if __name__ == '__main__':
    unittest.main(verbosity=2)
