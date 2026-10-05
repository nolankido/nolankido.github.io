"""Contracts for the approved editorial design and public resource catalog."""
from pathlib import Path
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
        from html import unescape
        previews = [unescape(v) for v in re.findall(r'<pre>(.*?)</pre>', content, re.S)]
        self.assertEqual(len(previews), 3)
        for (slug, title, description, note), preview in zip(RESOURCES, previews):
            self.assertEqual(preview, (ROOT / 'downloads' / (slug + '.md')).read_text())
            self.assertIn('id="' + slug + '"', content)
            self.assertIn('/notes/' + note + '/', content)

    def test_homepage_uses_real_catalog_counts(self):
        content = build.build_outputs()[Path('index.html')]
        self.assertEqual(content.count('<tr>'), 4)
        self.assertIn('03 notes in the collection', content)
        self.assertIn('03 practical templates', content)
        for section in ['interests', 'selected-notes', 'resources']:
            self.assertIn('id="' + section + '"', content)

    def test_fonts_disclosed_and_contact_script_unchanged(self):
        privacy = build.build_outputs()[Path('privacy/index.html')]
        self.assertIn('Google Fonts', privacy)
        self.assertIn('fallback fonts', privacy)
        import hashlib
        raw = (ROOT / 'assets/contact.js').read_bytes()
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        self.assertEqual(hashlib.sha1(blob).hexdigest(), '78838b313bc176b3c06ef7a9d3070746f5cbcd03')

if __name__ == '__main__':
    unittest.main(verbosity=2)
