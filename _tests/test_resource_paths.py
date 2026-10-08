"""Curated entry paths must stay connected to actual reviewed listings."""
from copy import deepcopy
from html import escape
from pathlib import Path
import json
import unittest
from test_site import ROOT, Page, build
import poker_resources as resources


class ResourcePathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = resources.load(ROOT)
        cls.by_id = {entry['id']: entry for entry in cls.entries}
        cls.output = build.build_outputs()[Path('poker/resources/index.html')]

    def test_six_paths_resolve_to_existing_ids_with_access_labels(self):
        rendered = resources.starting_paths(self.entries)
        self.assertEqual(len(resources.STARTING_PATHS), 6)
        self.assertEqual(len(Page(rendered).tags('article')), 6)
        for title, reason, ids in resources.STARTING_PATHS:
            self.assertTrue(title and reason)
            for ident in ids:
                entry = self.by_id[ident]
                self.assertIn('href="#resource-' + ident + '" data-resource-jump', rendered)
                self.assertIn(escape(entry['title']), rendered)
                self.assertIn('(' + entry['access'] + ')', rendered)
        self.assertNotIn('rel="external"', rendered)
        self.assertIn('not rankings', rendered)
        self.assertTrue(all('open' not in attrs for attrs in Page(rendered).tags('details')))

    def test_missing_duplicate_or_excessive_destinations_fail(self):
        for ids in [('unknown', 'holdem-rules'), ('holdem-rules', 'holdem-rules'),
                    ('holdem-rules',), tuple(list(self.by_id)[:5])]:
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                resources.starting_paths(self.entries, [('A path', 'A reason', ids)])

    def test_path_copy_and_live_metadata_are_escaped_not_duplicated(self):
        entries = deepcopy(self.entries)
        entry = next(e for e in entries if e['id'] == 'holdem-rules')
        entry.update(title='<img src=x onerror=alert(1)>', access='Mixed')
        rendered = resources.starting_paths(entries, [('<b>Title</b>', 'A & B', ('holdem-rules', 'mit-holdem'))])
        for value in ['&lt;b&gt;Title&lt;/b&gt;', 'A &amp; B', '&lt;img', '(Mixed)']:
            self.assertIn(value, rendered)
        for value in ['<img', '<b>Title</b>']:
            self.assertNotIn(value, rendered)

    def test_starting_points_do_not_inflate_the_unique_resource_inventory(self):
        cards = [a for a in Page(self.output).tags('article') if 'data-resource-card' in a]
        urls = [a['href'] for a in Page(self.output).tags('a') if a.get('rel') == 'external']
        self.assertEqual(len(cards), len(self.entries))
        self.assertCountEqual(urls, [e['url'] for e in self.entries])
        for a in Page(self.output).tags('a'):
            if a.get('href', '').startswith('#resource-'):
                self.assertIn(a['href'][len('#resource-'):], self.by_id)
                self.assertIn('data-resource-jump', a)

    def test_search_uses_existing_visible_text_without_duplicate_hidden_summaries(self):
        for entry in self.entries:
            rendered = resources.card(entry)
            self.assertNotIn('data-search=', rendered)
            self.assertIn(escape(entry['description']), rendered)
            if entry['notes']:
                self.assertIn(escape(entry['notes']), rendered)
        source = (ROOT / 'assets/poker-resources.js').read_text()
        self.assertIn('child.textContent', source)
        self.assertNotIn('node.dataset.search', source)

    def test_historical_and_technical_limits_are_visible(self):
        for ident, term in [('andrew-neeme-study', '2020'), ('brad-owen-wpt-vlog', '2024'),
                            ('hpt-rulebooks', '2013'), ('pagat-history', '2005'),
                            ('treys-evaluator', 'not executed'), ('gamcare-support', 'Regional')]:
            self.assertIn(term, self.by_id[ident]['notes'])
        self.assertIn('No binary, installation advice or calculation was tested', self.by_id['pio-quick-start']['notes'])
        self.assertIn('not calculation accuracy', self.by_id['cardplayer-equity']['notes'])

    def test_batch_record_names_only_released_resources_and_explicit_review_scope(self):
        batch = json.loads((ROOT / '_source/poker/RESOURCE_BATCH_003.json').read_text())
        self.assertEqual(len(batch['accepted_ids']), 26)
        self.assertEqual(len(set(batch['accepted_ids'])), 26)
        self.assertTrue(set(batch['accepted_ids']) <= set(self.by_id))
        self.assertFalse(batch['prior_82_rechecked'])
        self.assertFalse(batch['scheduled'])
        self.assertEqual(batch['baseline_resource_count'], 82)
        for ident in batch['accepted_ids']:
            self.assertEqual(self.by_id[ident]['review_method'], 'page')
        for candidate in batch['deferred']:
            self.assertNotIn(candidate['id'], self.by_id)
            self.assertTrue(candidate['reason'])


if __name__ == '__main__':
    unittest.main()
