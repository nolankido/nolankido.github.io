"""Turn 91: exact threshold calibration in the offline poker sensitivity lab.

Seven checks can run against the two standalone HTML files alone; the
remaining checks require the complete published site repository.
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
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.start_tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.start_tags.append((tag, dict(attrs)))


def errors(html):
    tags = Elements(html).start_tags
    buttons = [attrs for tag, attrs in tags if tag == 'button' and 'data-drill' in attrs]
    copy_buttons = [attrs for tag, attrs in tags if tag == 'button' and 'data-drill' not in attrs]
    inputs = {attrs['id']: attrs for tag, attrs in tags if tag == 'input' and 'id' in attrs}
    reasons = []
    controlled = {b.get('id'): b for b in copy_buttons}
    if (len(copy_buttons) != 2 or set(controlled) != {'study-select', 'study-reset'}
        or any(b.get('type') != 'button' or 'disabled' not in b or not b.get('aria-controls')
               for b in copy_buttons)):
        reasons.append('Study record select and reset buttons not controlled')
    expected = {'river', 'raise-low', 'raise-high', 'bluff-zero'}
    if len(buttons) != 4 or {b.get('data-drill') for b in buttons} != expected:
        reasons.append('Boundary preset coverage changed')
    if any(b.get('type') != 'button' or 'disabled' not in b or 'aria-controls' not in b
           for b in buttons):
        reasons.append('Unsafe or inaccessible boundary control')
    if len(inputs) != 4 or inputs.get('bluff-fold', {}).get('step') != '0.5' or any(
        val.get('step') != '1' for ident, val in inputs.items() if ident != 'bluff-fold'):
        reasons.append('Boundary step must permit exact 37.5%')
    if not all('disabled' in v for v in inputs.values()):
        reasons.append('No-JavaScript controls must start disabled')
    if sum(1 for tag, attrs in tags if tag == 'h1') != 1:
        reasons.append('Missing unique document title')
    if not any(tag == 'section' and attrs.get('id') == 'boundary-drill' for tag, attrs in tags):
        reasons.append('Missing boundary drill section')
    if 'const drills = {' not in html or 'button.addEventListener(\'click\'' not in html:
        reasons.append('Missing local-only click mapping')
    if not any(tag == 'noscript' for tag, attrs in tags):
        reasons.append('Missing offline fallback')
    if any(tag == 'script' and 'src' in attrs for tag, attrs in tags) or any(
        tag in ('form', 'iframe', 'object') for tag, attrs in tags):
        reasons.append('External script or data collection')
    if any(s in html for s in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage',
                               'innerHTML', 'https://', chr(0x2014))):
        reasons.append('Unexpected external behavior or typography')
    return reasons


class Turn91ThresholdDrill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.output = OUTPUT.read_text(encoding='utf-8')

    def test_authored_html_exactly_matches_published_bytes(self):
        self.assertEqual(self.source, self.output)
        self.assertTrue(self.source.startswith('<!doctype html>'))
        self.assertEqual(errors(self.source), [])

    def test_original_scenarios_and_their_default_results_remain(self):
        for marker in ('id="river-result"', 'id="raise-result"', 'id="bluff-result"',
                       'id="river-low"', 'id="river-high"', 'id="raise-equity"',
                       'id="bluff-fold"', '-1.20 to +1.60 BB', '37.5%', '3/11', '5/19'):
            self.assertIn(marker, self.output)
        self.assertEqual(self.output.count('<h1'), 1)
        self.assertIn('The fixed examples and formulas remain readable',
                      self.source.replace('original fixed examples and formulas remain readable',
                                          'The fixed examples and formulas remain readable'))

    def test_river_exact_boundary_three_point_example(self):
        values = [F(n, 100) * 40 - 10 for n in (24, 25, 26)]
        self.assertEqual(values, [F(-2, 5), F(0), F(2, 5)])
        for text in ('24%', '25%', '26%', '-0.40 BB', '+0.40 BB',
                     "river: [['river-low', 24], ['river-high', 26]]"):
            self.assertIn(text, self.source)

    def test_raise_exact_fraction_between_slider_integers(self):
        price = F(10, 38)
        self.assertEqual(price, F(5, 19))
        values = [F(26, 100) * 38 - 10, price * 38 - 10, F(27, 100) * 38 - 10]
        self.assertEqual(values, [F(-3, 25), F(0), F(13, 50)])
        for text in ('5/19 (about 26.3158%)', '-0.12 BB', '+0.26 BB',
                     "'raise-low': [['raise-equity', 26]]",
                     "'raise-high': [['raise-equity', 27]]"):
            self.assertIn(text, self.source)
        self.assertIn('cannot select that exact fraction', self.source)

    def test_bluff_half_percent_step_attains_exact_threshold(self):
        def ev(q):
            return q * 10 - (1 - q) * 6
        self.assertEqual([ev(F(37, 100)), ev(F(3, 8)), ev(F(38, 100))],
                         [F(-2, 25), F(0), F(2, 25)])
        self.assertIn('step="0.5" disabled', self.source)
        self.assertIn("'bluff-zero': [['bluff-fold', 37.5]]", self.source)
        self.assertIn('37.5%', self.source)
        self.assertIn('0 BB', self.source)

    def test_keyboard_live_results_and_print_static_proof(self):
        self.assertIn('el(preset[0][0]).focus()', self.source)
        self.assertIn('render();\n      el(preset[0][0]).focus();', self.source)
        self.assertIn('button.disabled = false', self.source)
        self.assertIn('button:focus-visible', self.source)
        self.assertIn('.drill-actions{display:none!important}', self.source)
        self.assertIn('class="drill-grid"', self.source)
        for ident in ('river-result', 'raise-result', 'bluff-result'):
            self.assertIn('id="' + ident + '" role="status"', self.source)

    def test_mutations_of_accuracy_and_no_script_fallback_are_detected(self):
        for before, after in (
            ('id="boundary-drill"', 'id="wrong-id"'),
            ('step="0.5" disabled', 'step="1" disabled'),
            ('data-drill="bluff-zero"', 'data-drill="missing"'),
            ('type="button" data-drill="river"', 'type="submit" data-drill="river"'),
            ('aria-controls="bluff-fold bluff-result" disabled', 'aria-controls="bluff-fold bluff-result"'),
            ("button.addEventListener('click'", "button.addEventListener('missing'"),
            ('<noscript>', '<!-- no fallback -->'),
        ):
            with self.subTest(change=before):
                self.assertIn(before, self.source)
                self.assertTrue(errors(self.source.replace(before, after, 1)))

    def test_existing_workshop_article_and_navigation_stay_unchanged(self):
        a = (ROOT / '_source/poker/pot-odds-workshop.html').read_text(encoding='utf-8')
        b = (ROOT / 'poker/pot-odds-workshop/index.html').read_text(encoding='utf-8')
        expr = re.compile(r'<nav class="article-navigation" aria-label="Continue studying">.*?</nav>')
        self.assertEqual(expr.search(a).group(), expr.search(b).group())
        self.assertEqual(a.count('href="' + ROUTE + '"'), 1)
        self.assertIn('<meta property="article:published_time" content="2026-10-06">', b)
        self.assertIn('<meta property="article:modified_time" content="2026-10-06">', b)

    def test_no_new_indexed_route_or_network_footprint(self):
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('https://nolankido.com' + ROUTE, sitemap)
        finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        self.assertNotIn(ROUTE, finder)
        release = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertEqual(release.count("'downloads/poker-pot-odds-sensitivity-lab.html'"), 1)

    def test_previous_safety_contract_and_browser_checks_were_updated(self):
        old = (ROOT / '_tests/test_turn90_offline_sensitivity_lab.py').read_text(encoding='utf-8')
        browser = (ROOT / '_tests/pot_odds_sensitivity_browser.py').read_text(encoding='utf-8')
        self.assertIn('"0.5" if a.get("id") == "bluff-fold" else "1"', old)
        self.assertIn('value="40" step="0.5" disabled', old)
        self.assertIn('"37.5"', browser)
        self.assertIn('data-drill="raise-low"', browser)
        self.assertIn('data-drill="bluff-zero"', browser)
        self.assertIn('test_turn91_threshold_boundary_drill.py',
                      (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8'))
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yaml', '.yml')
            for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
