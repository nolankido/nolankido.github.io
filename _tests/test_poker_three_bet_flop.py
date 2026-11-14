"""Turn 07: independent flop ledger and native discoverability contracts."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class ThreeBetFlopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.slug = 'three-bet-pot-flop-decisions'
        cls.route = f'/poker/{cls.slug}/'
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_library_finder_topics_feeds_and_sitemap(self):
        pages = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(pages), 1)
        self.assertTrue(pages[0]['poker_guide'])
        self.assertEqual(pages[0]['date'], '2026-11-14')
        self.assertIn('https://nolankido.com/poker/three-bet-pot-flop-decisions/',
                      self.article)
        self.assertIn('"datePublished": "2026-11-14"', self.article)
        for path in ('poker/library/index.html', 'poker/find/index.html',
                     'poker/topics/strategy/index.html',
                     'poker/topics/learn/index.html',
                     'poker/topics/cash-games/index.html', 'sitemap.xml',
                     'poker/feed.xml', 'writing.xml'):
            self.assertIn(self.route, self.outputs[Path(path)], path)

    def test_exercises_sources_scope_and_two_distinct_boards(self):
        self.assertIn('Every action, hand and board here is fictional', self.article)
        self.assertIn('A♣ 7♦ 2♠', self.article)
        self.assertIn('9♠ 8♠ 7♦', self.article)
        self.assertIn('T♣ 6♣', self.article)
        self.assertIn('PokerStars Learn', self.article)
        self.assertIn('GTO Wizard', self.article)
        self.assertIn('No solver was run', self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 5)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_preflop_and_checkback_geometry(self):
        blind_dead = Fraction(1, 2) + 1
        opening_total = Fraction(5, 2)
        threebet_total = 10
        self.assertEqual(threebet_total - opening_total, Fraction(15, 2))
        pot = 2 * threebet_total + blind_dead
        self.assertEqual(pot, Fraction(43, 2))
        behind = 100 - threebet_total
        self.assertEqual(behind, 90)
        self.assertEqual(Fraction(behind, 1) / pot, Fraction(180, 43))
        self.assertEqual(pot + 0 + 0, Fraction(43, 2))
        for phrase in ('10 + button 10 + folded small blind 0.5',
                       '90 / 21.5 ≈ 4.19', 'pot stays <strong>21.5 BB</strong>'):
            self.assertIn(phrase, self.article)

    def test_small_and_large_bet_call_ledgers(self):
        pot = Fraction(43, 2)
        for bet, facing, final, behind, spr, threshold in (
            (5, Fraction(53, 2), Fraction(63, 2), 85,
             Fraction(170, 63), Fraction(10, 63)),
            (14, Fraction(71, 2), Fraction(99, 2), 76,
             Fraction(152, 99), Fraction(28, 99)),
        ):
            self.assertEqual(pot + bet, facing)
            self.assertEqual(facing + bet, final)
            self.assertEqual(100 - 10 - bet, behind)
            self.assertEqual(Fraction(behind, 1) / final, spr)
            self.assertEqual(Fraction(bet, 1) / final, threshold)
        for phrase in ('21.5 + 5 = 26.5 BB', '26.5 + 5 = 31.5 BB',
                       '85 / 31.5 ≈ 2.70', '21.5 + 14 + 14 = 49.5 BB',
                       '76 / 49.5 ≈ 1.54', '5 / 31.5 ≈ 15.87%',
                       '14 / 49.5 ≈ 28.28%'):
            self.assertIn(phrase, self.article)

    def test_checkraise_is_raise_to_total_not_added_amount(self):
        pot = Fraction(43, 2)
        button_bet = 5
        cutoff_raise_to = 20
        self.assertGreaterEqual(cutoff_raise_to, 2 * button_bet)
        pot_facing_button = pot + button_bet + cutoff_raise_to
        button_call = cutoff_raise_to - button_bet
        self.assertEqual(pot_facing_button, Fraction(93, 2))
        self.assertEqual(button_call, 15)
        self.assertEqual(pot_facing_button + button_call, Fraction(123, 2))
        self.assertEqual(100 - 10 - cutoff_raise_to, 70)
        self.assertEqual(Fraction(70, 1) / Fraction(123, 2), Fraction(140, 123))
        for phrase in ('20 − 5 = 15 BB', '46.5 + 15 = 61.5 BB',
                       '70 / 61.5 ≈ 1.14'):
            self.assertIn(phrase, self.article)

    def test_four_existing_guides_link_from_substantive_prose(self):
        graph = poker_link_graph.scan(ROOT)
        target = next(item for item in graph['records'] if item['slug'] == self.slug)
        for source in ('three-bet-sizing-and-pot-geometry', 'reading-the-board',
                       'ranges-and-bets', 'first-flop-decisions'):
            self.assertIn('/poker/' + source + '/', target['prose_inbound_guides'])
        self.assertTrue(target['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(target['inbound_count'], 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
