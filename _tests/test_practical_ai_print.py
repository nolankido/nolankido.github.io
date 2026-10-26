"""Two complete practical-AI printouts with an exact frozen predecessor."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path
from unittest.mock import patch
import re
import unittest
import practical_ai_print_history as history

ROOT = Path(__file__).resolve().parents[1]

class PracticalAIPrintTests(unittest.TestCase):
    def test_all_four_files_restore_exact_published_parent(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name, item in history.change()['paths'].items():
            with self.subTest(name=name):
                now = (ROOT / name).read_bytes()
                self.assertEqual(sha256(now).hexdigest(), item['new_sha256'])
                previous = history.before(name, now)
                self.assertEqual(sha256(previous).hexdigest(), item['old_sha256'])
                self.assertEqual(history.before(Path(name), now.decode()).encode(), previous)
                self.assertEqual(history.before(name, previous), previous)

    def test_unknown_changes_and_corrupt_records_are_not_hidden(self):
        for name in history.PATHS:
            now = (ROOT / name).read_bytes()
            for altered in (now + b'!', b'!' + now, now[1:]):
                self.assertEqual(history.before(name, altered), altered)
            for field, value in [('old_sha256', '0'*64), ('new','nonexistent snippet')]:
                tampered = deepcopy(history.change())
                tampered['paths'][name][field] = value
                with self.subTest(name=name,field=field), patch.object(history, 'change', return_value=tampered):
                    with self.assertRaises(ValueError):
                        history.before(name, now)
        self.assertEqual(history.before('index.html', b'unrelated'), b'unrelated')

    def test_scoped_styles_and_content_addressed_generated_links(self):
        routes = [
          ('assets/summary-review.css','technology/check-ai-summary/index.html','.page-ai-summary-review','summary-sheet'),
          ('assets/ai-task-choice.css','technology/should-i-use-ai/index.html','.page-ai-task-choice','choice-sheet'),
        ]
        for css_name, page_name, scope, worksheet in routes:
            with self.subTest(css_name=css_name):
                css = (ROOT / css_name).read_text()
                page = (ROOT / page_name).read_text()
                self.assertIn('@media print', css)
                self.assertIn(scope, css)
                self.assertIn('::details-content', css)
                self.assertIn('content-visibility:visible!important;', css)
                self.assertIn('break-inside:auto', css)
                self.assertIn('white-space:pre-wrap', css)
                self.assertIn('a[download] { display:none!important; }', css)
                self.assertEqual(page.count('/' + css_name + '?v='),1)
                self.assertIn('/' + css_name + '?v=' + sha256(css.encode()).hexdigest()[:12],page)
                self.assertIn('<details class="' + worksheet + '">',page)

    def test_exact_downloads_and_original_disclosures_stay_closed(self):
        cases=[
          ('technology/check-ai-summary/index.html','downloads/ai-summary-review.txt','summary-sheet'),
          ('technology/should-i-use-ai/index.html','downloads/should-i-use-ai.txt','choice-sheet'),
        ]
        for name, download, css_class in cases:
            with self.subTest(name=name):
                page=(ROOT/name).read_text()
                text=re.search(r'<details class="' + css_class + r'"><summary>[^<]+</summary><pre>(.*?)</pre></details>',page,re.S)
                self.assertIsNotNone(text)
                self.assertEqual(unescape(text.group(1)),(ROOT/download).read_text())
                self.assertIn('href="/' + download + '" download',page)
                self.assertNotIn('<details class="' + css_class + '" open',page)
        summary=(ROOT/'technology/check-ai-summary/index.html').read_text()
        self.assertEqual(len(re.findall(r'<details class="summary-finding" id="finding-',summary)),6)
        self.assertIn('An optional prompt for a claim comparison',summary)
        self.assertNotIn('<textarea',summary)

if __name__=='__main__':
    unittest.main()
