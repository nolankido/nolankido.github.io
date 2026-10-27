"""Native walkthrough, exact preserved controls, and honest revision scope."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import re
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import task_brief_walkthrough_history as history
import later_release_history as later_history
import task_brief_disclosure_history as disclosure
import task_brief_print_history as printing

SOURCE = '_source/technology/task-brief.html'
PAGE = 'technology/task-brief/index.html'


class TaskBriefWalkthroughTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / SOURCE).read_text()
        cls.html = (ROOT / PAGE).read_text()
        cls.walk = re.search(r'<details class="brief-template" id="brief-walkthrough">(.*?)</details>', cls.source, re.S)[1]

    def test_optional_native_walkthrough_precedes_editor_without_new_input(self):
        self.assertLess(self.source.index('id="brief-walkthrough"'), self.source.index('id="brief-workspace"'))
        self.assertIn('<summary>Walk through the meeting example</summary>', self.walk)
        self.assertEqual(self.walk.count('<li>'), 4)
        self.assertNotRegex(self.walk, r'<(?:form|input|textarea|button|script|iframe|video)\b')
        self.assertNotIn(' open', self.source.split('id="brief-walkthrough"')[1].split('>')[0])

    def test_existing_example_text_and_controls_remain_byte_identical(self):
        source = printing.before(SOURCE, self.source)
        original = history.before(SOURCE, source)
        current = re.sub(r'<details class="brief-template" id="brief-walkthrough">.*?</details>', '', source, count=1, flags=re.S)
        current = current.replace(' id="brief-example-meeting"', '', 1)
        self.assertEqual(current, original)
        self.assertEqual(self.source.count('data-brief-example='), 6)
        self.assertEqual(self.source.count('data-use-example='), 6)

    def test_walkthrough_uses_exact_existing_control_labels(self):
        for label in ('Use this meeting example', 'Assemble my brief',
                      'Save as text', 'Copy brief', 'Select text manually'):
            self.assertIn('<strong>' + label + '</strong>', self.walk)
            self.assertRegex(self.source, r'<button\b[^>]*>' + re.escape(label) + '</button>')
        self.assertIn('Complete copyable plain text', self.walk)
        self.assertIn('<label for="brief-text">Complete copyable plain text</label>', self.source)

    def test_all_walkthrough_links_reach_native_local_targets(self):
        targets = re.findall(r'href="#([^"]+)"', self.walk)
        self.assertEqual(targets, ['brief-example-meeting', 'brief-blank', 'brief-workspace'])
        for target in targets:
            self.assertEqual(self.html.count('id="' + target + '"'), 1)
        self.assertNotIn('href="https:', self.walk)
        self.assertIn('<strong>Without JavaScript:</strong>', self.walk)

    def test_boundaries_do_not_imply_an_ai_answer_or_observed_outcome(self):
        for wording in ('illustrative walkthrough', 'not a real meeting or a measured result',
                        'does not run AI', 'not an answer to the task',
                        'confirm the file was saved', 'Leaving the page clears its entries',
                        'Nothing in this walkthrough sends a brief to an AI service'):
            self.assertIn(wording, self.walk)
        self.assertNotIn('data-umami-event', self.walk)

    def test_only_task_brief_revision_changes_in_manifest_and_sitemap(self):
        current = json.loads((ROOT / '_source/pages.json').read_text())
        old = json.loads(history.before('_source/pages.json', (ROOT / '_source/pages.json').read_text()))
        changed = [(a, b) for a, b in zip(old, current) if a != b]
        self.assertEqual(len(old), len(current))
        self.assertEqual(len(changed), 1)
        a, b = changed[0]
        self.assertEqual(b['id'], 'task-brief')
        self.assertEqual(b, {**a, 'updated': '2026-10-21'})
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        xml = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        rows = {n.findtext('s:loc', namespaces=ns): n.findtext('s:lastmod', namespaces=ns) for n in xml}
        self.assertEqual(rows['https://nolankido.com/technology/task-brief/'], '2026-10-21')
        self.assertEqual(history.pages(current), old)
        mutated = deepcopy(b); mutated['description'] += ' unreviewed'
        self.assertEqual(history.pages([mutated]), [mutated])
        self.assertIsNot(history.pages([b])[0], a)

    def test_complete_production_inventory_restores_the_verified_parent(self):
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        paths = later_history.files([p for p in paths if p])
        rows = sorted((p, sha256(history.before(p, later_history.before(p, (ROOT / p).read_bytes()))).hexdigest())
                      for p in paths if not p.startswith(('_tests/', '_reports/')))
        self.assertEqual(len(rows), history.change()['production_count'])
        self.assertEqual(sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(), history.change()['production_fingerprint'])
        self.assertEqual(set(history.change()['paths']), {SOURCE, PAGE, '_source/pages.json', 'sitemap.xml'})

    def test_exact_reversal_preserves_type_and_does_not_hide_unknown_changes(self):
        for name, item in history.change()['paths'].items():
            raw = disclosure.before(name, (ROOT / name).read_bytes())
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
            old = history.before(name, raw)
            self.assertEqual(sha256(old).hexdigest(), item['old_sha256'])
            self.assertEqual(history.before(Path(name), raw.decode()).encode(), old)
            self.assertEqual(history.before(name, old), old)
            for mutation in (raw + b'!', b'!' + raw, raw[1:]):
                self.assertEqual(history.before(name, mutation), mutation)

    def test_corrupt_history_refuses_restoration(self):
        name = SOURCE
        record = deepcopy(history.change()); record['paths'][name]['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=record), self.assertRaises(ValueError):
            history.before(name, (ROOT / name).read_bytes())
        for edits in ([[True, 1, '']], [[-1, 0, '']], [[2, 1, '']], [[0, 3, ''], [2, 4, '']]):
            record = deepcopy(history.change()); record['paths'][name]['edits'] = edits
            with self.subTest(edits=edits), patch.object(history, 'change', return_value=record), self.assertRaises(ValueError):
                history.before(name, (ROOT / name).read_bytes())


if __name__ == '__main__':
    unittest.main()
