"""Manual-copy guidance is concrete, consistent, and readable on phones."""

from hashlib import sha256
from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CUE = 'Selected, not copied. Press Ctrl+C or Command+C; on touch, choose Copy.'


class CopyShortcutGuidanceTests(unittest.TestCase):
    def test_visible_and_screen_reader_cue_explains_copy_without_claiming_success(self):
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        public = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        for html in (source, public):
            cues = re.findall(r'<p id="brief-selection-cue"[^>]*>(.*?)</p>', html, re.S)
            self.assertEqual(cues, [CUE])
            self.assertIn('id="brief-selection-cue" class="brief-selection-cue" hidden', html)
            self.assertIn('aria-describedby="brief-text-help"', html)
            self.assertIn('On Windows and Linux, press Ctrl+C; on Mac, press Command+C.', html)
            self.assertIn('On touchscreens, choose Copy from the text-selection menu.', html)
            self.assertIn('Paste into your own notes and verify the complete brief arrived.', html)
            self.assertIn('Selecting text does not copy it.', html)
            self.assertIn('The Copy brief button requests a clipboard write only when activated', html)
            self.assertEqual(html.count(CUE), 1)

        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        self.assertIn('const SELECTED_CUE = ' + repr(CUE) + ';', script)
        self.assertIn("output.setAttribute('aria-describedby', 'brief-selection-cue brief-text-help')", script)
        self.assertIn("output.setAttribute('aria-describedby', 'brief-text-help')", script)
        self.assertIn('Copy command detected, but this page cannot confirm clipboard contents.', script)

    def test_shortcut_guidance_wraps_and_changes_no_data_or_publication_policy(self):
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertRegex(css, r'\.brief-selection-cue\s*\{[^}]*overflow-wrap:\s*anywhere;')
        for asset, content in [('js', script), ('css', css)]:
            self.assertIn(f'task-brief.{asset}?v={sha256(content.encode()).hexdigest()[:12]}', html)
        for forbidden in ('preventDefault(', 'navigator.clipboard.readText(', 'execCommand(',
                          'fetch(', 'sendBeacon', 'localStorage', 'sessionStorage'):
            self.assertNotIn(forbidden, script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        entry = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertGreaterEqual(entry['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
