"""Preflop teaching correctness and independent preservation of all prior content."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import preflop_history as history
from test_viewer_guides import Tags

ROUTE = '/poker/starting-hand-decisions/'
CHECKS = ['features', 'position', 'action', 'price', 'depth', 'effective', 'future', 'record']


def feed_records(xml):
    return {i.findtext('link'): ET.tostring(i, encoding='unicode') for i in ET.fromstring(xml).findall('./channel/item')}


class PreflopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.text = cls.outputs[build.output_path(ROUTE)]
        cls.source = (ROOT / '_source/poker/starting-hand-decisions.html').read_text()
        cls.baseline = json.loads((ROOT / '_tests/preflop-baseline.json').read_text())

    def test_exact_inventory_and_frozen_predecessor_outputs(self):
        b = self.baseline
        self.assertEqual((len(b['pages']), len(b['outputs']), len(b['files'])), (172, 199, 345))
        self.assertEqual(len(self.pages), 173)
        self.assertEqual(history.pages(self.pages), b['pages'])
        outputs = history.outputs(self.outputs)
        self.assertEqual(set(map(str, outputs)), set(b['outputs']))
        for p, raw in outputs.items():
            self.assertEqual(sha256(raw.encode()).hexdigest(), b['outputs'][str(p)], str(p))
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        self.assertEqual(files - set(b['files']), set(history.change()['new_files']))
        self.assertEqual(set(history.change()['new_files']), {'_source/poker/starting-hand-decisions.html', 'assets/social/reader-poker-starting-hand-decisions.png'})
        changed = set()
        for p, digest in b['files'].items():
            raw = (ROOT / p).read_bytes()
            if sha256(raw).hexdigest() != digest: changed.add(p)
            self.assertEqual(sha256(history.before(p, raw)).hexdigest(), digest, p)
        self.assertEqual(changed, {'_source/pages.json', '_source/poker/library.json', '_source/poker/topics.json', '_source/reader-previews.json'})

    def test_all_existing_article_sources_metadata_assets_and_downloads_are_exact(self):
        # Direct hashes, independent of every historical reversal adapter.
        current = {p['id']: p for p in self.pages}
        for old in self.baseline['pages']:
            self.assertEqual(current[old['id']], old)
            path = '_source/' + old['source']
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), self.baseline['files'][path], path)
        for p, digest in self.baseline['files'].items():
            if p.startswith(('assets/', 'downloads/')):
                self.assertEqual(sha256((ROOT / p).read_bytes()).hexdigest(), digest, p)

    def test_existing_catalog_records_and_each_feed_item_survive(self):
        for path, old in self.baseline['catalogs'].items():
            now = json.loads((ROOT / path).read_text())
            if path.endswith('library.json'):
                now['entries'] = [v for v in now['entries'] if v['slug'] != 'starting-hand-decisions']
            else:
                del now['pages']['poker-starting-hand-decisions']
            self.assertEqual(now, old, path)
        for path, old in self.baseline['feed_items'].items():
            now = feed_records(self.outputs[Path(path)])
            self.assertEqual({k: now[k] for k in old}, old, path)
            self.assertEqual(set(now) - set(old), {'https://nolankido.com' + ROUTE} if path in ['poker/feed.xml', 'writing.xml'] else set())

    def test_eight_native_exercises_explain_context_without_prescribing_a_range(self):
        tags = Tags(self.source).items
        questions = [a for tag, a in tags if tag == 'details']
        self.assertEqual([a['id'] for a in questions], ['check-' + c for c in CHECKS])
        self.assertTrue(all('open' not in a for a in questions))
        self.assertEqual(len([a for tag, a in tags if tag == 'h2']), 10)
        for label in CHECKS:
            answer = re.search(r'id="check-' + label + r'".*?<div>(.*?)</div></details>', self.source, re.S)[1]
            self.assertGreater(len(re.sub('<[^>]+>', '', answer).split()), 40, label)
        self.assertGreater(len(re.sub('<[^>]+>', ' ', self.source).split()), 2500)
        for phrase in ['Every scene is fictional', 'No wager, playing account or purchase', 'Prepared with AI assistance',
                       'no prescribed best action', 'everyone has chips left after matching 6', 'fictional no-limit hold\'em cash game',
                       'enters an unopened pot with a raise', 'no form and stores no answers', 'October 14, 2026']:
            self.assertIn(phrase, self.source)
        self.assertNotRegex(self.source, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.source)

    def test_price_depth_and_final_record_arithmetic(self):
        small_call, big_call = 6 - 1, 6 - 2
        pot_before = sum([6, 1, 2]); pot_after = pot_before + big_call
        self.assertEqual((small_call, big_call, pot_before, pot_after), (5, 4, 9, 13))
        self.assertAlmostEqual(100 * big_call / pot_after, 30.8, places=1)
        self.assertEqual([8000 // bb for bb in [200, 400]], [40, 20])
        self.assertEqual([min(80, other) for other in [20, 120]], [20, 80])
        self.assertEqual([stack - 6 for stack in [14, 200]], [8, 194])
        # Final button example: two posted blinds plus the cutoff raise, then our call.
        self.assertEqual(sum([1, 2, 6, 6]), 15)
        self.assertEqual(150 // 2, 75)
        self.assertEqual([min(150, other) // 2 for other in [60, 200, 400]], [30, 75, 75])
        for phrase in ['4/13 is about 30.8%', '8,000 / 200 = 40 BB', '8,000 / 400 = 20 BB',
                       '20 BB effective against the short stack', '80 BB effective against the deeper stack',
                       'has only 8 left', 'has 194', 'pot becomes 15', '150 / 2 = 75 BB',
                       '30 BB against the cutoff; 75 BB against each blind']:
            self.assertIn(phrase, self.source)

    def test_navigation_search_schema_and_exact_live_bytes(self):
        for path in ['poker/first-decisions/index.html', 'poker/free-poker-learning-path/index.html', 'poker/library/index.html',
                     'poker/topics/learn/index.html', 'poker/find/index.html', 'find/index.html', 'notes/index.html', 'sitemap.xml']:
            self.assertIn(ROUTE, self.outputs[Path(path)], path)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.text, re.S)[1])
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-10-14')
        self.assertEqual(schema['author']['name'], 'Nolan Kido')
        self.assertIn('Poker Starting Hands for Beginners', self.text)
        targets = check_live.targets()
        self.assertEqual(targets[ROUTE], (200, self.text.encode()))
        self.assertEqual(targets['/assets/social/reader-poker-starting-hand-decisions.png'][0], 200)
        find = self.outputs[Path('find/index.html')]; prior = history.before('find/index.html', find)
        self.assertLess(len(find.encode()) - len(prior.encode()), 2048)
        payload = lambda s: re.search(r'id="find-section-data">(.*?)</script>', s, re.S)[1]
        self.assertLess(len(payload(find).encode()) - len(payload(prior).encode()), 1024)

    def test_history_rejects_unreviewed_changes(self):
        for path, old, new in [('poker/starting-hand-decisions/index.html', '30.8%', '40%'),
                               ('poker/first-decisions/index.html', '400', '401'),
                               ('_source/pages.json', 'The same cards. A different decision.', 'Invented expertise')]:
            raw = self.outputs[Path(path)] if path in map(str, self.outputs) else (ROOT / path).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertEqual(history.before(path, changed), changed)
            if path == history.OUTPUT: self.assertIn(Path(path), history.outputs({Path(path): changed}))
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id'] == history.ID)['description'] = 'Unsupported claim'
        self.assertEqual(len(history.pages(pages)), 173)
        self.assertEqual(history.before('assets/unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__': unittest.main()
