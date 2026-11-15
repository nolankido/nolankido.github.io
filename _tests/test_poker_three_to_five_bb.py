"""Turn 10: verify very-short-stack pot geometry and public discovery routes."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class ThreeToFiveBBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'three-to-five-bb-tournament-decisions'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_discoverable_with_canonical_metadata(self):
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

    def test_scope_sources_legal_tree_and_exercises(self):
        for phrase in ('nine-handed', 'single 1 BB big-blind ante',
                       'Stacks are stated', 'before', 'After-play study only',
                       'Poker TDA', '2026 Rules Version 1.1', 'Rule 49',
                       'HoldemResources', 'GTO Wizard', 'fictional',
                       'No proprietary chart', 'no solver',
                       'not a promise of profitable gambling',
                       'Prepared with AI assistance',
                       'The short all-in price is tiny'):
            self.assertIn(phrase.lower(), self.article.lower())
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count('class="short-stack-table" role="region" tabindex="0"'), 2)
        self.assertIn('poker-short-stack.css?v=', self.article)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 2)
        self.assertNotIn('\N{EM DASH}', self.article)
        for branch in ('#short-ledger', '#short-depths', '#short-seats',
                       '#short-ev', '#short-small-raise', '#short-posted-bb',
                       '#short-reshoves', '#short-practice'):
            self.assertIn(branch, self.article)

    def test_initial_pot_has_one_ante(self):
        sb = Fraction(1, 2)
        bb = Fraction(1)
        ante = Fraction(1)
        self.assertEqual(sb + bb + ante, Fraction(5, 2))
        self.assertIn('0.5 + 1 + 1 = 2.5 BB', self.article)
        self.assertIn('once per hand', self.article)
        self.assertIn('not a credit toward a later call', self.article)

    def test_three_four_five_bb_shoves_and_bb_call_prices(self):
        pot = Fraction(5, 2)
        for shove, extra_call, final_pot, percentage in (
            (3, 2, Fraction(15, 2), '26.67%'),
            (4, 3, Fraction(19, 2), '31.58%'),
            (5, 4, Fraction(23, 2), '34.78%'),
        ):
            self.assertEqual(shove - 1, extra_call)
            self.assertEqual(pot + shove + extra_call, final_pot)
            self.assertAlmostEqual(float(Fraction(extra_call) / final_pot) * 100,
                                   float(percentage[:-1]), places=2)
            self.assertIn(f'{extra_call} / {float(final_pot):g} ≈ <strong>{percentage}',
                          self.article)
        self.assertEqual(4 + pot, Fraction(13, 2))
        self.assertEqual((4 + pot) - 4, pot)
        self.assertIn('unmatched 4 BB bet is returned', self.article)

    def test_call_prices_by_seat_are_separate_branches(self):
        pot = Fraction(5, 2)
        shove = 4
        for live_post, extra, expected_final, price in (
            (0, 4, Fraction(21, 2), '38.10%'),
            (Fraction(1, 2), Fraction(7, 2), Fraction(10), '35%'),
            (1, 3, Fraction(19, 2), '31.58%'),
        ):
            self.assertEqual(shove - live_post, extra)
            self.assertEqual(pot + shove + extra, expected_final)
            self.assertAlmostEqual(float(extra / expected_final) * 100,
                                   float(price[:-1]), places=2)
            self.assertIn(price, self.article)
        self.assertIn('exactly one', self.article)
        self.assertIn('not a three-way pot', self.article)

    def test_fold_and_showdown_sensitivity_is_conditional(self):
        fold = Fraction(3, 10)
        for win, expected in ((Fraction(2, 5), Fraction(61, 100)),
                              (Fraction(3, 10), Fraction(-11, 200))):
            value = fold * Fraction(5, 2) + (1 - fold) * (
                win * Fraction(11, 2) - (1 - win) * 4)
            self.assertEqual(value, expected)
        self.assertEqual(Fraction(4, 1) / (4 + Fraction(5, 2)), Fraction(8, 13))
        self.assertEqual(Fraction(4, 1) / (4 + Fraction(3, 2)), Fraction(8, 11))
        for phrase in ('+0.61 BB', '−0.055 BB', '61.54%', '72.73%',
                       'Neither f nor q was measured'):
            self.assertIn(phrase, self.article)

    def test_legal_minraise_and_response_tree(self):
        pot = Fraction(5, 2)
        open_to = 2
        bb_already_posted = 1
        self.assertEqual(pot + open_to, Fraction(9, 2))
        self.assertEqual(pot + open_to + open_to - bb_already_posted, Fraction(11, 2))
        bb_reraise_to = 4
        self.assertEqual(pot + open_to + bb_reraise_to - bb_already_posted,
                         Fraction(15, 2))
        self.assertEqual(bb_reraise_to - open_to, 2)
        self.assertEqual(pot + 2 * bb_reraise_to - bb_already_posted,
                         Fraction(19, 2))
        for phrase in ('5.5 BB', '7.5 BB', '9.5 BB',
                       'A limp to 1 BB', 'cannot decide between them'):
            self.assertIn(phrase, self.article)

    def test_three_bb_big_blind_short_call_refund(self):
        bb_start = 3
        bb_remaining = bb_start - 1 - 1
        bb_live_total = 1 + bb_remaining
        co_start = 4
        unmatched = co_start - bb_live_total
        contested = bb_live_total * 2 + Fraction(1, 2) + 1
        self.assertEqual(bb_remaining, 1)
        self.assertEqual(unmatched, 2)
        self.assertEqual(contested, Fraction(11, 2))
        self.assertEqual(Fraction(bb_remaining) / contested, Fraction(2, 11))
        for phrase in ('unmatched excess returns', '5.5 BB', '18.18%',
                       'posting priority and eligibility rules'):
            self.assertIn(phrase, self.article)

    def test_full_and_short_rejam_are_not_confused(self):
        pot = Fraction(5, 2)
        hj_open = 2
        co_full_shove = 5
        hj_extra = co_full_shove - hj_open
        self.assertEqual(pot + hj_open + co_full_shove + hj_extra,
                         Fraction(25, 2))
        self.assertEqual(Fraction(hj_extra) / Fraction(25, 2), Fraction(6, 25))
        self.assertEqual(pot + 2 * hj_open, Fraction(13, 2))
        short_open = Fraction(5, 2)
        short_shove = Fraction(3)
        min_full_reraise = short_open + (short_open - 1)
        self.assertEqual(min_full_reraise, 4)
        self.assertLess(short_shove, min_full_reraise)
        short_extra = short_shove - short_open
        self.assertEqual(short_extra, Fraction(1, 2))
        self.assertEqual(pot + short_open + short_shove + short_extra,
                         Fraction(17, 2))
        self.assertEqual(short_extra / Fraction(17, 2), Fraction(1, 17))
        for phrase in ('12.5 BB', '6.5 BB', '24%', '8.5 BB', '5.88%',
                       'does <strong>not reopen</strong>'):
            self.assertIn(phrase, self.article)

    def test_five_contextual_inlinks_and_reachability(self):
        graph = poker_link_graph.scan(ROOT)
        target = next(record for record in graph['records']
                      if record['slug'] == self.slug)
        for source in ('short-stack-decisions', 'reading-preflop-charts',
                       'tournament-equity', 'tournament-formats',
                       'poker-rules-and-fair-play'):
            self.assertIn('/poker/' + source + '/', target['prose_inbound_guides'])
        self.assertTrue(target['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(target['inbound_count'], 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
