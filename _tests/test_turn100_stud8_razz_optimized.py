"""Turn 100: fail-closed seven-card Stud8 and Razz checks under optimized Python.

Standalone tests require only the existing fixed-case public Python download.
The final three integration tests require the full matching website checkout.
"""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import hashlib
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-stud8-razz-seven-card-check.py'
OUTPUT_SHA_NORMAL = '2fa8472b0cd8c2f42d7261d1f23dc781e32b9b79dff1a6656da5fb2ad5cd7639'
OUTPUT_SHA_SELF_TEST = '8a59e8dabcb063eff9ca63551c0647414180160f62da10ef5011d59920743185'


def run(source, mode='', self_test=True):
    args = [sys.executable] + ([mode] if mode else []) + [str(source)]
    if self_test:
        args.append('--self-test')
    return subprocess.run(args, text=True, capture_output=True, timeout=25)


def load():
    spec = spec_from_file_location('stud8_razz_turn100', SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Missing original published Stud8/Razz verifier')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Turn100StandaloneStud8Razz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')
        cls.mod = load()

    def test_original_self_test_output_is_unchanged_in_all_modes(self):
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                result = run(SCRIPT, mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, '')
                self.assertIn('PASS: Stud8/razz showdown, low qualifier, tie, street and exposure fixtures', result.stdout)
                self.assertEqual(hashlib.sha256(result.stdout.encode()).hexdigest(), OUTPUT_SHA_SELF_TEST)

    def test_default_output_unchanged_and_no_false_pass_line(self):
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                result = run(SCRIPT, mode, self_test=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(hashlib.sha256(result.stdout.encode()).hexdigest(), OUTPUT_SHA_NORMAL)
                self.assertNotIn('PASS:', result.stdout)
                for marker in ('Stud8 three-way quarter', 'Stud8 scoop', 'Razz wheel tie',
                               'Third-street bring-in', 'Fourth-street first'):
                    self.assertIn(marker, result.stdout)

    def test_no_optimization_elidable_asserts_and_exact_check_counts(self):
        tree = ast.parse(self.source)
        self.assertFalse([node for node in ast.walk(tree) if isinstance(node, ast.Assert)])
        fixture = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify')
        calls = [n for n in ast.walk(fixture) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'require']
        self.assertEqual(len(calls), 25)
        self.assertIn("raise AssertionError('Stud8/Razz fixed check failed: ' + case)", self.source)

    def test_stud8_and_razz_awards_have_independent_runtime_guards(self):
        self.assertEqual(self.source.count('if sum(results.values()) != Fraction(pot):'), 2)
        self.assertIn("raise ArithmeticError('Stud8 awards do not conserve the eligible pot')", self.source)
        self.assertIn("raise ArithmeticError('Razz awards do not conserve the eligible pot')", self.source)

    def mutate_and_reject(self, original, changed, message, import_only=False):
        self.assertEqual(self.source.count(original), 1)
        mutant = self.source.replace(original, changed, 1)
        with TemporaryDirectory() as folder:
            file = Path(folder) / 'stud8-razz-mutated.py'
            file.write_text(mutant, encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                with self.subTest(mode=mode or 'normal', case=message):
                    if import_only:
                        expr = ('import runpy; s = runpy.run_path(' + repr(str(file)) + '); '
                                + import_only)
                        args = [sys.executable] + ([mode] if mode else []) + ['-c', expr]
                        result = subprocess.run(args, capture_output=True, text=True, timeout=25)
                    else:
                        result = run(file, mode)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(message, result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_mutated_wheel_ranking_cannot_falsely_pass(self):
        old = "rank_high_five(('As', '2s', '3s', '4s', '5s')) == (8, 5)"
        new = "rank_high_five(('As', '2s', '3s', '4s', '5s')) == (8, 6)"
        self.mutate_and_reject(old, new, 'Stud8/Razz fixed check failed: wheel straight flush high')

    def test_mutated_stud8_award_is_rejected_under_every_python_mode(self):
        old = 'high_pool = Fraction(pot, 2) if lows else Fraction(pot)'
        new = 'high_pool = Fraction(pot, 2) if lows else Fraction(pot) - 1'
        self.mutate_and_reject(old, new, 'Stud8 awards do not conserve the eligible pot',
                               "s['stud8_awards'](s['VARIANT_PLAYERS'], 200)")

    def test_mutated_razz_award_is_rejected_under_every_python_mode(self):
        old = 'Fraction(pot, len(winners)) if name in winners else Fraction(0)'
        new = '(Fraction(pot, len(winners)) - 1) if name in winners else Fraction(0)'
        self.mutate_and_reject(old, new, 'Razz awards do not conserve the eligible pot',
                               "s['razz_awards'](s['VARIANT_PLAYERS'], 200)")

    def test_runtime_split_awards_conserve_odd_pots_as_fractions(self):
        cases = (
            (self.mod.stud8_awards, self.mod.QUARTER_PLAYERS, 301),
            (self.mod.stud8_awards, self.mod.SCOOP_PLAYERS, 201),
            (self.mod.stud8_awards, self.mod.VARIANT_PLAYERS, 199),
            (self.mod.razz_awards, self.mod.RAZZ_TIE_PLAYERS, 301),
            (self.mod.razz_awards, self.mod.VARIANT_PLAYERS, 199),
        )
        for function, players, chips in cases:
            with self.subTest(function=function.__name__, chips=chips):
                awards = function(players, chips)
                self.assertEqual(sum(awards.values()), Fraction(chips))
                self.assertTrue(all(isinstance(a, Fraction) for a in awards.values()))
        self.assertEqual(self.mod.stud8_awards(self.mod.QUARTER_PLAYERS, 301),
                         {'A': Fraction(903, 4), 'B': Fraction(301, 4), 'C': Fraction(0)})
        self.assertEqual(self.mod.razz_awards(self.mod.RAZZ_TIE_PLAYERS, 301),
                         {'A': Fraction(301, 2), 'B': Fraction(301, 2)})

    def test_stud_and_razz_award_different_winners_with_same_seven_cards(self):
        self.assertEqual(self.mod.stud8_awards(self.mod.VARIANT_PLAYERS, 200),
                         {'A': Fraction(200), 'B': Fraction(0)})
        self.assertEqual(self.mod.razz_awards(self.mod.VARIANT_PLAYERS, 200),
                         {'A': Fraction(0), 'B': Fraction(200)})
        self.assertEqual(self.mod.ace_five_five(('As','2s','3s','4s','5s')),
                         (0,5,4,3,2,1))

    def test_invalid_cards_or_pot_still_raise(self):
        with self.assertRaises(ValueError):
            self.mod.stud8_awards(self.mod.QUARTER_PLAYERS, -1)
        with self.assertRaises(ValueError):
            self.mod.razz_awards(self.mod.RAZZ_TIE_PLAYERS, -1)
        with self.assertRaises(ValueError):
            self.mod.seven_scores(('As',)*7)
        with self.assertRaises(ValueError):
            self.mod.seven_scores(('As','2c','3d'))
        with self.assertRaises(ValueError):
            self.mod.razz_awards({'A':self.mod.RAZZ_TIE_PLAYERS['A'],
                                  'B':self.mod.RAZZ_TIE_PLAYERS['A']}, 200)

    def test_standard_library_imports_no_network_no_new_inputs(self):
        tree = ast.parse(self.source)
        packages = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                packages.update(item.name.split('.')[0] for item in node.names)
            elif isinstance(node, ast.ImportFrom):
                packages.add(node.module.split('.')[0])
        self.assertEqual(packages, {'__future__','argparse','collections','fractions','itertools'})
        for forbidden in ('requests', 'urllib', 'socket', 'input(', 'fetch(', 'read_text(',
                          'write_text(', 'localStorage', chr(0x2014)):
            self.assertNotIn(forbidden, self.source)


class Turn100SiteIntegration(unittest.TestCase):
    def test_existing_indexed_stud_guide_links_remain(self):
        authored = (ROOT / '_source/poker/stud-hilo-razz-hand-reading.html').read_text(encoding='utf-8')
        public = (ROOT / 'poker/stud-hilo-razz-hand-reading/index.html').read_text(encoding='utf-8')
        path = '/downloads/poker-stud8-razz-seven-card-check.py'
        self.assertIn('href="' + path + '"', authored)
        self.assertIn('href="' + path + '"', public)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/stud-hilo-razz-hand-reading/">', public)

    def test_existing_public_release_inventory_and_sitemap_scope(self):
        live_check = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(live_check.count("'downloads/poker-stud8-razz-seven-card-check.py'"), 1)
        self.assertNotIn('poker-stud8-razz-seven-card-check.py', (ROOT/'sitemap.xml').read_text(encoding='utf-8'))

    def test_no_actions_and_manual_regression_registration(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertTrue((ROOT / '_tests/test_poker_stud8_razz.py').is_file())
        self.assertIn('test_turn100_stud8_razz_optimized.py', runner)
        workflows = ROOT / '.github/workflows'
        self.assertFalse(workflows.exists() and any(f.is_file() and f.suffix.lower() in ('.yaml','.yml') for f in workflows.iterdir()))


if __name__ == '__main__':
    unittest.main()
