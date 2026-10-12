"""Reader routes are deliberate curation, not new claims or duplicate articles."""
import choice_history
from copy import deepcopy
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import entrypoints
import check_live

class EntryPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.by_path = {p['path']: p for p in cls.pages}
        cls.config = entrypoints.load(ROOT, cls.pages)
        cls.outputs = build.build_outputs()

    def validate(self, config, pages=None):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); (root / '_source').mkdir()
            (root / '_source/entrypoints.json').write_text(json.dumps(config), encoding='utf-8')
            return entrypoints.load(root, self.pages if pages is None else pages)

    def test_four_interest_routes_come_before_optional_reading(self):
        page = self.outputs[Path('start-here/index.html')]
        self.assertEqual(page.count('class="entry-card"'), 4)
        self.assertEqual(page.count('class="identity-reading"'), 3)
        self.assertLess(page.index('id="start-routes-title"'), page.index('id="start-reading-title"'))
        last = 0
        for group in self.config['interests']:
            position = page.index('id="start-' + group['id'] + '"')
            self.assertGreater(position, last); last = position
            for path in group['paths']:
                self.assertIn('href="' + path + '"', page)
                self.assertIn(escape(self.by_path[path]['title']), page)
        for anchor in ['start-intro-title', 'start-routes-title', 'start-reading-title', 'reading-this-site']:
            self.assertIn('id="' + anchor + '"', page)
        self.assertIn('plans, not completed results', page)

    def test_resource_routes_are_labelled_and_original_worksheets_stay_reachable(self):
        page = self.outputs[Path('resources/index.html')]
        self.assertEqual(page.count('class="entry-card"'), 4)
        self.assertEqual(page.count('class="entry-link-kind"'), 8)
        for group in self.config['resources']:
            self.assertIn('href="#resources-' + group['id'] + '"', page)
            for item in group['links']:
                self.assertIn(escape(item['kind']), page)
                self.assertIn(escape(self.by_path[item['path']]['title']), page)
        self.assertIn('These three worksheets need no account.', page)
        self.assertNotIn('Nothing here needs an account.', page)
        for slug in ['decision-record', 'tool-trust-check', 'learning-loop']:
            self.assertIn('id="' + slug + '"', page)
            self.assertIn('href="/downloads/' + slug + '.md"', page)
        self.assertIn('href="#thinking-worksheets"', page)
        self.assertIn('id="thinking-worksheets"', page)
        self.assertIn('other people', page)

    def test_home_and_subject_pages_link_to_the_actual_resource_sections(self):
        self.assertIn('href="/resources/">find a useful resource', self.outputs[Path('index.html')])
        for path, anchor in [('technology/index.html', 'technology'), ('creative/index.html', 'creative')]:
            self.assertIn('href="/resources/#resources-' + anchor + '"', self.outputs[Path(path)])

    def test_every_note_has_two_contextual_next_readings_without_self_links(self):
        for page in self.pages:
            block = entrypoints.next_reading(self.config, self.pages, page)
            if not page.get('note'):
                self.assertEqual(block, ''); continue
            self.assertEqual(block.count('class="reader-next-item"'), 2)
            self.assertNotIn('href="' + page['path'] + '"', block)
            content = self.outputs[build.output_path(page['path'])]
            self.assertEqual(content.count('id="reader-next-title"'), 1)
            self.assertLess(content.index('id="about-this-essay"'), content.index('id="reader-next-title"'))
            for item in self.config['next_reading'][page['id']]:
                target = self.by_path[item['path']]
                self.assertIn(escape(item['reason']), block)
                self.assertIn(escape(target['title']), block)
                self.assertIn('datetime="' + target['date'] + '"', block)

    def test_page_scoped_asset_is_versioned_and_verified_live(self):
        sha = hashlib.sha256((ROOT / 'assets/entrypoints.css').read_bytes()).hexdigest()[:12]
        for page in self.pages:
            content = self.outputs[build.output_path(page['path'])]
            should_load = page['id'] in {'start-here', 'resources'} or bool(page.get('note'))
            self.assertEqual('/assets/entrypoints.css?v=' + sha in content, should_load)
        self.assertEqual(check_live.targets()['/assets/entrypoints.css'], (200, (ROOT / 'assets/entrypoints.css').read_bytes()))

    def test_preserved_sources_assets_feeds_and_article_dates(self):
        preserved = json.loads((ROOT / '_tests/entrypoints-baseline.json').read_text())
        for path, digest in preserved['files'].items():
            self.assertEqual(hashlib.sha256(choice_history.read(path)).hexdigest(), digest, path)
        for directory, digest in preserved['collections'].items():
            actual = hashlib.sha256()
            for file in sorted((ROOT / directory).rglob('*')):
                if file.is_file():
                    actual.update(file.relative_to(ROOT).as_posix().encode() + b'\0' + file.read_bytes() + b'\0')
            self.assertEqual(actual.hexdigest(), digest, directory)
        # The note feeds already include each article's original date and GUID.
        items = ET.fromstring(self.outputs[Path('feed.xml')]).findall('./channel/item')
        self.assertEqual(len(items), 6)
        for name in ['feed.xml', 'poker/feed.xml', 'living-well/feed.xml']:
            self.assertEqual(self.outputs[Path(name)], (ROOT / name).read_text())
        for page in self.pages:
            if page.get('note'):
                content = self.outputs[build.output_path(page['path'])]
                self.assertIn((ROOT / '_source' / page['source']).read_text().strip(), content)
                self.assertIn('Published <time datetime="' + page['date'] + '"', content)

    def test_rendering_is_escaped_and_does_not_mutate_sources(self):
        config = deepcopy(self.config); pages = deepcopy(self.pages)
        config['interests'][0]['title'] = '<img src=x onerror=alert(1)>'
        config['resources'][0]['links'][0]['kind'] = '<b>outside</b>'
        config['next_reading']['keep-the-judgment'][0]['reason'] = '<script>alert(1)</script>'
        next(p for p in pages if p['path'] == config['interests'][0]['paths'][0])['title'] = '<svg onload=alert(1)>'
        before = deepcopy((config, pages))
        snippets = [entrypoints.interest_cards(config, pages), entrypoints.resource_cards(config, pages),
                    entrypoints.next_reading(config, pages, next(p for p in pages if p['id'] == 'keep-the-judgment'))]
        for snippet in snippets:
            self.assertNotRegex(snippet, r'<(?:script|svg|img|b)[ >]')
            self.assertIn('&lt;', snippet)
        self.assertEqual((config, pages), before)

    def test_invalid_config_is_rejected_with_value_error(self):
        bad = [None, [], {}, {'interests': [], 'resources': [], 'next_reading': {}}]
        for name, key, value in [('interests', 'paths', '/technology/'), ('resources', 'links', None), ('interests', 'title', 1)]:
            c = deepcopy(self.config); c[name][0][key] = value; bad.append(c)
        c = deepcopy(self.config); c['interests'].reverse(); bad.append(c)
        c = deepcopy(self.config); c['next_reading']['keep-the-judgment'] = []; bad.append(c)
        c = deepcopy(self.config); del c['next_reading']['keep-the-judgment']; bad.append(c)
        c = deepcopy(self.config); c['next_reading']['keep-the-judgment'][0]['reason'] = ''; bad.append(c)
        for config in bad:
            with self.subTest(config=config), self.assertRaises(ValueError): self.validate(config)

    def test_invalid_or_duplicated_destinations_are_rejected(self):
        for path in ['/missing/', '/technology/?q=private', '//example.com/', '/technology/#section',
                     '/private/../about/', 'https://example.com/', '/living-well/notebook-or-ai/', [], None]:
            config = deepcopy(self.config); config['interests'][0]['paths'][0] = path
            with self.subTest(path=path), self.assertRaises(ValueError): self.validate(config)
        for path in ['/notes/keep-the-judgment/', '/technology/', '/living-well/notebook-or-ai/']:
            config = deepcopy(self.config); config['next_reading']['keep-the-judgment'][0]['path'] = path
            with self.assertRaises(ValueError): self.validate(config)
        for group in ['interests', 'resources']:
            config = deepcopy(self.config)
            key = 'paths' if group == 'interests' else 'links'
            config[group][0][key][1] = deepcopy(config[group][0][key][0])
            with self.assertRaises(ValueError): self.validate(config)
        config = deepcopy(self.config)
        config['next_reading']['keep-the-judgment'][1] = deepcopy(config['next_reading']['keep-the-judgment'][0])
        with self.assertRaises(ValueError): self.validate(config)
        pages = deepcopy(self.pages)
        next(p for p in pages if p['path'] == self.config['interests'][0]['paths'][0])['noindex'] = True
        with self.assertRaises(ValueError): self.validate(self.config, pages)

if __name__ == '__main__': unittest.main()
