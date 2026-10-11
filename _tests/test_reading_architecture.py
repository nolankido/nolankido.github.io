"""Cross-site writing is curation, not republishing or invented evidence."""
from copy import deepcopy
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import identity


class ReadingArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.config = identity.load(ROOT, cls.pages)
        cls.outputs = build.build_outputs()

    def validate(self, config, pages=None):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '_source').mkdir()
            (root / '_source/identity.json').write_text(json.dumps(config), encoding='utf-8')
            return identity.load(root, pages if pages is not None else self.pages)

    def test_four_cross_subject_routes_reuse_canonical_readings(self):
        by_path = {p['path']: p for p in self.pages}
        html = self.outputs[Path('notes/index.html')]
        self.assertEqual(html.count('class="section folio-row writing-route"'), 4)
        for route in self.config['reading_routes']:
            self.assertIn('id="' + route['id'] + '"', html)
            self.assertIn('href="#' + route['id'] + '"', html)
            for path in route['paths']:
                self.assertIn('href="' + path + '"', html)
                self.assertIn(escape(by_path[path]['title']), html)
                self.assertIn(escape(by_path[path]['description']), html)
        self.assertIn('id="general-notes"', html)
        for p in self.pages:
            if p.get('note'):
                self.assertIn(p['path'], html)

    def test_curation_does_not_republish_or_change_feed_scope(self):
        original = self.outputs[Path('feed.xml')]
        self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),
                         '9b3e05a7e14db5b1e751d18a7ff0c8cbaf47b7d60453c1e9c43424e8d57e223a')
        for name in ['feed.xml', 'living-well/feed.xml', 'poker/feed.xml']:
            self.assertEqual(self.outputs[Path(name)], (ROOT / name).read_text())
            links = [item.findtext('link') for item in ET.fromstring(self.outputs[Path(name)]).findall('./channel/item')]
            self.assertNotIn('https://nolankido.com/notes/', links)
        self.assertIn('separate feeds', self.outputs[Path('notes/index.html')])

    def test_shared_writing_link_keeps_existing_url_and_primary_navigation(self):
        for path, html in self.outputs.items():
            if path.suffix != '.html':
                continue
            with self.subTest(path=path):
                footer = html.split('<footer>')[1]
                self.assertIn('<a href="/notes/">Writing</a>', footer)
                nav = html.split('<ul class="nav-links">')[1].split('</ul>')[0]
                self.assertEqual(nav.count('<li>'), 6)
        self.assertIn('/notes/#creative', self.outputs[Path('creative/index.html')])
        self.assertIn('/notes/#technology', self.outputs[Path('technology/index.html')])

    def test_creative_practice_is_guidance_not_a_claimed_portfolio(self):
        html = self.outputs[Path('creative/index.html')]
        self.assertIn('not a portfolio of completed personal projects', html)
        for path in ['/living-well/rough-idea-to-small-creation/', '/living-well/preserve-family-story/']:
            self.assertIn('href="' + path + '"', html)
        self.assertNotIn('<iframe', html)
        self.assertNotIn('<form', html)

    def test_rejects_hubs_proposals_unpublished_and_duplicate_routes(self):
        proposals = [p['path'] for p in self.pages if p.get('living_well_kind') == 'experiment']
        self.assertEqual(len(proposals), 3)
        for path in proposals + ['/about/', '/unpublished/', self.config['reading_routes'][0]['paths'][1]]:
            config = deepcopy(self.config)
            config['reading_routes'][0]['paths'][0] = path
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.validate(config)
        config = deepcopy(self.config)
        config['selected'][0]['path'] = '/about/'
        with self.assertRaises(ValueError):
            self.validate(config)
        pages = deepcopy(self.pages)
        next(p for p in pages if p['path'] == self.config['selected'][0]['path'])['noindex'] = True
        with self.assertRaises(ValueError):
            self.validate(self.config, pages)

    def test_invalid_config_fails_with_a_useful_validation_error(self):
        for change in [lambda c: c.update(navigation=None), lambda c: c.update(selected=None),
                       lambda c: c.update(reading_routes=[]),
                       lambda c: c['reading_routes'][0].update(id='../oops'),
                       lambda c: c['reading_routes'][0].update(paths=[None, '/about/']),
                       lambda c: c['reading_routes'][0].update(title=' ')]:
            config = deepcopy(self.config)
            change(config)
            with self.assertRaises(ValueError):
                self.validate(config)

    def test_canonical_text_and_curated_copy_are_escaped_and_not_mutated(self):
        config = deepcopy(self.config)
        pages = deepcopy(self.pages)
        config['reading_routes'][0]['title'] = '<img src=x onerror=alert(1)>'
        path = config['reading_routes'][0]['paths'][0]
        page = next(p for p in pages if p['path'] == path)
        page['title'] = '<script>alert(1)</script>'
        page['description'] = '<iframe src="bad"></iframe>'
        before = deepcopy(pages)
        html = identity.reading_routes(config, pages)
        for element in ['<img', '<script', '<iframe']:
            self.assertNotIn(element, html)
        self.assertIn('&lt;script&gt;', html)
        self.assertEqual(before, pages)
        self.assertNotIn(chr(0x2014), html)


if __name__ == '__main__':
    unittest.main()
