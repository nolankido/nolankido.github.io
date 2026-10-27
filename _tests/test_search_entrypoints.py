"""Specific entry copy, truthful previews, and independent original-content integrity."""
from copy import deepcopy
from hashlib import sha256
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import shutil
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import build
import check_live
import presentation
import reader_previews
import search_entrypoints
import search_entry_history as history
import practical_navigation_history
import time_export_history
import poker_titles_history


class SearchEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.baseline = history.baseline()
        cls.entries = search_entrypoints.load(ROOT, cls.pages)
        cls.cards = json.loads((ROOT / reader_previews.SOURCE).read_text())['pages']

    def test_original_source_assets_and_downloads_survive_only_reviewed_export_recovery(self):
        self.assertEqual(len(self.baseline['files']), 220)
        for path, expected in self.baseline['files'].items():
            original=time_export_history.before(path,(ROOT / path).read_bytes())
            self.assertEqual(sha256(original).hexdigest(), expected, path)

    def test_all_original_bodies_survive_only_the_declared_entry_changes(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        self.assertEqual(len(self.baseline['bodies']), 171)
        for path, expected in self.baseline['bodies'].items():
            raw = history.before(path, historical_outputs[Path(path)])
            body = re.search(r'<body\b[^>]*>(.*?)</body>', raw, re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(), expected, path)

    def test_article_words_dates_and_all_five_feeds_survive_only_declared_navigation(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        old = {p['id']: p for p in self.baseline['pages']}
        count = 0
        for p in beginner_history.pages(self.pages):
            raw = historical_outputs[build.output_path(p['path'])]
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', raw)[1])
            if schema['@type'] != 'Article': continue
            count += 1
            self.assertEqual(poker_titles_history.pages([p])[0], old[p['id']], p['id'])
            raw = practical_navigation_history.before(build.output_path(p['path']), raw)
            body = re.search(r'<body\b[^>]*>(.*?)</body>', raw, re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(), self.baseline['bodies'][build.output_path(p['path']).as_posix()])
            self.assertNotIn('image', schema, 'A title card is not a representative article illustration')
        self.assertEqual(count, 90)
        for path, digest in self.baseline['feeds'].items():
            self.assertEqual(sha256(historical_outputs[Path(path)].encode()).hexdigest(), digest, path)

    def test_twelve_hubs_have_matching_visible_and_search_purpose(self):
        self.assertEqual(len(self.entries), 12)
        for p in self.pages:
            raw = self.outputs[build.output_path(p['path'])]
            if p['id'] in self.entries:
                self.assertFalse(p.get('date'))
                self.assertFalse(p.get('noindex'))
                expected_date = {'poker-library': '2026-10-15', 'poker-study': '2026-10-16', 'start-here': '2026-10-19', 'resources': '2026-10-19'}.get(p['id'], '2026-10-12')
                self.assertEqual(p['updated'], expected_date)
                self.assertEqual(raw.count('class="entry-summary"'), 1)
                self.assertIn('<p class="entry-summary">' + escape(p['description']) + '</p>', raw)
                self.assertIn('<h1 class="page-title">' + escape(p['title']) + '</h1>', raw)
                self.assertIn('<title>' + escape(p['seo_title']) + '</title>', raw)
            else:
                self.assertNotIn('class="entry-summary"', raw)
            self.assertEqual('/assets/search-entrypoints.css?' in raw, p['id'] in self.entries)

    def test_every_article_and_three_subject_hubs_have_a_distinct_preview(self):
        cfg = presentation.load(ROOT, self.pages)
        expected = {p['id'] for p in self.pages if reader_previews.eligible(p)}
        self.assertEqual(len(expected), 107)
        self.assertEqual(len(self.cards), 103)
        self.assertTrue(expected <= set(cfg['pages']))
        self.assertEqual(len({cfg['pages'][key]['src'] for key in expected}), len(expected))
        for key, retained in json.loads((ROOT / '_source/presentation.json').read_text())['pages'].items():
            self.assertEqual(cfg['pages'][key], retained)
        home = next(p for p in self.pages if p['id'] == 'home')
        # The later positioning release gives Home its own approved AI card.
        # Keep the full metadata contract, allowing only that URL and alt text.
        expected_home = self.baseline['social']['index.html'].replace(
            'https://nolankido.com/assets/social/nolan-kido.png',
            'https://nolankido.com/assets/social/nolan-kido-ai.png',
        ).replace(
            'Nolan Kido. Build useful things. Make room for a good life. nolankido.com.',
            'Nolan Kido. AI Works Human Decides. Practical AI for real life. nolankido.com.',
        )
        self.assertEqual(presentation.metadata(cfg, home, 'https://nolankido.com'), expected_home)

    def test_card_layout_and_status_match_the_complete_current_title(self):
        by_id = {p['id']: p for p in self.pages}
        total = 0
        for key, record in self.cards.items():
            raw = (ROOT / record['src'].lstrip('/')).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), record['sha256'])
            self.assertLess(len(raw), 25_000)
            total += len(raw)
            self.assertEqual(' '.join(record['layout']['lines']), by_id[key]['title'])
            self.assertEqual(record['path'], by_id[key]['path'])
        # New and deliberately retitled cards each retain the same 25 KB limit.
        added = [self.cards[k] for k in ['poker-tournament-trip-budget', 'poker-thunder-valley-poker-guide', 'poker-limped-multiway-pots', 'poker', 'poker-free-poker-learning-path']]
        added_bytes = sum(len((ROOT / card['src'].lstrip('/')).read_bytes()) for card in added)
        self.assertLess(total - added_bytes, 1_000_000)
        self.assertLess(total, 1_000_000 + len(added) * 25_000)
        experiments = [p for p in self.pages if p.get('living_well_kind') == 'experiment']
        self.assertEqual(len(experiments), 3)
        for p in experiments:
            self.assertIn('PROPOSED EXPERIMENT', self.cards[p['id']]['label'])
            self.assertIn('Proposed experiment:', self.cards[p['id']]['title'])

    def test_stale_title_wrong_scope_and_unreviewed_preview_bytes_are_rejected(self):
        original = json.loads((ROOT / reader_previews.SOURCE).read_text())
        key = next(iter(original['pages']))
        mutations = []
        for field, value in [('title', 'A made-up achievement'), ('path', '/unpublished/'), ('label', 'A COMPLETED EXPERIMENT'),
                             ('sha256', '0' * 64), ('src', '/assets/social/nolan-kido.png')]:
            item = deepcopy(original); item['pages'][key][field] = value; mutations.append(item)
        item = deepcopy(original); item['pages'][key]['layout']['lines'] = ['A truncated title']; mutations.append(item)
        with TemporaryDirectory() as tmp:
            root = Path(tmp); (root / '_source').mkdir()
            shutil.copytree(ROOT / 'assets/social', root / 'assets/social')
            for item in mutations:
                (root / reader_previews.SOURCE).write_text(json.dumps(item))
                with self.assertRaises(ValueError): reader_previews.load(root, self.pages, set())

    def test_entry_policy_does_not_mutate_input_or_republish_an_article(self):
        old = deepcopy(self.baseline['pages'])
        result = search_entrypoints.metadata(old, ROOT)
        self.assertEqual(old, self.baseline['pages'])
        self.assertEqual(history.pages(result), old)
        self.assertIsNot(result, old)
        marked = deepcopy(beginner_history.pages(self.pages)); next(p for p in marked if p['id'] == 'living-well-guides')['date'] = '2026-10-12'
        with self.assertRaises(ValueError): search_entrypoints.load(ROOT, marked)
        with self.assertRaises(ValueError): search_entrypoints.header({'entry_summary': 'One purpose'}, '<section>' + search_entrypoints.BEGIN + '</section>')
        injected = search_entrypoints.header({'entry_summary': '<script>alert(1)</script>'}, '<section></section>')
        self.assertIn('&lt;script&gt;', injected); self.assertNotIn('<script>', injected)

    def test_no_new_runtime_scripts_and_every_new_asset_is_verified_live(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        for path, old_scripts in self.baseline['scripts'].items():
            original=time_export_history.before(path,historical_outputs[Path(path)])
            scripts = re.findall(r'<script[^>]+src="([^"]+)"', original)
            self.assertEqual(scripts, old_scripts, path)
        targets = check_live.targets()
        self.assertIn('/assets/search-entrypoints.css', targets)
        for record in self.cards.values():
            self.assertEqual(targets[record['src']], (200, (ROOT / record['src'].lstrip('/')).read_bytes()))

    def test_integrity_view_keeps_unreviewed_article_changes_detectable(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        path = 'notes/trustworthy-tools/index.html'
        changed = historical_outputs[Path(path)].replace('A claim small enough to check', 'An unsupported new claim', 1)
        raw = history.before(path, changed)
        body = re.search(r'<body\b[^>]*>(.*?)</body>', raw, re.S)[1]
        self.assertNotEqual(sha256(body.encode()).hexdigest(), self.baseline['bodies'][path])


if __name__ == '__main__':
    unittest.main(verbosity=2)
