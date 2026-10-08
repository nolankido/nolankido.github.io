"""Taxonomy integrity, discoverability and privacy regressions."""
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_finder
import poker_library
import poker_resources
import poker_topics
from test_site import Page


class TopicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.guides = poker_library.load(ROOT, cls.pages)
        cls.resources = poker_resources.load(ROOT)
        cls.topics = poker_topics.load(ROOT, cls.pages, cls.guides, cls.resources)
        cls.outputs = build.build_outputs()
        cls.items = poker_finder.entries(ROOT, cls.pages, cls.guides, cls.resources)
        cls.annotated = poker_topics.annotate(cls.items, cls.topics)

    def test_all_guides_have_exactly_one_primary_home(self):
        self.assertEqual(Counter(s for t in self.topics for s in t['primary_guides']),
                         Counter(g['slug'] for g in self.guides))
        self.assertEqual(len(self.topics), 10)
        self.assertGreaterEqual(len(self.guides), 39)

    def test_every_external_resource_is_reachable(self):
        ids = {r['id'] for t in self.topics for r in t['resources']}
        self.assertEqual(ids, {r['id'] for r in self.resources})
        self.assertGreaterEqual(len(ids), 138)
        for t in self.topics:
            self.assertTrue(set(t['featured_resources']) <= {r['id'] for r in t['resources']})
            self.assertGreaterEqual(len(t['steps']), 2)

    def test_annotating_never_changes_existing_source_records(self):
        self.assertEqual(len(self.items), len(self.annotated))
        for before, after in zip(self.items, self.annotated):
            for key, value in before.items():
                if key != 'keywords':
                    self.assertEqual(after[key], value, (before['id'], key))
            self.assertEqual(len(after['topics']), len(set(after['topics'])))
            if before['kind'] in ('resource', 'glossary'):
                self.assertTrue(after['topics'])

    def test_topic_index_and_all_filter_links_exist(self):
        text = self.outputs[Path('poker/topics/index.html')]
        home = self.outputs[Path('poker/index.html')]
        for t in self.topics:
            detail = self.outputs[Path('poker/topics') / t['id'] / 'index.html']
            self.assertIn('id="' + t['id'] + '"', detail)
            self.assertIn('/poker/topics/' + t['id'] + '/', text)
            self.assertIn('/poker/topics/' + t['id'] + '/', home)
            for kind in ('', 'guide', 'resource'):
                self.assertIn(poker_topics.finder_url(t, kind).replace('&', '&amp;'), detail)
        self.assertIn('Topic counts overlap', text)
        self.assertIn('not complete', home)
        self.assertIn('/poker/topics/', self.outputs[Path('sitemap.xml')])

    def test_topic_memberships_match_generated_search_cards(self):
        page = Page(self.outputs[Path('poker/find/index.html')])
        attrs = {a['data-id']: a for _, a in page.elements if 'data-finder-card' in a}
        self.assertEqual(len(attrs), len(self.annotated))
        for item in self.annotated:
            self.assertEqual(set(attrs[item['id']]['data-topics'].split()), set(item['topics']))

    def test_every_guide_has_breadcrumb_and_external_source_return(self):
        for topic in self.topics:
            for slug in topic['primary_guides']:
                page = self.outputs[Path('poker') / slug / 'index.html']
                self.assertIn('aria-label="Breadcrumb"', page)
                self.assertIn('aria-label="Explore this poker subject"', page)
                self.assertIn('/poker/topics/' + topic['id'] + '/', page)
                self.assertIn('topic=' + topic['id'] + '&amp;kind=resource', page)

    def test_primary_navigation_has_one_current_location(self):
        for p in self.pages:
            if not p['path'].startswith('/poker/'):
                continue
            markup = self.outputs[build.output_path(p['path'])]
            nav = re.search(r'<nav class="subsite-links".*?</nav>', markup).group()
            if p.get('poker_guide') or p.get('poker_topic') or p['id'] in ('poker', 'poker-find', 'poker-topics', 'poker-resources', 'poker-library', 'poker-study', 'poker-hand-review'):
                self.assertEqual(nav.count('aria-current='), 1, p['path'])
            self.assertIn('/poker/topics/', nav)

    def test_source_cards_retain_access_and_review_evidence(self):
        for topic in self.topics:
            for r in topic['featured']:
                card = poker_topics.source_card(r)
                for value in (r['access'], r['reviewed_on'], 'Full listing', 'rel="external"'):
                    self.assertIn(value, card)
                self.assertIn('Search index only' if r['review_method'] == 'index' else 'Public page read', card)

    def test_support_is_not_hidden_behind_filters(self):
        for path in ('poker/index.html', 'poker/topics/index.html', 'poker/find/index.html'):
            self.assertIn('/poker/resources/#mental-game', self.outputs[Path(path)])
        safer = next(t for t in self.topics if t['id'] == 'safer-play')
        self.assertIn('ncpg', safer['featured_resources'])

    def test_invalid_references_fail_the_build(self):
        original = json.loads((ROOT / '_source/poker/topics.json').read_text())
        mutations = [
            lambda d: d['entries'][0]['primary_guides'].append('missing-guide'),
            lambda d: d['entries'][0]['primary_guides'].pop(),
            lambda d: d['entries'][0]['resource_categories'].append('unknown'),
            lambda d: d['entries'][0]['featured_resources'].append('missing-source'),
            lambda d: d['entries'][0].update(id='../unsafe'),
            lambda d: d['entries'][1].update(id='learn'),
            lambda d: d['entries'][0]['steps'][0].update(guide='missing-guide'),
            lambda d: d['entries'][0]['overview_routes'].append('/nonexistent/'),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / '_source/poker').mkdir(parents=True)
            for mutate in mutations:
                data = deepcopy(original); mutate(data)
                (root / '_source/poker/topics.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    poker_topics.load(root, self.pages, self.guides, self.resources)

    def test_unknown_glossary_reference_is_rejected(self):
        topics = deepcopy(self.topics)
        topics[0]['glossary_terms'].append('not-a-definition')
        with self.assertRaises(ValueError):
            poker_topics.annotate(self.items, topics)

    def test_generated_home_preserves_legacy_section_anchors(self):
        ids = {a.get('id') for _, a in Page(self.outputs[Path('poker/index.html')]).elements}
        for ident in ('watch', 'study', 'after-play', 'field-guide', 'online-resources',
                      'poker-intro-title', 'player-questions', 'resource-collections-title',
                      'viewer-learning-title', 'poker-stories-title', 'after-play-title',
                      'poker-study-title', 'poker-approach-title', 'poker-connect-title'):
            self.assertIn(ident, ids)

    def test_filter_url_rejects_unknown_source_type(self):
        with self.assertRaises(ValueError):
            poker_topics.finder_url(self.topics[0], 'private')

    def test_no_new_runtime_or_non_poker_asset_injection(self):
        self.assertNotIn('<script', (ROOT / '_source/poker/topics.html').read_text())
        for p in self.pages:
            output = self.outputs[build.output_path(p['path'])]
            self.assertEqual('/assets/poker-topics.css' in output, p['path'].startswith('/poker/'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
