"""Turn 98: make offline poker pot-odds verification fail closed under -O/-OO.

Eight standalone checks use only the exact public Python verifier and its
unchanged workbook. Three optional integration checks need a full site checkout.
"""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-pot-odds-sensitivity-verify.py'
WORKBOOK = ROOT / 'downloads/poker-pot-odds-sensitivity-workbook.md'


def invoke(path, mode='', arg='--self-test'):
    args = [sys.executable] + ([mode] if mode else []) + [str(path), arg]
    return subprocess.run(args, capture_output=True, text=True, timeout=15)


class Turn98StandaloneOptimizedPotOdds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = SCRIPT.read_text(encoding='utf-8')

    def test_unmodified_self_test_passes_three_interpreter_modes(self):
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                result = invoke(SCRIPT, mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS: exact fictional pot-odds', result.stdout)

    def test_original_fractional_json_is_unchanged_under_optimization(self):
        default = invoke(SCRIPT, arg='--json')
        self.assertEqual(default.returncode, 0, default.stderr)
        data = json.loads(default.stdout)
        self.assertEqual(data['river_call']['break_even_equity'], '1/4')
        self.assertEqual(data['raise_to']['break_even_equity'], '5/19')
        self.assertEqual(data['pure_bluff']['fold_break_even'], '3/8')
        self.assertEqual(data['pure_bluff']['caller_break_even_equity'], '3/11')
        for mode in ('-O', '-OO'):
            with self.subTest(mode=mode):
                test = invoke(SCRIPT, mode, '--json')
                self.assertEqual(test.returncode, 0, test.stderr)
                self.assertEqual(json.loads(test.stdout), data)

    def assert_corruption_fails(self, wrong_source, keyword):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'corrupted-fixed-check.py'
            path.write_text(wrong_source, encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                with self.subTest(mode=mode or 'normal', corruption=keyword):
                    result = invoke(path, mode)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('Fixed pot-odds check failed:', result.stderr)
                    self.assertIn(keyword, result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_incorrect_call_price_fails_under_all_optimizations(self):
        old = 'require(call_price(F(30), F(10)) == F(1, 4)'
        new = 'require(call_price(F(30), F(10)) == F(1, 5)'
        self.assertEqual(self.code.count(old), 1)
        self.assert_corruption_fails(self.code.replace(old, new, 1), 'call_price')

    def test_incorrect_bluff_threshold_fails_under_all_optimizations(self):
        old = 'require(pure_bluff_fold_price(F(10), F(6)) == F(3, 8)'
        new = 'require(pure_bluff_fold_price(F(10), F(6)) == F(1, 4)'
        self.assertEqual(self.code.count(old), 1)
        self.assert_corruption_fails(self.code.replace(old, new, 1), 'pure_bluff_fold_price')

    def test_check_ast_contains_no_optimized_away_asserts(self):
        tree = ast.parse(self.code)
        self.assertFalse([n for n in ast.walk(tree) if isinstance(n, ast.Assert)])
        main_check = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'self_test')
        calls = [n for n in ast.walk(main_check) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'require']
        self.assertEqual(len(calls), 10)
        self.assertIn('raise AssertionError("Fixed pot-odds check failed: " + explanation)', self.code)

    def test_non_elidable_helper_raises_meaningful_error(self):
        spec = spec_from_file_location('pot_odds_fixed_turn98', SCRIPT)
        self.assertIsNotNone(spec)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        module.require(True, 'valid')
        with self.assertRaisesRegex(AssertionError, 'Fixed pot-odds check failed: deliberately invalid'):
            module.require(False, 'deliberately invalid')
        self.assertEqual(module.call_price(F(30), F(10)), F(1, 4))

    def test_invalid_inputs_still_rejected(self):
        spec = spec_from_file_location('pot_odds_validation_turn98', SCRIPT)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        for fn, args in (
            (module.call_price, (F(30), F(0))),
            (module.call_ev, (F(30), F(10), F(101, 100))),
            (module.facing_raise_to, (F(10), F(4), F(3))),
            (module.pure_bluff_ev, (F(10), F(6), F(-1, 2))),
        ):
            with self.subTest(function=fn.__name__), self.assertRaises(ValueError):
                fn(*args)

    def test_standalone_is_safe_and_keeps_original_scope(self):
        imports = set()
        for n in ast.parse(self.code).body:
            if isinstance(n, ast.Import):
                imports.update(x.name.split('.')[0] for x in n.names)
            if isinstance(n, ast.ImportFrom):
                imports.add(n.module.split('.')[0])
        self.assertEqual(imports, {'__future__', 'argparse', 'fractions', 'json'})
        for forbidden in ('urllib', 'requests', 'socket', 'open(', 'read_text(',
                          'write_text(', 'localStorage', 'fetch(', chr(0x2014)):
            self.assertNotIn(forbidden, self.code)
        self.assertIn('not RTA', self.code)
        self.assertIn('future betting', self.code.lower())
        self.assertIn('fictional', WORKBOOK.read_text(encoding='utf-8').lower())


class Turn98SiteIntegration(unittest.TestCase):
    def test_parent_article_still_references_both_standalone_resources(self):
        src = (ROOT / '_source/poker/pot-odds-workshop.html').read_text(encoding='utf-8')
        html = (ROOT / 'poker/pot-odds-workshop/index.html').read_text(encoding='utf-8')
        for path in ('/downloads/poker-pot-odds-sensitivity-verify.py',
                     '/downloads/poker-pot-odds-sensitivity-workbook.md'):
            self.assertIn('href="' + path + '"', src)
            self.assertIn('href="' + path + '"', html)
        self.assertIn('rel="canonical" href="https://nolankido.com/poker/pot-odds-workshop/"', html)

    def test_existing_exact_get_inventory_and_sitemap_boundary(self):
        checker = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(checker.count("'downloads/poker-pot-odds-sensitivity-verify.py'"), 1)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('poker-pot-odds-sensitivity-verify.py', sitemap)
        finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        self.assertNotIn('poker-pot-odds-sensitivity-verify.py', finder)

    def test_existing_test_runner_and_no_github_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn89_pot_odds_sensitivity.py', runner)
        self.assertIn('test_turn98_optimized_pot_odds.py', runner)
        workflows = ROOT / '.github/workflows'
        self.assertFalse(workflows.exists() and any(
            f.is_file() and f.suffix.lower() in ('.yaml', '.yml') for f in workflows.iterdir()))


if __name__ == '__main__':
    unittest.main()
