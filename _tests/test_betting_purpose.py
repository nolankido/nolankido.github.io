"""Independent hand comparisons, decision accounting and prior-content preservation."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import betting_history as history
import checkpoint_history
from test_viewer_guides import Tags, best

ROUTE = '/poker/betting-with-a-purpose/'


class BettingPurposeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = checkpoint_history.pages(build.public_pages())
        cls.current_outputs = build.build_outputs()
        cls.outputs = checkpoint_history.outputs(cls.current_outputs)
        cls.source = (ROOT / '_source/poker/betting-with-a-purpose.html').read_text()
        cls.baseline = json.loads((ROOT / '_tests/betting-baseline.json').read_text())

    def test_every_old_article_metadata_asset_and_download_is_preserved(self):
        b = self.baseline
        self.assertEqual(b['commit'], 'dc39792022e74088dceca1d25d7a6c34a5d8c562')
        self.assertEqual(len(b['pages']), 176)
        current = {p['id']: p for p in self.pages}
        for old in b['pages']:
            self.assertEqual(current[old['id']], old, old['id'])
        changed = {'_source/pages.json', '_source/poker/library.json', '_source/poker/topics.json',
                   '_source/reader-previews.json', '_scripts/poker_reading.py'}
        for path, digest in b['files'].items():
            raw = checkpoint_history.before(path, (ROOT / path).read_bytes())
            if path not in changed:
                self.assertEqual(sha256(raw).hexdigest(), digest, path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), digest, path)
        self.assertEqual(history.pages(self.pages), b['pages'])
        restored = history.outputs(self.outputs)
        self.assertEqual(set(map(str, restored)), set(b['outputs']))
        for path, raw in restored.items():
            self.assertEqual(sha256(raw.encode()).hexdigest(), b['outputs'][str(path)], str(path))

    def test_all_old_feed_items_remain_exact(self):
        restored = history.outputs(self.outputs)
        for path in ['feed.xml', 'poker/feed.xml', 'technology/feed.xml', 'living-well/feed.xml', 'writing.xml']:
            items = lambda text: {i.findtext('link'): ET.tostring(i, encoding='unicode')
                                  for i in ET.fromstring(text).findall('./channel/item')}
            old, new = items(restored[Path(path)]), items(self.outputs[Path(path)])
            self.assertEqual({k: new[k] for k in old}, old, path)
            self.assertEqual(set(new) - set(old), {'https://nolankido.com' + ROUTE}
                             if path in ['poker/feed.xml', 'writing.xml'] else set(), path)

    def test_the_four_exact_hands_are_legal_and_compared_correctly(self):
        scene = next(a for _, a in Tags(self.source).items if a.get('data-example') == 'value')
        hole, board = scene['data-hole'].split(), scene['data-board'].split()
        self.assertEqual(best(hole + board), (1, 12, 11, 8, 5))
        opponents = [a['data-opponent'].split() for tag, a in Tags(self.source).items
                     if tag == 'tr' and 'data-opponent' in a]
        self.assertEqual(opponents, [['Qc', 'Td'], ['9h', '9d'], ['8h', '8d'], ['Ac', 'Kd']])
        expected = [(1, 12, 10, 8, 5), (1, 9, 12, 8, 5), (3, 8, 12, 5), (0, 14, 13, 12, 8, 5)]
        for hand, rank in zip(opponents, expected):
            self.assertEqual(len(set(hole + board + hand)), 9)
            self.assertEqual(best(hand + board), rank)
        self.assertEqual([best(hole + board) > best(h + board) for h in opponents], [True, True, False, True])
        for cards in ['Q-Q-J-8-5', 'Q-Q-T-8-5', '9-9-Q-8-5', '8-8-8-Q-5', 'A-K-Q-8-5']:
            self.assertIn(cards, self.source)

    def test_value_models_compare_the_same_decision_and_return_own_bets(self):
        # Derive terminal values from stacks/payouts, not from the article's totals.
        pot, stack = 40, 100
        wins = [True, True, False, True]
        def net(bet, calls):
            results = []
            for win, call in zip(wins, calls):
                remaining = stack - bet
                payout = (pot + bet * 2 if win else 0) if call else pot + bet
                results.append(remaining + payout - stack)
            return Fraction(sum(results), 4)
        checking = Fraction(sum(pot if w else 0 for w in wins), 4)
        self.assertEqual(checking, 30)
        self.assertEqual(net(10, [True, True, True, False]), Fraction(65, 2))
        self.assertEqual(net(10, [False, False, True, False]), Fraction(55, 2))
        self.assertEqual(net(20, [False, False, True, False]), 25)
        self.assertEqual(net(10, [True, True, True, False]) - checking, Fraction(5, 2))
        for formula in ['(40 + 40 + 0 + 40) / 4 = 30', '(50 + 50 - 10 + 40) / 4 = 32.5',
                        '(40 + 40 - 10 + 40) / 4 = 27.5', '(40 + 40 - 20 + 40) / 4 = 25']:
            self.assertIn(formula, self.source)
        self.assertIn('decision-point values, not full-hand profits', self.source)
        self.assertIn('with no raises', self.source)

    def test_bluff_thresholds_are_fold_frequencies_with_zero_showdown_value(self):
        scene = next(a for _, a in Tags(self.source).items if a.get('data-example') == 'bluff')
        hole, board, opponent = [scene[k].split() for k in ['data-hole', 'data-board', 'data-opponent']]
        self.assertEqual(len(set(hole + board + opponent)), 9)
        self.assertEqual(best(hole + board), (0, 13, 11, 10, 9, 5))
        self.assertEqual(best(opponent + board), (1, 12, 13, 9, 5))
        for bet in [10, 30]:
            threshold = Fraction(bet, 30 + bet)
            self.assertEqual(threshold * 30 - (1 - threshold) * bet, 0)
        self.assertEqual(Fraction(10, 40), Fraction(1, 4))
        self.assertEqual(Fraction(30, 60), Fraction(1, 2))
        for phrase in ['10 / (30 + 10) = 25%', '30 / (30 + 30) = 50%',
                       "not your hand's equity", 'the frequency with which you should bluff']:
            self.assertIn(phrase, self.source)

    def test_draw_example_improves_on_one_river_and_loses_on_the_other(self):
        scene = next(a for _, a in Tags(self.source).items if a.get('data-example') == 'draw')
        hole, board, opponent = [scene[k].split() for k in ['data-hole', 'data-board', 'data-opponent']]
        self.assertEqual(len(set(hole + board + opponent)), 8)
        self.assertLess(best(hole + board), best(opponent + board))
        for river, winning in [('6h', True), ('7c', False)]:
            self.assertEqual(len(set(hole + board + opponent + [river])), 9)
            self.assertEqual(best(hole + board + [river]) > best(opponent + board + [river]), winning)
        self.assertEqual(best(hole + board + ['6h']), (5, 14, 13, 11, 8, 6))
        self.assertIn('do not reuse it unchanged for this draw', self.source)

    def test_seven_answers_and_discovery_work_without_new_runtime(self):
        tags = Tags(self.source).items
        questions = [a for tag, a in tags if tag == 'details']
        self.assertEqual([a['id'] for a in questions], ['check-' + s for s in ['purpose','targets','compare','folds','size','bluff','draw']])
        self.assertTrue(all('open' not in a for a in questions))
        self.assertEqual(len([a for _, a in tags if a.get('role') == 'img']), 7)
        self.assertNotRegex(self.source, r'<(?:script|form|input|iframe)\b')
        self.assertNotIn('\u2014', self.source)
        self.assertIn('arithmetic is optional', self.source)
        for tag, a in tags:
            href = a.get('href', '')
            if not href.startswith('/poker/') or '#' not in href: continue
            route, anchor = href.split('#')
            self.assertIn('id="' + anchor + '"', self.outputs[build.output_path(route)], href)
        for path in ['poker/ranges-for-beginners/index.html', 'poker/topics/learn/index.html',
                     'poker/library/index.html', 'poker/find/index.html', 'find/index.html', 'notes/index.html', 'sitemap.xml']:
            self.assertIn(ROUTE, self.outputs[Path(path)], path)
        self.assertEqual(check_live.targets()[ROUTE], (200, self.current_outputs[build.output_path(ROUTE)].encode()))

    def test_history_keeps_unreviewed_claims_visible_in_a_fresh_process(self):
        path = '_source/pages.json'
        raw = (ROOT / path).read_text()
        tampered = raw.replace('Give your bet a purpose.', 'Guaranteed poker profits.', 1)
        self.assertNotEqual(raw, tampered)
        self.assertEqual(history.before(path, tampered), tampered)
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id'] == history.ID)['description'] = 'Unreviewed claim'
        self.assertEqual(len(history.pages(pages)), 177)
        command = 'import sys;sys.path.insert(0,"_tests");import choice_history;assert "_source/poker/betting-with-a-purpose.html" in choice_history.NEW_SOURCES'
        subprocess.run([sys.executable, '-c', command], cwd=ROOT, check=True, capture_output=True, text=True)


if __name__ == '__main__': unittest.main()
