"""Turn 92: preserve fictional assumptions in a safe, copyable offline study record.

The standalone suite is independent of a full site checkout. The integration
suite must run against the matching complete repository and its live checker.
No user hand entry, model call, database, download action, or network access.
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


class Tags(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


def static_note(html):
    notes = re.findall(r'<textarea\b([^>]*)>(.*?)</textarea>', html, re.S)
    if len(notes) != 1:
        raise ValueError('Expected one read-only study note')
    return notes[0]


def contract_problems(html):
    problems = []
    parsed = Tags(html).items
    ids = [attrs['id'] for _, attrs in parsed if 'id' in attrs]
    if len(ids) != len(set(ids)):
        problems.append('Duplicate ID')
    try:
        attrs, note = static_note(html)
    except ValueError as error:
        return [str(error)]
    if not all(marker in attrs for marker in ('id="study-record"', 'readonly', 'aria-describedby="study-record-help"')):
        problems.append('Study record must be private and read only')
    labels = [a for tag, a in parsed if tag == 'label']
    if len(labels) != 5 or len([x for x in labels if x.get('for') == 'study-record']) != 1:
        problems.append('Study record label and four original slider labels are required')
    buttons = [a for tag, a in parsed if tag == 'button']
    select_buttons = [a for a in buttons if a.get('id') == 'study-select']
    if len(select_buttons) != 1 or not all(x in select_buttons[0] for x in ('disabled',)) or (
        select_buttons[0].get('type') != 'button' or select_buttons[0].get('aria-controls') != 'study-record'):
        problems.append('Select control must be an initially disabled non-submitting button')
    reset_buttons = [a for a in buttons if a.get('id') == 'study-reset']
    if (len(reset_buttons) != 1 or 'disabled' not in reset_buttons[0]
        or reset_buttons[0].get('type') != 'button' or
        reset_buttons[0].get('aria-controls') !=
            'river-low river-high raise-equity bluff-fold study-record'):
        problems.append('Reset must be a controlled initially disabled button')
    if len(buttons) != 6 or len([a for a in buttons if a.get('data-drill')]) != 4:
        problems.append('Original four boundary controls must be preserved')
    if len([a for tag, a in parsed if tag == 'input']) != 4:
        problems.append('Only the four fictional model inputs are permitted')
    for snippet in (
        'Not a real hand, opponent estimate, solver output, or action recommendation.',
        'Selected lower 22%, upper 29%; evaluated band 22% to 29%.',
        '-1.20 BB to +1.60 BB',
        'Selected hypothetical showdown equity 25%. Modeled call EV versus folding -0.50 BB',
        'Selected hypothetical fold rate 40%. Modeled bluff EV versus checking +0.40 BB',
        'UNVERIFIED: No evidence for assumed opponent equity/fold rates',
        'Nothing is saved, transmitted, or copied automatically.',
    ):
        if snippet not in note:
            problems.append('Missing reproducible static note: ' + snippet)
    if not all(t in html for t in (
        "const lines = [", "el('study-record').value = lines.join('\\n')",
        "selectButton.addEventListener('click'", "record.focus();", "record.select();",
        "selectButton.disabled = false;", 'id="study-record-help"',
    )):
        problems.append('Missing live or accessible record logic')
    if not any(tag == 'noscript' for tag, _ in parsed):
        problems.append('No-script safety explanation missing')
    if any(tag in ('form', 'iframe', 'object') for tag, _ in parsed):
        problems.append('No submission or embedding allowed')
    if any(tag == 'script' and 'src' in attrs for tag, attrs in parsed):
        problems.append('No remote scripts allowed')
    if any(token in html for token in (
        'navigator.clipboard', 'localStorage', 'sessionStorage', 'XMLHttpRequest',
        'fetch(', 'indexedDB', 'document.cookie', 'innerHTML', 'https://', chr(0x2014),
    )):
        problems.append('No clipboard, persistence, network, untrusted HTML or prohibited punctuation')
    return problems


class StandaloneTurn92StudyRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.public = OUTPUT.read_text(encoding='utf-8')

    def test_authored_and_published_html_identical(self):
        self.assertEqual(self.source, self.public)
        self.assertEqual(contract_problems(self.source), [])
        self.assertTrue(self.source.startswith('<!doctype html>'))

    def test_initial_fictional_record_contains_three_models_and_exclusions(self):
        _, note = static_note(self.source)
        for name in ('1. RIVER CALL', '2. RAISE TO 14 BB', '3. PURE BLUFF'):
            self.assertEqual(note.count(name), 1)
        for excluded in ('no rake', 'side pots', 'future betting', 'bounties', 'ICM'):
            self.assertIn(excluded, note)
        self.assertIn('Action closes', note)
        self.assertIn('No evidence for assumed opponent equity/fold rates', note)

    def test_static_snapshot_river_fraction_exact(self):
        a, b = F(22, 100), F(29, 100)
        self.assertEqual(F(10, 40), F(1, 4))
        self.assertEqual([p * 40 - 10 for p in (a, b)], [F(-6, 5), F(8, 5)])
        self.assertIn('-1.20 BB to +1.60 BB', static_note(self.source)[1])

    def test_static_snapshot_raise_price_exact(self):
        self.assertEqual((10 + 4 + 14, 14 - 4, 10 + 4 + 14 + 10), (28, 10, 38))
        self.assertEqual(F(10, 38), F(5, 19))
        self.assertEqual(F(1, 4) * 38 - 10, F(-1, 2))
        self.assertIn('5/19 (about 26.3158%)', static_note(self.source)[1])

    def test_static_snapshot_zero_equity_bluff_exact(self):
        self.assertEqual(F(6, 10 + 6), F(3, 8))
        self.assertEqual(F(6, 10 + 6 + 6), F(3, 11))
        self.assertEqual(F(2, 5) * 10 - F(3, 5) * 6, F(2, 5))
        self.assertIn('Bettor break-even fold rate 37.5%', static_note(self.source)[1])

    def test_note_rerenders_from_all_four_model_controls(self):
        self.assertIn("const low = Number(el('river-low').value)", self.source)
        self.assertIn("const q = Number(el('raise-equity').value)", self.source)
        self.assertIn("const f = Number(el('bluff-fold').value)", self.source)
        self.assertIn('el(\'study-record\').value = lines.join(\'\\n\')', self.source)
        self.assertIn("input.addEventListener('input', render)", self.source)
        self.assertIn("button.addEventListener('click'", self.source)
        self.assertIn("el(preset[0][0]).focus()", self.source)
        self.assertIn("Math.min(low, high)", self.source)
        self.assertIn("Math.max(low, high)", self.source)

    def test_native_selection_requires_explicit_user_click(self):
        self.assertIn('id="study-select" type="button" aria-controls="study-record" disabled', self.source)
        self.assertIn("selectButton.addEventListener('click'", self.source)
        self.assertIn('record.focus();', self.source)
        self.assertIn('record.select();', self.source)
        self.assertNotIn('writeText(', self.source)
        self.assertNotIn('execCommand(', self.source)
        self.assertNotIn('createObjectURL(', self.source)

    def test_mutated_privacy_consent_and_static_fact_controls_fail(self):
        examples = (
            (' readonly spellcheck=', ' spellcheck='),
            ('disabled>Select full record', '>Select full record'),
            ('for="study-record"', 'for="absent-study"'),
            ('Selected lower 22%, upper 29%', 'Selected lower 100%, upper 0%'),
            ('record.select();', 'record.focus();'),
            ("const lines = [", "const missingLines = ["),
            ('<noscript>', '<!-- removed -->'),
        )
        for before, after in examples:
            with self.subTest(before=before):
                self.assertIn(before, self.source)
                tampered = self.source.replace(before, after, 1)
                self.assertNotEqual(tampered, self.source)
                self.assertTrue(contract_problems(tampered))


class SiteTurn92Integration(unittest.TestCase):
    def test_existing_boundary_and_slider_safety_tests_support_readonly_note(self):
        old = (ROOT / '_tests/test_turn90_offline_sensitivity_lab.py').read_text(encoding='utf-8')
        next_one = (ROOT / '_tests/test_turn91_threshold_boundary_drill.py').read_text(encoding='utf-8')
        self.assertIn('"study-record"', old)
        self.assertIn("copy_buttons = [attrs", next_one)
        self.assertIn("len(buttons) != 4", next_one)

    def test_manual_release_registration_and_browser_study_note_coverage(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        browser = (ROOT / '_tests/pot_odds_sensitivity_browser.py').read_text(encoding='utf-8')
        self.assertIn('test_turn92_private_study_record.py', runner)
        for marker in ('#study-record', '#study-select', 'record.input_value()',
                       'selectionStart === 0', 'is_disabled()'):
            self.assertIn(marker, browser)

    def test_source_resource_scope_sitemap_finder_and_no_actions(self):
        article = (ROOT / 'poker/pot-odds-workshop/index.html').read_text(encoding='utf-8')
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/pot-odds-workshop/">', article)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('https://nolankido.com' + ROUTE, sitemap)
        find = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        self.assertNotIn(ROUTE, find)
        release = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(release.count("'downloads/poker-pot-odds-sensitivity-lab.html'"), 1)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            item.is_file() and item.suffix.lower() in ('.yaml', '.yml')
            for item in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
