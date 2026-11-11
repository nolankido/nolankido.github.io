"""Manual-copy advice must track focus, not only a retained selection range."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BriefFocusLossTests(unittest.TestCase):
    def test_tab_away_refocus_reselect_copy_and_edit(self):
        script = r'''
const assert = require('node:assert/strict');
const elements = new Map();
let doc;
function el(id) {
  return {
    id, value: '', hidden: true, selectionStart: 0, selectionEnd: 0,
    textContent: '', children: [], handlers: {}, attributes: {},
    addEventListener(name, callback) { this.handlers[name] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    focus() {
      const previous = doc.activeElement;
      if (previous === this) return;
      if (previous) previous.handlers.blur?.();
      doc.activeElement = this;
      this.handlers.focus?.();
    },
    select() { this.selectionStart = 0; this.selectionEnd = this.value.length; },
    scrollIntoView() {},
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
doc = global.document = {
  activeElement: null,
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
  output: 'Short draft', review: 'Verify the draft', limits: '',
})) d(key).value = value;
d('build').handlers.click();
d('select').handlers.click();
const output = d('text');
const title = () => d('export-alternatives-title').textContent;
assert.equal(doc.activeElement, output);
assert.equal(output.selectionStart, 0);
assert.equal(output.selectionEnd, output.value.length);
assert.match(d('selection-cue').textContent, /^Selected, not copied/);

// Tab preserves the range in Chromium, but changes the keyboard copy target.
const nextControl = el('next-control');
nextControl.focus();
assert.equal(output.selectionEnd, output.value.length);
assert.equal(doc.activeElement, nextControl);
assert.match(d('selection-cue').textContent, /^Text box no longer focused/);
assert.match(title(), /^Text box no longer focused/);
assert.match(d('copy-status').textContent, /lost focus/);
assert.equal(output.attributes['aria-describedby'],
  'brief-selection-cue brief-text-help');
output.handlers.keyup(); // A late key event must not reassert a selected cue.
assert.match(d('selection-cue').textContent, /^Text box no longer focused/);

// Returning focus with the same full range safely restores selected guidance.
output.focus();
assert.match(d('selection-cue').textContent, /^Selected, not copied/);
assert.match(title(), /^Selected, not copied/);

// A changed range while away cannot be advertised as a full selection.
nextControl.focus();
output.selectionEnd = 2;
output.focus();
assert.match(d('selection-cue').textContent, /^Full selection not confirmed/);
assert.match(title(), /^Full selection not confirmed/);
assert.doesNotMatch(d('copy-status').textContent, /Complete text selected/);

// The nearby button can restore focus and complete selection from any state.
d('select').handlers.click();
assert.equal(doc.activeElement, output);
assert.equal(output.selectionEnd, output.value.length);
assert.match(d('selection-cue').textContent, /^Selected, not copied/);

// A native Copy command remains only a detection, including after Tab.
output.handlers.copy();
nextControl.focus();
assert.match(title(), /^Copy command detected/);
assert.match(d('copy-status').textContent, /cannot confirm clipboard contents/);

// Partial native Copy must retain the warning even if focus then leaves.
d('select').handlers.click();
output.selectionEnd = 2;
output.handlers.copy();
nextControl.focus();
assert.match(d('copy-status').textContent, /only part of the brief selected/);
assert.match(title(), /^Full brief no longer selected/);

// Editing a field removes the entire stale export and selection state.
d('goal').value = 'Another fictional goal';
d('goal').handlers.input();
assert.equal(d('result').hidden, true);
assert.equal(d('selection-cue').hidden, true);
assert.equal(d('export-alternatives').hidden, true);
console.log('Keyboard focus loss, re-entry, copy detection and reset: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True,
            text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_generated_script_and_no_transport(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        self.assertIn("output.addEventListener('blur'", script)
        self.assertIn("output.addEventListener('focus'", script)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage',
                          'innerHTML', 'execCommand('):
            self.assertNotIn(forbidden, script)


if __name__ == '__main__':
    unittest.main()
