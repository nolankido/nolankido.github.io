"""The assembled Task Brief opens with enough context for a phone reader."""

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'assets/task-brief.js'


class TaskBriefResultHandoffTests(unittest.TestCase):
    def test_build_rebuild_and_fallback_focus_without_losing_output(self):
        script = r'''
const assert = require('node:assert/strict');
const events = {focused:null,scrolls:[]};
function element(id) {
  return {
    id, value:'', textContent:'', hidden:true, handlers:{}, children:[],
    addEventListener(name, handler) {this.handlers[name] = handler;},
    focus() {events.focused=id;},
    scrollIntoView(options) {events.scrolls.push({id, options});},
    removeAttribute() {}, setAttribute() {},
    replaceChildren() {this.children=[];},
    appendChild(node) {this.children.push(node);},
    append(...items) {this.children.push(...items);},
    select() {}
  };
}
const fieldNames=['goal','materials','output','review','limits'];
const names=['editor','result','text','status','copy-status','confirm','preview',
  'confirm-title','confirm-message','confirm-yes','confirm-no','build','clear',
  'copy','select','print','download','result-title','unavailable','quick-meeting'];
for (const name of fieldNames) names.push(name,name+'-error');
const dom=Object.fromEntries(names.map(name=>['brief-'+name,element('brief-'+name)]));
global.document={
  getElementById:id=>dom[id],
  querySelectorAll:()=>[],
  createElement:tag=>element('created-'+tag)
};
global.window={addEventListener() {}};
global.location={hash:''};
require('./assets/task-brief.js');
const values={goal:'Clarify a small team decision',materials:'Public, fictional notes',
  output:'A short list with decisions and questions',review:'Check the source notes',
  limits:'Do not invent participants or commitments'};
for (const [name,value] of Object.entries(values)) dom['brief-'+name].value=value;
dom['brief-build'].handlers.click();
assert.equal(dom['brief-result'].hidden,false);
assert.equal(events.focused,'brief-result-title');
assert.deepEqual(events.scrolls,[{id:'brief-result-title',options:{block:'center',behavior:'instant'}}]);
assert.equal(dom['brief-preview'].children.length,6);
assert.equal(dom['brief-preview'].children[0].children[1].textContent,values.goal);
assert.match(dom['brief-text'].value,/PURPOSE\nClarify a small team decision/);
assert.match(dom['brief-status'].textContent,/No AI has run/);

// Editing hides the stale result, and rebuilding shows the updated copy.
dom['brief-goal'].value='A revised team decision';
dom['brief-goal'].handlers.input();
assert.equal(dom['brief-result'].hidden,true);
assert.equal(dom['brief-text'].value,'');
dom['brief-build'].handlers.click();
assert.equal(dom['brief-preview'].children[0].children[1].textContent,'A revised team decision');
assert.equal(events.scrolls.length,2);

// Older browsers that lack this convenience still get the focused heading.
delete dom['brief-result-title'].scrollIntoView;
dom['brief-build'].handlers.click();
assert.equal(events.focused,'brief-result-title');
assert.equal(events.scrolls.length,2);
assert.equal(dom['brief-result'].hidden,false);
console.log('Result handoff: PASS');
'''
        proc = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_result_handoff_is_explicitly_scoped_to_success(self):
        script = SCRIPT.read_text(encoding='utf-8')
        start = script.index("get('build').addEventListener('click', () => {")
        end = script.index("get('clear').addEventListener", start)
        build = script[start:end]
        self.assertIn('if (errors.length) {', build)
        self.assertLess(build.index('if (errors.length) {'), build.index('result.hidden = false;'))
        self.assertLess(build.index('resultTitle.focus();'), build.index("resultTitle.scrollIntoView({block: 'center', behavior: 'instant'})"))
        self.assertIn("typeof resultTitle.scrollIntoView === 'function'", build)
        self.assertEqual(script.count('resultTitle.scrollIntoView('),1)
        for forbidden in ('fetch(', 'localStorage', 'sessionStorage', 'sendBeacon', 'innerHTML'):
            self.assertNotIn(forbidden, script)

    def test_generated_page_uses_exact_updated_script_and_content_date(self):
        script_hash = sha256(SCRIPT.read_bytes()).hexdigest()[:12]
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + script_hash, html)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertGreaterEqual(brief['updated'], '2026-11-10')
        self.assertEqual(len(re.findall(r'id="brief-result-title"',html)),1)


if __name__ == '__main__':
    unittest.main()
