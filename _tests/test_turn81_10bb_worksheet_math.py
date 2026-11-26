"""Turn 81: independently reproduce the fictional ICM worksheet before release.

Python standard library only for the model; local site asset inventory required
by the last tests. No network, real-hand ranges, data submission or GitHub Actions.
"""
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import runpy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
WORKSHEET = ROOT / 'downloads/ten-bb-tournament-checklist.md'
CHECKER = ROOT / 'downloads/ten-bb-playbook-icm-verify.py'
ROUTE = '/downloads/ten-bb-tournament-checklist.md'


def hero_probabilities(stacks):
    """Independent three-player ICM enumeration; do not call the published code."""
    if len(stacks) != 3 or min(stacks) <= 0:
        raise ValueError('Surviving ICM states need exactly three positive stacks')
    totals = [F(0), F(0), F(0)]
    for order in permutations(range(3)):
        probability = F(1)
        chips = sum(stacks)
        for seat in order:
            probability *= F(stacks[seat], chips)
            chips -= stacks[seat]
        totals[order.index(0)] += probability
    return tuple(totals)


def independent_value(stacks):
    return sum(p * prize for p, prize in zip(
        hero_probabilities(stacks), (F(100), F(60), F(40))))


def worksheet_issues(text):
    required = (
        '# Ten Big Blinds: Six-Check Tournament Decision Sheet',
        '## Three calculations', '## Practice review',
        '## Worked example to revisit', '### Reproduce the prize-value comparison',
        '### Try two assumptions before looking up the results',
        '**Answer key (round dollars to cents)**',
        '| Fold | (9, 21, 5) | 9/35 | 3/7 | 11/35 | $64 |',
        '| Call and win | (20, 10, 5) | 4/7 | 34/105 | 11/105 | $1696/21, about $80.76 |',
        '| Call and lose | (0, 30, 5) | 0 | 0 | 1 | $40 |',
        '63/107', '58.88%', '45%',
        '| 45% | 0 BB | $58.34 | −$5.66 |',
        '| 50% | +1 BB | $60.38 | −$3.62 |',
        '| 55% | +2 BB | $62.42 | −$1.58 |',
        '| 60% | +3 BB | $64.46 | +$0.46 |',
        'no ties, no bounties or deals',
        'not a solver verdict',
        'https://nolankido.com/downloads/ten-bb-playbook-icm-verify.py',
    )
    return [token for token in required if token not in text]


class Turn81SelfContainedICM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKSHEET.read_text(encoding='utf-8')
        cls.model = runpy.run_path(str(CHECKER))['model']()

    def test_worksheet_still_begins_with_six_checks_and_no_at_table_recommendation(self):
        self.assertEqual(worksheet_issues(self.text), [])
        for number in range(1, 7):
            self.assertEqual(self.text.count('| **' + str(number) + '. '), 1)
        self.assertIn('study away from the table', self.text)
        self.assertIn('not a universal shove chart', self.text)
        self.assertNotIn(chr(0x2014), self.text)

    def test_three_states_conserve_chips_and_bust_receives_third_place(self):
        for stacks in ((9, 21, 5), (20, 10, 5), (0, 30, 5)):
            self.assertEqual(sum(stacks), 35)
        self.assertEqual(self.model['fold_stacks_bb'], (9, 21, 5))
        self.assertEqual(self.model['call_win_stacks_bb'], (20, 10, 5))
        self.assertEqual(self.model['call_lose_stacks_bb'], (0, 30, 5))
        self.assertEqual(self.model['payouts_dollars'], (100, 60, 40))
        self.assertEqual(F(self.model['lose_prize_exact']), F(40))

    def test_independent_finish_probabilities_and_exact_prize_values(self):
        self.assertEqual(hero_probabilities((9, 21, 5)), (F(9, 35), F(3, 7), F(11, 35)))
        self.assertEqual(hero_probabilities((20, 10, 5)), (F(4, 7), F(34, 105), F(11, 105)))
        self.assertEqual(independent_value((9, 21, 5)), F(64))
        self.assertEqual(independent_value((20, 10, 5)), F(1696, 21))
        self.assertEqual(F(self.model['fold_prize_exact']), F(64))
        self.assertEqual(F(self.model['win_prize_exact']), F(1696, 21))

    def test_threshold_is_from_prize_values_not_arbitrary_chart(self):
        fold = independent_value((9, 21, 5))
        win = independent_value((20, 10, 5))
        loss = F(40)
        threshold = (fold - loss) / (win - loss)
        self.assertEqual(threshold, F(63, 107))
        self.assertEqual(F(self.model['icm_break_even_exact']), threshold)
        self.assertEqual(F(self.model['chip_price_exact']), F(9, 20))
        self.assertAlmostEqual(float(threshold * 100), 58.88, delta=0.01)
        self.assertAlmostEqual(float((threshold - F(9, 20)) * 100), 13.88, delta=0.01)

    def test_sensitivity_rows_recompute_exactly_with_both_objectives(self):
        fold, win = F(64), F(1696, 21)
        expected = {
            45: (F(0), '$58.34', '−$5.66'),
            50: (F(1), '$60.38', '−$3.62'),
            55: (F(2), '$62.42', '−$1.58'),
            60: (F(3), '$64.46', '+$0.46'),
        }
        self.assertEqual([r['assumed_win_percent'] for r in self.model['hypothetical_win_probabilities']],
                         [45, 50, 55, 60])
        for row in self.model['hypothetical_win_probabilities']:
            percent = row['assumed_win_percent']
            p = F(percent, 100)
            chip_delta = 20 * p - 9
            call = p * win + (1 - p) * 40
            prize_delta = call - fold
            chip_expected, value_label, delta_label = expected[percent]
            with self.subTest(win_percent=percent):
                self.assertEqual(chip_delta, chip_expected)
                self.assertEqual(F(row['icm_call_minus_fold_exact']), prize_delta)
                self.assertAlmostEqual(row['icm_call_value_dollars'], float(call))
                self.assertAlmostEqual(row['icm_call_minus_fold_dollars'], float(prize_delta))
                self.assertIn(value_label, self.text)
                self.assertIn(delta_label, self.text)

    def test_negative_controls_reject_changed_math_and_missing_disclosure(self):
        for old, new in (
            ('63/107', '62/107'),
            ('$1696/21', '$1696/22'),
            ('| 55% | +2 BB | $62.42 | −$1.58 |', '| 55% | +2 BB | $62.42 | +$1.58 |'),
            ('no ties, no bounties or deals', 'all opponents known'),
            ('https://nolankido.com/downloads/ten-bb-playbook-icm-verify.py', '/missing.py'),
        ):
            with self.subTest(old=old):
                corrupt = self.text.replace(old, new)
                self.assertNotEqual(corrupt, self.text)
                self.assertTrue(worksheet_issues(corrupt))

    def test_download_still_registered_for_exact_source_byte_release(self):
        import check_live
        import tenbb_companion
        self.assertEqual(tenbb_companion.WORKSHEET, ROUTE.lstrip('/'))
        targets = check_live.targets(ROOT)
        self.assertEqual(targets[ROUTE], (200, WORKSHEET.read_bytes()))
        guide = (ROOT / 'poker/10bb/index.html').read_text(encoding='utf-8')
        self.assertIn('href="' + ROUTE + '"', guide)
        self.assertIn('href="/downloads/ten-bb-playbook-icm-verify.py"', guide)
        self.assertEqual(tenbb_companion.record(ROOT)['route'], '/poker/10bb/')

    def test_no_new_canonical_page_and_manual_release_only(self):
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('<loc>https://nolankido.com' + ROUTE + '</loc>', sitemap)
        self.assertEqual(sitemap.count('<loc>'), 231)
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn81_10bb_worksheet_math.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            file.is_file() and file.suffix.lower() in ('.yml', '.yaml')
            for file in actions.iterdir()))

if __name__ == '__main__':
    unittest.main()
