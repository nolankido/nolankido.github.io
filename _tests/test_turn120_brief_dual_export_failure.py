"""A failed second export must not re-offer the already failed first route."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DualExportFailureTests(unittest.TestCase):
    def test_failure_orders_reselection_and_new_assembly(self):
        script = r'''
const assert = require('node:assert/strict');
const elements = new Map();
function el(id) {
  return {
    id, value: '', hidden: true, selectionStart: 0, selectionEnd: 0,
    textContent: '', children: [], handlers: {},
    addEventListener(name, callback) { this.handlers[name] = callback; },
    setAttribute() {}, removeAttribute() {}, focus() {}, scrollIntoView() {},
    select() { this.selectionStart = 0; this.selectionEnd = this.value.length; },
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
global.window = {
  addEventListener() {}, scrollBy() {}, setTimeout() {},
  print() { throw new Error('Printer disabled'); }, innerHeight: 700,
};
global.location = {hash: ''};
global.URL.createObjectURL = () => { throw new Error('Downloads disabled'); };
require('./assets/task-brief.js');
const title = () => d('export-alternatives-title').textContent;
function fillAndBuild(label) {
  for (const [key, value] of Object.entries({
    goal: 'Fictional ' + label, materials: 'Public notes',
    output: 'Short draft', review: 'Compare with notes', limits: '',
  })) d(key).value = value;
  d('build').handlers.click();
  assert.equal(d('result').hidden, false);
}
function verifyLastRoute(last) {
  const other = last === 'print' ? 'download' : 'print';
  d(other).handlers.click();
  assert.equal(d('export-alternatives').hidden, false);
  assert.equal(d(last === 'print' ? 'print-alternative' : 'save-alternative').hidden, false);
  assert.equal(d(last === 'print' ? 'save-alternative' : 'print-alternative').hidden, true);
  d(last).handlers.click();
  assert.equal(d('save-alternative').hidden, true);
  assert.equal(d('print-alternative').hidden, true);
  assert.equal(title(), 'Save and print both unavailable. Use Ctrl+C, Cmd+C, or touch Copy.');
  assert.match(d('copy-status').textContent, /Save and print both failed/);
  assert.doesNotMatch(d('copy-status').textContent, /copied to the clipboard/);
  assert.equal(d('text').selectionStart, 0);
  assert.equal(d('text').selectionEnd, d('text').value.length);
  d('text').selectionEnd = 0;
  d('text').handlers.keyup();
  assert.match(title(), /^Full brief no longer selected/);
  d('select').handlers.click();
  assert.match(title(), /^Save and print both unavailable/);
  assert.equal(d('save-alternative').hidden, true);
  assert.equal(d('print-alternative').hidden, true);
  d('text').handlers.copy();
  assert.match(title(), /^Copy command detected/);
  assert.match(d('copy-status').textContent, /cannot confirm clipboard contents/);
}
fillAndBuild('print then download');
verifyLastRoute('download');
// An edited and newly assembled brief must receive a fresh set of choices.
d('goal').value = 'Fictional changed task';
d('goal').handlers.input();
fillAndBuild('download then print');
d('select').handlers.click();
assert.equal(d('save-alternative').hidden, false);
assert.equal(d('print-alternative').hidden, false);
assert.match(title(), /^Selected, not copied/);
verifyLastRoute('print');
console.log('Both export failure orders and reset: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True,
            text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_no_new_transport_and_generated_reference(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage',
                          'innerHTML', 'execCommand('):
            self.assertNotIn(forbidden, script)
        self.assertIn('unavailableExports.clear();', script)
        self.assertIn("unavailableExports.add(unavailable)", script)
        self.assertIn("unavailableExports.size === 2", script)
        self.assertIn('Save and print both unavailable.', script)


if __name__ == '__main__':
    unittest.main()
