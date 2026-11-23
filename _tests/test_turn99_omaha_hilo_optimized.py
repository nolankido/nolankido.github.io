"""Turn 99: keep Omaha/8 split-pot and fixed-card checks active under -O/-OO.

Standalone checks use only the original verified fixture and revised public script.
Three broader checks require the complete, matching site repository.
"""
from fractions import Fraction
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-omaha-hilo-split-enumerator.py'


def run(source, mode='', extra=('--self-test',)):
    return subprocess.run([sys.executable] + ([mode] if mode else []) +
                          [str(source), *extra], text=True,
                          capture_output=True, timeout=35)


def load():
    spec = spec_from_file_location('omaha_hilo_turn99', SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Missing exact fixed-case script')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Turn99StandaloneOptimizationSafeOmaha(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')
        cls.mod = load()

    def test_self_test_succeeds_normal_and_both_optimized_modes(self):
        output = None
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                result = run(SCRIPT, mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS: independent high/low selection, exact pot conservation and every river', result.stdout)
                self.assertEqual(result.stderr, '')
                if output is None:
                    output = result.stdout
                self.assertEqual(result.stdout, output)

    def test_default_mode_preserves_all_original_published_examples(self):
        normal = run(SCRIPT, extra=())
        optimized = run(SCRIPT, '-O', extra=())
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(normal.stdout, optimized.stdout)
        self.assertNotIn('PASS:', normal.stdout)
        for text in ('Three-player quarter', 'Scoop', 'No qualifying low',
                     'Counterfeit river 2h', 'Protected low river 2h',
                     'B takes low on: 2c, 2d, 2h', 'A best low on 37'):
            self.assertIn(text, normal.stdout)

    def test_no_ast_assert_remains_and_21_checks_remain_reachable(self):
        tree = ast.parse(self.source)
        self.assertFalse([node for node in ast.walk(tree) if isinstance(node, ast.Assert)])
        fixture = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'verify')
        calls = [node for node in ast.walk(fixture) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == 'require']
        self.assertEqual(len(calls), 21)
        self.assertIn("raise AssertionError('Omaha/8 fixed case failed: ' + case)", self.source)

    def test_bad_rank_fixture_fails_normal_and_optimized(self):
        old = "high_five(('As', '2h', '3d', '4c', '5s')) == (4, 5)"
        new = "high_five(('As', '2h', '3d', '4c', '5s')) == (4, 6)"
        self.assertEqual(self.source.count(old), 1)
        self.assert_bad_case(self.source.replace(old, new, 1),
                             'Omaha/8 fixed case failed: high-hand wheel straight')

    def test_bad_pot_conservation_fails_normal_and_optimized(self):
        old = 'high_pool = Fraction(pot)\n'
        new = 'high_pool = Fraction(pot) - 1\n'
        self.assertEqual(self.source.count(old), 1)
        self.assert_bad_case(self.source.replace(old, new, 1),
                             'ArithmeticError: Omaha/8 awarded shares do not conserve the contested pot')

    def assert_bad_case(self, content, error):
        with TemporaryDirectory() as td:
            file = Path(td) / 'mutated.py'
            file.write_text(content, encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                with self.subTest(mode=mode or 'normal', error=error):
                    result = run(file, mode)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error, result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_runtime_conservation_retains_fractional_shares_on_odd_pots(self):
        for players, board, value in (
            (self.mod.QUARTER_PLAYERS, self.mod.QUARTER_BOARD, 301),
            (self.mod.SCOOP_PLAYERS, self.mod.SCOOP_BOARD, 241),
            (self.mod.NO_LOW_PLAYERS, self.mod.NO_LOW_BOARD, 239),
        ):
            with self.subTest(chips=value):
                output = self.mod.awards(players, board, value)
                self.assertEqual(sum(output.values()), Fraction(value))
                self.assertTrue(all(isinstance(v, Fraction) for v in output.values()))
        self.assertEqual(self.mod.awards(self.mod.QUARTER_PLAYERS, self.mod.QUARTER_BOARD, 301),
                         {'A': Fraction(903, 4), 'B': Fraction(301, 4), 'C': Fraction(0)})

    def test_runtime_conservation_uses_explicit_raising_guard(self):
        self.assertIn('if sum(result.values()) != Fraction(pot):', self.source)
        self.assertIn("raise ArithmeticError('Omaha/8 awarded shares do not conserve the contested pot')", self.source)
        self.assertEqual(self.source.count('if sum(result.values()) != Fraction(pot):'), 1)

    def test_invalid_cards_and_negative_pot_still_rejected(self):
        with self.assertRaises(ValueError):
            self.mod.awards({'A':self.mod.TURN_A, 'B':self.mod.TURN_B},
                            self.mod.TURN_BOARD)
        with self.assertRaises(ValueError):
            self.mod.awards(self.mod.QUARTER_PLAYERS, self.mod.QUARTER_BOARD, -1)
        with self.assertRaises(ValueError):
            self.mod.omaha_scores(('As', 'As', '2c', '3d'), self.mod.QUARTER_BOARD)
        with self.assertRaises(ValueError):
            self.mod.awards({'A':self.mod.SCOOP_PLAYERS['A'],
                             'B':self.mod.SCOOP_PLAYERS['A']}, self.mod.SCOOP_BOARD)

    def test_no_new_network_or_private_data_dependencies(self):
        parsed = ast.parse(self.source)
        imports = set()
        for node in parsed.body:
            if isinstance(node, ast.Import):
                imports.update(item.name.split('.')[0] for item in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.split('.')[0])
        self.assertEqual(imports, {'__future__', 'argparse', 'collections', 'fractions', 'itertools'})
        for token in ('requests', 'urllib', 'socket', 'localStorage', 'fetch(',
                      'read_text(', 'write_text(', chr(0x2014)):
            self.assertNotIn(token, self.source)


class Turn99SiteIntegration(unittest.TestCase):
    def test_existing_guides_still_link_to_unchanged_download_path(self):
        source = (ROOT / '_source/poker/omaha-hilo-scoop-quarter-counterfeit.html').read_text(encoding='utf-8')
        html = (ROOT / 'poker/omaha-hilo-scoop-quarter-counterfeit/index.html').read_text(encoding='utf-8')
        path = '/downloads/poker-omaha-hilo-split-enumerator.py'
        self.assertIn(path, source)
        self.assertIn(path, html)
        self.assertIn('rel="canonical" href="https://nolankido.com/poker/omaha-hilo-scoop-quarter-counterfeit/"', html)

    def test_existing_public_exact_get_and_sitemap_scope_preserved(self):
        checker = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(checker.count("'downloads/poker-omaha-hilo-split-enumerator.py'"), 1)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('poker-omaha-hilo-split-enumerator.py', sitemap)

    def test_local_release_registration_and_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn99_omaha_hilo_optimized.py', runner)
        action_dir = ROOT / '.github/workflows'
        self.assertFalse(action_dir.exists() and any(
            x.is_file() and x.suffix.lower() in ('.yaml','.yml') for x in action_dir.iterdir()))


if __name__ == '__main__':
    unittest.main()
