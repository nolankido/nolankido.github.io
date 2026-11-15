"""Turn 09: river arithmetic, legal cards, publication and reader paths."""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


RANKS = {rank: number for number, rank in enumerate('23456789TJQKA', 2)}


def five_card_rank(cards):
    """Classify a five-card showdown from ranks and suits, independently of article text."""
    ranks = [RANKS[card[0]] for card in cards]
    counts = Counter(ranks)
    ordered = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
    flush = len({card[1] for card in cards}) == 1
    distinct = set(ranks)
    if 14 in distinct:
        distinct.add(1)
    straight_high = max((high for high in range(5, 15)
                         if set(range(high - 4, high + 1)).issubset(distinct)), default=0)
    if straight_high and flush:
        return (8, straight_high)
    if ordered[0][0] == 4:
        return (7, ordered[0][1], ordered[1][1])
    if ordered[0][0] == 3 and ordered[1][0] == 2:
        return (6, ordered[0][1], ordered[1][1])
    if flush:
        return (5, *sorted(ranks, reverse=True))
    if straight_high:
        return (4, straight_high)
    if ordered[0][0] == 3:
        return (3, ordered[0][1], *sorted((rank for rank in ranks
                                          if rank != ordered[0][1]), reverse=True))
    if ordered[0][0] == 2 and ordered[1][0] == 2:
        pairs = sorted((ordered[0][1], ordered[1][1]), reverse=True)
        return (2, *pairs, next(rank for rank in ranks if rank not in pairs))
    if ordered[0][0] == 2:
        return (1, ordered[0][1], *sorted((rank for rank in ranks
                                          if rank != ordered[0][1]), reverse=True))
    return (0, *sorted(ranks, reverse=True))


def seven_card_rank(cards):
    return max(five_card_rank(hand) for hand in combinations(cards, 5))


class ThreeBetRiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.slug = 'three-bet-pot-river-decisions'
        cls.route = f'/poker/{cls.slug}/'
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_metadata_and_indexing_surfaces(self):
        matches = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]['poker_guide'])
        self.assertEqual(matches[0]['date'], '2026-11-14')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-14"', self.article)
        for output in ('poker/library/index.html', 'poker/find/index.html',
                       'poker/topics/strategy/index.html',
                       'poker/topics/learn/index.html',
                       'poker/topics/cash-games/index.html',
                       'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(output)], output)

    def test_transparency_and_practice(self):
        for phrase in ('Every board, holding, action, response and opponent-range weight below is fictional',
                       'No solver was run', 'Prepared with AI assistance',
                       'PokerStars Learn', 'GTO Wizard',
                       'No gambling account or money is needed',
                       'uncalled 24 BB is returned',
                       'uncalled 61 BB is returned'):
            self.assertIn(phrase, self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 7)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_river_boards_are_unique_and_hand_descriptions_correct(self):
        hero = ['Ah', 'Kh']
        board_a = ['Ac', '7d', '2s', 'Ks', '3d']
        board_b = ['9s', '8s', '7d', '6s', '2d']
        board_b_alt = ['9s', '8s', '7d', '6s', 'Ts']
        value_hypothesis = ['Ad', 'Qd']
        better_hand = ['7c', '7h']
        missed_draw = ['Qs', 'Js']
        for board in (board_a, board_b, board_b_alt):
            self.assertEqual(len(set(board + hero)), 7)
        for possible_cutoff in (value_hypothesis, better_hand, missed_draw):
            self.assertEqual(len(set(board_a + hero + possible_cutoff)), 9)
        self.assertEqual(Counter(card[0] for card in board_a + hero)['A'], 2)
        self.assertEqual(Counter(card[0] for card in board_a + hero)['K'], 2)
        self.assertEqual(sum(card.endswith('s') for card in board_b), 3)
        self.assertEqual(sum(card.endswith('s') for card in board_b_alt), 4)
        self.assertEqual(set('6789T'), set(card[0] for card in board_b_alt))
        self.assertEqual(seven_card_rank(board_a + hero), (2, 14, 13, 7))
        self.assertEqual(seven_card_rank(board_b + hero), (0, 14, 13, 9, 8, 7))
        self.assertEqual(seven_card_rank(board_b_alt + hero), (4, 10))
        self.assertGreater(seven_card_rank(board_a + hero), seven_card_rank(board_a + value_hypothesis))
        self.assertGreater(seven_card_rank(board_a + hero), seven_card_rank(board_a + missed_draw))
        self.assertLess(seven_card_rank(board_a + hero), seven_card_rank(board_a + better_hand))
        self.assertGreater(seven_card_rank(board_b + hero), seven_card_rank(board_b + ['Qh', 'Jh']))
        self.assertLess(seven_card_rank(board_b + hero), seven_card_rank(board_b + ['Th', '4h']))
        self.assertLess(seven_card_rank(board_b + hero), seven_card_rank(board_b + ['Qs', 'Js']))
        self.assertLess(seven_card_rank(board_b_alt + hero), seven_card_rank(board_b_alt + ['Jd', '4h']))
        self.assertLess(seven_card_rank(board_b_alt + hero), seven_card_rank(board_b_alt + ['Qs', '4h']))
        for phrase in ('two pair, aces and kings', 'A-A-K-K-7',
                       'ace-high', 'A-K-9-8-7',
                       'T♠ instead of 2♦', 'jack-high straight'):
            self.assertIn(phrase, self.article)

    def test_two_turn_bet_call_branches_remain_separate(self):
        flop_pot = 2 * 10 + Fraction(1, 2) + 1  # both 10 BB plus dead 1.5 BB
        self.assertEqual(flop_pot, Fraction(43, 2))
        turn_pot = flop_pot + 2 * 5
        self.assertEqual(turn_pot, Fraction(63, 2))
        self.assertEqual(100 - 10 - 5, 85)
        for turn_bet, expected_pot, behind in ((12, Fraction(111, 2), 73),
                                                (24, Fraction(159, 2), 61)):
            self.assertEqual(turn_pot + 2 * turn_bet, expected_pot)
            self.assertEqual(85 - turn_bet, behind)
        self.assertEqual(Fraction(73, 1) / Fraction(111, 2), Fraction(146, 111))
        self.assertEqual(Fraction(61, 1) / Fraction(159, 2), Fraction(122, 159))
        for phrase in ('31.5 + 12 + 12', '31.5 + 24 + 24',
                       '73 / 55.5', '61 / 79.5'):
            self.assertIn(phrase, self.article)

    def test_check_back_bet_call_and_river_shove(self):
        small_pot = Fraction(111, 2)
        large_pot = Fraction(159, 2)
        bet = 24
        self.assertEqual(small_pot + bet, Fraction(159, 2))
        self.assertEqual(small_pot + 2 * bet, Fraction(207, 2))
        self.assertEqual(73 - bet, 49)
        self.assertAlmostEqual(float(Fraction(bet, 1) / (small_pot + 2 * bet)) * 100,
                               23.1884057971)
        self.assertEqual(large_pot + 61, Fraction(281, 2))
        self.assertEqual(large_pot + 2 * 61, Fraction(403, 2))
        self.assertEqual(61 - 61, 0)
        self.assertAlmostEqual(float(Fraction(61, 1) / Fraction(403, 2)) * 100,
                               30.2729528536)
        for phrase in ('55.5 + 24 + 24 = 103.5 BB',
                       '79.5 + 61 + 61 = 201.5 BB',
                       '24 / 103.5 ≈ 23.19%',
                       '61 / 201.5 ≈ 30.27%'):
            self.assertIn(phrase, self.article)

    def test_bluff_and_call_are_different_thresholds(self):
        for pot, bet, fold_price, call_price in (
            (Fraction(111, 2), 24, Fraction(16, 53), Fraction(16, 69)),
            (Fraction(159, 2), 61, Fraction(122, 281), Fraction(122, 403)),
        ):
            self.assertEqual(Fraction(bet, 1) / (pot + bet), fold_price)
            self.assertEqual(Fraction(bet, 1) / (pot + 2 * bet), call_price)
            self.assertGreater(fold_price, call_price)
        for phrase in ('24 / 79.5 ≈ <strong>30.19%',
                       '61 / 140.5 ≈ <strong>43.42%',
                       '24 / 103.5 ≈ <strong>23.19%',
                       '61 / 201.5 ≈ <strong>30.27%'):
            self.assertIn(phrase, self.article)

    def test_lead_bet_and_range_sensitivity(self):
        start_pot = Fraction(111, 2)
        lead = 18
        self.assertEqual(start_pot + lead, Fraction(147, 2))
        final = start_pot + 2 * lead
        self.assertEqual(final, Fraction(183, 2))
        self.assertEqual(73 - lead, 55)
        self.assertEqual(Fraction(lead, 1) / final, Fraction(12, 61))
        self.assertEqual(Fraction(1, 4) * final - lead, Fraction(39, 8))
        self.assertEqual(Fraction(1, 10) * final - lead, Fraction(-177, 20))
        for phrase in ('55.5 + 18 = 73.5 BB', '73.5 + 18 = 91.5 BB',
                       '18 / 91.5 ≈ 19.67%',
                       '0.25 × 91.5 − 18 = +4.875 BB',
                       '0.10 × 91.5 − 18 = −8.85 BB'):
            self.assertIn(phrase, self.article)

    def test_river_checkraise_to_total(self):
        pot = Fraction(111, 2)
        first_bet = 24
        raise_total = 60
        self.assertGreaterEqual(raise_total, 2 * first_bet)
        self.assertLessEqual(raise_total, 73)
        self.assertEqual(pot + first_bet + raise_total, Fraction(279, 2))
        amount_to_call = raise_total - first_bet
        self.assertEqual(amount_to_call, 36)
        self.assertEqual(pot + 2 * raise_total, Fraction(351, 2))
        self.assertEqual(73 - raise_total, 13)
        self.assertEqual(Fraction(amount_to_call, 1) / Fraction(351, 2),
                         Fraction(24, 117))
        for phrase in ('55.5 + 24 + 60 = 139.5 BB', '60 − 24 = 36 BB more',
                       '55.5 + 60 + 60 = 175.5 BB',
                       '36 / 175.5 ≈ 20.51%'):
            self.assertIn(phrase, self.article)

    def test_contextual_inlinks_and_reachability(self):
        graph = poker_link_graph.scan(ROOT)
        target = next(item for item in graph['records'] if item['slug'] == self.slug)
        for source in ('three-bet-pot-turn-decisions', 'turn-and-river-decisions',
                       'pot-odds-workshop', 'ranges-and-bets', 'range-combinations'):
            self.assertIn('/poker/' + source + '/', target['prose_inbound_guides'])
        self.assertTrue(target['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(target['inbound_count'], 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
