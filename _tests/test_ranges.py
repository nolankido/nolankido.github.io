"""Beginner range teaching correctness and independent preservation of all prior content."""
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
import ranges_history as history
import betting_history
from test_viewer_guides import Tags, best

ROUTE = '/poker/ranges-for-beginners/'
CHECKS = ['check', 'remove', 'compare', 'equal', 'weight', 'reveal']


def feed_records(xml):
    return {i.findtext('link'): ET.tostring(i, encoding='unicode') for i in ET.fromstring(xml).findall('./channel/item')}


class RangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = betting_history.pages(build.public_pages())
        cls.current_outputs = build.build_outputs()
        cls.outputs = betting_history.outputs(cls.current_outputs)
        cls.text = cls.outputs[build.output_path(ROUTE)]
        cls.source = (ROOT / '_source/poker/ranges-for-beginners.html').read_text()
        cls.baseline = json.loads((ROOT / '_tests/ranges-baseline.json').read_text())

    def test_exact_inventory_and_frozen_predecessor_outputs(self):
        b = self.baseline
        self.assertEqual((len(b['pages']), len(b['outputs']), len(b['files'])), (175, 202, 354))
        self.assertEqual(len(self.pages), 176)
        self.assertEqual(history.pages(self.pages), b['pages'])
        outputs = history.outputs(self.outputs)
        self.assertEqual(set(map(str, outputs)), set(b['outputs']))
        for p, raw in outputs.items():
            self.assertEqual(sha256(raw.encode()).hexdigest(), b['outputs'][str(p)], str(p))
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        files = betting_history.files(files)
        self.assertEqual(files - set(b['files']), set(history.change()['new_files']))
        self.assertEqual(set(history.change()['new_files']), {'_source/poker/ranges-for-beginners.html', 'assets/social/reader-poker-ranges-for-beginners.png'})
        changed = set()
        for p, digest in b['files'].items():
            raw = betting_history.before(p, (ROOT / p).read_bytes())
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
            now = json.loads(betting_history.before(path, (ROOT / path).read_text()))
            if path.endswith('library.json'):
                now['entries'] = [v for v in now['entries'] if v['slug'] != 'ranges-for-beginners']
            else:
                del now['pages']['poker-ranges-for-beginners']
            self.assertEqual(now, old, path)
        for path, old in self.baseline['feed_items'].items():
            now = feed_records(self.outputs[Path(path)])
            self.assertEqual({k: now[k] for k in old}, old, path)
            self.assertEqual(set(now) - set(old), {'https://nolankido.com' + ROUTE} if path in ['poker/feed.xml', 'writing.xml'] else set())

    def test_six_native_exercises_and_accessible_cards(self):
        tags = Tags(self.source).items
        questions = [a for tag, a in tags if tag == 'details']
        self.assertEqual([a['id'] for a in questions], ['check-' + c for c in CHECKS])
        self.assertTrue(all('open' not in a for a in questions))
        self.assertEqual(len([a for tag, a in tags if tag == 'h2']), 8)
        for label in CHECKS:
            answer = re.search(r'id="check-' + label + r'".*?<div>(.*?)</div></details>', self.source, re.S)[1]
            self.assertGreater(len(re.sub('<[^>]+>', '', answer).split()), 40, label)
        cards = [a for _, a in tags if a.get('role') == 'img']
        self.assertEqual(len(cards), 15)
        self.assertTrue(all(' of ' in a.get('aria-label', '') for a in cards))
        self.assertGreater(len(re.sub('<[^>]+>', ' ', self.source).split()), 2200)
        for phrase in ['Every scene is fictional', 'no wager, account or purchase', 'Prepared with AI assistance',
                       'no practice response is stored', 'not a recommended range', 'not Nolan', 'October 14, 2026']:
            self.assertIn(phrase, self.source)
        self.assertNotRegex(self.source, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.source)

    def test_each_exact_hand_and_all_four_comparisons(self):
        examples = {a['data-example']: a for _, a in Tags(self.source).items if 'data-example' in a}
        self.assertEqual(set(examples), {'known', 'aces', 'ace-king', 'nines', 'queen-jack'})
        known=examples['known']; hole=known['data-hole'].split(); board=known['data-board'].split()
        self.assertEqual(best(hole+board),(1,13,12,9,5))
        ranks={'aces':(1,14,13,9,5),'ace-king':(1,13,14,9,5),'nines':(3,9,13,5),'queen-jack':(0,13,12,11,9,5)}
        results=[]
        for name,rank in ranks.items():
            opponent=examples[name]['data-opponent'].split()
            self.assertEqual(len(set(hole+board+opponent)),9,name)
            self.assertEqual(best(opponent+board),rank,name)
            results.append(best(hole+board)>rank)
        self.assertEqual(results,[False,False,False,True])
        for text in ['K-K-Q-9-5','A-A-K-9-5','K-K-A-9-5','9-9-9-K-5','K-Q-J-9-5']:
            self.assertIn(text,self.source)

    def test_physical_exclusions_and_hand_labels_are_not_frequencies(self):
        from itertools import combinations
        known='Kh Qd Ks 9c 5h 3d 2c'.split()
        unseen={r+s for r in '23456789TJQKA' for s in 'cdhs'}-set(known)
        possible={frozenset(h) for h in combinations(sorted(unseen),2)}
        self.assertEqual(len(possible),990)
        for raw in ['Ac Ad','Kc Ah','9h 9d','Qh Jh']:
            self.assertIn(frozenset(raw.split()),possible)
        for raw in ['Ks As','Kh Jd']:
            self.assertNotIn(frozenset(raw.split()),possible)
        for text in ['four exact holdings','not eight cards','one exact two-card combination',
                     'six combinations','sixteen','not an additional known card','A guess']:
            self.assertIn(text,self.source)

    def test_equal_and_half_weights_with_exact_accounting(self):
        from fractions import Fraction as F
        pot,stack,bet=40,100,20
        current,final=pot+bet,pot+2*bet
        self.assertEqual((current,final,stack-bet),(60,80,80))
        self.assertEqual(pot+2*stack,final+2*(stack-bet))
        threshold=F(bet,final);self.assertEqual(threshold,F(1,4))
        equal=[F(1)]*4;half=[F(1),F(1),F(1),F(1,2)]
        equity=lambda w:w[-1]/sum(w)
        self.assertEqual((equity(equal),equity(half)),(F(1,4),F(1,7)))
        self.assertEqual(equity(equal)*final-bet,0)
        self.assertEqual(equity(half)*final-bet,F(-60,7))
        self.assertEqual(equity(equal)*current-(1-equity(equal))*bet,0)
        for text in ['20 / 80 = 25%','0.25 × 80 - 20 = 0','0.25 × 60 - 0.75 × 20 = 0',
                     '0.5 / 3.5 = 1 / 7','-60 / 7','-8.57','including the action history',
                     'do not multiply the same action history','no fees, side pots or tournament-prize effects']:
            self.assertIn(text,self.source)

    def test_navigation_search_schema_and_exact_live_bytes(self):
        for path in ['poker/turn-and-river-decisions/index.html', 'poker/library/index.html',
                     'poker/topics/learn/index.html', 'poker/find/index.html', 'find/index.html', 'notes/index.html', 'sitemap.xml']:
            self.assertIn(ROUTE, self.outputs[Path(path)], path)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.text, re.S)[1])
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-10-14')
        self.assertEqual(schema['author']['name'], 'Nolan Kido')
        self.assertIn('Poker Ranges for Beginners: Explained Practice', self.text)
        targets = check_live.targets()
        self.assertEqual(targets[ROUTE], (200, self.current_outputs[build.output_path(ROUTE)].encode()))
        self.assertEqual(targets['/assets/social/reader-poker-ranges-for-beginners.png'][0], 200)
        find = self.outputs[Path('find/index.html')]; prior = history.before('find/index.html', find)
        self.assertLess(len(find.encode()) - len(prior.encode()), 2048)
        payload = lambda s: re.search(r'id="find-section-data">(.*?)</script>', s, re.S)[1]
        self.assertLess(len(payload(find).encode()) - len(payload(prior).encode()), 1024)

    def test_history_rejects_unreviewed_changes(self):
        for path, old, new in [('poker/ranges-for-beginners/index.html', '20 / 80 = 25%', '20 / 80 = 50%'),
                               ('poker/turn-and-river-decisions/index.html', '12 / 48 = 25%', '12 / 48 = 50%'),
                               ('_source/pages.json', 'Your first poker range.', 'Invented expertise')]:
            raw = self.outputs[Path(path)] if path in map(str, self.outputs) else (ROOT / path).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertEqual(history.before(path, changed), changed)
            if path == history.OUTPUT: self.assertIn(Path(path), history.outputs({Path(path): changed}))
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id'] == history.ID)['description'] = 'Unsupported claim'
        self.assertEqual(len(history.pages(pages)), 176)
        self.assertEqual(history.before('assets/unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__': unittest.main()
