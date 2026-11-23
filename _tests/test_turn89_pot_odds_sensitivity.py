"""Turn 89: exact arithmetic, publication limits and discovery for the workbook.

Local-only. No GPU solver, live player inputs, model call, network access,
GitHub Actions, new analytics, or search visibility claims.
"""
from __future__ import annotations

import ast
from fractions import Fraction as F
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/poker-pot-odds-sensitivity-verify.py'
WORKBOOK = ROOT / 'downloads/poker-pot-odds-sensitivity-workbook.md'
SRC = ROOT / '_source/poker/pot-odds-workshop.html'
PUBLIC = ROOT / 'poker/pot-odds-workshop/index.html'
NAV = re.compile(r'<nav class="article-navigation" aria-label="Continue studying">.*?</nav>', re.S)
DOC = '/downloads/poker-pot-odds-sensitivity-workbook.md'
CODE = '/downloads/poker-pot-odds-sensitivity-verify.py'


class Turn89ExactMathAndWorkbook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKBOOK.read_text(encoding='utf-8')
        cls.script = SCRIPT.read_text(encoding='utf-8')
        cls.report = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), '--json'],
            text=True, capture_output=True, check=True, timeout=15).stdout)

    def test_script_self_test_executes_without_network_or_other_inputs(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--self-test'],
                                text=True, capture_output=True, check=True, timeout=15)
        self.assertIn('PASS: exact fictional pot-odds', result.stdout)
        tree = ast.parse(self.script)
        imports = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.update(part.name.split('.')[0] for part in node.names)
            if isinstance(node, ast.ImportFrom):
                imports.add(node.module.split('.')[0])
        self.assertEqual(imports, {'__future__', 'argparse', 'fractions', 'json'})
        for token in ('requests.', 'urllib.', 'socket.', 'open(', 'write_text(', 'read_text('):
            self.assertNotIn(token, self.script)

    def test_river_price_is_independent_of_equity_assumptions(self):
        river = self.report['river_call']
        p, c = 20 + 10, 10
        self.assertEqual((river['pot_at_decision'], river['additional_call'], river['final_pot']), (p, c, p+c))
        self.assertEqual(F(river['break_even_equity']), F(c, p+c))
        for q, expected in ((F(1, 5), F(-2)), (F(1, 4), F(0)), (F(3, 10), F(2))):
            self.assertEqual(F(river['equity_to_ev'][str(q)]), expected)
            self.assertEqual(q * F(40) - c, expected)
        self.assertEqual([F(x) for x in river['sensitivity_ev_interval']], [F(-6, 5), F(8, 5)])
        self.assertEqual(F(river['ev_change_per_equity_percentage_point']), F(2, 5))
        for term in ('25%', '-2 BB', '+2 BB', '22% to 29%', '-1.2 to +1.6 BB', '0.4 BB'):
            self.assertIn(term, self.text)

    def test_raise_to_reconstruction_and_model_price(self):
        row = self.report['raise_to']
        self.assertEqual((F(row['pot_at_decision']), F(row['additional_call']), F(row['final_pot'])),
                         (F(10 + 4 + 14), F(14 - 4), F(38)))
        self.assertEqual(F(row['break_even_equity']), F(5, 19))
        self.assertEqual(F(row['equity_to_ev']['1/4']), F(-1, 2))
        self.assertEqual(F(row['equity_to_ev']['3/10']), F(7, 5))
        for phrase in ('26.32%', '-0.5 BB', '+1.4 BB'):
            self.assertIn(phrase, self.text)

    def test_bettor_fold_threshold_is_different_from_caller_price(self):
        row = self.report['pure_bluff']
        self.assertEqual(F(row['fold_break_even']), F(6, 10+6))
        self.assertEqual(F(row['caller_break_even_equity']), F(6, 10+2*6))
        self.assertNotEqual(F(row['fold_break_even']), F(row['caller_break_even_equity']))
        for f, ev in ((F(3, 10), F(-6, 5)), (F(3, 8), F(0)), (F(2, 5), F(2, 5)), (F(1, 2), F(2))):
            self.assertEqual(F(row['fold_probability_to_ev'][str(f)]), ev)
            self.assertEqual(f*10 - (1-f)*6, ev)
        for phrase in ('37.5%', '27.27%', '-1.2 BB', '+0.4 BB'):
            self.assertIn(phrase, self.text)

    def test_four_independent_practice_answers_and_no_solver_promise(self):
        # Independently recomputed, not sourced from the companion script's report.
        self.assertEqual(F(9, 30), F(3, 10))  # A
        self.assertEqual((F(28, 100)*30-9, F(36, 100)*30-9), (F(-3, 5), F(9, 5)))
        self.assertEqual(F(9-3, 10+3+9+(9-3)), F(3, 14))  # B
        self.assertEqual(F(20, 100)*28-6, F(-2, 5))
        self.assertEqual((F(6, 12+6), F(30, 100)*12-F(70, 100)*6, F(6, 12+12)),
                         (F(1, 3), F(-3, 5), F(1, 4)))  # C
        self.assertEqual((F(5, 30), F(15, 100)*30-5, F(19, 100)*30-5, F(30, 100)),
                         (F(1, 6), F(-1, 2), F(7, 10), F(3, 10)))  # D
        for term in ('Four questions', 'Case A', 'Case B', 'Case C', 'Case D',
                     'Answer key', '21.43%', '33.33%', '16.67%', '0.3 BB'):
            self.assertIn(term, self.text)
        for scope in ('side pot', 'ICM', 'after-play', 'not a solver', 'future betting'):
            self.assertIn(scope.lower(), self.text.lower())
        self.assertNotIn(chr(0x2014), self.text)

    def test_input_validation_denies_impossible_price_or_probability(self):
        code = runpy.run_path(str(SCRIPT))
        for function, values in (
            ('call_price', (F(5), F(0))),
            ('call_ev', (F(30), F(10), F(11, 10))),
            ('call_ev', (F(30), F(10), F(-1, 10))),
            ('facing_raise_to', (F(10), F(4), F(4))),
            ('pure_bluff_ev', (F(10), F(6), F(-1, 10))),
            ('pure_bluff_fold_price', (F(0), F(6))),
        ):
            with self.subTest(function=function, values=values), self.assertRaises(ValueError):
                code[function](*values)


class Turn89SiteRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SRC.read_text(encoding='utf-8')
        cls.html = PUBLIC.read_text(encoding='utf-8')
        cls.workbook = WORKBOOK.read_text(encoding='utf-8')
        cls.code = SCRIPT.read_text(encoding='utf-8')

    def test_source_and_compiled_workshop_share_unchanged_canonical_and_single_nav(self):
        a, b = NAV.findall(self.source), NAV.findall(self.html)
        self.assertEqual(len(a), 1)
        self.assertEqual(a, b)
        for url in (DOC, CODE, '/poker/practice-room/', '/poker/range-combinations/'):
            self.assertEqual(a[0].count('href="' + url + '"'), 1)
        self.assertEqual(a[0].count(' download>'), 2)
        self.assertIn('href="https://www.pokerstars.com/poker/learn/lesson/pot-odds/"', self.source)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/pot-odds-workshop/">', self.html)
        self.assertIn('<meta property="article:modified_time" content="2026-10-06">', self.html)

    def test_source_navigation_does_not_reindex_private_workbook_answers(self):
        sys.path.insert(0, str(ROOT / '_scripts'))
        import poker_finder
        old_nav = '<nav class="article-navigation" aria-label="Continue studying"><a href="/poker/practice-room/">Test this in the practice room</a><a href="/poker/range-combinations/">Count the range behind the percentage</a></nav>'
        current_nav = NAV.search(self.source).group(0)
        self.assertEqual(self.source.count(current_nav), 1)
        before = self.source.replace(current_nav, old_nav)
        self.assertEqual(poker_finder.GuideText(before).sections,
                         poker_finder.GuideText(self.source).sections)
        finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        self.assertIn('301 entries available.', finder)
        self.assertNotIn('poker-pot-odds-sensitivity-workbook.md', finder)

    def test_exact_get_inventory_and_sitemap_scope_remain(self):
        sys.path.insert(0, str(ROOT / '_scripts'))
        import check_live
        targets = check_live.targets(ROOT)
        self.assertEqual(targets[DOC], (200, WORKBOOK.read_bytes()))
        self.assertEqual(targets[CODE], (200, SCRIPT.read_bytes()))
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn(DOC, sitemap)
        self.assertNotIn(CODE, sitemap)
        self.assertEqual(sitemap.count('<loc>https://nolankido.com/poker/pot-odds-workshop/</loc>'), 1)

    def test_generated_workshop_matches_current_build(self):
        sys.path.insert(0, str(ROOT / '_scripts'))
        import build
        self.assertEqual(build.build_outputs()[Path('poker/pot-odds-workshop/index.html')],
                         self.html)

    def test_runner_and_no_repository_authored_github_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn89_pot_odds_sensitivity.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yml', '.yaml')
            for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
