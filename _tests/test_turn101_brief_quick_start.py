"""The first-visit Task Brief shortcut reuses the safe existing example loader."""

from html import unescape
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source/technology/task-brief.html'
BUILT = ROOT / 'technology/task-brief/index.html'
FIELDS = ('goal', 'materials', 'output', 'review', 'limits')


class TaskBriefQuickStartTests(unittest.TestCase):
    def test_first_use_shortcut_is_inside_progressive_editor(self):
        for path in (SOURCE, BUILT):
            with self.subTest(path=path):
                html = path.read_text(encoding='utf-8')
                self.assertEqual(html.count('id="brief-quick-meeting"'), 1)
                self.assertEqual(html.count('data-brief-example='), 6)
                self.assertEqual(html.count('data-use-example='), 6)
                editor = html.index('id="brief-editor" hidden')
                helper = html.index('class="brief-quick-start"')
                button = html.index('id="brief-quick-meeting" type="button" hidden')
                first_field = html.index('id="brief-goal"')
                self.assertTrue(editor < helper < button < first_field)
                self.assertIn('Load the editable meeting example', html)
                self.assertIn('If you already started writing', html)
                self.assertIn('neither runs AI', html)
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        self.assertIn('.brief-quick-start { grid-column: 1 / -1;', css)
        self.assertRegex(css, r'@media print[\s\S]*?\.brief-quick-start\s*\{\s*display:\s*none')

    def test_quick_button_uses_the_existing_meeting_fields(self):
        source = SOURCE.read_text(encoding='utf-8')
        meeting = re.search(r'<details class="brief-example" id="brief-example-meeting" data-brief-example="meeting">(.*?)</details>', source, re.S)
        self.assertIsNotNone(meeting)
        values = {key: unescape(value) for key, value in re.findall(
            r'<dd data-brief-field="([^"]+)">(.*?)</dd>', meeting[1], re.S)}
        self.assertEqual(set(values), set(FIELDS))
        self.assertTrue(all(values.values()))

        # Run the actual production script against a minimal DOM. Assertions
        # cover first load, cancellation, confirmation, and the original
        # six-button route. No browser, network service, or real user data.
        script = r'''
const assert = require('node:assert/strict');
const meeting = __MEETING__;
let focused = '';
function element(id) {
  return {
    id, value:'', textContent:'', hidden:true, handlers:{},
    addEventListener(name, fn) { this.handlers[name] = fn; },
    focus() { focused = id; },
    removeAttribute() {}, setAttribute() {}, replaceChildren() {},
    appendChild() {}, select() {}
  };
}
const ids = ['editor','result','text','status','copy-status','confirm','preview',
 'confirm-title','confirm-message','confirm-yes','confirm-no','build','clear',
 'copy','select','print','download','result-title','unavailable','quick-meeting'];
for (const key of ['goal','materials','output','review','limits']) {
  ids.push(key, key + '-error');
}
const elements = Object.fromEntries(ids.map(id => ['brief-' + id, element('brief-' + id)]));
const card = {
  dataset: {briefExample:'meeting'},
  querySelectorAll(selector) {
    assert.equal(selector, '[data-brief-field]');
    return Object.entries(meeting).map(([key, value]) => ({
      dataset:{briefField:key}, textContent:value
    }));
  }
};
const oldButton = element('original-button');
oldButton.closest = selector => {
  assert.equal(selector, '[data-brief-example]');
  return card;
};
global.document = {
  getElementById: id => id === 'brief-example-meeting' ? card : elements[id],
  querySelectorAll: selector => selector === '[data-use-example]' ? [oldButton] : [],
  createElement: tag => element(tag)
};
global.window = {addEventListener() {}};
global.location = {hash:''};
require('./assets/task-brief.js');
const quick = elements['brief-quick-meeting'];
const goal = elements['brief-goal'];
const confirm = elements['brief-confirm'];
const click = item => {assert.equal(typeof item.handlers.click, 'function'); item.handlers.click();};
assert.equal(quick.hidden, false);
assert.equal(oldButton.hidden, false);
assert.equal(elements['brief-editor'].hidden, false);
for (const key of Object.keys(meeting)) assert.equal(elements['brief-' + key].value, '');

click(quick);
for (const [key, value] of Object.entries(meeting)) {
  assert.equal(elements['brief-' + key].value, value, key);
}
assert.match(elements['brief-status'].textContent, /Illustrative example loaded/);
assert.equal(focused, 'brief-goal');

goal.value = 'Keep my own draft';
click(quick);
assert.equal(goal.value, 'Keep my own draft');
assert.equal(confirm.hidden, false);
assert.equal(focused, 'brief-confirm-yes');
assert.match(elements['brief-confirm-title'].textContent, /Replace your entries/);
click(elements['brief-confirm-no']);
assert.equal(confirm.hidden, true);
assert.equal(goal.value, 'Keep my own draft');
assert.equal(focused, 'brief-quick-meeting');

click(quick);
click(elements['brief-confirm-yes']);
assert.equal(confirm.hidden, true);
for (const [key, value] of Object.entries(meeting)) {
  assert.equal(elements['brief-' + key].value, value, key);
}

goal.value = 'Changed again';
click(oldButton);
assert.equal(goal.value, 'Changed again');
assert.equal(confirm.hidden, false);
click(elements['brief-confirm-yes']);
assert.equal(goal.value, meeting.goal);

// A broken meeting record cannot silently replace anything.
delete meeting.review;
goal.value = 'Must stay';
click(quick);
assert.equal(goal.value, 'Must stay');
assert.equal(confirm.hidden, true);
console.log('Quick-start interaction: PASS');
'''.replace('__MEETING__', json.dumps(values))
        run = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_no_ai_submission_tracking_or_persistence_added(self):
        javascript = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        self.assertIn('loadExample(card, quickMeeting)', javascript)
        self.assertIn('loadExample(button.closest', javascript)
        for forbidden in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'sendBeacon', 'innerHTML'):
            self.assertNotIn(forbidden, javascript)

    def test_metadata_updated_for_real_page_change(self):
        manifest = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        entry = next(item for item in manifest if item.get('id') == 'task-brief')
        self.assertEqual(entry['updated'], '2026-11-10')
        self.assertIn('editable meeting example', entry['description'])
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertRegex(sitemap, r'<loc>https://nolankido\.com/technology/task-brief/</loc>\s*<lastmod>2026-11-10</lastmod>')


if __name__ == '__main__':
    unittest.main()
