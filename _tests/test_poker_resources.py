"""Contracts for a reviewed external directory, not endorsements or remote checks."""
from copy import deepcopy
from datetime import date, datetime, timezone
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from test_site import ROOT, Page, build
import poker_resources as resources
import poker_library
import check_live


class ResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = resources.load(ROOT)
        cls.outputs = build.build_outputs()
        cls.content = cls.outputs[Path('poker/resources/index.html')]

    def validate(self, entries, **kwargs):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / '_source/poker/resources.json'
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps({'version': 1, 'entries': entries}))
            return resources.load(root, **kwargs)

    def test_every_resource_has_a_distinct_destination_and_visible_review(self):
        # Counts can shrink when a stale resource is retired.
        self.assertTrue(self.entries)
        self.assertTrue(set(e['category'] for e in self.entries) <= set(resources.CATEGORIES))
        cards = [a for a in Page(self.content).tags('article') if 'data-resource-card' in a]
        self.assertEqual(len(cards), len(self.entries))
        urls = [a['href'] for a in Page(self.content).tags('a') if a.get('rel') == 'external']
        self.assertCountEqual(urls, [e['url'] for e in self.entries])
        for entry in self.entries:
            self.assertIn('id="resource-' + entry['id'] + '"', self.content)
            self.assertIn('Listing reviewed', resources.card(entry))
            self.assertIn(entry['access'], resources.card(entry))
            if entry['review_method'] == 'index':
                self.assertTrue(entry['notes'])
                self.assertIn('Search index only', resources.card(entry))

    def test_existing_guide_and_real_account_catalogues_remain_separate(self):
        indexed = poker_library.load(ROOT, build.public_pages())
        self.assertEqual(len(indexed), len([p for p in build.public_pages() if p.get('poker_guide')]) + 1)
        self.assertNotIn('resources', {entry['slug'] for entry in indexed})
        page = next(p for p in build.public_pages() if p['id'] == 'poker-resources')
        self.assertFalse(page.get('poker_guide'))
        self.assertNotIn('data-library-card', self.content)
        self.assertIn('/poker/resources/', self.outputs[Path('sitemap.xml')])
        for path in ['poker/index.html', 'poker/library/index.html', 'poker/study/index.html']:
            self.assertIn('/poker/resources/', self.outputs[Path(path)])

    def test_invalid_and_unreviewed_records_are_rejected(self):
        bad_changes = [{'id': 'Not a slug'}, {'category': 'made-up'}, {'access': 'All free'},
                       {'level': 'Expert guaranteed'}, {'reviewed_on': 'October 7'},
                       {'reviewed_on': '2026-10-08'}, {'review_method': 'unread'},
                       {'review_method': 'index', 'notes': ''}, {'description': ''},
                       {'notes': 'bad' + chr(0x2014)}, {'private_note': 'must not enter schema'}]
        for change in bad_changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate([{**self.entries[0], **change}], as_of=date(2026, 10, 7))
        with self.assertRaises(ValueError):
            self.validate([])
        with self.assertRaises(TypeError):
            self.validate(self.entries, as_of='2026-10-07')
        future = deepcopy(self.entries[0]); future['reviewed_on'] = '9999-12-31'
        with self.assertRaises(ValueError):
            self.validate([future])

    def test_url_normalization_rejects_duplicates_and_tracking(self):
        first = {**self.entries[0], 'url': 'https://www.example.org/study/'}
        duplicate = {**first, 'id': 'other-record', 'url': 'https://example.org/study#section'}
        with self.assertRaises(ValueError):
            self.validate([first, duplicate])
        with self.assertRaises(ValueError):
            self.validate([self.entries[0], self.entries[0]])
        for url in ['http://example.org/', 'https://user:pass@example.org/', 'https://127.0.0.1/',
                    'https://localhost/', 'https://nolankido.com/poker/', 'javascript:alert(1)',
                    'https://example.org/?utm_source=test', 'https://example.org/?ref=referral',
                    'https://example.org/?affid=4', 'https://example.org/ bad',
                    'https://example.org:9999/', 'https://example.org/\\bad']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                resources.canonical_url(url)
        self.assertEqual(resources.canonical_url('https://www.example.org/search/?q=ICM#part'),
                         'https://example.org/search?q=ICM')

    def test_markup_is_escaped_and_candidates_cannot_add_scripts(self):
        entry = {**self.entries[0], 'title': '<img src=x onerror=alert(1)>',
                 'description': '<script>bad()</script>', 'publisher': 'A & B',
                 'notes': '"quoted" <b>note</b>'}
        self.validate([entry])
        rendered = resources.card(entry)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('A &amp; B', rendered)
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('<img ', rendered)
        self.assertNotIn('<b>', rendered)

    def test_review_queue_is_explicit_deterministic_and_does_not_bump_dates(self):
        samples = [{**self.entries[0], 'id': ident, 'category': category,
                    'reviewed_on': '2026-10-07', 'review_method': method}
                   for ident, category, method in [('index-item', 'rules', 'index'),
                   ('schedule-item', 'events', 'page'), ('math-item', 'math', 'page')]]
        original = deepcopy(samples)
        initial = resources.review_queue(samples, date(2026, 10, 7))
        self.assertEqual({r['id'] for r in initial}, {'index-item'})
        later = resources.review_queue(samples, date(2026, 10, 21))
        self.assertEqual({r['id'] for r in later}, {'index-item', 'schedule-item'})
        self.assertEqual(samples, original)
        self.assertEqual(later, resources.review_queue(samples, date(2026, 10, 21)))
        today = datetime.now(timezone.utc).date().isoformat()
        output = subprocess.check_output(['python', str(ROOT / '_scripts/poker_resources.py'),
                                          '--as-of', today], text=True)
        report = json.loads(output)
        self.assertFalse(report['network_checks_performed'])
        self.assertEqual(report['total'], len(self.entries))

    def test_directory_is_progressive_local_only_and_live_verified(self):
        controls = next(a for _, a in Page(self.content).elements if a.get('id') == 'resource-controls')
        self.assertIn('hidden', controls)
        for a in Page(self.content).tags('article'):
            if 'data-resource-card' in a:
                self.assertNotIn('hidden', a)
        self.assertIn('/assets/poker-resources.js', self.content)
        self.assertIn('/assets/poker-resources.js', check_live.targets())
        self.assertIn('/poker/resources/', check_live.targets())
        for path, content in self.outputs.items():
            if path.suffix == '.html' and path != Path('poker/resources/index.html'):
                self.assertNotIn('/assets/poker-resources.js', content)
        source = (ROOT / 'assets/poker-resources.js').read_text()
        for bad in ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage',
                    'sendBeacon', 'umami', 'pushState', 'replaceState', '.innerHTML']:
            self.assertNotIn(bad, source)
        self.assertNotIn('<iframe', self.content)
        self.assertNotIn('<form', self.content)
        self.assertNotIn('<img', self.content)
        subprocess.run(['node', '--check', str(ROOT / 'assets/poker-resources.js')], check=True)


if __name__ == '__main__':
    unittest.main()
