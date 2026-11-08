"""Keep native section arrivals scoped to two source-owned public pages.

These are current build and reader contracts, not frozen whole-page snapshots.
The browser suite measures actual scroll clearance. All fixtures are local.
"""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import build_player_profile as player
import build_reply_audit_case as reply
import check_live
import player_sitemap
import reply_audit_case
from poker_reading import VisibleHeadings


ASSET = Path('assets/standalone-section-arrivals.css')
ASSET_ROUTE = '/' + ASSET.as_posix()
OWNERS = {
    '/poker/nolan-kido/': player,
    '/technology/review-reply-evidence-audit/': reply,
}
REQUIRED_ANCHORS = {
    '/poker/nolan-kido/': {
        'player-intro-title', 'player-record-title', 'player-study-title',
        'player-vlog-title', 'creator-introduction-title', 'player-sources-title',
    },
    '/technology/review-reply-evidence-audit/': {
        'reply-audit-intro', 'reply-audit-cases', 'reply-audit-source',
        'reply-audit-controls', 'reply-audit-boundaries', 'reply-audit-reproduce',
        'reply-audit-human', 'reply-audit-cost', 'reply-audit-conclusion',
    },
}


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.schemas = []
        self.in_schema = False
        self.schema_parts = []
        self.stack = []
        self.heading_ancestors = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.elements.append((tag, values))
        if tag == 'h2' and 'id' in values:
            self.heading_ancestors[values['id']] = {
                name for _, parent in self.stack
                for name in parent.get('class', '').split()
            }
        if tag not in self.VOID:
            self.stack.append((tag, values))
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema_parts = []

    def handle_data(self, text):
        if self.in_schema:
            self.schema_parts.append(text)

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_schema:
            self.schemas.append(json.loads(''.join(self.schema_parts)))
            self.in_schema = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def tags(self, tag):
        return [attrs for name, attrs in self.elements if name == tag]


class StandaloneReaderArrivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / ASSET).read_bytes()
        cls.version = sha256(cls.css).hexdigest()[:12]
        cls.reference = ASSET_ROUTE + '?v=' + cls.version
        cls.documents = {route: module.OUTPUT.read_text(encoding='utf-8')
                         for route, module in OWNERS.items()}
        cls.inventory = check_live.targets()

    def test_current_sources_render_exactly_and_have_registered_public_bytes(self):
        for route, module in OWNERS.items():
            with self.subTest(route=route):
                document = self.documents[route]
                source = module.SOURCE.read_text(encoding='utf-8')
                self.assertEqual(module.render(), document)
                self.assertTrue(source.strip())
                self.assertEqual(document.count(source), 1)
                self.assertEqual(self.inventory[route], (200, document.encode('utf-8')))
                self.assertNotIn(ASSET_ROUTE, source)
        self.assertEqual(self.inventory[ASSET_ROUTE], (200, self.css))

    def test_only_two_public_owners_load_the_unique_content_versioned_stylesheet(self):
        actual_owners = set()
        for route, (status, body) in self.inventory.items():
            if status != 200 or not (route.endswith('/') or route.endswith('.html')):
                continue
            document = body.decode('utf-8')
            references = [attrs for attrs in Document(document).tags('link')
                          if ASSET_ROUTE in attrs.get('href', '')]
            if references:
                actual_owners.add(route)
                self.assertEqual(references, [{'rel': 'stylesheet', 'href': self.reference}], route)
                self.assertEqual(document.count(ASSET_ROUTE), 1, route)
        self.assertEqual(actual_owners, set(OWNERS))
        for path, document in build.build_outputs().items():
            if path.suffix == '.html':
                self.assertNotIn(ASSET_ROUTE, document, path)

    def test_stylesheet_only_offsets_the_intended_native_targets(self):
        css = re.sub(r'/\*.*?\*/', '', self.css.decode('utf-8'), flags=re.S)
        self.assertEqual(css.count('@media'), 1)
        self.assertRegex(css, r'@media\s*\(max-width:\s*\d+px\)')
        blocks = re.findall(r'([^{}]+)\{([^{}]*)\}', css)
        self.assertEqual(len(blocks), 2)
        self.assertIn('scroll-margin-top:', css.split('@media', 1)[0])
        expected_selectors = [
            '.page-poker-player #main',
            '.page-poker-player .article-body h2[id]',
            '.page-poker-player #creator-introduction',
            '.page-review-reply-evidence-audit #main',
            '.page-review-reply-evidence-audit .reply-independent-case h2[id]',
        ]
        for selector, declarations in blocks:
            self.assertCountEqual([part.strip() for part in selector.split(',')], expected_selectors)
            properties = [part.split(':', 1)[0].strip()
                          for part in declarations.split(';') if part.strip()]
            self.assertEqual(properties, ['scroll-margin-top'])
        for token in ('@import', 'url(', '!important', 'scroll-behavior'):
            self.assertNotIn(token, css)

    def test_visible_source_headings_main_and_existing_creator_bookmark_survive(self):
        for route, module in OWNERS.items():
            with self.subTest(route=route):
                document = self.documents[route]
                parsed = Document(document)
                headings = VisibleHeadings(document).headings
                self.assertEqual(headings, VisibleHeadings(module.SOURCE.read_text(encoding='utf-8')).headings)
                identifiers = Counter(attrs['id'] for _, attrs in parsed.elements if 'id' in attrs)
                self.assertTrue(REQUIRED_ANCHORS[route] <= {anchor for anchor, _ in headings})
                for anchor, _ in headings:
                    self.assertEqual(identifiers[anchor], 1, anchor)
                    scope = 'article-body' if module is player else 'reply-independent-case'
                    self.assertIn(scope, parsed.heading_ancestors[anchor], anchor)
                self.assertEqual(parsed.tags('main'), [{'id': 'main', 'class': 'ledger', 'tabindex': '-1'}])
                self.assertEqual(identifiers['main'], 1)
                self.assertIn({'class': 'skip-link', 'href': '#main'}, parsed.tags('a'))
        profile = Document(self.documents['/poker/nolan-kido/'])
        legacy = [(tag, attrs) for tag, attrs in profile.elements
                  if attrs.get('id') == 'creator-introduction']
        self.assertEqual(legacy, [('section', {'id': 'creator-introduction',
                                              'aria-labelledby': 'creator-introduction-title'})])

    def test_current_identity_canonical_and_dates_agree_with_source_registries(self):
        self.assertEqual(player_sitemap.record(ROOT), (player_sitemap.URL, player_sitemap.MODIFIED))
        reply_record = reply_audit_case.record(ROOT)
        self.assertEqual((reply_record['date'], reply_record['updated']), (reply.PUBLISHED, reply.MODIFIED))
        for route, module in OWNERS.items():
            with self.subTest(route=route):
                parsed = Document(self.documents[route])
                canonicals = [attrs['href'] for attrs in parsed.tags('link') if attrs.get('rel') == 'canonical']
                self.assertEqual(canonicals, [module.URL])
                self.assertEqual(len(parsed.schemas), 1)
                schema = parsed.schemas[0]
                self.assertEqual(schema['url'], module.URL)
                self.assertEqual(schema['name'], module.TITLE)
                if module is player:
                    self.assertEqual(schema['@type'], 'WebPage')
                    self.assertEqual(schema['dateModified'], player_sitemap.MODIFIED)
                    self.assertEqual(schema['about']['@id'], player_sitemap.PERSON)
                else:
                    self.assertEqual(schema['@type'], 'Article')
                    self.assertEqual(schema['datePublished'], reply.PUBLISHED)
                    self.assertEqual(schema['dateModified'], reply.MODIFIED)
                    self.assertEqual(schema['author']['@id'], reply.PERSON)

    def test_missing_stylesheet_fails_both_builders_without_writing_outputs(self):
        with TemporaryDirectory() as folder:
            for module in OWNERS.values():
                with self.subTest(builder=module.__name__):
                    before = module.OUTPUT.read_bytes()
                    with patch.object(module, 'ROOT', Path(folder)):
                        with self.assertRaises(OSError):
                            module.render()
                    self.assertEqual(module.OUTPUT.read_bytes(), before)

    def test_inherited_stylesheet_references_are_rejected_instead_of_duplicated(self):
        with TemporaryDirectory() as folder:
            for module, shell_name in ((player, 'HUB'), (reply, 'SHELL')):
                original = getattr(module, shell_name).read_text(encoding='utf-8')
                for href in (ASSET_ROUTE, self.reference, ASSET_ROUTE + '?v=000000000000'):
                    with self.subTest(builder=module.__name__, reference=href):
                        self.assertNotIn(ASSET_ROUTE, original)
                        fixture = Path(folder) / 'shell.html'
                        fixture.write_text(original.replace('</head>',
                            f'<link rel="stylesheet" href="{href}">\n</head>', 1), encoding='utf-8')
                        with patch.object(module, shell_name, fixture):
                            with self.assertRaisesRegex(ValueError, 'inherit.*standalone reader stylesheet'):
                                module.render()

    def test_missing_or_ambiguous_head_rejects_stylesheet_injection(self):
        with TemporaryDirectory() as folder:
            for module, shell_name in ((player, 'HUB'), (reply, 'SHELL')):
                original = getattr(module, shell_name).read_text(encoding='utf-8')
                self.assertEqual(original.count('</head>'), 1)
                for replacement in ('', '</head>\n</head>'):
                    with self.subTest(builder=module.__name__, replacement=replacement):
                        fixture = Path(folder) / 'shell.html'
                        fixture.write_text(original.replace('</head>', replacement), encoding='utf-8')
                        with patch.object(module, shell_name, fixture):
                            with self.assertRaisesRegex(ValueError, 'exactly one'):
                                module.render()

    def test_changed_asset_bytes_produce_a_new_version_without_altering_page_content(self):
        changed = self.css + b'\n/* Local versioning fixture. */\n'
        version = sha256(changed).hexdigest()[:12]
        self.assertNotEqual(version, self.version)
        with TemporaryDirectory() as folder:
            root = Path(folder)
            asset = root / ASSET
            asset.parent.mkdir(parents=True)
            asset.write_bytes(changed)
            for route, module in OWNERS.items():
                with self.subTest(route=route), patch.object(module, 'ROOT', root):
                    rendered = module.render()
                    reference = ASSET_ROUTE + '?v=' + version
                    self.assertEqual(rendered.count(reference), 1)
                    self.assertEqual(rendered.replace(reference, self.reference, 1), self.documents[route])


if __name__ == '__main__':
    unittest.main()
