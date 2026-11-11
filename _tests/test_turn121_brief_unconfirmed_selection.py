"""Manual Copy must not claim full selection when the browser declines it."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UnconfirmedSelectionTests(unittest.TestCase):
    def test_noop_throw_manual_reselect_and_edit_transitions(self):
        script = r'''
const assert = require('node:assert/strict');
const elements = new Map();
function el(id) {
  return {
    id, value: '', hidden: true, textContent: '', handlers: {},
    selectionStart: 0, selectionEnd: 0, children: [], attributes: {},
    addEventListener(name, callback) { this.handlers[name] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    focus() {}, scrollIntoView() {},
    select() {}, // First attempt is blocked without throwing.
    getBoundingClientRect() { return {top: 250, bottom: 300}; },
    replaceChildren(...nodes) {
      this.children = nodes;
      if (id === 'brief-export-alternatives-title') {
        this.textContent = nodes.map(node => node.textContent).join('');
      }
    },
    append(...nodes) { this.children.push(...nodes); },
    appendChild(node) { this.children.push(node); },
    remove() {}, click() {},
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
  createTextNode: text => ({textContent: text}),
};
global.window = {addEventListener() {}, scrollBy() {}, setTimeout() {}, innerHeight: 700};
global.location = {hash: ''};
require('./assets/task-brief.js');
for (const [key, value] of Object.entries({
  goal: 'Fictional goal', materials: 'Public notes',
  output: 'Short draft', review: 'Check the notes', limits: '',
})) d(key).value = value;
d('build').handlers.click();
const output = d('text');
assert.ok(output.value.length > 0);

// No-op browser selection must produce an honest alternative instruction.
d('select').handlers.click();
assert.equal(d('export-alternatives').hidden, false);
assert.equal(d('selection-cue').textContent,
  'Full selection not confirmed. In the text box, choose Select all, then Copy.');
assert.equal(d('export-alternatives-title').textContent,
  'Full selection not confirmed. Select all in the text box, then Copy.');
assert.match(d('copy-status').textContent, /Ctrl\+A or Cmd\+A/);
assert.match(d('copy-status').textContent, /touch and hold/);
assert.doesNotMatch(d('copy-status').textContent, /Complete text selected/);
assert.equal(output.attributes['aria-describedby'],
  'brief-selection-cue brief-text-help');
output.handlers.keyup();
assert.match(d('selection-cue').textContent, /^Full selection not confirmed/);

// A real manual Select all event restores the confirmed copy instructions.
output.selectionStart = 0;
output.selectionEnd = output.value.length;
output.handlers.select();
assert.match(d('selection-cue').textContent, /^Selected, not copied/);
assert.match(d('export-alternatives-title').textContent, /^Selected, not copied/);
assert.match(d('copy-status').textContent, /Complete text selected, not copied/);

// An exception from the browser API must also remain a usable manual route.
output.selectionEnd = 0;
output.select = () => { throw new Error('Selection not supported'); };
d('select').handlers.click();
assert.match(d('selection-cue').textContent, /^Full selection not confirmed/);
assert.match(d('copy-status').textContent, /choose Select all, then Copy/);
assert.equal(d('result').hidden, false);
assert.equal(output.value.includes('WORKING INSTRUCTIONS'), true);

d('goal').value = 'Another fictional goal';
d('goal').handlers.input();
assert.equal(d('result').hidden, true);
assert.equal(d('selection-cue').hidden, true);
assert.equal(d('export-alternatives').hidden, true);
console.log('Unconfirmed selection, native reselect and edit: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True,
            text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_no_transport_and_generated_script_version(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        self.assertIn('Full selection not confirmed.', script)
        self.assertIn('if (output.selectionStart === 0 && output.selectionEnd === output.value.length) {', script)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage',
                          'innerHTML', 'execCommand('):
            self.assertNotIn(forbidden, script)


if __name__ == '__main__':
    unittest.main()
