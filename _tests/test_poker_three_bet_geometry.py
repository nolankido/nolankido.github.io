"""Turn 06: independent three-bet pot geometry and native discovery checks."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class ThreeBetGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.slug = 'three-bet-sizing-and-pot-geometry'
        cls.route = '/poker/' + cls.slug + '/'
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_library_finder_topics_feeds_and_sitemap(self):
        pages = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(pages), 1)
        self.assertTrue(pages[0]['poker_guide'])
        self.assertEqual(pages[0]['date'], '2026-11-14')
        self.assertIn('https://nolankido.com/poker/three-bet-sizing-and-pot-geometry/',
                      self.article)
        self.assertIn('"datePublished": "2026-11-14"', self.article)
        for path in ('poker/library/index.html', 'poker/find/index.html',
                     'poker/topics/strategy/index.html',
                     'poker/topics/learn/index.html',
                     'poker/topics/cash-games/index.html', 'sitemap.xml',
                     'poker/feed.xml', 'writing.xml'):
            self.assertIn(self.route, self.outputs[Path(path)], path)

    def test_disclosure_public_sources_and_practice_are_visible(self):
        self.assertIn('fictional and made for arithmetic practice', self.article)
        self.assertIn('do not establish any solver-approved size', self.article)
        self.assertIn('Prepared with AI assistance', self.article)
        self.assertIn('Poker Tournament Directors Association', self.article)
        self.assertIn('GTO Wizard', self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 5)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_button_three_bet_pots_and_flop_sprs(self):
        open_total = Fraction(5, 2)
        dead_blinds = Fraction(1, 2) + 1
        pot_before = open_total + dead_blinds
        self.assertEqual(pot_before, 4)
        self.assertEqual(open_total + (open_total - 1), 4)
        for raise_to, expected_now, expected_call, expected_flop, behind in (
            (8, 12, Fraction(11, 2), Fraction(35, 2), 92),
            (10, 14, Fraction(15, 2), Fraction(43, 2), 90),
            (12, 16, Fraction(19, 2), Fraction(51, 2), 88),
        ):
            self.assertEqual(pot_before + raise_to, expected_now)
            self.assertEqual(raise_to - open_total, expected_call)
            self.assertEqual(expected_now + expected_call, expected_flop)
            self.assertEqual(2 * raise_to + dead_blinds, expected_flop)
            self.assertEqual(100 - raise_to, behind)
        self.assertEqual(Fraction(92, 1) / Fraction(35, 2), Fraction(184, 35))
        self.assertEqual(Fraction(90, 1) / Fraction(43, 2), Fraction(180, 43))
        self.assertEqual(Fraction(88, 1) / Fraction(51, 2), Fraction(176, 51))
        for text in ('92 / 17.5 ≈ 5.26', '90 / 21.5 ≈ 4.19',
                     '88 / 25.5 ≈ 3.45', '5.5 BB', '7.5 BB', '9.5 BB'):
            self.assertIn(text, self.article)

    def test_flat_call_versus_three_bet_and_same_raise_different_seats(self):
        open_total = Fraction(5, 2)
        dead_blinds = Fraction(3, 2)
        single_raised_pot = 2 * open_total + dead_blinds
        self.assertEqual(single_raised_pot, Fraction(13, 2))
        self.assertEqual(Fraction(100, 1) - open_total, Fraction(195, 2))
        self.assertEqual(Fraction(195, 2) / single_raised_pot, 15)
        threebet = 10
        pot_ip = 2 * threebet + dead_blinds
        pot_oop = 2 * threebet + 1  # BB folds; SB is the continuing player.
        self.assertEqual(pot_ip, Fraction(43, 2))
        self.assertEqual(pot_oop, 21)
        self.assertEqual(threebet - Fraction(1, 2), Fraction(19, 2))
        self.assertEqual(threebet - open_total, Fraction(15, 2))
        self.assertEqual(Fraction(90, 1) / pot_oop, Fraction(30, 7))
        self.assertEqual(pot_ip - pot_oop, Fraction(1, 2))
        for text in ('SPR = 97.5 / 6.5 = 15', '10 + 10 + 1 = 21 BB',
                     'SPR = 90 / 21 ≈ 4.29', '9.5 BB now'):
            self.assertIn(text, self.article)

    def test_fourbet_minimum_pot_and_remaining_stack(self):
        open_total = Fraction(5, 2)
        threebet = 10
        full_increment = threebet - open_total
        min_fourbet_total = threebet + full_increment
        fourbet = 24
        dead_blinds = Fraction(3, 2)
        self.assertEqual(full_increment, Fraction(15, 2))
        self.assertEqual(min_fourbet_total, Fraction(35, 2))
        self.assertEqual(fourbet - open_total, Fraction(43, 2))
        pot_after_fourbet = fourbet + threebet + dead_blinds
        self.assertEqual(pot_after_fourbet, Fraction(71, 2))
        self.assertEqual(fourbet - threebet, 14)
        final_pot = 2 * fourbet + dead_blinds
        self.assertEqual(final_pot, Fraction(99, 2))
        self.assertEqual(100 - fourbet, 76)
        self.assertEqual(Fraction(76, 1) / final_pot, Fraction(152, 99))
        self.assertEqual(pot_after_fourbet - fourbet, Fraction(23, 2))
        for text in ('17.5 BB total', '35.5 BB', '49.5 BB',
                     'SPR = 76 / 49.5 ≈ 1.54', '11.5 BB'):
            self.assertIn(text, self.article)

    def test_stack_depth_and_pure_bluff_model_are_not_solver_claims(self):
        pot = Fraction(43, 2)
        self.assertEqual(Fraction(40 - 10, 1) / pot, Fraction(60, 43))
        self.assertEqual(Fraction(100 - 10, 1) / pot, Fraction(180, 43))
        self.assertEqual(Fraction(10, 10 + 4), Fraction(5, 7))
        self.assertIn('SPR = 30 / 21.5 ≈ 1.40', self.article)
        self.assertIn('10 / (10 + 4) ≈ 71.4%', self.article)
        self.assertIn('deliberately unrealistic binary model', self.article)

    def test_four_existing_guides_link_in_substantive_prose(self):
        graph = poker_link_graph.scan(ROOT)
        target = next(item for item in graph['records'] if item['slug'] == self.slug)
        for source in ('blind-defense', 'facing-preflop-raises',
                       'poker-math-reference', 'reading-preflop-charts'):
            self.assertIn('/poker/' + source + '/', target['prose_inbound_guides'])
        self.assertTrue(target['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(target['inbound_count'], 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
