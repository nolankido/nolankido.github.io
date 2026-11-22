"""Turn 78: first-visit readers reach a real free course or 10 BB study guide.

No added SEO page, paid service, remote request, form, or invented result.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
CLASS = 'start-poker-learning-route'
BEGINNER = '/poker/free-poker-learning-path/'
SHORT = '/poker/10bb/'


def one_paragraph(html: str) -> str:
    parts = re.findall(
        r'<p class="small-copy ' + CLASS + r'">.*?</p>', html, flags=re.S)
    if len(parts) != 1:
        raise ValueError('exactly one poker learning handoff required')
    return parts[0]


def contract_errors(html: str) -> list[str]:
    try:
        paragraph = one_paragraph(html)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for required in (
        'href="' + BEGINNER + '"',
        'href="' + SHORT + '"',
        'six-lesson Poker Foundations course',
        'written 10 BB Playbook',
        'free worksheet',
        'fictional ICM example',
        'not a solver verdict for a real hand',
    ):
        if paragraph.count(required) != 1:
            errors.append('missing or repeated real study destination or limit: ' + required)
    if any(fragment in paragraph for fragment in (
        'utm_', '<script', 'onclick=', 'guaranteed winnings',
        '100% win', chr(0x2014),
    )):
        errors.append('unreviewed tracking, behavior, exaggeration or punctuation')
    task = re.search(r'<ul class="task-route-list">.*?</ul>', html, flags=re.S)
    if not task or not (
        html.index('id="start-tasks-title"')
        < task.start() < task.end()
        < html.index(paragraph)
        < html.index('class="small-copy start-pilot-route"')
    ):
        errors.append('original four tasks and AI pilot must keep their order')
    return errors


class Turn78PokerReaderHandoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/start-here.html').read_text(encoding='utf-8')
        cls.public = (ROOT / 'start-here/index.html').read_text(encoding='utf-8')
        cls.course = (ROOT / 'poker/free-poker-learning-path/index.html').read_text(
            encoding='utf-8')
        cls.short = (ROOT / 'poker/10bb/index.html').read_text(encoding='utf-8')

    def test_same_native_reader_handoff_in_source_and_published_html(self):
        for html in (self.source, self.public):
            self.assertEqual(contract_errors(html), [])
            self.assertEqual(html.count('href="' + BEGINNER + '"'), 1)
            self.assertEqual(html.count('href="' + SHORT + '"'), 1)
        self.assertEqual(one_paragraph(self.source), one_paragraph(self.public))

    def test_existing_four_tasks_and_original_pilot_remain_intact(self):
        for html in (self.source, self.public):
            task = re.search(r'<ul class="task-route-list">(.*?)</ul>', html, re.S)
            self.assertIsNotNone(task)
            self.assertEqual(task.group(1).count('<li>'), 4)
            for path in (
                '/technology/task-brief/',
                '/technology/check-ai-answers/',
                '/living-well/weekly-reset/',
                '/poker/first-live-tournament/',
            ):
                self.assertIn('href="' + path + '"', task.group(1))
            self.assertIn('class="small-copy start-release-proof"', html)
            self.assertIn('class="small-copy start-pilot-route"', html)

    def test_free_course_and_poker_playbook_are_real_published_pages(self):
        for route in (BEGINNER, SHORT):
            self.assertTrue((ROOT / route.lstrip('/') / 'index.html').is_file())
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com' + BEGINNER + '">',
            self.course)
        self.assertIn('six connected lessons', self.course)
        self.assertNotIn('<meta name="robots" content="noindex', self.course)
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com' + SHORT + '">',
            self.short)
        self.assertIn('No video is required.', self.short)
        for question in range(1, 7):
            self.assertIn('id="q' + str(question) + '"', self.short)
        self.assertIn('href="/downloads/ten-bb-tournament-checklist.md"', self.short)
        self.assertTrue((ROOT / 'downloads/ten-bb-tournament-checklist.md').is_file())
        self.assertIn('href="/downloads/ten-bb-playbook-icm-verify.py"', self.short)

    def test_original_start_here_metadata_and_canonical_unmodified(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        start = next(p for p in pages if p['path'] == '/start-here/')
        self.assertEqual(start['updated'], '2026-11-21')
        self.assertEqual(self.public.count('<h1'), 1)
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com/start-here/">',
            self.public)

    def test_builder_still_generates_exact_checked_in_public_page(self):
        import build
        self.assertEqual(
            build.build_outputs()[Path('start-here/index.html')], self.public)

    def test_browser_contract_uses_real_keyboard_paths_and_both_script_modes(self):
        browser = (ROOT / '_tests/entrypoints_browser.py').read_text(encoding='utf-8')
        self.assertIn("for javascript in [True, False]:", browser)
        for route in (BEGINNER, SHORT):
            self.assertIn("'" + route + "'", browser)
        self.assertIn("'.start-poker-learning-route a[href=\"' + target + '\"]'", browser)
        self.assertIn("page.keyboard.press('Enter')", browser)
        self.assertIn("'keyboard_routes': 30", browser)

    def test_negative_controls_detect_unsupported_or_missing_claims(self):
        original = one_paragraph(self.source)
        variants = (
            original.replace(BEGINNER, '/poker/unpublished-course/', 1),
            original.replace(SHORT, '/poker/missing-guide/', 1),
            original.replace('fictional ICM example', 'guaranteed winnings', 1),
            original.replace('not a solver verdict for a real hand',
                             'a solver verdict for every real hand', 1),
            original + original,
        )
        for fragment in variants:
            with self.subTest(text=fragment[:72]):
                tampered = self.source.replace(original, fragment, 1)
                self.assertNotEqual(contract_errors(tampered), [])

    def test_existing_manual_check_runner_and_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn78_poker_reader_handoff.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            file.suffix.lower() in ('.yml', '.yaml')
            for file in actions.iterdir() if file.is_file()
        ))


if __name__ == '__main__':
    unittest.main()
