"""Practical Living Well paths, source boundaries, and unchanged prior readings."""
from html import escape
from pathlib import Path
import hashlib
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import living_well as lw

SLUGS = {
    'technology-for-real-life', 'scattered-notes-to-next-step',
    'shared-plan-people-can-use', 'find-the-document-you-need',
    'rough-idea-to-small-creation', 'make-digital-reading-easier',
    'reflection-with-your-judgment-intact', 'did-the-tool-actually-help',
}
OLD_READING_DIGEST = '79d2ae896b9ac0cdaf5ae2d585b5022107a6477c051a4a83bac5fd0a511ce0bb'

class UtilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = {e['slug']: e for e in lw.load(ROOT)}
        cls.new = {s:e for s,e in cls.entries.items() if e.get('series') == 'technology-for-real-life'}
        cls.outputs = build.build_outputs()

    def test_eight_substantive_guides_with_explicit_outcomes(self):
        self.assertEqual(set(self.new), SLUGS)
        self.assertEqual(len(lw.manifest(ROOT)), 75)
        self.assertEqual(len(self.entries), 34)
        for slug,e in self.new.items():
            with self.subTest(slug=slug):
                self.assertEqual(e['kind'], 'guide')
                self.assertEqual(e['published'], '2026-10-10')
                self.assertEqual(e['evidence_status'], 'worked-guide-not-firsthand-result')
                self.assertTrue(e['outcome'].strip())
                self.assertNotIn('updated', e)
                self.assertGreaterEqual(len(e['sections']), 5)
                text = e['lead'] + ' '.join(' '.join(s['paragraphs']) for s in e['sections'])
                self.assertGreaterEqual(len(re.findall(r'\b[\w\'-]+\b', re.sub('<[^>]+>', ' ', text))), 390)
                self.assertEqual(len(e['related']), 2)
        self.assertEqual(self.new['technology-for-real-life']['format'], 'practice-path')

    def test_hub_and_existing_navigation_reach_every_guide(self):
        hub = self.outputs[Path('living-well/technology-for-real-life/index.html')]
        guides = self.outputs[Path('living-well/guides/index.html')]
        live = check_live.targets()
        for slug,e in self.new.items():
            route = '/living-well/' + slug + '/'
            self.assertIn('href="' + route + '"', guides)
            self.assertIn(route, self.outputs[Path('sitemap.xml')])
            self.assertIn(route, live)
            self.assertIn('href="' + route + '"', self.outputs[Path('living-well/topics')/e['topic']/'index.html'])
            if slug != 'technology-for-real-life':
                self.assertIn('href="' + route + '"', hub)
                self.assertIn('technology-for-real-life', e['related'])
        self.assertLess(guides.index('href="/living-well/technology-for-real-life/"'), guides.index('href="/living-well/meditation-without-buying-a-lifestyle/"'))

    def test_original_twenty_six_readings_are_exactly_preserved(self):
        old = {s:e for s,e in self.entries.items() if s not in SLUGS}
        self.assertEqual(len(old), 26)
        digest = hashlib.sha256(json.dumps(old, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(digest, OLD_READING_DIGEST)
        feed = ET.fromstring(self.outputs[Path('living-well/feed.xml')])
        items = feed.findall('./channel/item')
        self.assertEqual(len(items), 31)
        self.assertEqual(len({i.findtext('guid') for i in items}), 31)
        field = self.outputs[Path('living-well/field-notes/index.html')]
        self.assertIn('No completed personal field notes are published here yet', field)
        self.assertEqual(sum(e['kind'] == 'experiment' for e in self.entries.values()), 3)

    def test_source_scope_is_visible_and_not_an_installation_claim(self):
        for slug,e in self.new.items():
            page = self.outputs[Path('living-well')/slug/'index.html']
            self.assertIn('Prepared with AI assistance', page)
            for s in e.get('sources', []):
                self.assertTrue(s['url'].startswith('https://'))
                self.assertEqual(s['checked'], '2026-10-10')
                self.assertIn('href="' + escape(s['url'], quote=True) + '"', page)
                self.assertIn(escape(s['note']), page)
                self.assertIn('href="#sources-and-context"', page)
            self.assertNotRegex(page, r'<(?:form|input|textarea|iframe)\b')
            self.assertEqual(re.findall(r'<script[^>]+src="([^"]+)"', page), ['https://cloud.umami.is/script.js'])
            self.assertNotIn(chr(0x2014), page)

    def test_illustrative_arithmetic_counts_setup_checking_and_maintenance(self):
        original = 6 * 5
        first_group = 12 + 2 * 5 + 1 * 5 + 3
        later_group = 2 * 5 + 1 * 5 + 3
        self.assertEqual(original, 30)
        self.assertEqual(first_group, original)
        self.assertEqual(later_group, 18)
        self.assertEqual(original - later_group, 12)
        guide = json.dumps(self.new['did-the-tool-actually-help']).lower()
        self.assertIn('illustrative', guide)
        self.assertIn('not measured', guide)

    def test_worksheet_downloads_and_existing_resource_catalog_remain(self):
        for path,content in lw.worksheet_exports().items():
            self.assertEqual(self.outputs[path], content)
            self.assertEqual((ROOT/path).read_text(), content)
        self.assertEqual(len(lw.worksheet_exports()), 5)
        catalog = json.loads((ROOT/'_source/living-well/resources.json').read_text())
        self.assertEqual(len(catalog['resources']), 66)
        self.assertEqual(len(catalog['shelves']), 12)

if __name__ == '__main__':
    unittest.main(verbosity=2)
