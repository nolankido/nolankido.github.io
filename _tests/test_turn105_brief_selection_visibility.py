"""Task Brief manual-selection fallbacks keep focused text below the header."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'assets/task-brief.js'


class TaskBriefSelectionVisibilityTests(unittest.TestCase):
    def test_all_selection_paths_preserve_selection_and_correct_header_overlap(self):
        script = r'''
const assert = require('node:assert/strict');
const events = {focused:null, selections:0, scrolls:[], outputTop:43};
function element(id) {
  return {
    id, value:'', textContent:'', hidden:true, handlers:{}, children:[],
    addEventListener(name,handler) {this.handlers[name]=handler;},
    focus() {events.focused=id;},
    select() {events.selections+=1; this.selectionStart=0; this.selectionEnd=this.value.length;},
    getBoundingClientRect() {return {top:events.outputTop};},
    removeAttribute() {}, setAttribute() {}, remove() {},
    replaceChildren() {this.children=[];},
    appendChild(node) {this.children.push(node);},
    append(...items) {this.children.push(...items);}
  };
}
const names=['editor','result','text','status','copy-status','confirm','preview',
 'confirm-title','confirm-message','confirm-yes','confirm-no','build','clear',
 'copy','select','print','download','result-title','unavailable','quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for (const name of fields) names.push(name,name+'-error');
const dom=Object.fromEntries(names.map(n=>['brief-'+n,element('brief-'+n)]));
global.document={
  getElementById:id=>dom[id],
  querySelectorAll:()=>[],
  querySelector:selector=>selector==='.site-header'?{getBoundingClientRect:()=>({bottom:153})}:null,
  createElement:tag=>element('created-'+tag)
};
global.window={
  addEventListener() {},
  scrollBy(options) {events.scrolls.push(options); events.outputTop-=options.top;}
};
global.location={hash:''};
Object.defineProperty(global,'navigator',{value:{},configurable:true});
URL.createObjectURL=()=>{throw Error('unavailable');};
require('./assets/task-brief.js');
const values={goal:'A fictional decision',materials:'Redacted public notes',
 output:'One action list',review:'Compare with source',limits:'No invented commitments'};
for (const [key,value] of Object.entries(values)) dom['brief-'+key].value=value;
dom['brief-build'].handlers.click();
assert.equal(dom['brief-result'].hidden,false);

async function checkClick(path, expectedMessage) {
  events.outputTop=43;
  const earlierScrolls=events.scrolls.length;
  await dom['brief-'+path].handlers.click();
  assert.equal(events.focused,'brief-text');
  assert.equal(dom['brief-text'].selectionStart,0);
  assert.equal(dom['brief-text'].selectionEnd,dom['brief-text'].value.length);
  assert.equal(events.outputTop,173);
  assert.equal(events.scrolls.length,earlierScrolls+1);
  assert.deepEqual(events.scrolls.at(-1),{top:-130,behavior:'instant'});
  assert.match(dom['brief-copy-status'].textContent,expectedMessage);
}
(async()=>{
  await checkClick('select',/Complete text selected/);
  await checkClick('copy',/Automatic copy is unavailable/);
  await checkClick('print',/Printing is unavailable/);
  await checkClick('download',/Download unavailable/);
  // Already visible text must not jump just because it was selected.
  events.outputTop=240;
  const before=events.scrolls.length;
  await dom['brief-select'].handlers.click();
  assert.equal(events.scrolls.length,before);
  assert.equal(events.outputTop,240);
  // Geometry and scroll APIs are conveniences, not prerequisites to selecting.
  delete dom['brief-text'].getBoundingClientRect;
  delete global.window.scrollBy;
  await dom['brief-select'].handlers.click();
  assert.equal(events.focused,'brief-text');
  assert.equal(dom['brief-text'].selectionEnd,dom['brief-text'].value.length);
  console.log('Selection visibility: PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        proc = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_only_explicit_selection_paths_scroll_and_no_network_is_added(self):
        script = SCRIPT.read_text(encoding='utf-8')
        self.assertEqual(script.count('output.focus(); output.select();'), 1)
        self.assertEqual(script.count('selectVisibleText('), 5)
        self.assertIn("if (Number.isFinite(top) && top < inset + 20 && typeof window.scrollBy === 'function')", script)
        self.assertIn("window.scrollBy({top: top - inset - 20, behavior: 'instant'});", script)
        self.assertLess(script.index('output.focus(); output.select();'), script.index('window.scrollBy({top:'))
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)

    def test_generated_page_uses_new_script_without_backdating_content(self):
        script_hash = sha256(SCRIPT.read_bytes()).hexdigest()[:12]
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + script_hash, html)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertEqual(brief['updated'], '2026-11-10')
        self.assertIn('id="brief-export-intro"', html)


if __name__ == '__main__':
    unittest.main()
