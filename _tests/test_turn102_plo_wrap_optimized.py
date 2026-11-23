"""Turn 102: verify fixed PLO wrap examples under every Python optimization mode.

The six-script audit is deliberately bounded to the published poker verifiers
identified in Turns 97-101. No new dependency, input source, or network access.
"""
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import hashlib
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-plo-wrap-enumerator.py'
AUDITED = (
    'poker-opponent-frequency-verify.py',
    'poker-pot-odds-sensitivity-verify.py',
    'poker-omaha-hilo-split-enumerator.py',
    'poker-stud8-razz-seven-card-check.py',
    'poker-plo-flush-pair-enumerator.py',
    'poker-plo-wrap-enumerator.py',
)
OUTPUT_NORMAL = 'd6e4504dbbeafcaccd37d3ecba5734c261602b8bcd22baa74337eeace5f89ddc'
OUTPUT_SELF_TEST = '19ba70e679b9b35c26acd5158c33ef7f9150494482b491ee40119664296ad2fb'


def run(path, mode='', self_test=True):
    args = [sys.executable] + ([mode] if mode else []) + [str(path)]
    if self_test:
        args.append('--self-test')
    return subprocess.run(args, text=True, capture_output=True, timeout=30)


def load(path, name):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Cannot load the published fixed-case verifier')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Turn102StandalonePLOWrap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')
        cls.mod = load(SCRIPT, 'plo_wrap_turn102')

    def test_original_cli_output_in_all_modes(self):
        for mode in ('', '-O', '-OO'):
            for self_test, digest in ((False, OUTPUT_NORMAL), (True, OUTPUT_SELF_TEST)):
                with self.subTest(mode=mode or 'normal', self_test=self_test):
                    result = run(SCRIPT, mode, self_test)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, '')
                    self.assertEqual(hashlib.sha256(result.stdout.encode()).hexdigest(), digest)
                    self.assertEqual('PASS:' in result.stdout, self_test)

    def test_all_fifteen_fixed_checks_are_explicit(self):
        tree = ast.parse(self.source)
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(tree)))
        checks = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_checks')
        calls = [n for n in ast.walk(checks) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'require']
        self.assertEqual(len(calls), 15)

    def reject_mutation(self, original, changed, expected):
        self.assertEqual(self.source.count(original), 1)
        with TemporaryDirectory() as folder:
            candidate = Path(folder) / 'mutant.py'
            candidate.write_text(self.source.replace(original, changed, 1), encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                with self.subTest(mode=mode or 'normal', expected=expected):
                    result = run(candidate, mode)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('PLO wrap fixed check failed: ' + expected, result.stderr)
                    self.assertNotIn('PASS:', result.stdout)

    def test_wrong_wheel_score_cannot_pass(self):
        self.reject_mutation('five_card_high(("Ac", "2h", "3s", "4d", "5c")) == (4, 5)',
                             'five_card_high(("Ac", "2h", "3s", "4d", "5c")) == (4, 6)',
                             'wheel straight')

    def test_wrong_blocker_count_cannot_pass(self):
        self.reject_mutation('len(blocked) == 14', 'len(blocked) == 13',
                             '14 completions after blockers')

    def test_wrong_redraw_count_cannot_pass(self):
        self.reject_mutation('len(outcome["opponent"]) == 11',
                             'len(outcome["opponent"]) == 12', '11 rival-winning rivers')

    def test_real_card_validation_works_on_imported_scorer_in_all_modes(self):
        checks = [('Ax', '2x', '3x', '4x', '5x'), ('1c', '2c', '3c', '4c', '5c'),
                  ('Ac', 'Ac', '3c', '4c', '5c'), ('Ac', '2c', '3c', '4c')]
        for cards in checks:
            with self.subTest(cards=cards), self.assertRaises(ValueError):
                self.mod.five_card_high(cards)
        for mode in ('', '-O', '-OO'):
            expr = ('import runpy; m = runpy.run_path(' + repr(str(SCRIPT)) + '); '
                    "m['five_card_high'](('Ax','2x','3x','4x','5x'))")
            result = subprocess.run([sys.executable] + ([mode] if mode else []) + ['-c', expr],
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ValueError: Unknown or duplicated physical card', result.stderr)

    def test_wrap_and_blocker_counts_have_independent_deck_construction(self):
        m = self.mod
        unseen = set(m.DECK) - set(m.WRAP_HERO + m.WRAP_FLOP)
        expected = {c for c in unseen if c[0] in 'KQ987'}
        self.assertEqual(len(unseen), 45)
        self.assertEqual(len(expected), 16)
        self.assertEqual(set(m.wrap_next_card_completions()), expected)
        self.assertEqual(Counter(c[0] for c in expected), {'K': 4, 'Q': 3, '9': 3, '8': 3, '7': 3})
        blocked = expected - set(m.BLOCKER_OPPONENT)
        self.assertEqual(len(blocked), 14)
        self.assertEqual(set(m.wrap_next_card_completions(m.BLOCKER_OPPONENT)), blocked)
        self.assertEqual(expected - blocked, {'Kd', 'Qd'})
        self.assertEqual(len(unseen - set(m.BLOCKER_OPPONENT)), 41)

    def test_redraw_partitions_all_forty_physical_rivers(self):
        m = self.mod
        results = m.redraw_river_outcomes()
        unknown = set(m.DECK) - set(m.WRAP_HERO + m.REDRAW_TURN + m.REDRAW_OPPONENT)
        self.assertEqual(len(unknown), 40)
        expected = {c for c in unknown if c[1] == 'c' or c[0] == 'Q'}
        self.assertEqual(set(results['opponent']), expected)
        self.assertEqual(set(results['hero']), unknown - expected)
        self.assertEqual(results['tie'], ())
        self.assertEqual(sum(map(len, results.values())), 40)
        self.assertEqual(len(expected), 11)

    def test_independent_flush_evaluator_agrees_on_every_river(self):
        m = self.mod
        prior = load(ROOT / 'downloads/poker-plo-flush-pair-enumerator.py', 'plo_flush_turn101')
        for river in m.remaining_cards(m.WRAP_HERO, m.REDRAW_TURN, m.REDRAW_OPPONENT):
            board = m.REDRAW_TURN + (river,)
            for holes in (m.WRAP_HERO, m.REDRAW_OPPONENT):
                with self.subTest(river=river, holes=holes):
                    self.assertEqual(m.best_omaha_high(holes, board), prior.omaha_high(holes, board))

    def test_no_new_external_imports_or_network_inputs(self):
        imports = set()
        for n in ast.parse(self.source).body:
            if isinstance(n, ast.Import):
                imports.update(x.name.split('.')[0] for x in n.names)
            elif isinstance(n, ast.ImportFrom):
                imports.add(n.module.split('.')[0])
        self.assertEqual(imports, {'__future__', 'argparse', 'collections', 'itertools'})
        for forbidden in ('requests', 'urllib', 'socket', 'input(', 'fetch(', 'write_text(', chr(0x2014)):
            self.assertNotIn(forbidden, self.source)


class Turn102AuditedVerifierSuite(unittest.TestCase):
    def test_all_six_audited_scripts_have_no_elidable_assertions(self):
        for filename in AUDITED:
            with self.subTest(script=filename):
                path = ROOT / 'downloads' / filename
                self.assertFalse(any(isinstance(n, ast.Assert)
                                     for n in ast.walk(ast.parse(path.read_text(encoding='utf-8')))))

    def test_all_six_audited_scripts_pass_under_each_python_mode(self):
        for filename in AUDITED:
            reference = None
            for mode in ('', '-O', '-OO'):
                with self.subTest(script=filename, mode=mode or 'normal'):
                    result = run(ROOT / 'downloads' / filename, mode)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('PASS:', result.stdout)
                    if reference is None:
                        reference = result.stdout
                    self.assertEqual(result.stdout, reference)


class Turn102SiteIntegration(unittest.TestCase):
    def test_original_guide_and_download_links_are_preserved(self):
        authored = (ROOT / '_source/poker/plo-wrap-redraw-blockers.html').read_text(encoding='utf-8')
        public = (ROOT / 'poker/plo-wrap-redraw-blockers/index.html').read_text(encoding='utf-8')
        for filename in ('poker-plo-wrap-enumerator.py', 'poker-plo-after-play-review.md'):
            for content in (authored, public):
                self.assertIn('href="/downloads/' + filename + '"', content)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/plo-wrap-redraw-blockers/">', public)

    def test_public_asset_inventory_and_no_sitemap_inflation(self):
        live = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(live.count("'downloads/poker-plo-wrap-enumerator.py'"), 1)
        self.assertNotIn('poker-plo-wrap-enumerator.py', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))

    def test_manual_registration_and_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn102_plo_wrap_optimized.py', runner)
        self.assertTrue((ROOT / '_tests/test_poker_plo_wrap.py').is_file())
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(p.is_file() and p.suffix.lower() in ('.yaml','.yml')
                                                 for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
