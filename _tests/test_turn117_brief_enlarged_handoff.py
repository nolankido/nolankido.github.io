"""The answer-checking step must be reachable before a tall export textarea."""

from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attributes):
        if tag == 'a':
            self.links.append(dict(attributes))


class EnlargedTextHandoffTests(unittest.TestCase):
    def test_next_check_is_a_single_native_link_next_to_export(self):
        for route in ('_source/technology/task-brief.html',
                      'technology/task-brief/index.html'):
            with self.subTest(route=route):
                html = (ROOT / route).read_text(encoding='utf-8')
                ids = ('brief-preview', 'brief-export-intro', 'brief-copy',
                       'brief-download', 'brief-print', 'brief-select',
                       'brief-copy-status', 'brief-result-next',
                       'brief-text-label', 'brief-text')
                positions = [html.index('id="' + name + '"') for name in ids]
                self.assertEqual(positions, sorted(positions))
                for name in ids:
                    self.assertEqual(html.count('id="' + name + '"'), 1, name)
                self.assertRegex(html,
                                 r'<p id="brief-copy-status"[^>]*></p>\s*'
                                 r'<p class="brief-help" id="brief-result-next">')
                handoff = re.search(r'<p class="brief-help" id="brief-result-next">(.*?)</p>',
                                    html, re.S)
                self.assertIsNotNone(handoff)
                parser = AnchorParser()
                parser.feed(handoff.group(1))
                self.assertEqual(parser.links, [{'href': '#brief-next-check'}])
                self.assertIn('After confirming your saved or copied brief', handoff.group(1))
                self.assertIn('The next step is on this page', handoff.group(1))
                self.assertEqual(html.count('id="brief-next-check"'), 1)
                # The link remains within the assembled result. Opening the
                # guide is never a prerequisite for reviewing or exporting.
                self.assertLess(html.index('id="brief-result"'), handoff.start())
                self.assertLess(handoff.end(), html.index('</section></div></div></section>',
                                                            handoff.end()))

    def test_reader_zoom_and_focus_have_an_unclipped_target(self):
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        reader = (ROOT / '_tests/task_brief_reader_browser.py').read_text(encoding='utf-8')
        self.assertIn('#brief-result-next { border-left: 3px solid var(--green);', css)
        self.assertIn('overflow-wrap: anywhere;', css)
        self.assertIn('html { font-size: 200% !important; }', reader)
        self.assertIn("page.locator('#brief-result-next a[href=\"#brief-next-check\"]')", reader)
        self.assertIn("assert page.evaluate('location.hash') == '#brief-next-check'", reader)
        self.assertIn('targetTop >= headerBottom - 1', reader)
        shared = (ROOT / 'assets/site-core.css').read_text(encoding='utf-8')
        self.assertIn(':where(a, button, input, select, textarea, summary):focus-visible',
                      shared)

    def test_handoff_remains_on_page_without_automatic_export(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        self.assertNotIn("get('result-next')", script)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage'):
            self.assertNotIn(forbidden, script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        entry = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertEqual(entry['updated'], '2026-11-11')
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertRegex(sitemap,
                         r'<loc>https://nolankido\.com/technology/task-brief/</loc>\s*'
                         r'<lastmod>2026-11-11</lastmod>')


if __name__ == '__main__':
    unittest.main()
