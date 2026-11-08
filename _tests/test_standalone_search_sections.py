"""Current section-search coverage for the five verified standalone pages.

Run locally. Fixtures contain only copied public source, public HTML and the
existing offline tools. No network, private drafts or user queries are read.
"""
from collections import Counter
from copy import deepcopy
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import local_laptop_case
import player_find
import player_sitemap
import poker_episode
import poker_standoff_episode
import reply_audit_case
import search_sections
import site_find

PUBLICATIONS = (
    (player_sitemap, player_sitemap.RELATIVE),
    (poker_episode, poker_episode.OUTPUT),
    (poker_standoff_episode, poker_standoff_episode.OUTPUT),
    (local_laptop_case, local_laptop_case.OUTPUT),
    (reply_audit_case, reply_audit_case.OUTPUT),
)
ALLOWED_ROUTES = frozenset({
    '/poker/nolan-kido/',
    '/poker/episodes/portland-meadows-ep1/',
    '/poker/episodes/portland-meadows-standoff/',
    '/technology/local-ai-gaming-laptop/',
    '/technology/review-reply-evidence-audit/',
})
FIND_DATA = re.compile(r'<script type="application/json" id="find-section-data">(.*?)</script>', re.S)
SCHEMA_DATA = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def copy_publication(root, registry, output):
    paths = [registry.SOURCE, output]
    if registry is player_sitemap:
        paths.extend([Path('about/index.html'), Path('poker/index.html')])
    if hasattr(registry, 'TOOL'):
        paths.extend([registry.TOOL, Path('technology/index.html')])
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)


def changed_schema(document, keys, value):
    matches = list(SCHEMA_DATA.finditer(document))
    if len(matches) != 1:
        raise AssertionError('Fixture needs one public schema')
    match = matches[0]
    data = json.loads(match[1])
    target = data
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return document[:match.start(1)] + encoded + document[match.end(1):]


class HeadingInventory(HTMLParser):
    """Independently check destination uniqueness and actual H2 text."""
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.headings = {}
        self.heading = None
        self.parts = []
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids[attrs['id']] += 1
        if tag == 'h2':
            self.heading = attrs.get('id')
            self.parts = []
        if tag == 'br' and self.heading is not None:
            self.parts.append(' ')

    def handle_data(self, data):
        if self.heading is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'h2' and self.heading is not None:
            self.headings[self.heading] = ' '.join(''.join(self.parts).split())
            self.heading = None


class StandaloneSearchSectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.manifest = search_sections.index(cls.outputs, cls.pages)
        cls.complete = search_sections.index(cls.outputs, cls.pages, ROOT)
        cls.cards = player_find.add(ROOT, site_find.entries(ROOT, cls.pages))
        cls.manual_cards = player_find.add(ROOT, [])
        cls.rendered = cls.outputs[search_sections.PAGE]

    def run_node(self, code, data):
        result = subprocess.run(
            ['node', '-e', code], cwd=ROOT, input=json.dumps(data),
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_every_existing_search_card_has_matching_section_coverage(self):
        paths = [card['path'] for card in self.cards]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(set(self.complete), set(paths))
        self.assertEqual({card['path'] for card in self.manual_cards}, ALLOWED_ROUTES)
        self.assertEqual(set(self.complete) - set(self.manifest), ALLOWED_ROUTES)
        self.assertEqual(len(self.complete), len(self.manifest) + len(ALLOWED_ROUTES))
        for path, headings in self.manifest.items():
            self.assertEqual(self.complete[path], headings, path)
        for path in ALLOWED_ROUTES:
            self.assertNotIn(build.output_path(path), self.outputs)
            self.assertTrue(self.complete[path], path)
        excluded = {p['path'] for p in self.pages
                    if p.get('noindex') or p.get('living_well_kind') == 'experiment'}
        self.assertFalse(excluded.intersection(self.complete))

    def test_standalone_labels_are_real_unique_public_heading_targets(self):
        for registry, output in PUBLICATIONS:
            with self.subTest(path=registry.ROUTE):
                document = (ROOT / output).read_text(encoding='utf-8')
                inventory = HeadingInventory(document)
                rows = self.complete[registry.ROUTE]
                self.assertEqual(rows, search_sections.headings(document))
                for anchor, label in rows:
                    self.assertEqual(inventory.ids[anchor], 1, anchor)
                    self.assertEqual(inventory.headings[anchor], label, anchor)

    def test_current_packed_data_decodes_exactly_with_existing_browser_code(self):
        matches = FIND_DATA.findall(self.rendered)
        self.assertEqual(len(matches), 1)
        # Current baseline is 61,975 bytes before the standalone headings.
        # This modern budget does not rewrite the older historical snapshot.
        self.assertLess(len(matches[0].encode('utf-8')), 70000)
        self.run_node('''
const assert = require('node:assert/strict');
const {decodeSections} = require('./assets/site-find.js');
const {packed, expected} = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
assert.deepEqual(JSON.parse(JSON.stringify(decodeSections(packed))), expected);
''', {'packed': json.loads(matches[0]), 'expected': self.complete})
        robots = re.findall(r'<meta name="robots" content="([^"]+)"', self.rendered)
        self.assertEqual(len(robots), 1)
        self.assertEqual({directive.strip() for directive in robots[0].split(',')},
                         {'noindex', 'follow'})

    def test_current_matcher_finds_previously_missing_sections(self):
        rows = [dict(card, searchTitle=card['search_title'],
                     subjects=' '.join(site_find.INTERESTS[k] for k in card['interests']),
                     before=self.manifest.get(card['path'], []),
                     sections=self.complete[card['path']]) for card in self.cards]
        cases = [
            ['form factor', local_laptop_case.ROUTE, 'laptop-hardware'],
            ['invented offer', reply_audit_case.ROUTE, 'reply-audit-boundaries'],
            ['tournament media', player_sitemap.ROUTE, 'creator-introduction-title'],
            ['final round', poker_standoff_episode.ROUTE, 'standoff-format-title'],
            ['money bubble', poker_episode.ROUTE, 'six-four-decision'],
        ]
        self.run_node('''
const assert = require('node:assert/strict');
const {score, matchingSections} = require('./assets/site-find.js');
const {rows, cases} = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
for (const [query, path, anchor] of cases) {
  const row = rows.find(r => r.path === path);
  assert(row, path);
  assert.equal(score({...row, sections: row.before}, query), -1, path);
  assert(score(row, query) >= 0, path);
  assert(matchingSections(row, query).some(section => section[0] === anchor), path);
  const oldMatches = rows.filter(r => score({...r, sections: r.before}, query) >= 0);
  assert(oldMatches.every(r => score(r, query) >= 0), 'Existing result lost: ' + query);
}
for (const query of ['???', 'the and', 'nonexistentfixturewordzz']) {
  assert(rows.every(r => score(r, query) === -1), query);
}
const laptop = rows.find(r => r.path === '/technology/local-ai-gaming-laptop/');
assert(score({...laptop, sections: laptop.before}, 'LM Studio') >= 0);
assert(matchingSections(laptop, 'LM Studio').some(section => section[0] === 'laptop-studio'));
''', {'rows': rows, 'cases': cases})

    def test_two_argument_and_empty_root_calls_do_not_fabricate_publications(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            # An unregistered HTML file is not authority to index its contents.
            draft = root / 'private-draft/index.html'
            draft.parent.mkdir(parents=True)
            draft.write_text('<main><h2 id="draft">Unregistered fixture</h2></main>', encoding='utf-8')
            self.assertEqual(search_sections.index(self.outputs, self.pages, root), self.manifest)
            self.assertEqual(search_sections.index({}, [], root), {})
            plain = {search_sections.PAGE: '<main>Search</main>'}
            first = search_sections.apply(dict(plain), [])
            second = search_sections.apply(dict(plain), [], root)
            self.assertEqual(first, second)

    def test_validation_rejects_missing_or_divergent_public_source(self):
        for registry, output in PUBLICATIONS:
            with self.subTest(path=registry.ROUTE), TemporaryDirectory() as folder:
                root = Path(folder)
                copy_publication(root, registry, output)
                self.assertEqual(set(search_sections.index({}, [], root)), {registry.ROUTE})
                source = root / registry.SOURCE
                original = source.read_text(encoding='utf-8')
                source.unlink()
                with self.assertRaises(ValueError):
                    search_sections.index({}, [], root)
                source.write_text(original + '\n<p>Unpublished fixture change</p>', encoding='utf-8')
                with self.assertRaises(ValueError):
                    search_sections.index({}, [], root)
                source.write_text(original, encoding='utf-8')
                (root / output).unlink()
                with self.assertRaises(ValueError):
                    search_sections.index({}, [], root)

    def test_validation_rejects_noindex_wrong_canonical_identity_and_date(self):
        for registry, output in PUBLICATIONS:
            with TemporaryDirectory() as folder:
                root = Path(folder)
                copy_publication(root, registry, output)
                published = root / output
                original = published.read_text(encoding='utf-8')
                identity = 'about' if registry is player_sitemap else 'author'
                changes = {
                    'noindex': original.replace('</head>', '<meta name="robots" content="noindex,follow"></head>', 1),
                    'canonical': original.replace('rel="canonical" href="' + registry.URL + '"',
                                                  'rel="canonical" href="https://example.invalid/wrong/"', 1),
                    'identity': changed_schema(original, [identity, '@id'], 'https://example.invalid/#someone'),
                    'date': changed_schema(original, ['dateModified'], '2099-01-01'),
                }
                for kind, changed in changes.items():
                    with self.subTest(path=registry.ROUTE, invalid=kind):
                        self.assertNotEqual(changed, original)
                        published.write_text(changed, encoding='utf-8')
                        with self.assertRaises(ValueError):
                            search_sections.index({}, [], root)
                published.write_text(original, encoding='utf-8')
                self.assertEqual(set(search_sections.index({}, [], root)), {registry.ROUTE})

    def test_hidden_and_disclosure_content_is_not_indexed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            copy_publication(root, player_sitemap, player_sitemap.RELATIVE)
            source = root / player_sitemap.SOURCE
            published = root / player_sitemap.RELATIVE
            original = source.read_text(encoding='utf-8')
            supplement = '''
<h2 id="fixture-visible">Visible <em>fixture</em><span hidden>secret</span></h2>
<details open><summary>Open disclosure</summary><h2 id="fixture-answer">Answer fixture</h2></details>
<details><summary>Closed disclosure</summary><h2 id="fixture-closed">Closed fixture</h2></details>
<div hidden><h2 id="fixture-hidden">Hidden fixture</h2></div>
<div aria-hidden="true"><h2 id="fixture-decoration">Decoration fixture</h2></div>
<nav><h2 id="fixture-nav">Navigation fixture</h2></nav>
<h3 id="fixture-minor">Minor heading fixture</h3>
<h2 id="invalid fixture">Invalid anchor fixture</h2>
'''
            replacement = original + supplement
            document = published.read_text(encoding='utf-8').replace(original, replacement, 1)
            document = document.replace('</main>', '</main><h2 id="fixture-outside">Outside fixture</h2>', 1)
            source.write_text(replacement, encoding='utf-8')
            published.write_text(document, encoding='utf-8')
            rows = search_sections.index({}, [], root)[player_sitemap.ROUTE]
            self.assertEqual([row for row in rows if row[0].startswith('fixture-')],
                             [['fixture-visible', 'Visible fixture']])
            self.assertNotIn('invalid fixture', {row[0] for row in rows})

    def test_standalone_heading_text_cannot_escape_json_script(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            copy_publication(root, player_sitemap, player_sitemap.RELATIVE)
            source = root / player_sitemap.SOURCE
            published = root / player_sitemap.RELATIVE
            original = source.read_text(encoding='utf-8')
            label = '</script><script>alert(1)</script>&'
            replacement = original + '<h2 id="fixture-safe">' + escape(label) + '</h2>'
            document = published.read_text(encoding='utf-8').replace(original, replacement, 1)
            source.write_text(replacement, encoding='utf-8')
            published.write_text(document, encoding='utf-8')
            rendered = search_sections.apply({search_sections.PAGE: '<main>Search</main>'}, [], root)
            html = rendered[search_sections.PAGE]
            payload = FIND_DATA.findall(html)
            self.assertEqual(len(payload), 1)
            self.assertEqual(html.count('<script'), 1)
            self.assertNotIn(label, html)
            self.assertIn('\\u003c/script\\u003e', payload[0])
            self.run_node('''
const assert = require('node:assert/strict');
const {decodeSections} = require('./assets/site-find.js');
const {packed, path, label} = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
assert(decodeSections(packed)[path].some(row => row[0] === 'fixture-safe' && row[1] === label));
''', {'packed': json.loads(payload[0]), 'path': player_sitemap.ROUTE, 'label': label})

    def test_duplicate_or_missing_main_and_duplicate_visible_anchor_fail(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            copy_publication(root, player_sitemap, player_sitemap.RELATIVE)
            published = root / player_sitemap.RELATIVE
            original = published.read_text(encoding='utf-8')
            for changed in (
                original.replace('</main>', '<h2 id="player-intro-title">Repeated fixture</h2></main>', 1),
                original.replace('</main>', '</main><main>Extra main fixture</main>', 1),
                re.sub(r'</?main\b[^>]*>', '', original),
            ):
                with self.subTest(change=changed[:80]):
                    self.assertNotEqual(changed, original)
                    published.write_text(changed, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        search_sections.index({}, [], root)

    def test_existing_manifest_and_generated_ownership_cannot_be_overridden(self):
        for path in ALLOWED_ROUTES:
            with self.subTest(path=path, owner='excluded manifest'):
                pages = [*self.pages, {'id': 'fixture-excluded', 'path': path, 'noindex': True}]
                with self.assertRaises(ValueError):
                    search_sections.index(self.outputs, pages, ROOT)
            with self.subTest(path=path, owner='generated output'):
                outputs = {**self.outputs, build.output_path(path): '<main>Generated fixture</main>'}
                with self.assertRaises(ValueError):
                    search_sections.index(outputs, self.pages, ROOT)

    def test_projection_does_not_mutate_inputs_or_publications(self):
        protected = [path for registry, output in PUBLICATIONS for path in (registry.SOURCE, output)]
        protected.extend(Path(path) for path in (
            'sitemap.xml', 'feed.xml', 'writing.xml', 'technology/feed.xml', 'poker/feed.xml',
        ))
        before_files = {path: (ROOT / path).read_bytes() for path in protected}
        before_pages = deepcopy(self.pages)
        before_outputs = dict(self.outputs)
        before_cards = deepcopy(self.cards)
        self.assertEqual(search_sections.index(self.outputs, self.pages, ROOT), self.complete)
        self.assertEqual(self.pages, before_pages)
        self.assertEqual(self.outputs, before_outputs)
        self.assertEqual(player_find.add(ROOT, site_find.entries(ROOT, self.pages)), before_cards)
        for path, content in before_files.items():
            self.assertEqual((ROOT / path).read_bytes(), content, path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
