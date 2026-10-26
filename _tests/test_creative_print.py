"""Creative Work prints its complete blank brief without changing prior releases."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path
from unittest.mock import patch
import json
import re
import unittest

import creative_print_history as history

ROOT = Path(__file__).resolve().parents[1]

class CreativePrintTests(unittest.TestCase):
    def test_four_exact_paths_restore_published_parent(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name, record in history.change()['paths'].items():
            with self.subTest(path=name):
                new = (ROOT / name).read_bytes()
                self.assertEqual(sha256(new).hexdigest(), record['new_sha256'])
                old = history.before(name, new)
                self.assertEqual(sha256(old).hexdigest(), record['old_sha256'])
                self.assertEqual(history.before(Path(name), new.decode()).encode(), old)
                self.assertEqual(history.before(name, old), old)

    def test_unknown_edits_are_never_hidden(self):
        for name in history.PATHS:
            new = (ROOT / name).read_bytes()
            for changed in (b'!' + new, new + b'!', new[1:]):
                self.assertEqual(history.before(name, changed), changed)
        self.assertEqual(history.before('downloads/creative-brief.txt', b'private'), b'private')

    def test_malformed_predecessor_fails_closed(self):
        name = 'assets/first-steps.css'
        new = (ROOT / name).read_bytes()
        for field, value in [('old_sha256','0'*64), ('edits',[{'start':-1,'new':'x','old':''}]),
                             ('edits',[{'start':1,'new':'unexpected','old':''}]),
                             ('edits',[{'start':1,'new':None,'old':''}])]:
            corrupted = deepcopy(history.change())
            corrupted['paths'][name][field] = value
            with self.subTest(field=field,value=value), patch.object(history,'change',return_value=corrupted):
                with self.assertRaises(ValueError):
                    history.before(name,new)

    def test_page_hint_and_complete_template_share_one_download(self):
        source = (ROOT / '_source/creative/home.html').read_text()
        page = (ROOT / 'creative/index.html').read_text()
        sheet = (ROOT / 'downloads/creative-brief.txt').read_text()
        phrase = 'The entire blank brief prints even while this preview is closed.'
        self.assertEqual(source.count(phrase), 1)
        self.assertEqual(page.count(phrase), 1)
        self.assertEqual(page.count('class="creative-template"'), 1)
        self.assertRegex(page, r'<details class="creative-template"><summary>[^<]+</summary><pre>')
        match = re.search(r'<details class="creative-template">.*?<pre>(.*?)</pre>',page,re.S)
        self.assertIsNotNone(match)
        self.assertEqual(unescape(match.group(1)), sheet)
        self.assertIn('href="/downloads/creative-brief.txt" download',page)
        self.assertNotIn('<form',page)
        self.assertNotIn('<textarea',page)

    def test_scoped_print_rules_and_content_addressed_delivery(self):
        css = (ROOT / 'assets/first-steps.css').read_text()
        print_block = css.split('/* Print the complete blank creative brief',1)[1].split('/* Homepage growth:',1)[0]
        self.assertIn('@media print {',print_block)
        for selector in ['.page-creative .creative-template::details-content',
                         '.page-creative .creative-template > :not(summary)',
                         '.page-creative .creative-template summary::marker',
                         '.page-creative .creative-template pre',
                         '.page-creative .creative-print-help']:
            self.assertIn(selector,print_block)
        self.assertIn('content-visibility: visible !important;', print_block)
        self.assertIn('background: white; color: black;',print_block)
        token = sha256(css.encode()).hexdigest()[:12]
        for route in ('index.html','creative/index.html'):
            page = (ROOT / route).read_text()
            self.assertIn('/assets/first-steps.css?v='+token,page)
            self.assertEqual(page.count('/assets/first-steps.css?v='),1)
        home = (ROOT / 'index.html').read_text()
        self.assertNotIn('creative-print-help',home)
        self.assertNotIn('::details-content',home)
        self.assertEqual(len(re.findall(r'<script[^>]*src=',(ROOT/'creative/index.html').read_text())),1)

if __name__=='__main__':
    unittest.main()
