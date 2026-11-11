"""The visible fallback must explain native Copy even if the cue scrolls away."""

from hashlib import sha256
from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class VisibleFallbackCopyTests(unittest.TestCase):
    def test_panel_title_retains_copy_instruction_at_extreme_reflow(self):
        expected = ('<p id="brief-export-alternatives-title">'
                    '<strong>Selected, not copied.</strong> '
                    'Ctrl+C, Cmd+C, or touch Copy.</p>')
        for route in ('_source/technology/task-brief.html',
                      'technology/task-brief/index.html'):
            with self.subTest(route=route):
                html = (ROOT / route).read_text(encoding='utf-8')
                panel = re.search(
                    r'<div id="brief-export-alternatives".*?</div>', html, re.S)
                self.assertIsNotNone(panel)
                self.assertIn('role="group" aria-labelledby="brief-export-alternatives-title" hidden',
                              panel.group(0))
                self.assertIn(expected, panel.group(0))
                self.assertLess(panel.group(0).index(expected),
                                panel.group(0).index('id="brief-save-alternative"'))
                self.assertLess(panel.group(0).index('id="brief-save-alternative"'),
                                panel.group(0).index('id="brief-print-alternative"'))
                self.assertIn('Check the download or PDF before leaving.', html)
                self.assertIn('A request does not confirm a save.', html)
                self.assertEqual(html.count('id="brief-export-alternatives-title"'), 1)
                self.assertEqual(html.count('id="brief-selection-cue"'), 1)

    def test_selection_does_not_become_a_false_clipboard_success(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        self.assertIn("get('select').addEventListener('click'", script)
        self.assertIn('showExportAlternatives();\n    selectVisibleText(', script)
        self.assertIn('Complete text selected, but not copied.', script)
        self.assertIn('The text is selected, not copied by this fallback.', script)
        self.assertIn("output.focus(); output.select();", script)
        self.assertIn('output.scrollTop = 0;', script)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage'):
            self.assertNotIn(forbidden, script)
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        self.assertIn('.brief-export-alternatives {', css)
        self.assertIn('overflow-wrap: anywhere;', css)
        self.assertIn('min-height: 44px;', css)

    def test_enlarged_text_browser_contract_and_generated_assets(self):
        reader = (ROOT / '_tests/task_brief_reader_browser.py').read_text(encoding='utf-8')
        for marker in ('html { font-size: 200% !important; }',
                       "page.locator('#brief-select').click()",
                       "title = panel.locator('#brief-export-alternatives-title').inner_text()",
                       "el.selectionStart === 0 && el.selectionEnd === el.value.length",
                       "width, 'manual selection overflows'"):
            self.assertIn(marker, reader)
        page = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        css = (ROOT / 'assets/task-brief.css').read_bytes()
        script = (ROOT / 'assets/task-brief.js').read_bytes()
        self.assertIn('task-brief.css?v=' + sha256(css).hexdigest()[:12], page)
        self.assertIn('task-brief.js?v=' + sha256(script).hexdigest()[:12], page)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        entry = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertEqual(entry['updated'], '2026-11-11')


if __name__ == '__main__':
    unittest.main()
