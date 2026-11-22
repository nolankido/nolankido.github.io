"""Turn 71: source-backed AI release route and five-page offline mobile contract.

No network, private dashboards, new tracking, paid services or GitHub Actions.
Chromium checks are exercised separately by visibility_core_journeys_browser.py.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEST = '/technology/checking-ai-website-changes/'
DOWNLOAD = '/downloads/website-check-offline-runbook.md'
CLASS = 'start-release-proof'


def paragraph(html):
    found = re.findall(
        r'<p class="small-copy ' + CLASS + r'">.*?</p>', html, flags=re.S
    )
    if len(found) != 1:
        raise ValueError('exactly one first-party source-checked release route required')
    return found[0]


def contract_errors(html):
    try:
        part = paragraph(html)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for expected in (f'href="{DEST}"',
                     'real source-checked release',
                     'before-and-after source',
                     'independent parser check',
                     'free release checklist',
                     'not a measured AI speedup or search-ranking gain'):
        if part.count(expected) != 1:
            errors.append('missing or repeated source/limit: ' + expected)
    if any(x in part for x in ('onclick=', '<script', 'utm_', chr(0x2014))):
        errors.append('unapproved behavior, marketing instrumentation or punctuation')
    return errors


class Turn71StartHereReleasePath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/start-here.html').read_text(encoding='utf-8')
        cls.public = (ROOT / 'start-here/index.html').read_text(encoding='utf-8')
        cls.home = (ROOT / 'index.html').read_text(encoding='utf-8')
        cls.case = (ROOT / 'technology/checking-ai-website-changes/index.html').read_text(
            encoding='utf-8')

    def test_one_source_identical_public_route_with_honest_limits(self):
        self.assertEqual(contract_errors(self.source), [])
        self.assertEqual(contract_errors(self.public), [])
        self.assertEqual(paragraph(self.source), paragraph(self.public))

    def test_existing_project_section_structure_preserved(self):
        for html in (self.source, self.public):
            self.assertEqual(html.count('class="small-copy start-release-proof"'), 1)
            self.assertLess(html.index('id="start-projects-title"'),
                            html.index('class="small-copy start-release-proof"'))
            self.assertIn('href="/technology/local-ai-review-replies/"', html)
            self.assertIn('href="/technology/dinner-on-time/"', html)
            self.assertNotIn('id="new-release-page"', html)

    def test_documented_case_and_download_really_exist(self):
        self.assertIn(f'href="{DEST}"', self.home)
        self.assertIn('id="case-evidence"', self.case)
        self.assertIn(f'href="{DOWNLOAD}"', self.case)
        self.assertTrue((ROOT / DOWNLOAD.lstrip('/')).is_file())

    def test_original_canonical_and_dates_not_reinvented(self):
        self.assertIn('<link rel="canonical" href="https://nolankido.com/start-here/">',
                      self.public)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        record = next(p for p in pages if p['path'] == '/start-here/')
        self.assertEqual(record['updated'], '2026-11-21')
        self.assertEqual(self.public.count('<h1'), 1)

    def test_offline_browser_covers_five_routes_and_true_styles(self):
        checker = (ROOT / '_tests/visibility_core_journeys_browser.py').read_text(
            encoding='utf-8')
        for route in ("'/'", "'/start-here/'", "'/technology/'",
                      "'/books/'", "'/poker/10bb/'"):
            self.assertIn(route, checker)
        for fragment in ("WIDTHS = (320, 390, 768, 1440)",
                         "'/styles.css'", "ROOT / parts.path.lstrip('/')",
                         "document.documentElement.scrollWidth",
                         "java_script_enabled=False", "context.route('**/*'"):
            self.assertIn(fragment, checker)

    def test_adversarial_change_cannot_pass_source_contract(self):
        original = paragraph(self.source)
        variants = (
            original.replace(DEST, '/technology/nonexistent/', 1),
            original.replace('not a measured AI speedup or search-ranking gain',
                             'proves AI ranked the site', 1),
            original.replace('independent parser check', 'a model opinion', 1),
            original + original,
        )
        for variant in variants:
            with self.subTest(variant=variant[:80]):
                changed = self.source.replace(original, variant, 1)
                self.assertNotEqual(contract_errors(changed), [])

    def test_manual_release_registration_and_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn71_start_here_release_navigation.py', runner)
        self.assertIn("glob('*_browser.py')", runner)
        workflows = ROOT / '.github/workflows'
        self.assertFalse(workflows.exists() and any(
            p.suffix.lower() in ('.yml', '.yaml') for p in workflows.iterdir()
        ))


if __name__ == '__main__':
    unittest.main()
