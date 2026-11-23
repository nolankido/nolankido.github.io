"""Turn 101: keep PLO blocker and paired-board checks active under -O/-OO.

Standalone tests use only the original fictional four-card PLO Python download.
Three optional site-integration checks need the complete matching checkout.
"""
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from math import comb
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import hashlib
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-plo-flush-pair-enumerator.py'
NORMAL_SHA = '3bfb805c1be4b721d51d4f5256b189f71215225b5759e7e588f7fb3987d40da6'
SELF_TEST_SHA = 'd5eeaddf4f77cad9ad96471e68059997a8b2b30d1081ab90fa2083e1a80b067e'


def run(source, mode='', self_test=True):
    args = [sys.executable] + ([mode] if mode else []) + [str(source)]
    if self_test:
        args.append('--self-test')
    return subprocess.run(args, capture_output=True, text=True, timeout=50)


def load():
    spec = spec_from_file_location('plo_flush_pair_turn101', SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Missing fixed PLO verifier')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Turn101StandalonePLOFlush(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')
        cls.mod = load()

    def test_original_self_test_output_unchanged_across_python_modes(self):
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                result = run(SCRIPT, mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, '')
                self.assertIn('PASS: verified all Omaha high rules, combinations, blocker counts and rivers', result.stdout)
                self.assertEqual(hashlib.sha256(result.stdout.encode()).hexdigest(), SELF_TEST_SHA)

    def test_default_output_preserves_original_explained_counts(self):
        for mode in ('', '-O', '-OO'):
            with self.subTest(mode=mode or 'normal'):
                result = run(SCRIPT, mode, self_test=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(hashlib.sha256(result.stdout.encode()).hexdigest(), NORMAL_SHA)
                self.assertNotIn('PASS:', result.stdout)
                for marker in ('25830/148995', '31185/148995', '6699/148995',
                               '9/40 opponent wins', '10/40 opponent wins',
                               'Opponent-winning rivers: (none)'):
                    self.assertIn(marker, result.stdout)

    def test_no_optimization_elidable_asserts_and_fifteen_reachable_checks(self):
        tree = ast.parse(self.source)
        self.assertFalse([node for node in ast.walk(tree) if isinstance(node, ast.Assert)])
        method = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'verify')
        calls = [x for x in ast.walk(method) if isinstance(x, ast.Call)
                 and isinstance(x.func, ast.Name) and x.func.id == 'require']
        self.assertEqual(len(calls), 15)
        self.assertIn("raise AssertionError('PLO flush/pair fixed check failed: ' + case)", self.source)

    def test_three_or_five_private_cards_are_rejected_in_all_modes(self):
        for hero in (('As', 'Kh', 'Qd'), ('As', 'Kh', 'Qd', 'Jc', '2h')):
            for mode in ('', '-O', '-OO'):
                with self.subTest(hero=hero, mode=mode or 'normal'):
                    code = ('import runpy; m=runpy.run_path(' + repr(str(SCRIPT)) + '); '
                            'm["four_card_flush_holdings"](' + repr(hero) + ')')
                    args = [sys.executable] + ([mode] if mode else []) + ['-c', code]
                    result = subprocess.run(args, capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('ValueError: PLO blocker count needs exactly four private cards', result.stderr)

    def bad_fixture_fails(self, altered, phrase):
        with TemporaryDirectory() as folder:
            file = Path(folder) / 'bad-plo-fixture.py'
            file.write_text(altered, encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                with self.subTest(mode=mode or 'normal', corruption=phrase):
                    result = run(file, mode)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('PLO flush/pair fixed check failed: ' + phrase, result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_mutated_flush_deal_count_fails_all_modes(self):
        old = "blocker == {'all': 148995, 'flush': 25830, 'ace_flush': 0}"
        new = "blocker == {'all': 148995, 'flush': 25831, 'ace_flush': 0}"
        self.assertEqual(self.source.count(old), 1)
        self.bad_fixture_fails(self.source.replace(old, new, 1), 'ace blocker exact flush deal counts')

    def test_mutated_exact_river_count_fails_all_modes(self):
        old = "len(set_case['rival']) == 9"
        new = "len(set_case['rival']) == 10"
        self.assertEqual(self.source.count(old), 1)
        self.bad_fixture_fails(self.source.replace(old, new, 1), 'set rival nine winning rivers')

    def test_independent_binomial_counts_match_enumerator(self):
        expected_with_block = sum(comb(9, n) * comb(36, 4 - n) for n in (2, 3, 4))
        expected_without = sum(comb(10, n) * comb(35, 4 - n) for n in (2, 3, 4))
        self.assertEqual((expected_with_block, expected_without), (25830, 31185))
        self.assertEqual(comb(45, 4), 148995)
        self.assertEqual(comb(44, 3) - comb(35, 3), 6699)
        for hero, expected in ((self.mod.ACE_BLOCKER_HERO, (25830, 0)),
                               (self.mod.NO_SPADE_HERO, (31185, 6699))):
            actual = self.mod.four_card_flush_holdings(hero)
            self.assertEqual((actual['flush'], actual['ace_flush']), expected)
            self.assertEqual(actual['all'], 148995)

    def test_independent_paired_board_outcomes_and_blocker_difference(self):
        a = self.mod.faceup_rivers(self.mod.SET_HERO, self.mod.SET_RIVAL)
        b = self.mod.faceup_rivers(self.mod.NO_SEVEN_BLOCK_HERO, self.mod.SET_RIVAL)
        c = self.mod.faceup_rivers(self.mod.SET_HERO, self.mod.ONE_QUEEN_RIVAL)
        self.assertEqual(set(a['rival']), {'Qc', '8c', '8d', '8h', '3c', '3d', '3h', '7c', '7s'})
        self.assertEqual((len(a['hero']), len(a['rival']), len(a['tie'])), (31, 9, 0))
        self.assertEqual((len(b['hero']), len(b['rival']), len(b['tie'])), (30, 10, 0))
        self.assertEqual(set(b['rival']) - set(a['rival']), {'7h'})
        self.assertEqual((len(c['hero']), len(c['rival']), len(c['tie'])), (40, 0, 0))
        self.assertEqual(len(list(combinations(self.mod.remaining(self.mod.SET_HERO,
                                        self.mod.SET_RIVAL, self.mod.TURN_BOARD), 1))), 40)

    def test_bad_cards_fail_and_remaining_deck_guard_is_explicit(self):
        self.assertIn("if len(unseen) != 45:", self.source)
        self.assertIn("raise ArithmeticError('PLO flop fixture must leave exactly 45 unseen cards')", self.source)
        self.assertIn("raise ValueError('PLO blocker count needs exactly four private cards')", self.source)
        with self.assertRaises(ValueError):
            self.mod.four_card_flush_holdings(('As', 'As', '2h', '3d'))
        with self.assertRaises(ValueError):
            self.mod.four_card_flush_holdings(('ZZ', 'Kh', '2h', '3d'))
        with self.assertRaises(ValueError):
            self.mod.omaha_high(('As', 'Kh', 'Qd', 'Jc'), ('As', '8s', '3s'))

    def test_no_external_requests_and_original_standard_library_imports(self):
        packages = set()
        for node in ast.parse(self.source).body:
            if isinstance(node, ast.Import):
                packages.update(n.name.split('.')[0] for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                packages.add(node.module.split('.')[0])
        self.assertEqual(packages, {'__future__', 'argparse', 'collections', 'itertools', 'math'})
        for token in ('import requests', 'urllib', 'socket', 'fetch(', 'read_text(',
                      'write_text(', 'localStorage', chr(0x2014)):
            self.assertNotIn(token, self.source)


class Turn101SiteIntegration(unittest.TestCase):
    def test_original_indexed_guide_and_companion_link_preserved(self):
        authored = (ROOT / '_source/poker/plo-nut-flush-paired-board.html').read_text(encoding='utf-8')
        public = (ROOT / 'poker/plo-nut-flush-paired-board/index.html').read_text(encoding='utf-8')
        route = '/downloads/poker-plo-flush-pair-enumerator.py'
        self.assertIn('href="' + route + '"', authored)
        self.assertIn('href="' + route + '"', public)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/plo-nut-flush-paired-board/">', public)

    def test_original_download_inventory_and_sitemap_exclusion(self):
        script = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(script.count("'downloads/poker-plo-flush-pair-enumerator.py'"), 1)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('poker-plo-flush-pair-enumerator.py', sitemap)
        finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        self.assertNotIn('poker-plo-flush-pair-enumerator.py', finder)

    def test_manual_release_registration_and_no_actions(self):
        suite = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertTrue((ROOT / '_tests/test_poker_plo_flush_pair.py').is_file())
        self.assertIn('test_turn101_plo_flush_pair_optimized.py', suite)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            x.is_file() and x.suffix.lower() in ('.yaml','.yml')
            for x in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
