"""Turn 93: full private study note prints without a clipped form control.

Eight standalone tests use the self-contained lab only. Three integration tests
require a matching complete website checkout. No PDF or browser dependency here.
"""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source/poker/pot-odds-sensitivity-lab.html'
PUBLIC = ROOT / 'downloads/poker-pot-odds-sensitivity-lab.html'
ROUTE = '/downloads/poker-pot-odds-sensitivity-lab.html'


def sections(html):
    note = re.findall(r'<textarea\b[^>]*id="study-record"[^>]*>(.*?)</textarea>', html, re.S)
    printed = re.findall(r'<pre\b[^>]*id="study-print"[^>]*>(.*?)</pre>', html, re.S)
    if len(note) != 1 or len(printed) != 1:
        raise ValueError('Exactly one editable-view note and print view required')
    return note[0], printed[0]


def print_problems(html):
    errors = []
    try:
        note, printed = sections(html)
    except ValueError as exc:
        return [str(exc)]
    if note != printed:
        errors.append('Static print contents must equal textarea contents')
    if '<pre class="study-print" id="study-print" aria-hidden="true">' not in html:
        errors.append('Screen-hidden noninteractive print mirror required')
    if '.study-print{display:none}' not in html:
        errors.append('Print mirror must not be visible on screen')
    if '#study-record-panel .study-record-box{display:none!important}' not in html:
        errors.append('Clipped textarea must not print')
    if '#study-record-panel .study-print{display:block!important;' not in html:
        errors.append('Full text must print')
    if '#study-record-panel{break-inside:auto;page-break-inside:auto}' not in html:
        errors.append('Study panel must be allowed to span paper pages')
    if 'white-space:pre-wrap;overflow-wrap:anywhere' not in html:
        errors.append('Print text must wrap at paper width')
    if "el('study-print').textContent = el('study-record').value;" not in html:
        errors.append('Print mirror must update when current note changes')
    if 'aria-describedby="study-record-help"' not in html:
        errors.append('Accessible existing note help missing')
    for token in ('localStorage', 'sessionStorage', 'navigator.clipboard',
                  'document.cookie', 'XMLHttpRequest', 'fetch(', '<form',
                  '<iframe', '<script src=', chr(0x2014)):
        if token in html:
            errors.append('Privacy/network/source restriction violated: ' + token)
    return errors


class Turn93StandalonePrint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.public = PUBLIC.read_text(encoding='utf-8')

    def test_source_and_public_are_identical_and_print_contract_passes(self):
        self.assertEqual(self.source, self.public)
        self.assertEqual(print_problems(self.source), [])

    def test_static_print_contains_every_fictional_case_and_final_warning(self):
        _, printable = sections(self.source)
        for marker in ('1. RIVER CALL', '2. RAISE TO 14 BB', '3. PURE BLUFF',
                       'UNVERIFIED: No evidence for assumed opponent',
                       'Nothing is saved, transmitted, or copied automatically.'):
            self.assertIn(marker, printable)
        self.assertGreater(len(printable.splitlines()), 17)

    def test_print_does_not_clip_original_scrollable_textarea(self):
        self.assertIn('rows="17" readonly', self.source)
        self.assertIn('#study-record-panel .study-record-box{display:none!important}', self.source)
        self.assertIn('#study-record-panel .study-print{display:block!important;', self.source)
        self.assertIn('break-inside:auto', self.source)

    def test_render_updates_print_only_as_text_not_markup(self):
        self.assertIn("el('study-record').value = lines.join('\\n');", self.source)
        self.assertIn("el('study-print').textContent = el('study-record').value;", self.source)
        self.assertNotIn("el('study-print').innerHTML", self.source)
        self.assertEqual(self.source.count('id="study-print"'), 1)

    def test_no_javascript_fallback_print_has_same_static_words(self):
        note, printed = sections(self.source)
        self.assertEqual(note, printed)
        self.assertIn('<noscript>', self.source)
        self.assertIn('id="study-select" type="button"', self.source)
        self.assertIn('disabled>Select full record', self.source)
        self.assertIn('no rake, side pots, future betting, bounties, or ICM', printed)

    def test_printable_poker_maths_are_still_correct(self):
        self.assertEqual([F(k,100)*40-10 for k in (22,29)], [F(-6,5),F(8,5)])
        self.assertEqual(F(10,38),F(5,19))
        self.assertEqual(F(25,100)*38-10,F(-1,2))
        self.assertEqual(F(6,16),F(3,8))
        self.assertEqual(F(2,5)*10-F(3,5)*6,F(2,5))
        printable = sections(self.source)[1]
        for marker in ('-1.20 BB to +1.60 BB','-0.50 BB','+0.40 BB','3/11'):
            self.assertIn(marker, printable)

    def test_safety_regressions_catch_clipping_stale_print_and_privacy(self):
        examples = (
            ('#study-record-panel .study-record-box{display:none!important}', '/* textarea visible */'),
            ('#study-record-panel .study-print{display:block!important;', '#study-record-panel .study-print{display:none!important;'),
            ("el('study-print').textContent = el('study-record').value;", '/* print mirror not updated */'),
            ('<pre class="study-print" id="study-print" aria-hidden="true">', '<pre class="study-print" id="study-print">'),
            ('UNVERIFIED: No evidence for assumed opponent', 'ASSUMPTIONS VERIFIED'),
            ('break-inside:auto;page-break-inside:auto', 'break-inside:avoid;page-break-inside:avoid'),
        )
        for before, after in examples:
            with self.subTest(change=before):
                self.assertIn(before, self.source)
                self.assertTrue(print_problems(self.source.replace(before, after, 1)))

    def test_original_sliders_and_boundary_buttons_unmodified(self):
        self.assertEqual(len(re.findall(r'<input\b[^>]*type="range"', self.source)), 4)
        self.assertEqual(self.source.count('data-drill='), 4)
        self.assertIn('step="0.5" disabled', self.source)
        self.assertEqual(self.source.count('role="status"'), 3)
        self.assertIn('content="noindex, follow"', self.source)
        self.assertIn("connect-src 'none'", self.source)


class Turn93SiteIntegration(unittest.TestCase):
    def test_original_indexed_workshop_remains_different_page(self):
        article = (ROOT / 'poker/pot-odds-workshop/index.html').read_text(encoding='utf-8')
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/pot-odds-workshop/">', article)
        self.assertNotIn('id="study-print"', article)
        self.assertIn('href="' + ROUTE + '"', article)

    def test_release_inventory_browser_checks_and_runner_cover_print(self):
        self.assertEqual((ROOT / '_scripts/check_live.py').read_text(encoding='utf-8').count(
            "'downloads/poker-pot-odds-sensitivity-lab.html'"), 1)
        browser = (ROOT / '_tests/pot_odds_sensitivity_browser.py').read_text(encoding='utf-8')
        for marker in ('#study-print', 'study-print', 'emulate_media(media="print")',
                       'mirror.text_content()'):
            self.assertIn(marker, browser)
        self.assertIn('test_turn93_full_print_record.py',
                      (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8'))

    def test_no_new_sitemap_finder_or_action_workflows(self):
        self.assertNotIn(ROUTE, (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        self.assertNotIn(ROUTE, (ROOT / 'poker/find/index.html').read_text(encoding='utf-8'))
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yaml','.yml')
            for p in actions.iterdir()))


if __name__=='__main__': unittest.main()
