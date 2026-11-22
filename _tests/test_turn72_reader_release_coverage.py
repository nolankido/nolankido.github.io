"""Turn 72: fail-closed evidence and download coverage for three reader journeys.

All checks are local. HTTP verification is supplied only by the separate
priority release checker; these assertions never claim a production pass.
"""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import check_live
import diagnose_live_crawl
import tenbb_companion

WORKSHEET = '/downloads/ten-bb-tournament-checklist.md'
CODE = '/downloads/ten-bb-playbook-icm-verify.py'
CASE_WORKSHEET = '/downloads/website-check-offline-runbook.md'
BOOK_WORKSHEET = '/downloads/one-workflow-ai-pilot-worksheet.md'


class Turn72CriticalReaderCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playbook = (ROOT / 'poker/10bb/index.html').read_text(encoding='utf-8')
        cls.targets = check_live.targets(ROOT)

    def test_original_poker_study_guide_and_worksheet_stay_together(self):
        self.assertEqual(tenbb_companion.WORKSHEET, WORKSHEET.lstrip('/'))
        self.assertIn('href="' + WORKSHEET + '"', self.playbook)
        for route in (tenbb_companion.ROUTE, WORKSHEET, CODE):
            self.assertIn(route, self.targets)
            self.assertEqual(self.targets[route][0], 200)
        self.assertEqual(self.targets[WORKSHEET][1],
                         (ROOT / WORKSHEET.lstrip('/')).read_bytes())
        self.assertEqual(self.targets[CODE][1],
                         (ROOT / CODE.lstrip('/')).read_bytes())

    def test_missing_playbook_link_is_a_release_blocker(self):
        corrupted = self.playbook.replace(
            'href="' + WORKSHEET + '"', 'href="/downloads/missing.md"')
        self.assertNotEqual(self.playbook, corrupted)
        with self.assertRaisesRegex(ValueError, 'six-check worksheet'):
            tenbb_companion.inspect(corrupted)

    def test_missing_file_is_a_release_blocker(self):
        with tempfile.TemporaryDirectory() as scratch:
            temp = Path(scratch)
            for route in ('poker/10bb/index.html', tenbb_companion.CODE):
                output = temp / route
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes((ROOT / route).read_bytes())
            with self.assertRaisesRegex(ValueError, 'written worksheet is missing'):
                tenbb_companion.record(temp)

    def test_changed_entry_and_all_free_assets_are_priority_live_targets(self):
        required = {
            '/', '/start-here/', '/technology/', '/poker/', '/poker/10bb/',
            '/technology/checking-ai-website-changes/',
            '/technology/ai-website-visibility/',
            '/technology/ai-workflow-pilot/',
            '/books/', '/books/one-workflow-at-a-time/',
            CASE_WORKSHEET, BOOK_WORKSHEET, WORKSHEET, CODE,
        }
        self.assertTrue(required.issubset(set(diagnose_live_crawl.PRIORITY)))
        self.assertEqual(len(diagnose_live_crawl.PRIORITY),
                         len(set(diagnose_live_crawl.PRIORITY)))
        for route in required:
            with self.subTest(route=route):
                self.assertIn(route, self.targets)
                self.assertEqual(self.targets[route][0], 200)

    def test_three_journeys_exist_in_actual_public_page_source(self):
        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        start = (ROOT / 'start-here/index.html').read_text(encoding='utf-8')
        books = (ROOT / 'books/index.html').read_text(encoding='utf-8')
        poker = (ROOT / 'poker/index.html').read_text(encoding='utf-8')
        book = (ROOT / 'books/one-workflow-at-a-time/index.html').read_text(
            encoding='utf-8')
        case = (ROOT / 'technology/checking-ai-website-changes/index.html').read_text(
            encoding='utf-8')
        self.assertIn('href="/technology/checking-ai-website-changes/"', home)
        self.assertIn('class="small-copy start-release-proof"', start)
        self.assertIn('href="' + CASE_WORKSHEET + '" download', case)
        self.assertIn('href="/books/one-workflow-at-a-time/"', books)
        self.assertIn('href="' + BOOK_WORKSHEET + '" download', book)
        self.assertIn('href="/poker/10bb/#practice-title"', poker)
        self.assertIn('href="' + WORKSHEET + '" download', self.playbook)

    def test_new_browser_checks_are_genuine_keyboard_and_download_steps(self):
        browser = (ROOT / '_tests/visibility_three_reader_journeys_browser.py').read_text(
            encoding='utf-8')
        for marker in (
            "WIDTHS = (320, 390, 1440)",
            'for scripts_enabled in (False, True):',
            "page.keyboard.press('Enter')",
            'page.expect_download()',
            'download.failure()',
            'ThreadingHTTPServer',
            "('127.0.0.1', 0)",
            "else route.abort()",
            "response.status == 200",
            'body == expected',
        ):
            self.assertIn(marker, browser)
        self.assertNotIn('http' + 's://fonts.googleapis.com', browser)
        self.assertNotIn('cloud.umami.is', browser)

    def test_manual_only_release_and_existing_inconclusive_policy(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn72_reader_release_coverage.py', runner)
        self.assertIn("glob('*_browser.py')", runner)
        self.assertEqual(diagnose_live_crawl.classify_failure('URLError'), 'inconclusive')
        self.assertEqual(
            diagnose_live_crawl.classify_failure('Response bytes do not match the checked-out release'),
            'observed_mismatch')
        workflows = ROOT / '.github/workflows'
        self.assertFalse(workflows.exists() and any(
            p.suffix.lower() in ('.yml', '.yaml') for p in workflows.iterdir()))


if __name__ == '__main__':
    unittest.main()
