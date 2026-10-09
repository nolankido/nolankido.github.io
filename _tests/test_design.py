"""Contracts for the preserved visual design and revised public content."""
from pathlib import Path
from html import unescape
import hashlib
import json
import re
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from catalog import RESOURCES
import build

class DesignTests(unittest.TestCase):
    def test_every_generated_page_uses_shared_design(self):
        for path, content in build.build_outputs().items():
            if path.suffix != '.html':
                continue
            with self.subTest(path=path):
                self.assertIn('class="ledger"', content)
                self.assertIn('/resources/', content)
                for font in ['Schibsted+Grotesk', 'Source+Serif+4', 'IBM+Plex+Mono']:
                    self.assertIn(font, content)
                self.assertIn('ledger-20261005', content)
                self.assertNotRegex(content, r'\[(?:City|CITY|Mon|MON|YYYY|N)\b')
                self.assertNotIn('80+ titles', content)

    def test_resource_previews_match_downloads(self):
        content = build.build_outputs()[Path('resources/index.html')]
        previews = [unescape(v) for v in re.findall(r'<pre>(.*?)</pre>', content, re.S)]
        self.assertEqual(len(previews), len(RESOURCES))
        for (slug, title, description, note), preview in zip(RESOURCES, previews):
            self.assertEqual(preview, (ROOT / 'downloads' / (slug + '.md')).read_text())
            self.assertIn('id="' + slug + '"', content)
            self.assertIn('/notes/' + note + '/', content)
            self.assertIn((ROOT / '_source/examples' / (slug + '.html')).read_text(), content)
        self.assertEqual(content.count('class="worked-example"'), len(RESOURCES))
        for label in ['Who it is for:', 'How to use it:', 'When not to use it:']:
            self.assertEqual(content.count(label), len(RESOURCES))

    def test_homepage_is_a_static_destination_selector(self):
        content = build.build_outputs()[Path('index.html')]
        for destination in ['/technology/', '/poker/', '/creative/', '/notes/', '/about/', '/contact/']:
            self.assertIn(destination, content)
        for obsolete in ['stat-strip', 'selected-notes', 'reading-table', 'class="resource-list"', 'featured_note', '<time']:
            self.assertNotIn(obsolete, content)
        self.assertEqual(content.count('class="destination destination-'), 4)
        self.assertLess(content.index('destination-technology'), content.index('destination-poker'))
        self.assertLess(content.index('destination-poker'), content.index('destination-creative'))

    def test_fonts_disclosed_and_reviewed_asset_contracts(self):
        privacy = build.build_outputs()[Path('privacy/index.html')]
        self.assertIn('Google Fonts', privacy)
        self.assertIn('fallback fonts', privacy)
        expected = {'styles.css': 'aa3896d2168bd26cb4d1ac233e71429002bcc1ea', 'assets/site.css': '0f3af161751edadf1e0f552c226484309370dc49', 'assets/contact.js': '65663ddee4a515c63a9f1d7e35e7ef47b3d21f8a'}
        for path, sha in expected.items():
            raw = (ROOT / path).read_bytes()
            blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
            self.assertEqual(hashlib.sha1(blob).hexdigest(), sha, path)

if __name__ == '__main__':
    unittest.main(verbosity=2)
