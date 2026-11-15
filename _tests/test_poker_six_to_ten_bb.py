"""Turn 11: exact 6–10 BB tournament action-tree math and public integration."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class SixToTenBBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'six-to-ten-bb-tournament-decisions'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_publication_and_indexing(self):
        matches = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]['poker_guide'])
        self.assertEqual(matches[0]['date'], '2026-11-15')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for output in ('poker/library/index.html', 'poker/find/index.html',
                       'poker/topics/tournaments/index.html',
                       'poker/topics/strategy/index.html',
                       'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(output)], output)

    def test_transparency_accessible_tables_and_practice(self):
        for phrase in ('After-play study only', 'nine players dealt in',
                       'one fully paid 1 BB big-blind ante',
                       'before forced contributions',
                       'fictional', 'not a solved strategy',
                       'Poker TDA 2026 Rules Version 1.1',
                       'HoldemResources', 'GTO Wizard',
                       'not an at-table tool or a promise of gambling profit',
                       'Prepared with AI assistance'):
            self.assertIn(phrase.lower(), self.article.lower())
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 9)
        self.assertEqual(self.article.count('class="short-stack-table" role="region" tabindex="0"'), 3)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 3)
        self.assertIn('poker-short-stack.css?v=', self.article)
        self.assertNotIn('\N{EM DASH}', self.article)
        for fragment in ('#bridge-ledger', '#bridge-shoves', '#bridge-opens',
                         '#bridge-rejam', '#bridge-defense', '#bridge-sb',
                         '#bridge-short-raise', '#bridge-ev', '#bridge-practice'):
            self.assertIn(fragment, self.article)

    def test_pot_has_exactly_one_ante(self):
        initial = Fraction(1, 2) + 1 + 1
        self.assertEqual(initial, Fraction(5, 2))
        self.assertIn('0.5 + 1 + 1 = 2.5 BB', self.article)
        self.assertIn('There is one BBA per hand, not nine', self.article)

    def test_six_eight_ten_bb_shoves_vs_covering_bb(self):
        initial = Fraction(5, 2)
        for shove, extra, final, percent in (
            (6, 5, Fraction(27, 2), '37.04%'),
            (8, 7, Fraction(35, 2), '40%'),
            (10, 9, Fraction(43, 2), '41.86%'),
        ):
            self.assertEqual(shove - 1, extra)
            self.assertEqual(initial + shove + extra, final)
            self.assertAlmostEqual(float(Fraction(extra) / final) * 100,
                                   float(percent[:-1]), places=2)
            self.assertIn(f'{extra} / {float(final):g}', self.article)
            self.assertIn(percent, self.article)
        self.assertEqual(8 + initial, Fraction(21, 2))
        self.assertEqual(8 + initial - 8, initial)
        self.assertIn('uncalled 8 BB is returned', self.article)

    def test_two_blind_opens_preserve_a_flop_and_spr(self):
        pot = Fraction(5, 2) + 2 + 1
        self.assertEqual(pot, Fraction(11, 2))
        for stack, behind, spr in ((6, 4, '0.73 SPR'),
                                   (8, 6, '1.09 SPR'),
                                   (10, 8, '1.45 SPR')):
            self.assertEqual(stack - 2, behind)
            self.assertAlmostEqual(float(Fraction(behind) / pot),
                                   float(spr.split()[0]), places=2)
            self.assertIn(spr, self.article)
        self.assertIn('further betting', self.article)

    def test_full_eight_bb_rejam_vs_hj_open(self):
        initial = Fraction(5, 2)
        hj_open = Fraction(5, 2)
        co_shove = 8
        call = co_shove - hj_open
        final = initial + hj_open + co_shove + call
        self.assertEqual(call, Fraction(11, 2))
        self.assertEqual(final, Fraction(37, 2))
        self.assertAlmostEqual(float(call / final) * 100, 29.73, places=2)
        self.assertEqual(20 - co_shove, 12)
        returned = co_shove - hj_open
        self.assertEqual(returned, Fraction(11, 2))
        self.assertEqual(initial + 2 * hj_open, Fraction(15, 2))
        self.assertEqual(co_shove + initial + hj_open, 13)
        self.assertIn('18.5 BB', self.article)
        self.assertIn('29.73%', self.article)
        self.assertIn('13 BB', self.article)
        self.assertIn('net gain of 5 BB', self.article)

    def test_big_blind_defends_button_shove_vs_open_separately(self):
        start_bb = 12
        after_post = start_bb - 1 - 1
        self.assertEqual(after_post, 10)
        called_minraise_pot = Fraction(5, 2) + 2 + (2 - 1)
        called_shove_pot = Fraction(5, 2) + 8 + (8 - 1)
        self.assertEqual(called_minraise_pot, Fraction(11, 2))
        self.assertEqual(called_shove_pot, Fraction(35, 2))
        self.assertEqual(after_post - 1, 9)
        self.assertEqual(after_post - 7, 3)
        self.assertEqual(Fraction(1) / called_minraise_pot, Fraction(2, 11))
        self.assertEqual(Fraction(7) / called_shove_pot, Fraction(2, 5))
        for phrase in ('18.18%', '40%', 'not', 'showdown-equity requirement',
                       'more betting is possible'):
            self.assertIn(phrase, self.article)

    def test_small_blind_first_in_ante_and_profit_baselines(self):
        start_sb = 8
        sb_post = Fraction(1, 2)
        sb_extra = start_sb - sb_post
        bb_extra = start_sb - 1
        contested = Fraction(5, 2) + sb_extra + bb_extra
        self.assertEqual(contested, 17)
        self.assertAlmostEqual(float(Fraction(bb_extra) / contested) * 100,
                               41.18, places=2)
        returned = start_sb - 1
        self.assertEqual(returned, 7)
        pot_awarded = 1 + 1 + 1
        final_sb = returned + pot_awarded
        self.assertEqual(final_sb, 10)
        self.assertEqual(final_sb - start_sb, 2)
        self.assertEqual(final_sb - (start_sb - sb_post), Fraction(5, 2))
        for phrase in ('41.18%', '7 BB', '3 BB',
                       '+2 BB', 'two different baselines'):
            self.assertIn(phrase, self.article)

    def test_short_four_bet_multiway_and_reopening_rights(self):
        initial = Fraction(5, 2)
        co_open = 2
        btn_call = 2
        bb_reraise_extra = 6 - 1
        pot_after_three_bet = initial + co_open + btn_call + bb_reraise_extra
        self.assertEqual(pot_after_three_bet, Fraction(23, 2))
        pot_after_co_jam = pot_after_three_bet + (8 - co_open)
        self.assertEqual(pot_after_co_jam, Fraction(35, 2))
        pot_after_btn_call = pot_after_co_jam + (8 - btn_call)
        self.assertEqual(pot_after_btn_call, Fraction(47, 2))
        pot_after_bb_call = pot_after_btn_call + (8 - 6)
        self.assertEqual(pot_after_bb_call, Fraction(51, 2))
        self.assertEqual(3 * 8 + Fraction(1, 2) + 1, pot_after_bb_call)
        self.assertEqual(6 - 2, 4)
        self.assertEqual(6 + 4, 10)
        self.assertLess(8, 10)
        for phrase in ('11.5 BB', '17.5 BB', '23.5 BB', '25.5 BB',
                       '10 BB total', 'does <strong>not reopen</strong>',
                       'later side pot'):
            self.assertIn(phrase, self.article)

    def test_conditional_chip_ev_and_ante_sensitivity(self):
        fold = Fraction(3, 10)
        for win, expected in ((Fraction(2, 5), Fraction(1, 20)),
                              (Fraction(3, 10), Fraction(-47, 40))):
            ev = fold * Fraction(5, 2) + (1 - fold) * (
                win * Fraction(19, 2) - (1 - win) * 8)
            self.assertEqual(ev, expected)
        self.assertEqual(Fraction(8) / (8 + Fraction(5, 2)), Fraction(16, 21))
        self.assertEqual(Fraction(8) / (8 + Fraction(3, 2)), Fraction(16, 19))
        for phrase in ('+0.05 BB', '−1.175 BB', '76.19%', '84.21%',
                       'Neither rate is observed'):
            self.assertIn(phrase, self.article)

    def test_contextual_inlinks_and_entrypoint_reachability(self):
        graph = poker_link_graph.scan(ROOT)
        new = next(record for record in graph['records'] if record['slug'] == self.slug)
        for source in ('three-to-five-bb-tournament-decisions',
                       'short-stack-decisions', 'facing-preflop-raises',
                       'blind-defense', 'reading-preflop-charts',
                       'tournament-equity', 'position-and-stacks'):
            self.assertIn('/poker/' + source + '/', new['prose_inbound_guides'])
        self.assertTrue(new['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(new['inbound_count'], 7)
        self.assertGreaterEqual(new['outbound_count'], 8)


if __name__ == '__main__':
    unittest.main(verbosity=2)
