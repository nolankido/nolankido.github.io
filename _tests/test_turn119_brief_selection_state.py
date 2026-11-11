"""The nearby native-copy fallback must reflect actual selection state."""

from hashlib import sha256
from pathlib import Path
import json
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SelectionStateTests(unittest.TestCase):
    def test_partial_full_native_copy_and_reset_transitions(self):
        script = r'''
const assert = require('node:assert/strict');
const elements = new Map();
function el(id) {
  return {
    id, value: '', hidden: true, selectionStart: 0, selectionEnd: 0,
    textContent: '', children: [], handlers: {},
    addEventListener(name, callback) { this.handlers[name] = callback; },
    setAttribute() {}, removeAttribute() {},
    focus() {}, scrollIntoView() {},
    select() { this.selectionStart = 0; this.selectionEnd = this.value.length; },
    getBoundingClientRect() { return { top: 250, bottom: 300 }; },
    replaceChildren(...nodes) {
      this.children = nodes;
      if (id === 'brief-export-alternatives-title') {
        this.textContent = nodes.map(node => node.textContent).join('');
      }
    },
    append(...nodes) { this.children.push(...nodes); },
    appendChild(node) { this.children.push(node); },
    remove() {}, click() {}
  };
}
const names = ['editor', 'result', 'text', 'selection-cue',
  'export-alternatives', 'export-alternatives-title',
  'save-alternative', 'print-alternative', 'status', 'copy-status',
  'confirm', 'preview', 'confirm-title', 'confirm-message', 'confirm-yes',
  'confirm-no', 'build', 'clear', 'copy', 'select', 'print', 'download',
  'result-title', 'unavailable', 'quick-meeting'];
for (const key of ['goal', 'materials', 'output', 'review', 'limits']) {
  names.push(key, key + '-error');
}
for (const name of names) elements.set('brief-' + name, el('brief-' + name));
const d = name => elements.get('brief-' + name);
global.document = {
  getElementById: id => elements.get(id),
  querySelectorAll: () => [], querySelector: () => null,
  createElement: tag => el('created-' + tag),
  createTextNode: text => ({ textContent: text }),
};
global.window = { addEventListener() {}, scrollBy() {}, setTimeout() {} };
global.location = { hash: '' };
require('./assets/task-brief.js');
assert.equal(d('export-alternatives-title').textContent,
  'Selected, not copied. Ctrl+C, Cmd+C, or touch Copy.');
for (const [key, value] of Object.entries({
  goal: 'Fictional goal', materials: 'Anonymized public notes',
  output: 'A short draft', review: 'Check against the notes', limits: ''
})) d(key).value = value;
d('build').handlers.click();
d('select').handlers.click();
const output = d('text');
const title = () => d('export-alternatives-title').textContent;
assert.equal(d('export-alternatives').hidden, false);
assert.equal(output.selectionStart, 0);
assert.equal(output.selectionEnd, output.value.length);
assert.match(title(), /^Selected, not copied/);

// The nearby fallback itself must warn when the full selection disappears.
output.selectionEnd = 0;
output.handlers.keyup();
assert.equal(title(),
  'Full brief no longer selected. Choose Select text manually again.');
assert.match(d('copy-status').textContent, /no longer selected/);

// Native re-selection resets the warning without claiming a clipboard write.
output.selectionEnd = output.value.length;
output.handlers.select();
assert.equal(title(), 'Selected, not copied. Ctrl+C, Cmd+C, or touch Copy.');
assert.match(d('copy-status').textContent, /not copied/);

// An OS Copy event is observable, but clipboard success is not confirmed.
output.handlers.copy();
assert.equal(title(), 'Copy command detected. Paste elsewhere to verify.');
assert.match(d('copy-status').textContent, /cannot confirm clipboard contents/);
assert.doesNotMatch(d('copy-status').textContent, /Brief copied to the clipboard/);

// A fresh manual selection replaces the old copy status.
d('select').handlers.click();
assert.match(title(), /^Selected, not copied/);
output.selectionEnd = 2;
output.handlers.copy();
assert.match(title(), /^Full brief no longer selected/);
assert.match(d('copy-status').textContent, /only part of the brief selected/);

// Any new field edit hides the actions and resets stale state.
d('goal').value = 'Another fictional goal';
d('goal').handlers.input();
assert.equal(d('export-alternatives').hidden, true);
assert.equal(title(), 'Selected, not copied. Ctrl+C, Cmd+C, or touch Copy.');
assert.equal(d('result').hidden, true);
console.log('Native Copy, partial selection, reselect and reset: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True,
            timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_live_group_name_carries_initial_copy_instruction(self):
        for name in ('_source/technology/task-brief.html',
                     'technology/task-brief/index.html'):
            with self.subTest(name=name):
                html = (ROOT / name).read_text(encoding='utf-8')
                self.assertIn(
                    'role="group" aria-labelledby="brief-export-alternatives-title" hidden',
                    html)
                self.assertIn(
                    '<p id="brief-export-alternatives-title"><strong>Selected, not copied.'
                    '</strong> Ctrl+C, Cmd+C, or touch Copy.</p>', html)
                self.assertEqual(html.count('id="brief-export-alternatives-title"'), 1)

    def test_script_hash_is_current_and_no_new_transport(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage',
                          'innerHTML', 'execCommand('):
            self.assertNotIn(forbidden, script)
        self.assertIn('title.replaceChildren(strong, document.createTextNode(parts[1]));',
                      script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(item for item in pages if item.get('id') == 'task-brief')
        self.assertEqual(brief['updated'], '2026-11-11')


if __name__ == '__main__':
    unittest.main()
