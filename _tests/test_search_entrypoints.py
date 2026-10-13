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
import build
import check_live
import presentation
import reader_previews
import search_entrypoints
import search_entry_history as history
import practical_navigation_history


class SearchEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.baseline = history.baseline()
        cls.entries = search_entrypoints.load(ROOT, cls.pages)
        cls.cards = json.loads((ROOT / reader_previews.SOURCE).read_text())['pages']

    def test_every_original_source_asset_and_download_is_byte_identical(self):
        self.assertEqual(len(self.baseline['files']), 220)
        for path, expected in self.baseline['files'].items():
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), expected, path)

    def test_all_original_bodies_survive_only_the_declared_entry_changes(self):
        self.assertEqual(len(self.baseline['bodies']), 171)
        for path, expected in self.baseline['bodies'].items():
            raw = history.before(path, self.outputs[Path(path)])
            body = re.search(r'<body\b[^>]*>(.*?)</body>', raw, re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(), expected, path)

    def test_article_words_dates_and_all_five_feeds_survive_only_declared_navigation(self):
        old = {p['id']: p for p in self.baseline['pages']}
        count = 0
        for p in self.pages:
            raw = self.outputs[build.output_path(p['path'])]
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', raw)[1])
            if schema['@type'] != 'Article': continue
            count += 1
            self.assertEqual(p, old[p['id']], p['id'])
            raw = practical_navigation_history.before(build.output_path(p['path']), raw)
            body = re.search(r'<body\b[^>]*>(.*?)</body>', raw, re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(), self.baseline['bodies'][build.output_path(p['path']).as_posix()])
            self.assertNotIn('image', schema, 'A title card is not a representative article illustration')
        self.assertEqual(count, 90)
        for path, digest in self.baseline['feeds'].items():
            self.assertEqual(sha256(self.outputs[Path(path)].encode()).hexdigest(), digest, path)

    def test_twelve_hubs_have_matching_visible_and_search_purpose(self):
        self.assertEqual(len(self.entries), 12)
        for p in self.pages:
            raw = self.outputs[build.output_path(p['path'])]
            if p['id'] in self.entries:
                self.assertFalse(p.get('date'))
                self.assertFalse(p.get('noindex'))
                self.assertEqual(p['updated'], '2026-10-12')
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
        self.assertEqual(len(expected), 93)
        self.assertEqual(len(self.cards), 89)
        self.assertTrue(expected <= set(cfg['pages']))
        self.assertEqual(len({cfg['pages'][key]['src'] for key in expected}), len(expected))
        for key, retained in json.loads((ROOT / '_source/presentation.json').read_text())['pages'].items():
            self.assertEqual(cfg['pages'][key], retained)
        home = next(p for p in self.pages if p['id'] == 'home')
        self.assertEqual(presentation.metadata(cfg, home, 'https://nolankido.com'), self.baseline['social']['index.html'])

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
        self.assertLess(total, 1_000_000)
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
        marked = deepcopy(self.pages); next(p for p in marked if p['id'] == 'living-well-guides')['date'] = '2026-10-12'
        with self.assertRaises(ValueError): search_entrypoints.load(ROOT, marked)
        with self.assertRaises(ValueError): search_entrypoints.header({'entry_summary': 'One purpose'}, '<section>' + search_entrypoints.BEGIN + '</section>')
        injected = search_entrypoints.header({'entry_summary': '<script>alert(1)</script>'}, '<section></section>')
        self.assertIn('&lt;script&gt;', injected); self.assertNotIn('<script>', injected)

    def test_no_new_runtime_scripts_and_every_new_asset_is_verified_live(self):
        for path, old_scripts in self.baseline['scripts'].items():
            scripts = re.findall(r'<script[^>]+src="([^"]+)"', self.outputs[Path(path)])
            self.assertEqual(scripts, old_scripts, path)
        targets = check_live.targets()
        self.assertIn('/assets/search-entrypoints.css', targets)
        for record in self.cards.values():
            self.assertEqual(targets[record['src']], (200, (ROOT / record['src'].lstrip('/')).read_bytes()))

    def test_integrity_view_keeps_unreviewed_article_changes_detectable(self):
        path = 'notes/trustworthy-tools/index.html'
        changed = self.outputs[Path(path)].replace('A claim small enough to check', 'An unsupported new claim', 1)
        raw = history.before(path, changed)
        body = re.search(r'<body\b[^>]*>(.*?)</body>', raw, re.S)[1]
        self.assertNotEqual(sha256(body.encode()).hexdigest(), self.baseline['bodies'][path])


if __name__ == '__main__':
    unittest.main(verbosity=2)
