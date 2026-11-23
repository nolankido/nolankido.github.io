"""Turn 105: fixed multiway ICM ledger and honest optional reading estimates."""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from itertools import permutations
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
READ_TIME = ROOT / '_scripts/poker_read_time.py'


def load(path, name):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Missing local module: ' + str(path))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MultiwayICMStandalone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load(SCRIPT, 'turn105_model')
        cls.workbook = WORKBOOK.read_text(encoding='utf-8')

    def test_all_six_ranking_orders_conserve_chips_and_prize_pool(self):
        m = self.model
        for order in permutations(m.PLAYERS):
            for call in (False, True):
                with self.subTest(order=order, call=call):
                    state = m.settle(order, call)
                    self.assertEqual(sum(state), 27)
                    self.assertGreaterEqual(min(state), 0)
                    self.assertEqual(sum(m.prize_values(state)), 100)
                    if not call:
                        self.assertEqual(state[1], 10)
                    else:
                        self.assertGreaterEqual(state[1], 5)

    def test_refund_and_distinct_pot_eligibility(self):
        m = self.model
        expected = {
            ('H', 'Y', 'X'): ((0, 10, 17), (0, 27, 0)),
            ('H', 'X', 'Y'): ((12, 10, 5), (0, 27, 0)),
            ('X', 'H', 'Y'): ((12, 10, 5), (12, 15, 0)),
            ('X', 'Y', 'H'): ((12, 10, 5), (12, 5, 10)),
            ('Y', 'H', 'X'): ((0, 10, 17), (0, 5, 22)),
            ('Y', 'X', 'H'): ((0, 10, 17), (0, 5, 22)),
        }
        for order, states in expected.items():
            self.assertEqual((m.settle(order, False), m.settle(order, True)), states)
        self.assertEqual(m.prize_values((0, 27, 0)), (F(0), F(70), F(30)))

    def test_independent_closed_form_icm_and_expected_value(self):
        # This uses closed-form second-place paths, not the verifier's permutation routine.
        f1 = 30 + 40 * F(10, 27)
        f2 = 70 * F(10, 27) + 30 * (F(12, 27)*F(10, 15) + F(5, 27)*F(10, 22))
        c1 = F(70)
        c2 = 30 + 40 * F(15, 27)
        c3 = 70 * F(5, 27) + 30 * (F(12, 27)*F(5, 15) + F(10, 27)*F(5, 17))
        self.assertEqual((f1, f2, c1, c2, c3), (F(1210,27),F(11090,297),F(70),F(470,9),F(9490,459)))
        fold = F(1,10)*f1 + F(9,10)*f2
        call = F(1,10)*c1 + F(3,10)*c2 + F(3,5)*c3
        self.assertEqual((fold, call, call-fold), (F(11312,297),F(5366,153),-F(15226,5049)))
        self.assertEqual(12*F(1,10)+10*F(2,5)-5, F(1,5))
        self.assertEqual(F(100,27)*F(1,5), F(20,27))
        r = self.model.verify()
        self.assertEqual(F(r['expected_prizes_X_H_Y']['fold'][1]), fold)
        self.assertEqual(F(r['expected_prizes_X_H_Y']['call'][1]), call)
        self.assertEqual(F(r['hero_call_minus_fold_chips']), F(1,5))

    def test_workbook_contains_exact_results_and_model_limits(self):
        for phrase in ('27 BB', '5 BB more', '12 BB main pot', '10 BB side pot',
                       '11312/297', '5366/153', '15226/5049', '10.2 BB',
                       '$38.09', '$35.07', '20/27', 'not a claim about every tournament',
                       'other three possible strict ranking orders have probability zero',
                       'Unknown probabilities must remain unknown'):
            self.assertIn(phrase, self.workbook)
        self.assertNotIn(chr(0x2014), self.workbook)
        self.assertIn('https://nolankido.com/downloads/poker-multiway-icm-verify.py', self.workbook)

    def test_cli_modes_identical_and_optimizer_safe(self):
        original = None
        for mode in ('', '-O', '-OO'):
            args = [sys.executable] + ([mode] if mode else []) + [str(SCRIPT)]
            output = subprocess.run(args, capture_output=True, text=True, check=True, timeout=15).stdout
            self.assertEqual(json.loads(output), self.model.verify())
            if original is None:
                original = output
            self.assertEqual(output, original)
            result = subprocess.run(args + ['--self-test'], capture_output=True, text=True, check=True, timeout=15)
            self.assertIn('PASS: fictional three-way', result.stdout)

    def test_corrupted_expected_prize_is_rejected_in_all_modes(self):
        source = SCRIPT.read_text(encoding='utf-8')
        original = "== F(5366, 153), 'call prize value'"
        self.assertEqual(source.count(original), 1)
        with TemporaryDirectory() as folder:
            path = Path(folder)/'bad.py'
            path.write_text(source.replace(original, "== F(1), 'call prize value'"), encoding='utf-8')
            for mode in ('', '-O', '-OO'):
                args = [sys.executable] + ([mode] if mode else []) + [str(path), '--self-test']
                result = subprocess.run(args, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Multiway ICM check failed: call prize value', result.stderr)
                self.assertNotIn('PASS:', result.stdout)

    def test_invalid_state_and_strict_rankings_are_rejected(self):
        for state in ((-1, 10, 18), (4, 14, 8), (27, 0), (True, 17, 9)):
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.model.prize_values(state)
        for order in (('H', 'H', 'X'), ('X', 'Y'), ('X', 'H', 'Z')):
            with self.subTest(order=order), self.assertRaises(ValueError):
                self.model.settle(order, True)
        with self.assertRaises(ValueError):
            self.model.settle(('X', 'H', 'Y'), 1)

    def test_fixed_script_has_no_elidable_asserts_or_external_dependencies(self):
        source = SCRIPT.read_text(encoding='utf-8')
        tree = ast.parse(source)
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(tree)))
        imports = set()
        for n in tree.body:
            if isinstance(n, ast.Import):
                imports.update(i.name for i in n.names)
            elif isinstance(n, ast.ImportFrom):
                imports.add(n.module)
        self.assertEqual(imports, {'fractions', 'itertools', 'argparse', 'json'})
        for token in ('input(', 'open(', 'write_text(', 'requests', 'urllib', 'socket', chr(0x2014)):
            self.assertNotIn(token, source)


class OptionalReadingTimeStandalone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load(READ_TIME, 'turn105_reading_time')

    def test_existing_225_word_boundary_and_script_exclusion(self):
        minutes = self.mod.minutes
        self.assertEqual(minutes('<p>' + 'word '*225 + '</p>'), 1)
        self.assertEqual(minutes('<p>' + 'word '*226 + '</p>'), 2)
        self.assertEqual(minutes('<script>' + 'word '*1000 + '</script><p>Read this</p>'), 1)

    def test_ordinary_answer_explanations_still_count(self):
        self.assertEqual(self.mod.minutes('<p>Core lesson</p><details><summary>Practice</summary><p>'+
                                          'answer '*225+'</p></details>'), 2)

    def test_marked_optional_details_do_not_inflate_core_estimate(self):
        core = '<p>' + 'word '*225 + '</p>'
        extra = ('<details class="poker-details" data-reading-optional="true">'
                 '<summary>Optional advanced example (extra reading time)</summary>'
                 '<div><p>'+ 'extra '*1000 + '</p></div></details>')
        self.assertEqual(self.mod.minutes(core + extra), 1)
        self.assertEqual(self.mod.minutes(extra.replace(' data-reading-optional="true"','') + core), 6)

    def test_nested_optional_disclosures_resume_visible_core_after_closing(self):
        source = ('<p>'+'word '*225+'</p><details data-reading-optional="true"><summary>Extra</summary>'
                  '<details><summary>Nested</summary><p>'+ 'word '*1000+'</p></details><p>Still optional</p>'
                  '</details><p>More core</p>')
        self.assertEqual(self.mod.minutes(source), 2)

    def test_unmarked_or_false_details_and_non_details_marker_cannot_hide_core(self):
        for markup in ('<details data-reading-optional="false">', '<div data-reading-optional="true">'):
            tag = markup[1:].split()[0]
            with self.subTest(tag=markup):
                self.assertEqual(self.mod.minutes('<p>Core</p>'+markup+'word '*225+'</'+tag+'>'),2)


class Turn105SiteIntegration(unittest.TestCase):
    def test_existing_routes_keep_core_reading_estimates_and_optional_labels(self):
        reader = load(READ_TIME, 'turn105_reading_time_site')
        for slug, expected, anchor in (
            ('satellite-bubble-seat-equity', 14, 'sat-tie-branch'),
            ('bounty-knockout-equity', 15, 'bounty-mystery-draw'),
            ('tournament-equity', 7, None),
        ):
            with self.subTest(slug=slug):
                authored = (ROOT / '_source/poker' / (slug+'.html')).read_text(encoding='utf-8')
                generated = (ROOT / 'poker' / slug / 'index.html').read_text(encoding='utf-8')
                self.assertEqual(reader.minutes(authored), expected)
                self.assertIn(f'About {expected} min read', generated)
                self.assertIn(f'<link rel="canonical" href="https://nolankido.com/poker/{slug}/">', generated)
                if anchor:
                    marker = 'id="'+anchor+'" data-reading-optional="true">'
                    for page in (authored, generated):
                        self.assertEqual(page.count(marker), 1)
                        self.assertIn('Advanced example (extra reading time):',page)
                else:
                    link = 'href="/downloads/poker-multiway-icm-workbook.md" download'
                    for page in (authored, generated):
                        self.assertEqual(page.count(link), 1)

    def test_read_time_policy_is_disclosed_and_imported_by_library(self):
        self.assertIn('from poker_read_time import PlainText, minutes',
                      (ROOT/'_scripts/poker_library.py').read_text(encoding='utf-8'))
        text = 'Explicitly labelled advanced examples and separate downloads take additional study time.'
        for path in ('_source/poker/library.html','poker/library/index.html'):
            self.assertIn(text,(ROOT/path).read_text(encoding='utf-8'))

    def test_public_downloads_registered_no_sitemap_inflation(self):
        inventory = (ROOT/'_scripts/check_live.py').read_text(encoding='utf-8')
        sitemap = (ROOT/'sitemap.xml').read_text(encoding='utf-8')
        for name in ('poker-multiway-icm-workbook.md','poker-multiway-icm-verify.py'):
            self.assertEqual(inventory.count("'downloads/"+name+"'"),1)
            self.assertNotIn(name,sitemap)

    def test_full_builder_and_finder_parity_manual_runner_no_actions(self):
        sys.path.insert(0,str(ROOT/'_scripts'))
        import build
        outputs = build.build_outputs()
        for route in ('poker/tournament-equity/index.html','poker/satellite-bubble-seat-equity/index.html',
                      'poker/bounty-knockout-equity/index.html','poker/library/index.html', 'poker/find/index.html'):
            self.assertEqual(outputs[Path(route)],(ROOT/route).read_text(encoding='utf-8'),route)
        self.assertIn('test_turn105_multiway_icm_workbook.py',(ROOT/'_scripts/local_release_checks.py').read_text(encoding='utf-8'))
        workflows = ROOT/'.github/workflows'
        self.assertFalse(workflows.exists() and any(p.is_file() and p.suffix.lower() in ('.yml','.yaml') for p in workflows.iterdir()))


if __name__ == '__main__':
    unittest.main()
