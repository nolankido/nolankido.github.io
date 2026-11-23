"""Fail-closed poker frequency verification, including optimized Python modes.

Standalone tests use only the exact published fixed-case script. Three
integration tests require the full site repository and its release inventory.
"""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-opponent-frequency-verify.py'


def execute(source: Path, optimize: str, flag: str):
    args = [sys.executable]
    if optimize:
        args.append(optimize)
    return subprocess.run(args + [str(source), flag], text=True,
                          capture_output=True, timeout=20, check=False)


class Turn97StandaloneOptimizedChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')

    def test_fixed_self_test_passes_all_python_optimization_modes(self):
        for flag in ('', '-O', '-OO'):
            with self.subTest(mode=flag or 'normal'):
                result = execute(SCRIPT, flag, '--self-test')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS: fixed fictional opportunity denominators', result.stdout)

    def test_json_report_is_identical_in_all_optimization_modes(self):
        baseline = json.loads(execute(SCRIPT, '', '--json').stdout)
        self.assertEqual(baseline['position_mix_reversal']['A']['pooled']['observed_rate'], '22.0%')
        self.assertEqual(baseline['position_mix_reversal']['B']['pooled']['observed_rate'], '27.5%')
        self.assertEqual(baseline['fictional_beta_prior']['posterior_mean'], '21.43%')
        for flag in ('-O', '-OO'):
            with self.subTest(mode=flag):
                result = execute(SCRIPT, flag, '--json')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), baseline)

    def test_tampered_wilson_checkpoint_fails_even_when_optimized(self):
        original = 'require(r["comparison"]["wilson_95"] == ["10.5%", "34.8%"]'
        changed = 'require(r["comparison"]["wilson_95"] == ["0.0%", "0.0%"]'
        self.assertEqual(self.source.count(original), 1)
        self._assert_mutant_fails(self.source.replace(original, changed), 'wilson_95')

    def test_tampered_simpson_checkpoint_fails_even_when_optimized(self):
        original = 'require(mix["A"]["pooled"] == {"successes": 11, "opportunities": 50, "observed_rate": "22.0%"}'
        changed = 'require(mix["A"]["pooled"] == {"successes": 11, "opportunities": 50, "observed_rate": "21.0%"}'
        self.assertEqual(self.source.count(original), 1)
        self._assert_mutant_fails(self.source.replace(original, changed), 'pooled')

    def _assert_mutant_fails(self, candidate, expected_label):
        with TemporaryDirectory() as folder:
            p = Path(folder) / 'altered-check.py'
            p.write_text(candidate, encoding='utf-8')
            for flag in ('', '-O', '-OO'):
                with self.subTest(mode=flag or 'normal',label=expected_label):
                    result = execute(p, flag, '--self-test')
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('Fixed example self-test failed:', result.stderr)
                    self.assertIn(expected_label, result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_self_test_has_no_optimization_elidable_assert_statements(self):
        parsed = ast.parse(self.source)
        self.assertFalse([n for n in ast.walk(parsed) if isinstance(n, ast.Assert)])
        function = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'self_test')
        requires = [n for n in ast.walk(function) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == 'require']
        self.assertEqual(len(requires), 27)
        self.assertIn('if not condition:', self.source)
        self.assertIn('raise AssertionError("Fixed example self-test failed: " + expression)',self.source)

    def test_require_reports_failures_without_the_assert_statement(self):
        spec = spec_from_file_location('turn97_poker_fixed_cases', SCRIPT)
        self.assertIsNotNone(spec)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        module.require(True, 'expected')
        with self.assertRaisesRegex(AssertionError, 'Fixed example self-test failed: intentional'):
            module.require(False, 'intentional')
        self.assertEqual(module.observed_rate(3, 12), Fraction(1,4))

    def test_script_keeps_private_no_network_and_standard_library_scope(self):
        imports = set()
        for item in ast.parse(self.source).body:
            if isinstance(item, ast.Import):
                imports.update(n.name.split('.')[0] for n in item.names)
            elif isinstance(item, ast.ImportFrom):
                imports.add(item.module.split('.')[0])
        self.assertEqual(imports, {'__future__', 'argparse', 'fractions', 'json',
                                   'math', 'statistics'})
        for token in ('import requests', 'urllib', 'socket', 'fetch(', 'open(',
                      'read_text(', 'write_text(', 'localStorage', chr(0x2014)):
            self.assertNotIn(token, self.source)


class Turn97FullSiteIntegration(unittest.TestCase):
    def test_revised_script_has_unchanged_publication_path_and_parent_links(self):
        src = (ROOT / '_source/poker/poker-under-uncertainty.html').read_text(encoding='utf-8')
        html = (ROOT / 'poker/poker-under-uncertainty/index.html').read_text(encoding='utf-8')
        self.assertIn('href="/downloads/poker-opponent-frequency-verify.py" download', src)
        self.assertIn('href="/downloads/poker-opponent-frequency-verify.py" download', html)
        self.assertIn('rel="canonical" href="https://nolankido.com/poker/poker-under-uncertainty/"', html)

    def test_no_sitemap_finder_or_release_inventory_changes(self):
        self.assertNotIn('poker-opponent-frequency-verify.py',
                         (ROOT/'sitemap.xml').read_text(encoding='utf-8'))
        self.assertNotIn('poker-opponent-frequency-verify.py',
                         (ROOT/'poker/find/index.html').read_text(encoding='utf-8'))
        inventory = (ROOT/'_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(inventory.count("'downloads/poker-opponent-frequency-verify.py'"),1)

    def test_manual_runner_includes_optimization_tests_and_no_actions(self):
        runner = (ROOT/'_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn95_poker_opponent_frequency.py', runner)
        self.assertIn('test_turn96_position_mix_reversal.py', runner)
        self.assertIn('test_turn97_optimized_frequency_self_test.py', runner)
        actions = ROOT/'.github/workflows'
        self.assertFalse(actions.exists() and any(p.is_file() and p.suffix.lower() in ('.yml','.yaml') for p in actions.iterdir()))

if __name__ == '__main__':
    unittest.main()
