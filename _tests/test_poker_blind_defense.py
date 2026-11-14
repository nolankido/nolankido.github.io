"""Turn 05: blind-defense teaching fixtures, publishing, and contextual links."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class BlindDefenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.slug = 'blind-defense'
        cls.route = '/poker/' + cls.slug + '/'
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_discovery_and_indexing(self):
        matches = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]['poker_guide'])
        self.assertEqual(matches[0]['date'], '2026-11-14')
        self.assertIn('https://nolankido.com/poker/blind-defense/', self.article)
        self.assertIn('"datePublished": "2026-11-14"', self.article)
        for route in ('poker/library/index.html', 'poker/find/index.html',
                      'poker/topics/strategy/index.html',
                      'poker/topics/learn/index.html',
                      'poker/topics/cash-games/index.html', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(route)], route)

    def test_editorial_scope_and_answers(self):
        self.assertIn('fictional', self.article)
        self.assertIn('not solved defense frequencies', self.article)
        self.assertIn('Prepared with AI assistance', self.article)
        self.assertIn('Poker Tournament Directors Association', self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 4)
        self.assertNotIn('\N{EM DASH}', self.article)
        self.assertIn('Squeeze calculation', self.article)
        self.assertIn('Blind versus blind', self.article)

    def test_button_open_accounting(self):
        button_open = Fraction(5, 2)
        sb = Fraction(1, 2)
        bb = 1
        threebet = 9
        pot_before = button_open + sb + bb
        self.assertEqual(pot_before, 4)
        self.assertEqual(button_open - sb, 2)
        self.assertEqual(button_open - bb, Fraction(3, 2))
        self.assertEqual(pot_before + (button_open - sb), 6)
        self.assertEqual(pot_before + (threebet - sb), Fraction(25, 2))
        self.assertEqual(pot_before + (button_open - bb), Fraction(11, 2))
        self.assertEqual(pot_before + (threebet - bb), 12)
        self.assertEqual(2 * threebet + bb, 19)
        self.assertEqual(2 * threebet + sb, Fraction(37, 2))
        for text in ('4 BB', '6 BB', '12.5 BB', '5.5 BB', '12 BB',
                     '19 BB', '18.5 BB'):
            self.assertIn(text, self.article)

    def test_blind_versus_blind_options(self):
        sb = Fraction(1, 2)
        bb = 1
        pot = sb + bb
        self.assertEqual(pot, Fraction(3, 2))
        self.assertEqual(pot + (bb - sb), 2)
        sb_raise = 3
        self.assertEqual(pot + (sb_raise - sb), 4)
        self.assertEqual(pot + (sb_raise - sb) + (sb_raise - bb), 6)
        self.assertEqual(Fraction(100 - sb_raise, 6), Fraction(97, 6))
        for text in ('1.5 BB', '2 BB', '4 BB',
                     'SPR = 97 / 6 ≈ 16.17'):
            self.assertIn(text, self.article)

    def test_open_cold_call_and_squeeze(self):
        opener = Fraction(5, 2)
        caller = Fraction(5, 2)
        dead_sb = Fraction(1, 2)
        bb = 1
        squeeze_to = 11
        facing_pot = opener + caller + dead_sb + bb
        self.assertEqual(facing_pot, Fraction(13, 2))
        self.assertEqual(facing_pot + (opener - bb), 8)
        squeezed_pot = facing_pot + (squeeze_to - bb)
        self.assertEqual(squeezed_pot, Fraction(33, 2))
        self.assertEqual(squeeze_to - opener, Fraction(17, 2))
        self.assertEqual(squeezed_pot + (squeeze_to - opener), 25)
        self.assertEqual(squeezed_pot + 2 * (squeeze_to - opener), Fraction(67, 2))
        self.assertEqual(squeezed_pot - squeeze_to, Fraction(11, 2))
        self.assertEqual(100 - squeeze_to, 89)
        for text in ('6.5 BB', '8 BB', '16.5 BB', '25 BB',
                     '33.5 BB', '5.5 BB', '89 BB behind'):
            self.assertIn(text, self.article)

    def test_tournament_big_blind_ante_is_dead_money(self):
        button_open = Fraction(5, 2)
        sb = Fraction(1, 2)
        bb = 1
        bb_ante = 1
        self.assertEqual(button_open + sb + bb + bb_ante, 5)
        self.assertEqual(button_open - bb, Fraction(3, 2))
        self.assertEqual(5 + Fraction(3, 2), Fraction(13, 2))
        self.assertEqual(25 - bb - bb_ante, 23)
        self.assertEqual(23 - Fraction(3, 2), Fraction(43, 2))
        for text in ('5 BB', '6.5 BB', '23 BB behind', '21.5 BB behind'):
            self.assertIn(text, self.article)

    def test_three_existing_guides_link_in_context(self):
        graph = poker_link_graph.scan(ROOT)
        guide = next(row for row in graph['records'] if row['slug'] == self.slug)
        for slug in ('facing-preflop-raises', 'position-and-stacks',
                     'limped-multiway-pots'):
            self.assertIn('/poker/' + slug + '/', guide['prose_inbound_guides'])
        self.assertTrue(guide['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(guide['inbound_count'], 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
