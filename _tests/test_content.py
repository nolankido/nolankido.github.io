"""Editorial, arithmetic, update-date, and reader-path regression checks."""
from fractions import Fraction
from html import unescape
import json
import hashlib
from pathlib import Path
import re
from statistics import mean, median
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

class ContentTests(unittest.TestCase):
    def test_curated_links_and_archive_cover_published_notes(self):
        outputs = build.build_outputs()
        pages = json.loads((ROOT / '_source/pages.json').read_text())
        selection = json.loads((ROOT / '_source/selection.json').read_text())
        notes = [p for p in pages if p.get('note')]
        self.assertEqual(set(selection['note_order']), {p['id'] for p in notes})
        for p in notes:
            self.assertIn(p['path'], outputs[Path('notes/index.html')])
        self.assertIn('generous-explanations', selection['selected_notes'])
        self.assertIn('finishing-is-a-decision', selection['selected_notes'])
        self.assertIn('I build useful tools, play tournament poker, and explore ideas through writing and visual storytelling.', outputs[Path('index.html')])
        self.assertIn('A simple hello is welcome too.', outputs[Path('contact/index.html')])

    def test_revisions_are_visible_and_machine_readable(self):
        outputs = build.build_outputs()
        pages = json.loads((ROOT / '_source/pages.json').read_text())
        for p in pages:
            if p.get('revision'):
                content = outputs[build.output_path(p['path'])]
                self.assertIn(p['revision'], unescape(content))
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.S).group(1))
                self.assertEqual(schema['dateModified'], p['updated'])
                self.assertEqual(schema['datePublished'], p['date'])
                self.assertIn('article:modified_time', content)
        self.assertEqual(outputs, build.build_outputs(), 'A build must not change dates or output by itself')
        sitemap = ET.fromstring(outputs[Path('sitemap.xml')])
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for item in sitemap.findall('s:url', ns):
            route = item.findtext('s:loc', namespaces=ns).removeprefix('https://nolankido.com')
            p = next(p for p in pages if p['path'] == route)
            self.assertEqual(item.findtext('s:lastmod', namespaces=ns), p.get('updated', p.get('date')))

    def test_worked_arithmetic_and_text_agree(self):
        values = [2, 2, 2, 2, 22]
        self.assertEqual(median(values), 2)
        self.assertEqual(mean(values), 6)
        self.assertEqual(median([2, 4, 6, 8]), 5)
        self.assertEqual(Fraction(40, 100) * 100, 40)
        self.assertEqual(Fraction(30, 100) * 100, 30)
        self.assertEqual(Fraction(1, 2) + Fraction(1, 3), Fraction(5, 6))
        self.assertEqual(Fraction(1, 4) + Fraction(1, 2), Fraction(3, 4))
        self.assertEqual(Fraction(1, 3) + Fraction(1, 6), Fraction(1, 2))
        tool = (ROOT / '_source/notes/trustworthy-tools.html').read_text()
        self.assertIn('<strong>Median:</strong> 2', tool)
        self.assertIn('(2 + 2 + 2 + 2 + 22) / 5 = 6', tool)
        decision = (ROOT / '_source/notes/decision-quality.html').read_text()
        self.assertIn('0.40 × $100 + 0.60 × $0 = $40', decision)
        self.assertIn('30 percent', decision)
        for slug in ['decision-record', 'tool-trust-check', 'learning-loop']:
            self.assertIn('Fictional example', (ROOT / '_source/examples' / (slug + '.html')).read_text())

    def test_no_new_tracking_scripts_and_no_private_worksheet_form(self):
        outputs = build.build_outputs()
        for path, content in outputs.items():
            if path.suffix != '.html':
                continue
            sources = re.findall(r'<script[^>]+src="([^"]+)"', content)
            self.assertEqual(sources, ['/assets/contact.js?v=' + hashlib.sha256((ROOT / 'assets/contact.js').read_bytes()).hexdigest()[:12]] if path == Path('contact/index.html') else [])
        self.assertNotIn('<form', outputs[Path('resources/index.html')])
        self.assertNotIn('reason for contact, and your message', outputs[Path('privacy/index.html')])
        self.assertIn('Topic and additional context are optional.', outputs[Path('privacy/index.html')])

    def test_date_and_route_validation(self):
        for value in ['2026-02-30', '2026-1-5', 'yesterday']:
            with self.assertRaises(ValueError):
                build.date_value(value)
        for route in ['//host/', '/%2e%2e/private/', '/a/../b/', '/a?b', '/a#b', '/_source/']:
            with self.assertRaises(ValueError):
                build.output_path(route)

if __name__ == '__main__':
    unittest.main(verbosity=2)
