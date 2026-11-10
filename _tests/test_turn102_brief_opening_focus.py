"""After loading a long Task Brief example, editing starts at its first words."""

from html import unescape
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'assets/task-brief.js'
SOURCE = ROOT / '_source/technology/task-brief.html'


class TaskBriefOpeningFocusTests(unittest.TestCase):
    def test_original_and_quick_examples_open_at_start_after_keyboard_actions(self):
        source = SOURCE.read_text(encoding='utf-8')
        meeting = re.search(r'<details class="brief-example" id="brief-example-meeting"[^>]*>(.*?)</details>', source, re.S)
        self.assertIsNotNone(meeting)
        values = {key: unescape(value) for key, value in re.findall(
            r'<dd data-brief-field="([^"]+)">(.*?)</dd>', meeting[1], re.S)}
        self.assertEqual(set(values), {'goal', 'materials', 'output', 'review', 'limits'})

        # Focus in the fake browser deliberately sets the caret at the end
        # and scrolls a long field down, reproducing the 320px observed state.
        # The production script must correct both before the reader starts.
        script = r'''
const assert = require('node:assert/strict');
const values = __VALUES__;
let focused = '';
function el(id) {
  return {
    id, value:'', textContent:'', hidden:true, handlers:{}, scrollTop:0,
    addEventListener(name, fn) {this.handlers[name] = fn;},
    focus() {
      focused = id;
      if (id === 'brief-goal') {
        this.selectionStart = this.value.length;
        this.selectionEnd = this.value.length;
        this.scrollTop = 48;
      }
    },
    setSelectionRange(start, end) {this.selectionStart=start;this.selectionEnd=end;},
    removeAttribute() {}, setAttribute() {}, replaceChildren() {}, appendChild() {}
  };
}
const fields = ['goal','materials','output','review','limits'];
const names = ['editor','result','text','status','copy-status','confirm','preview',
  'confirm-title','confirm-message','confirm-yes','confirm-no','build','clear',
  'copy','select','print','download','result-title','unavailable','quick-meeting'];
for (const key of fields) names.push(key, key+'-error');
const dom = Object.fromEntries(names.map(key=>['brief-'+key,el('brief-'+key)]));
const card = {dataset:{briefExample:'meeting'},querySelectorAll(selector) {
  assert.equal(selector,'[data-brief-field]');
  return Object.entries(values).map(([key,value])=>({dataset:{briefField:key},textContent:value}));
}};
const old = el('original-example');
old.closest = () => card;
global.document = {
  getElementById: id => id==='brief-example-meeting'?card:dom[id],
  querySelectorAll: selector => selector==='[data-use-example]'?[old]:[],
  createElement: tag => el(tag)
};
global.window = {addEventListener() {}};
global.location = {hash:''};
require('./assets/task-brief.js');
const quick=dom['brief-quick-meeting'],goal=dom['brief-goal'];
const click = button => button.handlers.click();
function checkOpening() {
  assert.equal(focused,'brief-goal');
  assert.equal(goal.value,values.goal);
  assert.equal(goal.selectionStart,0);
  assert.equal(goal.selectionEnd,0);
  assert.equal(goal.scrollTop,0);
}
assert.equal(quick.hidden,false);
click(quick);
checkOpening();
goal.value='Keep my own words';
click(quick);
assert.equal(dom['brief-confirm'].hidden,false);
assert.equal(goal.value,'Keep my own words');
click(dom['brief-confirm-yes']);
checkOpening();
goal.value='A second draft';
click(old);
assert.equal(goal.value,'A second draft');
click(dom['brief-confirm-yes']);
checkOpening();
console.log('Opening-caret interaction: PASS');
'''.replace('__VALUES__', json.dumps(values))
        result = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_only_caret_and_scroll_repositioned_in_example_loader(self):
        source = SCRIPT.read_text(encoding='utf-8')
        match = re.search(r'function loadExample\(card, button\) \{(.*?)\n  \}', source, re.S)
        self.assertIsNotNone(match)
        loader = match[1]
        focus = loader.index('inputs.goal.focus();')
        selection = loader.index('inputs.goal.setSelectionRange(0, 0);')
        scroll = loader.index('inputs.goal.scrollTop = 0;')
        self.assertLess(focus, selection)
        self.assertLess(selection, scroll)
        self.assertIn('requestChange(() =>', loader)
        self.assertIn('Object.keys(assemble(values).errors).length', loader)
        self.assertIn('loadExample(button.closest', source)
        self.assertIn('loadExample(card, quickMeeting)', source)
        for forbidden in ('fetch(', 'localStorage', 'sessionStorage', 'sendBeacon', 'innerHTML'):
            self.assertNotIn(forbidden, source)


if __name__ == '__main__':
    unittest.main()
