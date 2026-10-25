"""Exact, bounded preservation for the mobile Task Brief disclosure repair."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import unittest

import task_brief_disclosure_history as history
import task_brief_print_history as printing

ROOT = Path(__file__).resolve().parents[1]


class TaskBriefDisclosureTests(unittest.TestCase):
    def test_two_exact_production_deltas_and_predecessors(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name, record in history.change()['paths'].items():
            raw = printing.before(name, (ROOT / name).read_bytes())
            self.assertEqual(sha256(raw).hexdigest(), record['new_sha256'])
            older = history.before(name, raw)
            self.assertEqual(sha256(older).hexdigest(), record['old_sha256'])
            self.assertEqual(history.before(Path(name), raw.decode()).encode(), older)
            self.assertEqual(history.before(name, older), older)

    def test_unknown_changes_are_not_concealed(self):
        for name in history.PATHS:
            raw = (ROOT / name).read_bytes()
            for altered in (raw + b'x', b'x' + raw, raw[1:]):
                self.assertEqual(history.before(name, altered), altered)
        self.assertEqual(history.before('index.html', b'unrelated'), b'unrelated')

    def test_source_and_page_remain_native_and_deterministic(self):
        css = (ROOT / 'assets/task-brief.css').read_text()
        page = (ROOT / 'technology/task-brief/index.html').read_text()
        self.assertEqual(css.count('min-height: 44px; box-sizing: border-box; padding-block: 8px;'), 1)
        self.assertIn('.brief-example summary, .brief-template summary', css)
        self.assertIn('<summary>Walk through the meeting example</summary>', page)
        self.assertIn('<summary>Turn meeting notes into a usable plan</summary>', page)
        self.assertIn('<div id="brief-editor" hidden', page)
        self.assertIn('/assets/task-brief.css?v=' + sha256(css.encode()).hexdigest()[:12], page)
        self.assertNotIn('aria-expanded=', css)

    def test_corrupt_predecessor_is_rejected(self):
        record = deepcopy(history.change())
        record['paths']['assets/task-brief.css']['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=record):
            with self.assertRaises(ValueError):
                history.before('assets/task-brief.css', (ROOT / 'assets/task-brief.css').read_bytes())


if __name__ == '__main__':
    unittest.main()
