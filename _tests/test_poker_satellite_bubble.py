"""Turn 12: independently verify a two-seat satellite ICM lesson."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


def finish_probabilities(player, stacks):
    """Exact three-player Malmuth-Harville ICM, all permutations."""
    indices = list(range(3))
    total = sum(stacks)
    result = [Fraction(0), Fraction(0), Fraction(0)]
    for first in indices:
        for second in indices:
            if second == first:
                continue
            third = next(i for i in indices if i not in (first, second))
            likelihood = Fraction(stacks[first], total) * Fraction(
                stacks[second], total - stacks[first]
            )
            rank = (first, second, third).index(player)
            result[rank] += likelihood
    return tuple(result)


class SatelliteBubbleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'satellite-bubble-seat-equity'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_and_discovery(self):
        pages = [p for p in self.pages if p['path'] == self.route]
        self.assertEqual(len(pages), 1)
        self.assertTrue(pages[0]['poker_guide'])
        self.assertEqual(pages[0]['date'], '2026-11-15')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for output in ('poker/library/index.html', 'poker/find/index.html',
                       'poker/topics/tournaments/index.html',
                       'poker/topics/strategy/index.html',
                       'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(output)], output)

    def test_visible_model_conventions_and_transparency(self):
        for phrase in ('For after-play study only', 'three remaining players',
                       'two identical seats', 'no ante', 'before posting',
                       'fictional', 'not</em> a solver result',
                       'Standard ICM', 'GTO Wizard', 'HoldemResources',
                       'Prepared with AI assistance', 'promise of gambling profit'):
            self.assertIn(phrase.lower(), self.article.lower())
        self.assertNotIn('\N{EM DASH}', self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count('class="short-stack-table" role="region" tabindex="0"'), 3)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 3)
        self.assertIn('poker-short-stack.css?v=', self.article)
        for fragment in ('#sat-structure', '#sat-hand', '#sat-model', '#sat-call',
                         '#sat-payouts', '#sat-short', '#sat-practice', '#sat-record'):
            self.assertIn(fragment, self.article)

    def test_blinds_and_pot_chips_are_conserved(self):
        a, b, c = Fraction(10), Fraction(10), Fraction(1)
        initial = Fraction(1, 2) + 1
        sb_added = a - Fraction(1, 2)
        self.assertEqual(initial, Fraction(3, 2))
        self.assertEqual(initial + sb_added, 11)
        extra_call = a - 1
        self.assertEqual(extra_call, 9)
        self.assertEqual(initial + sb_added + extra_call, 20)
        self.assertEqual((a, b, c), (10, 10, 1))
        for branch in ((11, 9, 1), (0, 20, 1), (20, 0, 1)):
            self.assertEqual(sum(branch), a + b + c)
        for text in ('0.5 + 1 = <strong>1.5 BB</strong>',
                     '<strong>11 BB</strong>', '11 + 9 = 20 BB',
                     'Pot: 0.5 + 1', 'A 11, B 9, C 1'):
            self.assertIn(text, self.article)

    def test_fold_state_icm_by_all_finish_permutations(self):
        # A, B, C after BB folds an SB open-jam.
        stacks = (11, 9, 1)
        first, second, third = finish_probabilities(1, stacks)
        self.assertEqual(first, Fraction(3, 7))
        self.assertEqual(second, Fraction(69, 140))
        self.assertEqual(third, Fraction(11, 140))
        self.assertEqual(first + second, Fraction(129, 140))
        self.assertAlmostEqual(float(first + second) * 100, 92.14, places=2)
        for text in ('3 / 7', '33 / 70', '3 / 140',
                     '69 / 140', '129 / 140', '92.14%'):
            self.assertIn(text, self.article)

    def test_two_seats_conserved_across_all_players(self):
        stacks = (11, 9, 1)
        tickets = [sum(finish_probabilities(i, stacks)[:2]) for i in range(3)]
        self.assertEqual(tickets, [Fraction(33, 35),
                                   Fraction(129, 140),
                                   Fraction(19, 140)])
        self.assertEqual(sum(tickets), 2)
        self.assertIn('19 / 140', self.article)
        self.assertIn('33 / 35', self.article)
        self.assertIn('two complete seat units', self.article)

    def test_closed_action_chip_price_and_seat_threshold(self):
        call_cost = 9
        called_pot = 20
        fold_chips = 9
        fold_seat = Fraction(129, 140)
        self.assertEqual(Fraction(call_cost, called_pot), Fraction(9, 20))
        self.assertEqual(Fraction(fold_chips, called_pot), Fraction(9, 20))
        self.assertEqual(fold_seat / 1, Fraction(129, 140))
        self.assertIn('9 / 20 = 45%', self.article)
        self.assertIn('q = 129 / 140', self.article)

    def test_stipulated_sixty_percent_win_inverts_objective(self):
        q = Fraction(3, 5)
        call_chips = q * 20
        call_seats = q
        self.assertEqual(call_chips, 12)
        self.assertEqual(call_chips - 9, 3)
        self.assertEqual(Fraction(129, 140) - call_seats,
                         Fraction(9, 28))
        self.assertAlmostEqual(float(Fraction(9, 28)) * 100,
                               32.14, places=2)
        self.assertIn('+3 BB', self.article)
        self.assertIn('−32.14 percentage points', self.article)
        self.assertIn('0.60 × 20', self.article)

    def test_winner_only_payout_collapses_to_chip_share(self):
        fold = finish_probabilities(1, (11, 9, 1))[0]
        win = finish_probabilities(1, (0, 20, 1))[0]
        self.assertEqual(fold, Fraction(3, 7))
        self.assertEqual(win, Fraction(20, 21))
        self.assertEqual(fold / win, Fraction(9, 20))
        self.assertIn('20 / 21', self.article)

    def test_seventy_thirty_payout_is_not_a_satellite(self):
        fold = finish_probabilities(1, (11, 9, 1))
        win = finish_probabilities(1, (0, 20, 1))
        fold_dollars = 70 * fold[0] + 30 * fold[1]
        win_dollars = 70 * win[0] + 30 * win[1]
        self.assertEqual(fold_dollars, Fraction(627, 14))
        self.assertEqual(win_dollars, Fraction(1430, 21))
        self.assertEqual(fold_dollars / win_dollars, Fraction(1881, 2860))
        self.assertAlmostEqual(float(fold_dollars / win_dollars) * 100,
                               65.77, places=2)
        for token in ('$627 / 14', '$1430 / 21', '1881 / 2860', '65.77%'):
            self.assertIn(token, self.article)

    def test_payout_comparisons_are_explicitly_conditional(self):
        for phrase in ('winner only', 'two equal seats', '$70 first',
                       'no ties', 'unknown parameter', 'a universal preflop',
                       'not the same problem', 'future blind',
                       'milestone', 'different structures'):
            self.assertIn(phrase.lower(), self.article.lower())

    def test_contextual_inlinks_and_entrypoint_reachability(self):
        graph = poker_link_graph.scan(ROOT)
        new = next(r for r in graph['records'] if r['slug'] == self.slug)
        for source in ('tournament-formats', 'tournament-equity',
                       'six-to-ten-bb-tournament-decisions',
                       'short-stack-decisions', 'choosing-a-tournament',
                       'reading-preflop-charts', 'practice-room'):
            self.assertIn('/poker/' + source + '/',
                          new['prose_inbound_guides'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())
        self.assertTrue(new['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(new['inbound_count'], 7)
        self.assertGreaterEqual(new['outbound_count'], 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
