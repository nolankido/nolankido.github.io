"""Turn 94: a local-only reset restores the original fictional poker examples.

Eight standalone tests cover the exact source and public HTML. Three
integration checks require the complete matching website checkout.
No player data, cookies, automatic copies or network calls are involved.
"""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source/poker/pot-odds-sensitivity-lab.html'
OUTPUT = ROOT / 'downloads/poker-pot-odds-sensitivity-lab.html'
ROUTE = '/downloads/poker-pot-odds-sensitivity-lab.html'


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def reset_problems(html):
    issues = []
    tags = Elements(html).tags
    ids = [a['id'] for _, a in tags if 'id' in a]
    if len(ids) != len(set(ids)):
        issues.append('Duplicate HTML IDs')
    buttons = [a for tag, a in tags if tag == 'button']
    reset = [a for a in buttons if a.get('id') == 'study-reset']
    select = [a for a in buttons if a.get('id') == 'study-select']
    drills = [a for a in buttons if a.get('data-drill')]
    if len(reset) != 1 or reset[0].get('type') != 'button' or (
        'disabled' not in reset[0] or reset[0].get('aria-controls') !=
        'river-low river-high raise-equity bluff-fold study-record'):
        issues.append('Reset must start disabled without JavaScript and identify controlled elements')
    if len(select) != 1 or select[0].get('type') != 'button' or 'disabled' not in select[0]:
        issues.append('Existing study select button changed')
    if len(buttons) != 6 or len(drills) != 4:
        issues.append('Expect exactly four old presets and two note actions')
    inputs = [a for tag, a in tags if tag == 'input']
    defaults = {'river-low': ('22', '1'), 'river-high': ('29', '1'),
                'raise-equity': ('25', '1'), 'bluff-fold': ('40', '0.5')}
    if len(inputs) != 4 or any(a.get('id') not in defaults or
         (a.get('value'), a.get('step')) != defaults.get(a.get('id')) for a in inputs):
        issues.append('Four fixed original model default inputs changed')
    for required in (
        "const resetButton = el('study-reset');",
        'resetButton.disabled = false;',
        "resetButton.addEventListener('click', () => {",
        "for (const input of document.querySelectorAll('input[type=\"range\"]')) input.value = input.defaultValue;",
        "render();\n    el('river-low').focus();",
        "el('study-record').value = lines.join('\\n');",
        "el('study-print').textContent = el('study-record').value;",
        "record.select();",
        'Restore original example settings to return all four assumptions and both study records',
        '.study-actions{margin-top:12px;display:flex;flex-wrap:wrap;gap:10px}',
        '@media print{',
        '.study-actions{display:none!important}',
        'id="study-print" aria-hidden="true"',
        '<noscript>',
    ):
        if required not in html:
            issues.append('Missing reset or print contract: ' + required)
    for forbidden in ('navigator.clipboard', 'localStorage', 'sessionStorage',
                      'XMLHttpRequest', 'fetch(', 'document.cookie', 'indexedDB',
                      'innerHTML', '<form', '<iframe', '<script src=', chr(0x2014)):
        if forbidden in html:
            issues.append('Unexpected persistence, network, form or unsafe source')
    return issues


class Turn94StandaloneReset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.output = OUTPUT.read_text(encoding='utf-8')

    def test_exact_source_and_public_html_and_offline_policy(self):
        self.assertEqual(self.source, self.output)
        self.assertEqual(reset_problems(self.source), [])
        self.assertIn('content="noindex, follow"', self.source)
        self.assertIn("connect-src 'none'", self.source)

    def test_one_reset_button_initially_disabled_with_explicit_scope(self):
        parsed = Elements(self.source).tags
        button = next(a for tag, a in parsed if tag == 'button' and a.get('id') == 'study-reset')
        self.assertEqual(button['type'], 'button')
        self.assertIn('disabled', button)
        self.assertEqual(button['aria-controls'], 'river-low river-high raise-equity bluff-fold study-record')
        self.assertEqual(self.source.count('id="study-reset"'), 1)
        self.assertEqual(self.source.count('data-drill='), 4)

    def test_all_four_original_defaults_have_correct_independent_math(self):
        self.assertEqual([F(q,100)*40-10 for q in (22,29)], [F(-6,5),F(8,5)])
        self.assertEqual(F(25,100)*38-10, F(-1,2))
        self.assertEqual(F(40,100)*10-F(60,100)*6, F(2,5))
        self.assertEqual(F(10,38), F(5,19))
        for value in ('value="22" disabled', 'value="29" disabled',
                      'value="25" step="1" disabled', 'value="40" step="0.5" disabled'):
            self.assertIn(value, self.source)

    def test_reset_uses_actual_dom_defaults_not_an_unchecked_literal_map(self):
        self.assertIn("input.value = input.defaultValue;", self.source)
        self.assertIn("resetButton.addEventListener('click', () => {", self.source)
        self.assertIn("render();\n    el('river-low').focus();", self.source)
        self.assertEqual(self.source.count('input.value = input.defaultValue;'), 1)

    def test_study_record_and_print_mirror_use_same_render_path(self):
        self.assertIn("el('study-record').value = lines.join('\\n');", self.source)
        self.assertIn("el('study-print').textContent = el('study-record').value;", self.source)
        textarea = re.findall(r'<textarea\b[^>]*id="study-record"[^>]*>(.*?)</textarea>', self.source, re.S)
        mirror = re.findall(r'<pre\b[^>]*id="study-print"[^>]*>(.*?)</pre>', self.source, re.S)
        self.assertEqual(len(textarea), 1)
        self.assertEqual(textarea, mirror)
        self.assertIn('UNVERIFIED: No evidence for assumed opponent', mirror[0])
        self.assertIn('3. PURE BLUFF', mirror[0])

    def test_native_copy_select_and_original_preset_behavior_retained(self):
        self.assertIn("selectButton.addEventListener('click', () => {", self.source)
        self.assertIn("record.select();", self.source)
        for ident in ('river', 'raise-low', 'raise-high', 'bluff-zero'):
            self.assertIn('data-drill="' + ident + '"', self.source)
        self.assertIn("el(preset[0][0]).focus();", self.source)
        self.assertNotIn('navigator.clipboard', self.source)

    def test_reset_and_selection_stay_hidden_in_print_while_note_prints(self):
        self.assertIn('.study-actions{display:none!important}', self.source)
        self.assertIn('#study-record-panel .study-print{display:block!important;', self.source)
        self.assertIn('#study-record-panel{break-inside:auto;page-break-inside:auto}', self.source)
        self.assertIn('Restore original example settings', self.source)
        self.assertIn('Nothing is saved, transmitted, or copied automatically.', self.source)

    def test_negative_controls_detect_reset_malfunctions(self):
        mutations = (
            ('id="study-reset" type="button"', 'id="study-reset" type="submit"'),
            ('disabled>Restore original example settings', '>Restore original example settings'),
            ('input.value = input.defaultValue;', 'input.value = "50";'),
            ('resetButton.disabled = false;', 'resetButton.disabled = true;'),
            ("render();\n    el('river-low').focus();", "el('river-low').focus();"),
            ('id="study-print" aria-hidden="true"', 'id="removed-print" aria-hidden="true"'),
            ('value="22" disabled', 'value="45" disabled'),
        )
        for before, after in mutations:
            with self.subTest(before=before):
                self.assertIn(before, self.source)
                self.assertTrue(reset_problems(self.source.replace(before, after, 1)))


class Turn94SiteIntegration(unittest.TestCase):
    def test_original_legacy_safety_guards_keep_four_and_only_four_sliders(self):
        t91 = (ROOT / '_tests/test_turn91_threshold_boundary_drill.py').read_text(encoding='utf-8')
        t92 = (ROOT / '_tests/test_turn92_private_study_record.py').read_text(encoding='utf-8')
        self.assertIn("'study-select', 'study-reset'", t91)
        self.assertIn('len(buttons) != 6', t92)
        self.assertEqual(Elements(SOURCE.read_text(encoding='utf-8')).tags.count(('form', {})), 0)

    def test_broader_browser_suite_and_local_runner_cover_the_reset(self):
        browser = (ROOT / '_tests/pot_odds_sensitivity_browser.py').read_text(encoding='utf-8')
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        for marker in ('#study-reset', 'input_value()', 'study-print', 'is_disabled()'):
            self.assertIn(marker, browser)
        self.assertIn('test_turn94_restore_lab_baseline.py', runner)

    def test_no_sitemap_inflation_and_release_inventory_unchanged(self):
        self.assertNotIn(ROUTE, (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        self.assertNotIn(ROUTE, (ROOT / 'poker/find/index.html').read_text(encoding='utf-8'))
        self.assertIn("'downloads/poker-pot-odds-sensitivity-lab.html'", (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8'))
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(p.is_file() and p.suffix.lower() in ('.yml', '.yaml') for p in actions.iterdir()))


if __name__=='__main__':
    unittest.main()
