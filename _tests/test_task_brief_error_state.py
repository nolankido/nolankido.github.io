"""A reproduced stale description, exact two-file repair, and frozen parent."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import task_brief_error_history as history
import later_release_history as later_history
import task_brief_walkthrough_history as walkthrough
import task_brief_print_history as printing

OLD = "      input.removeAttribute('aria-invalid');\n      get(key + '-error').hidden = true;"
NEW = "      input.removeAttribute('aria-invalid');\n      get(key + '-error').textContent = '';\n      get(key + '-error').hidden = true;"


class TaskBriefErrorStateTests(unittest.TestCase):
    def test_runtime_repair_is_only_clearing_the_edited_error_text(self):
        script = printing.before('assets/task-brief.js', (ROOT / 'assets/task-brief.js').read_text())
        self.assertEqual(script.count(NEW), 1)
        self.assertEqual(script.replace(NEW, OLD, 1), history.before('assets/task-brief.js', script))

    def test_rendered_page_changes_only_the_script_content_version(self):
        path = 'technology/task-brief/index.html'
        page = walkthrough.before(path, (ROOT / path).read_text())
        script = printing.before('assets/task-brief.js', (ROOT / 'assets/task-brief.js').read_bytes())
        old_script = history.before('assets/task-brief.js', script)
        current = '/assets/task-brief.js?v=' + sha256(script).hexdigest()[:12]
        previous = '/assets/task-brief.js?v=' + sha256(old_script).hexdigest()[:12]
        self.assertEqual(page.count(current), 1)
        self.assertEqual(page.replace(current, previous, 1), history.before(path, page))

    def test_all_production_paths_restore_the_actual_published_parent(self):
        record = history.change()
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        files = later_history.files([p for p in paths if p and not p.startswith(('_tests/', '_reports/'))])
        rows = sorted((p, sha256(history.before(p, later_history.before(p, (ROOT / p).read_bytes()))).hexdigest()) for p in files)
        self.assertEqual(len(rows), record['production_count'])
        self.assertEqual(sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(),
                         record['production_fingerprint'])

    def test_assembly_and_validation_are_identical_to_the_parent(self):
        original = history.before('assets/task-brief.js', (ROOT / 'assets/task-brief.js').read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'original.js'
            source.write_bytes(original)
            code = r'''
const assert = require('node:assert/strict');
const previous = require(process.argv[1]);
const current = require('./assets/task-brief.js');
assert.deepEqual(current.FIELDS, previous.FIELDS);
assert.equal(current.INSTRUCTIONS, previous.INSTRUCTIONS);
const valid = {goal:'Sort fictional books',materials:'12 books, three boxes',output:'A checklist',review:'Compare against source',limits:''};
const cases = [valid, null, {}, {...valid,goal:'   '}, {...valid,review:'\r\n'}, {...valid,limits:'x'.repeat(601)}, {...valid,materials:'<img src=x>\r\n& literal'}];
for (const values of cases) assert.deepEqual(current.assemble(values), previous.assemble(values));
console.log('Seven current/parent assembly cases match.');
'''
            run = subprocess.run(['node', '-e', code, str(source)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_reversal_is_exact_idempotent_and_type_preserving(self):
        for name, item in history.change()['paths'].items():
            raw = walkthrough.before(name, (ROOT / name).read_bytes())
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
            old = history.before(name, raw)
            self.assertEqual(sha256(old).hexdigest(), item['old_sha256'])
            self.assertEqual(history.before(Path(name), raw.decode()).encode(), old)
            self.assertEqual(history.before(name, old), old)

    def test_unknown_edits_are_not_concealed(self):
        for name in history.PATHS:
            raw = (ROOT / name).read_bytes()
            for mutation in (raw + b'!', b'!' + raw, raw[1:]):
                self.assertEqual(history.before(name, mutation), mutation)
        self.assertEqual(history.before('unrelated', b'unchanged'), b'unchanged')

    def test_corrupt_predecessor_hash_cannot_hide_a_change(self):
        name = 'assets/task-brief.js'
        record = deepcopy(history.change())
        record['paths'][name]['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=record):
            with self.assertRaises(ValueError):
                history.before(name, (ROOT / name).read_bytes())

    def test_invalid_offsets_cannot_reconstruct_history(self):
        name = 'assets/task-brief.js'
        for edits in ([[True, 1, '']], [[-1, 0, '']], [[2, 1, '']],
                      [[0, 3, ''], [2, 4, '']], [[0, 999999999, '']]):
            record = deepcopy(history.change())
            record['paths'][name]['edits'] = edits
            with self.subTest(edits=edits), patch.object(history, 'change', return_value=record):
                with self.assertRaises(ValueError):
                    history.before(name, (ROOT / name).read_bytes())


if __name__ == '__main__':
    unittest.main()
