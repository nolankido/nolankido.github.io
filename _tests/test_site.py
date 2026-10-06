"""Dependency-free content and build regression checks. Run from the repository root."""
import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / '_scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.feed(content)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
    def tags(self, name):
        return [attrs for tag, attrs in self.elements if tag == name]

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = {p: Page(s) for p, s in cls.outputs.items() if p.suffix == '.html'}
        cls.manifest = build.public_pages()

    def test_committed_output_matches_source(self):
        for path, content in self.outputs.items():
            with self.subTest(path=str(path)):
                self.assertEqual((ROOT / path).read_text(encoding='utf-8'), content)

    def test_single_heading_landmarks_and_unique_ids(self):
        for path, page in self.pages.items():
            with self.subTest(path=str(path)):
                for tag in ['h1', 'main', 'title']:
                    self.assertEqual(len(page.tags(tag)), 1, tag)
                ids = [a['id'] for _, a in page.elements if 'id' in a]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(page.tags('html')[0].get('lang'), 'en')
                self.assertTrue(any(a.get('href') == '#main' for a in page.tags('a')))
                self.assertTrue(any(a.get('href') == '/privacy/' for a in page.tags('a')))

    def test_metadata_and_json(self):
        for p in self.manifest:
            path = build.output_path(p['path'])
            page = self.pages[path]
            meta = {a.get('name', a.get('property')): a.get('content') for a in page.tags('meta')}
            self.assertEqual(meta['description'], p['description'])
            self.assertEqual(meta['og:url'], 'https://nolankido.com' + p['path'])
            canonical = [a for a in page.tags('link') if a.get('rel') == 'canonical']
            self.assertEqual(canonical[0]['href'], meta['og:url'])
            schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.outputs[path], re.S)
            self.assertEqual(len(schemas), 1)
            self.assertEqual(json.loads(schemas[0])['url'], meta['og:url'])
            self.assertNotRegex(self.outputs[path], r'\$\{[a-z_]+\}')

    def test_all_internal_links_assets_and_fragments(self):
        for path, page in self.pages.items():
            for tag, attrs in page.elements:
                for key in ['href', 'src']:
                    if key not in attrs:
                        continue
                    url = urlsplit(attrs[key])
                    if url.scheme or url.netloc:
                        continue
                    relative = unquote(url.path)
                    target = (ROOT / relative.lstrip('/')) if relative.startswith('/') else (ROOT / path).parent / relative
                    if not relative:
                        target = ROOT / path
                    if target.is_dir():
                        target = target / 'index.html'
                    with self.subTest(page=str(path), link=attrs[key]):
                        self.assertTrue(target.is_file(), str(target))
                        if url.fragment and target.suffix == '.html':
                            ids = [a.get('id') for _, a in Page(target.read_text()).elements]
                            self.assertIn(url.fragment, ids)

    def test_feed_and_sitemap_agree_with_notes(self):
        notes = [p for p in self.manifest if p.get('note')]
        feed = ET.fromstring(self.outputs[Path('feed.xml')])
        links = [i.findtext('link') for i in feed.findall('./channel/item')]
        self.assertEqual(set(links), {'https://nolankido.com' + p['path'] for p in notes})
        self.assertEqual(len(links), len(notes))
        sitemap = ET.fromstring(self.outputs[Path('sitemap.xml')])
        urls = [e.text for e in sitemap.iter() if e.tag.endswith('}loc')]
        self.assertEqual(set(urls), {'https://nolankido.com' + p['path'] for p in self.manifest if not p.get('noindex')})
        self.assertNotIn('https://nolankido.com/404.html', urls)

    def test_contact_and_data_boundaries(self):
        contact = self.pages[Path('contact/index.html')]
        form = contact.tags('form')[0]
        self.assertEqual(form['action'], 'https://submit-form.com/uPlTgRTAR')
        required = {a['name'] for _, a in contact.elements if 'required' in a}
        self.assertEqual(required, {'name', 'email', 'message'})
        self.assertIn('disabled', contact.tags('fieldset')[0])
        self.assertTrue(any(a.get('id') == 'form-success' and 'hidden' in a for _, a in contact.elements))
        vcard = self.outputs[Path('nolan-kido.vcf')]
        self.assertNotIn('EMAIL', vcard)
        self.assertNotIn('TEL', vcard)
        for path, content in self.outputs.items():
            self.assertNotIn(chr(0x2014), content, str(path))
            self.assertNotRegex(content, r'(?i)(mailto:|-----BEGIN .*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20,})')
        for path, page in self.pages.items():
            scripts = [a['src'] for a in page.tags('script') if 'src' in a]
            self.assertEqual(len(scripts), 1 if path == Path('contact/index.html') else 0)
        js = (ROOT / 'assets/contact.js').read_text()
        for forbidden in ['console.log', 'localStorage', 'sessionStorage']:
            self.assertNotIn(forbidden, js)

    def test_note_transparency(self):
        for p in self.manifest:
            if p.get('note'):
                self.assertIn('Prepared with AI assistance.', self.outputs[build.output_path(p['path'])])

    def test_route_validation(self):
        for route in ['bad', '/../private', '/x?y', '/x#y']:
            with self.assertRaises(ValueError):
                build.output_path(route)
        self.assertEqual(build.output_path('/about/'), Path('about/index.html'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
