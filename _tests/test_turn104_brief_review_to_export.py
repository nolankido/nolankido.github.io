"""After reviewing the six-part brief, export actions are next in reading order."""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source/technology/task-brief.html'
PAGE = ROOT / 'technology/task-brief/index.html'


class IdAndGroupParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.entries = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.entries.append((attrs['id'], tag, attrs))


class TaskBriefReviewToExportTests(unittest.TestCase):
    def records(self, path):
        parser = IdAndGroupParser()
        parser.feed(path.read_text(encoding='utf-8'))
        return parser.entries

    def test_export_follows_six_section_preview_before_duplicate_text(self):
        expected = ['brief-preview', 'brief-export-intro', 'brief-copy',
                    'brief-download', 'brief-print', 'brief-select',
                    'brief-copy-status', 'brief-text', 'brief-result-next']
        for path in (SOURCE, PAGE):
            with self.subTest(path=path.name):
                records = self.records(path)
                ids = [entry[0] for entry in records]
                for name in expected:
                    self.assertEqual(ids.count(name), 1, name)
                self.assertEqual([name for name in ids if name in expected], expected)

    def test_export_is_labeled_and_requires_a_deliberate_action(self):
        for path in (SOURCE, PAGE):
            with self.subTest(path=path.name):
                html = path.read_text(encoding='utf-8')
                self.assertIn('id="brief-export-intro"', html)
                self.assertIn('Review all six sections above before exporting.', html)
                self.assertIn('role="group" aria-labelledby="brief-export-intro"', html)
                self.assertIn('id="brief-copy-status" role="status" aria-live="polite"', html)
                self.assertRegex(html, r'<textarea id="brief-text" readonly\b')
                self.assertIn('aria-describedby="brief-text-help"', html)
                self.assertIn('Nothing is saved when you leave this page.', html)
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        for action in ('copy', 'download', 'print', 'select'):
            self.assertIn("get('" + action + "').addEventListener('click'", script)
        self.assertIn("if (result.hidden || !output.value) return;", script)
        for forbidden in ('fetch(', 'localStorage', 'sessionStorage', 'sendBeacon'):
            self.assertNotIn(forbidden, script)

    def test_print_still_outputs_only_reviewed_preview_and_date_is_unchanged(self):
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        self.assertIn('#brief-result > :not(#brief-result-title):not(.brief-print-note):not(#brief-preview)', css)
        self.assertIn('#brief-preview .brief-preview-part', css)
        page = PAGE.read_text(encoding='utf-8')
        self.assertEqual(len(re.findall(r'id="brief-result-title"', page)), 1)
        self.assertIn('2026-11-10', (ROOT / '_source/pages.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
