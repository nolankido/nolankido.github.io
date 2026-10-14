"""Turn and river teaching correctness and independent preservation of all prior content."""
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
import river_history as history
from test_viewer_guides import Tags, best

ROUTE = '/poker/turn-and-river-decisions/'
CHECKS = ['turn', 'river', 'check', 'ace-high', 'call', 'share']


def feed_records(xml):
    return {i.findtext('link'): ET.tostring(i, encoding='unicode') for i in ET.fromstring(xml).findall('./channel/item')}


class RiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.text = cls.outputs[build.output_path(ROUTE)]
        cls.source = (ROOT / '_source/poker/turn-and-river-decisions.html').read_text()
        cls.baseline = json.loads((ROOT / '_tests/river-baseline.json').read_text())

    def test_exact_inventory_and_frozen_predecessor_outputs(self):
        b = self.baseline
        self.assertEqual((len(b['pages']), len(b['outputs']), len(b['files'])), (174, 201, 349))
        self.assertEqual(len(self.pages), 175)
        self.assertEqual(history.pages(self.pages), b['pages'])
        outputs = history.outputs(self.outputs)
        self.assertEqual(set(map(str, outputs)), set(b['outputs']))
        for p, raw in outputs.items():
            self.assertEqual(sha256(raw.encode()).hexdigest(), b['outputs'][str(p)], str(p))
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        self.assertEqual(files - set(b['files']), set(history.change()['new_files']))
        self.assertEqual(set(history.change()['new_files']), {'_source/poker/turn-and-river-decisions.html', 'assets/social/reader-poker-turn-and-river-decisions.png'})
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
                now['entries'] = [v for v in now['entries'] if v['slug'] != 'turn-and-river-decisions']
            else:
                del now['pages']['poker-turn-and-river-decisions']
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
        self.assertEqual(len(cards), 23)
        self.assertTrue(all(' of ' in a.get('aria-label', '') for a in cards))
        self.assertGreater(len(re.sub('<[^>]+>', ' ', self.source).split()), 2200)
        for phrase in ['Every scene is fictional', 'no wager, account or purchase', 'Prepared with AI assistance',
                       'no answer form and stores no practice responses', 'not a recommended betting strategy',
                       'win or share the pot at showdown', 'October 14, 2026']:
            self.assertIn(phrase, self.source)
        self.assertNotRegex(self.source, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.source)

    def test_all_shown_hands_and_rank_comparisons_by_best_five(self):
        examples = {a['data-example']: a for _, a in Tags(self.source).items if 'data-example' in a}
        self.assertEqual(set(examples), {'turn-pair', 'river-pair', 'ace-high', 'shared-straight'})
        for case in examples.values():
            cards = ' '.join(case.get(k, '') for k in ['data-hole', 'data-opponent', 'data-board', 'data-turn']).split()
            self.assertEqual(len(cards), len(set(cards)))
        case = examples['turn-pair']; hole = case['data-hole'].split(); flop = case['data-board'].split()
        self.assertEqual(best(hole + flop), (1, 11, 12, 7, 2))
        self.assertEqual(best(hole + flop + [case['data-turn']]), (1, 11, 13, 12, 7))
        case = examples['river-pair']; board = case['data-board'].split()
        self.assertEqual(best(hole + board), (1, 11, 13, 12, 8))
        self.assertEqual(sum(c.endswith('h') for c in hole + board), 4)
        self.assertEqual(best('As Qc'.split() + board), (0, 14, 13, 12, 11, 8))
        self.assertEqual(best('Ks Td'.split() + board), (1, 13, 11, 10, 8))
        self.assertGreater(best(hole + board), best('As Qc'.split() + board))
        self.assertLess(best(hole + board), best('Ks Td'.split() + board))
        case = examples['ace-high']; board = case['data-board'].split()
        self.assertEqual(best(case['data-hole'].split() + board), (0, 14, 13, 12, 8, 7))
        self.assertEqual(best(case['data-opponent'].split() + board), (0, 12, 11, 10, 8, 7))
        for phrase in ['J-J-K-Q-7', 'J-J-K-Q-8', 'A-K-Q-J-8', 'K-K-J-T-8', 'A-K-Q-8-7', 'Q-J-T-8-7']:
            self.assertIn(phrase, self.source)

    def test_all_990_legal_opposing_hands_share_the_broadway_board(self):
        from itertools import combinations
        case = next(a for _, a in Tags(self.source).items if a.get('data-example') == 'shared-straight')
        hole = case['data-hole'].split(); board = case['data-board'].split()
        unseen = {r+s for r in '23456789TJQKA' for s in 'cdhs'} - set(hole + board)
        expected = best(hole + board); self.assertEqual(expected, (4, 14))
        comparisons = [best(list(other) + board) for other in combinations(sorted(unseen), 2)]
        self.assertEqual(len(comparisons), 990)
        self.assertTrue(all(value == expected for value in comparisons))
        self.assertIn('Pairs and three of a kind rank below the straight', self.source)
        self.assertIn('Your equity is <strong>50%</strong>', self.source)

    def test_river_call_and_shared_pot_accounting_with_fractional_equity(self):
        from fractions import Fraction
        initial_pot, stack, bet = 24, 60, 12
        current = initial_pot + bet; final = current + bet; remaining = stack - bet
        self.assertEqual((current, final, remaining), (36, 48, 48))
        self.assertEqual(final + 2 * remaining, initial_pot + 2 * stack)
        price = Fraction(bet, final); self.assertEqual(price, Fraction(1, 4))
        self.assertEqual(price * final - bet, 0)
        outright_win, tie = Fraction(0), Fraction(1)
        equity = outright_win + tie / 2
        self.assertEqual(equity, Fraction(1, 2))
        returned = equity * final; gain = returned - bet
        self.assertEqual((returned, gain), (24, 12))
        self.assertEqual(remaining + returned - stack, gain)
        for phrase in ['current pot is 36', 'final pot of 48', 'Each player would have 48',
                       '12 / 48 = 25%', '24 - 12 = 12', 'win or share the pot at showdown',
                       'A call does not ask the bettor to fold', 'there is no sixth',
                       'only when the required action is complete']:
            self.assertIn(phrase.lower(), self.source.lower())

    def test_navigation_search_schema_and_exact_live_bytes(self):
        for path in ['poker/first-flop-decisions/index.html', 'poker/library/index.html',
                     'poker/topics/learn/index.html', 'poker/find/index.html', 'find/index.html', 'notes/index.html', 'sitemap.xml']:
            self.assertIn(ROUTE, self.outputs[Path(path)], path)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.text, re.S)[1])
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-10-14')
        self.assertEqual(schema['author']['name'], 'Nolan Kido')
        self.assertIn('Poker Turn &amp; River: Beginner Decisions &amp; Practice', self.text)
        targets = check_live.targets()
        self.assertEqual(targets[ROUTE], (200, self.text.encode()))
        self.assertEqual(targets['/assets/social/reader-poker-turn-and-river-decisions.png'][0], 200)
        find = self.outputs[Path('find/index.html')]; prior = history.before('find/index.html', find)
        self.assertLess(len(find.encode()) - len(prior.encode()), 2048)
        payload = lambda s: re.search(r'id="find-section-data">(.*?)</script>', s, re.S)[1]
        self.assertLess(len(payload(find).encode()) - len(payload(prior).encode()), 1024)

    def test_history_rejects_unreviewed_changes(self):
        for path, old, new in [('poker/turn-and-river-decisions/index.html', '12 / 48 = 25%', '12 / 48 = 50%'),
                               ('poker/first-flop-decisions/index.html', '21.6%', '50%'),
                               ('_source/pages.json', 'Your turn and river decisions.', 'Invented expertise')]:
            raw = self.outputs[Path(path)] if path in map(str, self.outputs) else (ROOT / path).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertEqual(history.before(path, changed), changed)
            if path == history.OUTPUT: self.assertIn(Path(path), history.outputs({Path(path): changed}))
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id'] == history.ID)['description'] = 'Unsupported claim'
        self.assertEqual(len(history.pages(pages)), 175)
        self.assertEqual(history.before('assets/unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__': unittest.main()
