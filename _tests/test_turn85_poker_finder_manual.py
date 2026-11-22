"""Turn 85: the standalone 10 BB guide belongs in native, private Poker Find.

One source-validated manual guide, eight visible H2 section destinations,
no exercise spoilers, no invented video, and no extra canonical SEO page.
"""
from pathlib import Path
import json
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import player_find
import poker_finder
import poker_library
import poker_resources
import poker_topics
import poker_selection
import search_sections
import tenbb_companion

ROUTE = tenbb_companion.ROUTE
ID = 'standalone-tenbb'


class Turn85ManualPokerFinder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.guides = poker_library.load(ROOT, cls.pages)
        cls.resources = poker_resources.load(ROOT)
        cls.raw = poker_finder.entries(ROOT, cls.pages, cls.guides, cls.resources)
        cls.topics = poker_topics.load(ROOT, cls.pages, cls.guides, cls.resources)
        cls.index = poker_selection.annotate(
            poker_topics.annotate(cls.raw, cls.topics),
            poker_selection.load(ROOT, cls.resources))
        cls.manual = next(e for e in cls.index if e['id'] == ID)
        cls.html = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        cls.playbook = (ROOT / tenbb_companion.OUTPUT).read_text(encoding='utf-8')

    def test_standalone_guide_is_reused_from_validated_public_identity(self):
        validated = player_find.tenbb_entry(ROOT)
        self.assertIsNotNone(validated)
        items = [e for e in self.index if e['url'] == ROUTE]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], ID)
        for field, other in [('title', 'title'), ('description', 'description'),
                             ('search_title', 'search_title')]:
            self.assertEqual(self.manual[field], validated[other])
        self.assertEqual(self.manual['kind'], 'guide')
        self.assertEqual(self.manual['access'], 'Free')
        self.assertIn('Standalone written tournament guide', self.manual['meta'])
        self.assertIn('not a real-hand solver verdict', self.manual['notes'])
        self.assertIn('No video is required.', self.playbook)

    def test_current_finder_adds_exactly_one_canonical_guide_without_resources_changes(self):
        manifest_urls = {
            p['path'] for p in self.pages
            if p['path'].startswith('/poker/') and not p.get('noindex')
            and p['path'] != '/poker/find/'
        }
        guide_urls = {e['url'] for e in self.raw if e['kind'] == 'guide'}
        resource_urls = {e['url'] for e in self.raw if e['kind'] == 'resource'}
        glossary = [e for e in self.raw if e['kind'] == 'glossary']
        self.assertEqual(guide_urls, manifest_urls | {ROUTE})
        self.assertEqual(resource_urls, {r['url'] for r in self.resources})
        self.assertEqual(len(glossary), 48)
        self.assertEqual(len(guide_urls), 107)
        self.assertEqual(len(self.raw), 301)
        self.assertEqual(len({e['id'] for e in self.raw}), 301)
        self.assertEqual(len({e['url'] for e in self.raw}), 301)

    def test_section_search_uses_only_eight_visible_h2_not_hidden_answers(self):
        expected = search_sections.headings(self.playbook)
        self.assertEqual(len(expected), 8)
        self.assertEqual([(s['anchor'], s['title']) for s in self.manual['sections']],
                         [tuple(row) for row in expected])
        for section in self.manual['sections']:
            self.assertEqual(section['text'], section['title'])
            self.assertNotIn(section['anchor'], {'q1-title', 'q6-title'})
            self.assertNotIn('Show answer and reasoning', section['text'])
            self.assertIn('id="' + section['anchor'] + '"', self.playbook)

    def test_manual_guide_is_searchable_under_tournament_and_strategy_filters(self):
        self.assertEqual(self.manual['topics'], ['tournaments', 'strategy'])
        self.assertIn('10BB', self.manual['keywords'])
        self.assertIn('ICM', self.manual['keywords'])
        self.assertIn('data-finder-card data-id="standalone-tenbb"', self.html)
        self.assertIn('data-topics="tournaments strategy"', self.html)
        self.assertIn('href="/poker/10bb/"', self.html)
        self.assertIn(
            'Eight visible section headings; read full guide for explanations', self.html)
        self.assertEqual(self.html.count('data-id="standalone-tenbb"'), 1)
        self.assertEqual(self.html.count('data-finder-passage data-anchor="six-checks-title"'), 1)

    def test_generated_card_is_exactly_the_current_finder_renderer(self):
        actual_card = poker_finder.render([self.manual])['poker_finder_cards']
        self.assertEqual(self.html.count(actual_card), 1)
        self.assertEqual(actual_card.count('data-finder-passage'), 8)
        self.assertNotIn('id="q1"', actual_card)
        self.assertNotIn('Show answer and reasoning', actual_card)

    def test_builder_reproduces_complete_large_finder_html(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path('poker/find/index.html')], self.html)

    def test_existing_75_guide_library_and_search_disclosure_remain_truthful(self):
        library = (ROOT / 'poker/library/index.html').read_text(encoding='utf-8')
        self.assertEqual(len(re.findall(r'\bdata-library-card\b', library)), 75)
        self.assertIn('All 75 free guides.', library)
        self.assertIn('301 entries available.', self.html)
        self.assertIn('107 on-site pages, 146 external resources and 48 glossary entries.', self.html)
        self.assertIn('The standalone 10 BB Playbook provides its eight visible section headings only',
                      self.html)
        self.assertIn('<meta name="robots" content="noindex, follow">', self.html)
        self.assertNotIn('href="/poker/10bb/"', library[library.index('id="poker-library"'):])

    def test_invalid_manual_publication_fails_closed(self):
        with patch.object(poker_finder.player_find, 'tenbb_entry',
                          side_effect=ValueError('missing required worksheet')):
            with self.assertRaisesRegex(ValueError, 'missing required worksheet'):
                poker_finder.entries(ROOT, self.pages, self.guides, self.resources)

    def test_duplicate_manifest_and_corrupted_headings_are_rejected(self):
        fake = {'id': 'duplicate-tenbb', 'path': ROUTE, 'title': 'Duplicate',
                'description': 'Not an approved publication', 'kicker': 'Poker'}
        with self.assertRaisesRegex(ValueError, 'duplicates manifest'):
            poker_finder.entries(ROOT, [*self.pages, fake], self.guides, self.resources)
        with patch.object(poker_finder.search_sections, 'headings',
                          return_value=[['six-checks-title', 'One heading']]):
            with self.assertRaisesRegex(ValueError, 'headings changed'):
                poker_finder.entries(ROOT, self.pages, self.guides, self.resources)

    def test_offline_browser_checks_real_search_and_both_topic_filters(self):
        browser = (ROOT / '_tests/finder_browser.py').read_text(encoding='utf-8')
        self.assertIn("search.fill('10 BB Playbook')", browser)
        self.assertIn("page.locator('#finder-topic').select_option('tournaments')", browser)
        self.assertIn("page.locator('#finder-topic').select_option('strategy')", browser)
        self.assertIn("page.locator('#finder-kind').select_option('resource')", browser)
        self.assertIn("manual.locator('[data-finder-passage]').count()==8", browser)

    def test_runner_sitemap_scope_and_no_github_actions(self):
        manual_runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn85_poker_finder_manual.py', manual_runner)
        locs = re.findall(r'<loc>([^<]+)</loc>',
                          (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        self.assertEqual((len(locs), len(set(locs))), (230, 230))
        self.assertEqual(locs.count('https://nolankido.com/poker/10bb/'), 1)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            file.is_file() and file.suffix.lower() in ('.yml', '.yaml')
            for file in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
