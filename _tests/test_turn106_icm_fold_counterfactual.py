"""Turn 106: same call states, different counterfactual folds and prize values."""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-multiway-icm-verify.py'
WORKBOOK = ROOT / 'downloads/poker-multiway-icm-workbook.md'
LINK = ('<a href="/downloads/poker-multiway-icm-workbook.md" download '
        'aria-label="Download the three-way side-pot ICM worksheet">Side-pot ICM worksheet</a>')


def load():
    spec = spec_from_file_location('turn106_model', SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Missing local verifier')
    obj = module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class FoldCounterfactualStandalone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load()
        cls.report = cls.model.verify()['fold_baseline_sensitivity']
        cls.a = cls.report['x_survives']
        cls.b = cls.report['y_eliminates_x']
        cls.workbook = WORKBOOK.read_text(encoding='utf-8')
        cls.code = SCRIPT.read_text(encoding='utf-8')

    def test_all_original_call_states_and_probabilities_are_identical(self):
        for case in (self.a, self.b):
            self.assertEqual([F(x['probability']) for x in case['branches']],
                             [F(1, 5), F(1, 4), F(11, 20)])
            self.assertEqual([x['call']['stacks_X_H_Y'] for x in case['branches']],
                             [[0, 27, 0], [12, 15, 0], [12, 5, 10]])
            self.assertEqual(case['main_win_probability'], '1/5')
            self.assertEqual(case['side_win_probability'], '9/20')
            self.assertEqual(case['hero_expected_chips'], {'fold': '10', 'call': '119/10'})
            self.assertEqual(case['hero_call_minus_fold_chips'], '19/10')
        self.assertEqual(self.a['expected_prizes_X_H_Y']['call'],
                         self.b['expected_prizes_X_H_Y']['call'])

    def test_different_fold_settlements_and_single_opponent_bust(self):
        self.assertEqual([row['fold']['stacks_X_H_Y'] for row in self.a['branches']],
                         [[12, 10, 5]] * 3)
        self.assertEqual([row['fold']['stacks_X_H_Y'] for row in self.b['branches']],
                         [[0, 10, 17], [12, 10, 5], [12, 10, 5]])
        self.assertEqual([row['ranking'] for row in self.a['branches']],
                         ['H > X > Y', 'X > H > Y', 'X > Y > H'])
        self.assertEqual([row['ranking'] for row in self.b['branches']],
                         ['H > Y > X', 'X > H > Y', 'X > Y > H'])

    def test_exact_arithmetic_by_independent_closed_form(self):
        f_three = 70 * F(10, 27) + 30 * (F(12, 27)*F(10, 15) + F(5, 27)*F(10, 22))
        f_two = 30 + 40 * F(10, 27)
        c_three = 70 * F(5, 27) + 30 * (F(12, 27)*F(5, 15) + F(10, 27)*F(5, 17))
        c_two = 30 + 40 * F(15, 27)
        call = F(1, 5)*70 + F(1, 4)*c_two + F(11, 20)*c_three
        fold_a = f_three
        fold_b = F(4, 5)*f_three + F(1, 5)*f_two
        self.assertEqual((call, fold_a, fold_b), (F(17638,459), F(11090,297), F(11534,297)))
        self.assertEqual((call-fold_a, call-fold_b), (F(5488,5049), -F(2060,5049)))
        self.assertEqual(12*F(1, 5)+10*F(9, 20)-5, F(19, 10))
        self.assertEqual(F(self.a['hero_call_minus_fold_prizes']), call-fold_a)
        self.assertEqual(F(self.b['hero_call_minus_fold_prizes']), call-fold_b)
        self.assertGreater(call, fold_a)
        self.assertLess(call, fold_b)

    def test_every_branch_and_expectation_conserves_both_pools(self):
        for case in (self.a, self.b):
            for row in case['branches']:
                for action in ('fold', 'call'):
                    self.assertEqual(sum(row[action]['stacks_X_H_Y']), 27)
                    self.assertEqual(sum(map(F, row[action]['prize_equities_X_H_Y'])), 100)
            for values in case['expected_prizes_X_H_Y'].values():
                self.assertEqual(sum(map(F, values)), 100)

    def test_duplicate_rankings_cannot_silently_reweight_the_distribution(self):
        with self.assertRaisesRegex(ArithmeticError, 'each strict ranking appears at most once'):
            self.model._report_for_weights(((('X','H','Y'),F(1,2)),
                                            (('X','H','Y'),F(1,2))))

    def test_workbook_keeps_exact_results_and_counterfactual_scope(self):
        for phrase in ('## 6. Advanced comparison: the missing counterfactual fold',
                       '20% main-pot win chance', '45% side-pot win chance', '+1.9 BB',
                       '$17638/459 ≈ $38.43', '$11090/297 ≈ $37.34', '$11534/297 ≈ $38.84',
                       '$5488/5049', '−$2060/5049', '+$1.09', '−$0.41',
                       'does not establish that these particular joint distributions are realizable',
                       'a counterfactual outcome may be unobservable',
                       'fold_baseline_sensitivity'):
            self.assertIn(phrase, self.workbook)
        self.assertNotIn(chr(0x2014), self.workbook)

    def test_legacy_fixture_retains_original_exact_values(self):
        original = self.model.branch_report()
        new = self.model.verify()
        self.assertEqual({k: v for k, v in new.items() if k != 'fold_baseline_sensitivity'}, original)
        self.assertEqual(new['hero_call_minus_fold_prizes'], '-15226/5049')

    def test_corrupted_counterfactual_expected_value_fails_all_python_modes(self):
        old = "== F(11534, 297),"
        self.assertEqual(self.code.count(old), 1)
        with TemporaryDirectory() as temp:
            path = Path(temp)/'bad_fold.py'
            path.write_text(self.code.replace(old, "== F(11090, 297),",1), encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                with self.subTest(mode=mode or 'normal'):
                    args = [sys.executable] + ([mode] if mode else []) + [str(path), '--self-test']
                    result = subprocess.run(args, capture_output=True, text=True, timeout=15)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Multiway ICM check failed: Y-eliminates-X fold baseline', result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_unchanged_cli_and_report_are_optimization_safe(self):
        expected = self.model.verify()
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(self.code))))
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                args = [sys.executable] + ([mode] if mode else []) + [str(SCRIPT)]
                result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=15)
                self.assertEqual(json.loads(result.stdout), expected)
                result = subprocess.run(args+['--self-test'], check=True, capture_output=True, text=True, timeout=15)
                self.assertIn('PASS: fictional three-way', result.stdout)


class Turn106SiteIntegration(unittest.TestCase):
    def test_bounty_jump_navigation_and_original_core_estimate(self):
        source = (ROOT/'_source/poker/bounty-knockout-equity.html').read_text(encoding='utf-8')
        public = (ROOT/'poker/bounty-knockout-equity/index.html').read_text(encoding='utf-8')
        for html in (source, public):
            self.assertEqual(html.count(LINK), 1)
            self.assertEqual(html.count('class="poker-details viewer-question"'), 8)
            self.assertEqual(html.count('class="short-stack-table" role="region" tabindex="0"'), 4)
        sys.path.insert(0, str(ROOT/'_scripts'))
        import poker_read_time
        import poker_finder
        self.assertEqual(poker_read_time.minutes(source), 15)
        self.assertEqual(poker_read_time.minutes(source.replace(LINK,'')), 15)
        self.assertEqual(poker_finder.GuideText(source).sections,
                         poker_finder.GuideText(source.replace(LINK,'')).sections)
        self.assertIn('About 15 min read', public)

    def test_full_builder_parity_and_release_registration(self):
        sys.path.insert(0, str(ROOT/'_scripts'))
        import build
        path = Path('poker/bounty-knockout-equity/index.html')
        self.assertEqual(build.build_outputs()[path], (ROOT/path).read_text(encoding='utf-8'))
        self.assertIn('test_turn106_icm_fold_counterfactual.py',
                      (ROOT/'_scripts/local_release_checks.py').read_text(encoding='utf-8'))
        self.assertNotIn('poker-multiway-icm-workbook.md', (ROOT/'sitemap.xml').read_text(encoding='utf-8'))
        actions = ROOT/'.github/workflows'
        self.assertFalse(actions.exists() and any(p.suffix.lower() in ('.yaml','.yml') for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
