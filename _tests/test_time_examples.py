"""Editable examples preserve the existing source, arithmetic and privacy scope."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build, time_examples
import time_examples_history as history
from test_site import Page


class TimeExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/time-examples-baseline.json').read_text())

    def test_only_one_page_and_its_scoped_script_change(self):
        b = self.baseline
        self.assertEqual(sha256(json.dumps(build.public_pages(), sort_keys=True, ensure_ascii=False).encode()).hexdigest(), b['pages_sha256'])
        self.assertEqual(set(map(str, self.outputs)), set(b['outputs']))
        changed = []
        for path, expected in b['outputs'].items():
            raw = self.outputs[Path(path)]
            if sha256(raw.encode()).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw).encode()).hexdigest(), expected, path)
        self.assertEqual(changed, [time_examples.PATH])
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file()}
        self.assertEqual(files, set(b['files']))
        changed = []
        for path, expected in b['files'].items():
            raw = (ROOT / path).read_bytes()
            if sha256(raw).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), expected, path)
        self.assertEqual(changed, [history.SCRIPT])

    def test_rendered_values_match_all_three_original_worked_examples(self):
        doc = Page(time_examples.blocks()[0])
        rows = [json.loads(a['data-time-example']) for a in doc.tags('button') if 'data-time-example' in a]
        expected = [dict(zip(time_examples.KEYS, values)) for values in [
            ['30', '8', '7', '6', '60', '15'],
            ['30', '8', '7', '1', '60', '0'],
            ['20', '5', '18', '10', '10', '5'],
        ]]
        self.assertEqual(rows, expected)
        run = subprocess.run(['node', '-e', 'const a=require("./assets/workflow-time.js"),rows=JSON.parse(require("fs").readFileSync(0,"utf8")); console.log(JSON.stringify(rows.map(a.calculate)));'],
                             cwd=ROOT, input=json.dumps(rows), text=True, capture_output=True, check=True)
        values = json.loads(run.stdout)
        self.assertEqual([(v['usual'], v['changed'], v['net']) for v in values], [(18000, 16500, 1500), (3000, 7500, -4500), (20000, 24500, -4500)])
        source = (ROOT / '_source/technology/ai-time-savings.html').read_text()
        for phrase in ['Six repetitions, 60 minutes of setup, and 15 minutes of upkeep',
                       'do the task once, with 60 minutes of setup and no upkeep',
                       'Ten repetitions, 10 minutes of setup, and 5 minutes of upkeep']:
            self.assertIn(phrase, source)
        old = history.before(history.SCRIPT, (ROOT / history.SCRIPT).read_text())
        current = (ROOT / history.SCRIPT).read_text()
        self.assertEqual(old.split('  const editor =')[0], current.split('  const editor =')[0])

    def test_controls_have_native_fallback_and_insertion_fails_closed(self):
        body = (ROOT / '_source/technology/ai-time-savings.html').read_text()
        page = {'id': 'ai-time-savings'}
        result = time_examples.decorate(page, body)
        self.assertEqual(history.before(time_examples.PATH, result), body)
        self.assertEqual(time_examples.decorate({'id': 'about'}, body), body)
        for invalid in [result, body.replace('<div id="time-editor" hidden>', '')]:
            with self.assertRaises(ValueError):
                time_examples.decorate(page, invalid)
        doc = Page(time_examples.blocks()[0])
        picker = next(a for a in doc.tags('div') if a.get('id') == 'time-example-picker')
        self.assertIn('hidden', picker)
        self.assertTrue(all(a['type'] == 'button' for a in doc.tags('button')))
        self.assertEqual([sha256(b.encode()).hexdigest() for b in time_examples.blocks()], history.change()['blocks'])
        self.assertNotIn('\u2014', ''.join(time_examples.blocks()))

    def test_frozen_adapter_exposes_unreviewed_changes(self):
        for path, old, new in [(history.SCRIPT, 'const perRun =', 'const perRunChanged ='),
                               (history.SCRIPT, 'Fictional example starting point:', 'Verified result:'),
                               (time_examples.PATH, 'Keep my comparison', 'Erase without asking'),
                               (time_examples.PATH, 'Net saving: 15 minutes.', 'Net saving: 50 minutes.')]:
            value = (ROOT / path).read_text()
            modified = value.replace(old, new, 1)
            self.assertNotEqual(modified, value)
            self.assertNotEqual(history.before(path, modified), history.before(path, value))
        self.assertEqual(history.before('about/index.html', 'untouched'), 'untouched')
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
