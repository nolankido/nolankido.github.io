"""Turn 95: validate original fictional opponent-frequency study and disclosure.

Local-only release suite. This does not import an opponent tracker, collect hands,
run a poker solver, fetch any site or assert population behavior.
"""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import ast
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / 'downloads/poker-opponent-frequency-evidence-workbook.md'
CHECKER = ROOT / 'downloads/poker-opponent-frequency-verify.py'
SOURCE = ROOT / '_source/poker/poker-under-uncertainty.html'
PUBLIC = ROOT / 'poker/poker-under-uncertainty/index.html'
WORKBOOK_ROUTE = '/downloads/poker-opponent-frequency-evidence-workbook.md'
CHECKER_ROUTE = '/downloads/poker-opponent-frequency-verify.py'
NAV = ('<nav class="poker-jump" aria-label="Practice opportunity denominators and sample uncertainty">'
       '<a href="' + WORKBOOK_ROUTE + '" download>Work through an original opponent-frequency evidence worksheet</a>'
       '<a href="' + CHECKER_ROUTE + '" download>Verify the fixed Wilson and Beta calculations (Python)</a>'
       '</nav>')


def module():
    spec = spec_from_file_location('fixed_poker_frequency', CHECKER)
    assert spec and spec.loader
    obj = module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class Turn95FrequencyStandalone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workbook = WORKBOOK.read_text(encoding='utf-8')
        cls.code = CHECKER.read_text(encoding='utf-8')
        cls.verifier = module()
        cls.report = cls.verifier.report()

    def test_standalone_worksheet_is_substantial_and_source_bounded(self):
        self.assertGreater(len(self.workbook.split()), 1050)
        for phrase in ('not player statistics', '3 / 12 = 25%',
                       '3 / 50 = 6%', '8 / 40 = 20%',
                       'Beta(9,33)', 'Beta(4,10)', '7 / 8 = 87.5%',
                       'No account', 'after play', 'verified opportunities'):
            self.assertIn(phrase.lower(), self.workbook.lower())
        self.assertNotIn(chr(0x2014), self.workbook)
        self.assertNotIn('<form', self.workbook)

    def test_reproducible_script_runs_two_modes_and_fixed_model(self):
        for mode in ('--self-test', '--json'):
            out = subprocess.run([sys.executable, str(CHECKER), mode],
                                 capture_output=True, text=True, check=True, timeout=20)
            self.assertEqual(out.stderr, '')
            if mode == '--self-test':
                self.assertIn('PASS: fixed fictional opportunity denominators', out.stdout)
            else:
                self.assertEqual(json.loads(out.stdout), self.report)

    def test_correct_3bet_denominator_is_eligible_opportunities(self):
        r = self.report['initial_opportunities']
        self.assertEqual(Fraction(3, 12), Fraction(1, 4))
        self.assertEqual(self.verifier.observed_rate(3, 12), Fraction(1, 4))
        self.assertEqual((r['hands_dealt'], r['eligible_3bet_opportunities'],
                          r['observed_3bets'], r['ineligible_hands']), (50, 12, 3, 38))
        self.assertEqual(r['observed_rate'], '25.0%')
        self.assertEqual(r['wrong_dealt_hand_denominator_rate'], '6.0%')

    def test_wilson_95_limits_match_independent_model(self):
        a = self.report['initial_opportunities']['wilson_95']
        b = self.report['comparison']['wilson_95']
        self.assertEqual(a, ['8.9%', '53.2%'])
        self.assertEqual(b, ['10.5%', '34.8%'])
        self.assertEqual(self.report['comparison']['observed_rate'], '20.0%')
        self.assertEqual(self.report['zero_successes']['wilson_95'], ['0.0%', '24.2%'])
        self.assertLess(float(b[1][:-1]) - float(b[0][:-1]),
                        float(a[1][:-1]) - float(a[0][:-1]))
        for token in ('8.9% to 53.2%', '10.5% to 34.8%', '24.2%'):
            self.assertIn(token, self.workbook)

    def test_stated_beta_prior_alternative_and_tail_quantiles(self):
        r = self.report['fictional_beta_prior']
        self.assertEqual(r['prior_shapes'], [6, 24])
        self.assertEqual(r['posterior_shapes'], [9, 33])
        self.assertEqual(r['posterior_mean'], '21.43%')
        self.assertEqual(r['equal_tailed_credible_95'], ['10.6%', '34.9%'])
        self.assertEqual(r['alternative_posterior_shapes'], [4, 10])
        self.assertEqual(r['alternative_posterior_mean'], '28.57%')
        self.assertEqual(Fraction(9, 42), Fraction(3, 14))
        self.assertEqual(Fraction(4, 14), Fraction(2, 7))
        for quantile in (0.025, 0.975):
            q = self.verifier.beta_quantile(quantile, 9, 33)
            self.assertAlmostEqual(self.verifier.beta_cdf(q, 9, 33), quantile, places=9)

    def test_second_trap_is_a_conditional_flop_cbet_sample(self):
        r = self.report['other_denominator_trap']
        self.assertEqual(r['conditional_rate'], '87.5%')
        self.assertEqual(r['invalid_as_conditional_rate'], '23.3%')
        self.assertEqual(Fraction(7, 8), Fraction(7, 8))
        self.assertIn('7 / 30 = 23.3%', self.workbook)

    def test_invalid_counts_cannot_silently_create_poker_stats(self):
        for a, b in ((-1, 12), (13, 12), (1, 0), (1.5, 12), (True, 12)):
            with self.subTest(counts=(a, b)):
                with self.assertRaises(ValueError):
                    self.verifier.observed_rate(a, b)
        for a, b in ((0, 2), (-1, 2), (2, 0)):
            with self.assertRaises(ValueError):
                self.verifier.beta_cdf(0.4, a, b)

    def test_script_has_only_standard_library_imports_and_no_network(self):
        tree = ast.parse(self.code)
        imports = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.update(name.name.split('.')[0] for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.split('.')[0])
        self.assertEqual(imports, {'__future__', 'argparse', 'fractions', 'json',
                                   'math', 'statistics'})
        for token in ('requests', 'urllib', 'socket', 'open(', 'read_text(',
                      'write_text(', 'fetch(', 'localStorage', 'prompt('):
            self.assertNotIn(token, self.code)
        self.assertNotIn(chr(0x2014), self.code)


class Turn95SiteIntegration(unittest.TestCase):
    def test_existing_author_article_and_generated_output_have_unique_nav(self):
        source = SOURCE.read_text(encoding='utf-8')
        public = PUBLIC.read_text(encoding='utf-8')
        self.assertEqual(source.count(NAV), 1)
        self.assertEqual(public.count(NAV), 1)
        self.assertEqual(source.count('id="frequencies"'), 1)
        self.assertLess(source.index('id="frequencies"'), source.index(NAV))
        self.assertIn('<p>That is extremely wide.</p>\n' + NAV, source)
        self.assertIn('id="frequencies"', public)
        self.assertIn('rel="canonical" href="https://nolankido.com/poker/poker-under-uncertainty/"', public)
        self.assertNotIn(chr(0x2014), NAV)

    def test_existing_index_and_sitemap_not_inflated_by_new_downloads(self):
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        for route in (WORKBOOK_ROUTE, CHECKER_ROUTE):
            self.assertNotIn('https://nolankido.com' + route, sitemap)
            self.assertNotIn(route, finder)
        self.assertIn('301 entries available.', finder)
        release = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        for name in ('poker-opponent-frequency-evidence-workbook.md',
                     'poker-opponent-frequency-verify.py'):
            self.assertEqual(release.count("'downloads/" + name + "'"), 1)

    def test_full_builder_parity_and_no_github_actions(self):
        sys.path.insert(0, str(ROOT / '_scripts'))
        import build
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path('poker/poker-under-uncertainty/index.html')],
                         PUBLIC.read_text(encoding='utf-8'))
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn95_poker_opponent_frequency.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yml', '.yaml') for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
