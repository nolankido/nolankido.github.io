"""Turn 08: independently verify three-bet turn ledgers and discovery."""

from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class ThreeBetTurnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.slug = 'three-bet-pot-turn-decisions'
        cls.route = f'/poker/{cls.slug}/'
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_discovery_canonical_and_feed_registration(self):
        pages = [item for item in self.pages if item['path'] == self.route]
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0]['date'], '2026-11-14')
        self.assertTrue(pages[0]['poker_guide'])
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-14"', self.article)
        for path in ('poker/library/index.html', 'poker/find/index.html',
                     'poker/topics/strategy/index.html',
                     'poker/topics/learn/index.html',
                     'poker/topics/cash-games/index.html',
                     'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(path)], path)

    def test_scope_sources_and_practice(self):
        self.assertIn('Every board, holding and action is fictional', self.article)
        self.assertIn('No solver was run', self.article)
        self.assertIn('GTO Wizard', self.article)
        self.assertIn('PokerStars Learn', self.article)
        self.assertIn('Prepared with AI assistance', self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 6)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_turn_cards_are_real_distinct_hands(self):
        board_a = ['Ac', '7d', '2s', 'Ks']
        board_b = ['9s', '8s', '7d', '6s']
        hero = ['Ah', 'Kh']
        self.assertEqual(len(set(board_a + hero)), 6)
        self.assertEqual(len(set(board_b + hero)), 6)
        ranks_a = Counter(card[0] for card in board_a + hero)
        self.assertEqual(sorted(ranks_a.values()), [1, 1, 2, 2])
        self.assertEqual(ranks_a['A'], 2)
        self.assertEqual(ranks_a['K'], 2)
        self.assertEqual(sum(card.endswith('s') for card in board_b), 3)
        self.assertEqual(sum(card.endswith('s') for card in board_b + hero), 3)
        self.assertTrue(set('6789T').issubset(set('T6' + ''.join(card[0] for card in board_b))))
        for phrase in ('A♣ 7♦ 2♠, turn K♠', '9♠ 8♠ 7♦, turn 6♠',
                       'two pair, aces and kings', 'still <strong>ace-high</strong>'):
            self.assertIn(phrase, self.article)

    def test_preflop_checkback_and_flop_bet_call_are_separate(self):
        dead_blinds = Fraction(1, 2) + 1
        flop = 2 * 10 + dead_blinds
        self.assertEqual(flop, Fraction(43, 2))
        self.assertEqual(100 - 10, 90)
        b5_pot = flop + 2 * 5
        self.assertEqual(b5_pot, Fraction(63, 2))
        self.assertEqual(90 - 5, 85)
        self.assertEqual(Fraction(85, 1) / b5_pot, Fraction(170, 63))
        for phrase in ('10 + 10 + 0.5 + 1 = 21.5 BB',
                       '90 / 21.5 ≈ 4.19', '85 / 31.5 ≈ 2.70'):
            self.assertIn(phrase, self.article)

    def test_delayed_bet_and_probe_share_numbers_not_action(self):
        original = Fraction(43, 2)
        delayed_bet = 8
        facing = original + delayed_bet
        final = facing + delayed_bet
        self.assertEqual(facing, Fraction(59, 2))
        self.assertEqual(final, Fraction(75, 2))
        self.assertEqual(90 - delayed_bet, 82)
        self.assertEqual(Fraction(82, 1) / final, Fraction(164, 75))
        self.assertEqual(Fraction(delayed_bet, 1) / original, Fraction(16, 43))
        for phrase in ('21.5 + 8 = 29.5 BB', '29.5 + 8 = 37.5 BB',
                       '82 / 37.5 ≈ 2.19', '8 / 21.5 ≈ 37.2%'):
            self.assertIn(phrase, self.article)

    def test_small_and_large_turn_bet_and_call_ledgers(self):
        pot = Fraction(63, 2)
        for bet, facing, final, behind, spr, price in (
            (12, Fraction(87, 2), Fraction(111, 2), 73,
             Fraction(146, 111), Fraction(8, 37)),
            (24, Fraction(111, 2), Fraction(159, 2), 61,
             Fraction(122, 159), Fraction(16, 53)),
        ):
            self.assertEqual(pot + bet, facing)
            self.assertEqual(facing + bet, final)
            self.assertEqual(85 - bet, behind)
            self.assertEqual(Fraction(behind, 1) / final, spr)
            self.assertEqual(Fraction(bet, 1) / final, price)
        for phrase in ('31.5 + 12 + 12 = 55.5 BB',
                       '31.5 + 24 + 24 = 79.5 BB',
                       '73 / 55.5 ≈ 1.32', '61 / 79.5 ≈ 0.77',
                       '12 / 55.5 ≈ 21.62%', '24 / 79.5 ≈ 30.19%'):
            self.assertIn(phrase, self.article)

    def test_turn_checkraise_to_total_and_river_geometry(self):
        pot = Fraction(63, 2)
        first_bet = 12
        raise_total = 36
        self.assertGreaterEqual(raise_total, 2 * first_bet)
        facing = pot + first_bet + raise_total
        remaining_call = raise_total - first_bet
        final = facing + remaining_call
        self.assertEqual(facing, Fraction(159, 2))
        self.assertEqual(remaining_call, 24)
        self.assertEqual(final, Fraction(207, 2))
        self.assertEqual(85 - raise_total, 49)
        self.assertEqual(Fraction(49, 1) / final, Fraction(98, 207))
        self.assertEqual(Fraction(24, 1) / Fraction(63, 2), Fraction(16, 21))
        self.assertEqual(Fraction(61, 1) / Fraction(159, 2), Fraction(122, 159))
        self.assertEqual(Fraction(73, 1) / Fraction(111, 2), Fraction(146, 111))
        for phrase in ('31.5 + 12 + 36 = 79.5 BB',
                       '36 − 12 = 24 BB', '31.5 + 36 + 36 = 103.5 BB',
                       '49 / 103.5 ≈ 0.47', '61 / 79.5 ≈ 76.7%',
                       '73 / 55.5 ≈ 131.5%'):
            self.assertIn(phrase, self.article)

    def test_substantive_inlinks_from_existing_guides(self):
        graph = poker_link_graph.scan(ROOT)
        target = next(item for item in graph['records'] if item['slug'] == self.slug)
        for source in ('three-bet-pot-flop-decisions', 'turn-and-river-decisions',
                       'ranges-and-bets', 'pot-odds-workshop'):
            self.assertIn('/poker/' + source + '/', target['prose_inbound_guides'])
        self.assertTrue(target['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(target['inbound_count'], 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
