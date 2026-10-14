"""Postflop teaching correctness and independent preservation of all prior content."""
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
import flop_history as history
from test_viewer_guides import Tags, best

ROUTE = '/poker/first-flop-decisions/'
CHECKS = ['pair-and-draw', 'action', 'purpose', 'straight', 'shared', 'counterfeit', 'second-payment', 'snapshot']


def feed_records(xml):
    return {i.findtext('link'): ET.tostring(i, encoding='unicode') for i in ET.fromstring(xml).findall('./channel/item')}


class FlopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.text = cls.outputs[build.output_path(ROUTE)]
        cls.source = (ROOT / '_source/poker/first-flop-decisions.html').read_text()
        cls.baseline = json.loads((ROOT / '_tests/flop-baseline.json').read_text())

    def test_exact_inventory_and_frozen_predecessor_outputs(self):
        b = self.baseline
        self.assertEqual((len(b['pages']), len(b['outputs']), len(b['files'])), (173, 200, 347))
        self.assertEqual(len(self.pages), 174)
        self.assertEqual(history.pages(self.pages), b['pages'])
        outputs = history.outputs(self.outputs)
        self.assertEqual(set(map(str, outputs)), set(b['outputs']))
        for p, raw in outputs.items():
            self.assertEqual(sha256(raw.encode()).hexdigest(), b['outputs'][str(p)], str(p))
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        self.assertEqual(files - set(b['files']), set(history.change()['new_files']))
        self.assertEqual(set(history.change()['new_files']), {'_source/poker/first-flop-decisions.html', 'assets/social/reader-poker-first-flop-decisions.png'})
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
                now['entries'] = [v for v in now['entries'] if v['slug'] != 'first-flop-decisions']
            else:
                del now['pages']['poker-first-flop-decisions']
            self.assertEqual(now, old, path)
        for path, old in self.baseline['feed_items'].items():
            now = feed_records(self.outputs[Path(path)])
            self.assertEqual({k: now[k] for k in old}, old, path)
            self.assertEqual(set(now) - set(old), {'https://nolankido.com' + ROUTE} if path in ['poker/feed.xml', 'writing.xml'] else set())

    def test_eight_native_exercises_and_accessible_cards(self):
        tags = Tags(self.source).items
        questions = [a for tag, a in tags if tag == 'details']
        self.assertEqual([a['id'] for a in questions], ['check-' + c for c in CHECKS])
        self.assertTrue(all('open' not in a for a in questions))
        self.assertEqual(len([a for tag, a in tags if tag == 'h2']), 10)
        for label in CHECKS:
            answer = re.search(r'id="check-' + label + r'".*?<div>(.*?)</div></details>', self.source, re.S)[1]
            self.assertGreater(len(re.sub('<[^>]+>', '', answer).split()), 40, label)
        cards = [a for _, a in tags if a.get('role') == 'img']
        self.assertEqual(len(cards), 30)
        self.assertTrue(all(' of ' in a.get('aria-label', '') for a in cards))
        self.assertGreater(len(re.sub('<[^>]+>', ' ', self.source).split()), 2400)
        for phrase in ['Every scene is fictional', 'no wager, account or purchase', 'Prepared with AI assistance',
                       'no universally correct action', 'current hands after the turn', 'October 14, 2026',
                       'your choices are fold, call or make a permitted raise', '12 total on this street, not 16']:
            self.assertIn(phrase, self.source)
        self.assertNotRegex(self.source, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.source)

    def test_shown_hands_and_changing_winners_by_exhaustive_best_five(self):
        examples = {a['data-example']: a for _, a in Tags(self.source).items if 'data-example' in a}
        self.assertEqual(set(examples), {'pair-and-draw', 'open-ended', 'gutshot', 'flush-loses', 'counterfeit'})
        for case in examples.values():
            all_cards = ' '.join(case.get(k, '') for k in ['data-hole', 'data-opponent', 'data-board', 'data-turn', 'data-river']).split()
            self.assertEqual(len(all_cards), len(set(all_cards)))
        made = examples['pair-and-draw']; known = (made['data-hole'] + ' ' + made['data-board']).split()
        self.assertEqual(best(known), (1, 10, 14, 7, 2))
        self.assertEqual(sum(c.endswith('h') for c in known), 4)
        case = examples['flush-loses']; board = case['data-board'].split() + [case['data-turn']]
        self.assertEqual(best(case['data-hole'].split() + board), (5, 13, 12, 11, 8, 3))
        self.assertEqual(best(case['data-opponent'].split() + board), (6, 8, 3))
        case = examples['counterfeit']; hole = case['data-hole'].split(); other = case['data-opponent'].split(); board = case['data-board'].split()
        self.assertEqual(best(hole + board), (2, 9, 4, 13))
        self.assertGreater(best(hole + board), best(other + board))
        for card in [case['data-turn'], case['data-river']]:
            board.append(card)
            self.assertEqual(best(hole + board), (2, 13, 9, 4))
            self.assertEqual(best(other + board), (2, 13, 12, 9))
        flop = 'Ts 7h 2h'.split()
        self.assertGreater(best('Ah Th'.split() + flop), best('Tc 9d'.split() + flop))
        self.assertLess(best('Ah Th'.split() + flop), best('7s 7d'.split() + flop))
        for phrase in ['T-T-A-7-2', 'K-Q-J-8-3', '8-8-8-3-3', 'K-K-9-9-4', 'K-K-Q-Q-9']:
            self.assertIn(phrase, self.source)

    def test_every_unseen_card_in_both_straight_exercises(self):
        deck = {rank + suit for rank in '23456789TJQKA' for suit in 'cdhs'}
        cases = {a['data-example']: a for _, a in Tags(self.source).items if 'data-completing-ranks' in a}
        self.assertEqual(set(cases), {'open-ended', 'gutshot'})
        for name, case in cases.items():
            known = (case['data-hole'] + ' ' + case['data-board']).split()
            unseen = deck - set(known); self.assertEqual(len(unseen), 47)
            actual = {c for c in unseen if best(known + [c])[0] == 4}
            expected = {rank + suit for rank in case['data-completing-ranks'] for suit in 'cdhs'}
            self.assertEqual(actual, expected, name)
            self.assertEqual(len(actual), 8 if name == 'open-ended' else 4)
        self.assertIn('the four fours and four nines', self.source)
        self.assertIn('the four sixes', self.source)

    def test_both_ledgers_conserve_chips_and_charge_only_the_new_call(self):
        # Street payments are separate from the pot already in the middle.
        pot, stacks = 18, [50, 50]
        total = pot + sum(stacks)
        for payment, expected_pot, expected_stack in [(6, 30, 44), (15, 60, 29)]:
            pot += 2 * payment; stacks = [n - payment for n in stacks]
            self.assertEqual((pot, stacks), (expected_pot, [expected_stack] * 2))
            self.assertEqual(pot + sum(stacks), total)
        initial_pot, initial_stack, bet, raised_to = 13, 94, 4, 12
        current = initial_pot + bet + raised_to; additional = raised_to - bet
        final = current + additional; remaining = initial_stack - raised_to
        self.assertEqual((current, additional, final, remaining), (29, 8, 37, 82))
        self.assertEqual(final + 2 * remaining, initial_pot + 2 * initial_stack)
        self.assertAlmostEqual(100 * additional / final, 21.6, places=1)
        for phrase in ['would become 60', 'Both players would then have 29', '13 + 4 + 12 = 29', '12 - 4 = 8', 'pot becomes 37', '82 remaining', '8 / 37 is about 21.6%']:
            self.assertIn(phrase, self.source)

    def test_navigation_search_schema_and_exact_live_bytes(self):
        for path in ['poker/starting-hand-decisions/index.html', 'poker/free-poker-learning-path/index.html', 'poker/library/index.html',
                     'poker/topics/learn/index.html', 'poker/find/index.html', 'find/index.html', 'notes/index.html', 'sitemap.xml']:
            self.assertIn(ROUTE, self.outputs[Path(path)], path)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.text, re.S)[1])
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-10-14')
        self.assertEqual(schema['author']['name'], 'Nolan Kido')
        self.assertIn('Poker After the Flop: Beginner Lessons &amp; Practice', self.text)
        targets = check_live.targets()
        self.assertEqual(targets[ROUTE], (200, self.text.encode()))
        self.assertEqual(targets['/assets/social/reader-poker-first-flop-decisions.png'][0], 200)
        find = self.outputs[Path('find/index.html')]; prior = history.before('find/index.html', find)
        self.assertLess(len(find.encode()) - len(prior.encode()), 2048)
        payload = lambda s: re.search(r'id="find-section-data">(.*?)</script>', s, re.S)[1]
        self.assertLess(len(payload(find).encode()) - len(payload(prior).encode()), 1024)

    def test_history_rejects_unreviewed_changes(self):
        for path, old, new in [('poker/first-flop-decisions/index.html', '21.6%', '50%'),
                               ('poker/starting-hand-decisions/index.html', '8,000 / 200', '9,000 / 200'),
                               ('_source/pages.json', 'Your first decisions after the flop.', 'Invented expertise')]:
            raw = self.outputs[Path(path)] if path in map(str, self.outputs) else (ROOT / path).read_text()
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertEqual(history.before(path, changed), changed)
            if path == history.OUTPUT: self.assertIn(Path(path), history.outputs({Path(path): changed}))
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id'] == history.ID)['description'] = 'Unsupported claim'
        self.assertEqual(len(history.pages(pages)), 174)
        self.assertEqual(history.before('assets/unrelated.bin', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__': unittest.main()
