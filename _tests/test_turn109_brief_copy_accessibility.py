"""Manual copy has a concise visible cue and accurate focus description."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
COPY_CUE = 'Selected, not copied. Press Ctrl+C or Command+C; on touch, choose Copy.'


class ManualCopyAccessibilityTests(unittest.TestCase):
    def test_selection_cue_is_announced_on_focus_only_while_applicable(self):
        script = r'''
const assert=require('node:assert/strict');
let focused=null, focusDescription=null, clipboardPromise=Promise.resolve();
const dom={};
function element(id) {
  const attrs=new Map(id==='brief-text'?[['aria-describedby','brief-text-help']]:[]);
  return {
    id, textContent:'', value:'', hidden:true, children:[], handlers:{},
    addEventListener(name, handler) {this.handlers[name]=handler;},
    setAttribute(name,value) {attrs.set(name,value);},
    getAttribute(name) {return attrs.get(name)??null;},
    removeAttribute(name) {attrs.delete(name);},
    focus() {focused=id; focusDescription=this.getAttribute('aria-describedby');},
    select() {this.selectionStart=0;this.selectionEnd=this.value.length;},
    getBoundingClientRect() {return {top:240,bottom:300};},
    replaceChildren() {this.children=[];},
    append(...items) {this.children.push(...items);},
    appendChild(item) {this.children.push(item);},
    click() {}, remove() {}
  };
}
const names=['editor','result','text','text-label','selection-cue','status',
  'copy-status','confirm','preview','confirm-title','confirm-message',
  'confirm-yes','confirm-no','build','clear','copy','select','print',
  'download','result-title','unavailable','quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for(const field of fields) names.push(field,field+'-error');
for(const name of names) dom['brief-'+name]=element('brief-'+name);
global.document={
  getElementById:id=>dom[id], querySelectorAll:()=>[],
  querySelector:()=>null, createElement:tag=>element('created-'+tag)
};
global.window={
  addEventListener() {}, setTimeout() {}, scrollBy() {}, print() {}
};
global.location={hash:''};
Object.defineProperty(global,'navigator',{value:{clipboard:{
  writeText() {return clipboardPromise;}
}},configurable:true});
URL.createObjectURL=()=> 'blob:fictional';
URL.revokeObjectURL=()=>{};
require('./assets/task-brief.js');
const output=dom['brief-text'], cue=dom['brief-selection-cue'];
const status=dom['brief-copy-status'];
const initial='brief-text-help';
const active='brief-selection-cue brief-text-help';
assert.equal(cue.hidden,true);
assert.equal(output.getAttribute('aria-describedby'),initial);
for(const [key,value] of Object.entries({
  goal:'Fictional purpose',materials:'Generic notes',output:'Short note',
  review:'Check against notes',limits:'Do not invent details'
})) dom['brief-'+key].value=value;
dom['brief-build'].handlers.click();
assert.equal(output.getAttribute('aria-describedby'),initial);
assert.equal(dom['brief-result'].hidden,false);

function assertManualSelection(message) {
  assert.equal(cue.hidden,false);
  assert.equal(output.getAttribute('aria-describedby'),active);
  assert.equal(focused,'brief-text');
  // Description must be set BEFORE focus fires to be announced reliably.
  assert.equal(focusDescription,active);
  assert.equal(output.selectionStart,0);
  assert.equal(output.selectionEnd,output.value.length);
  assert.equal(output.scrollTop,0);
  assert.match(status.textContent,message);
}
function assertNoStaleCue() {
  assert.equal(cue.hidden,true);
  assert.equal(output.getAttribute('aria-describedby'),initial);
}
(async()=>{
  dom['brief-select'].handlers.click();
  assertManualSelection(/Complete text selected, but not copied/);
  await dom['brief-copy'].handlers.click();
  assertNoStaleCue();
  clipboardPromise=Promise.reject(Error('Permission denied'));
  await dom['brief-copy'].handlers.click();
  assertManualSelection(/Automatic copy is unavailable/);
  dom['brief-print'].handlers.click();
  assertNoStaleCue();
  window.print=()=>{throw Error('Unavailable');};
  dom['brief-print'].handlers.click();
  assertManualSelection(/Printing is unavailable/);
  dom['brief-download'].handlers.click();
  assertNoStaleCue();
  URL.createObjectURL=()=>{throw Error('Unavailable');};
  dom['brief-download'].handlers.click();
  assertManualSelection(/Download unavailable/);
  dom['brief-goal'].handlers.input();
  assertNoStaleCue();
  dom['brief-build'].handlers.click();
  assertNoStaleCue();
  console.log('Focus description and visible-copy transitions: PASS');
})().catch(err=>{console.error(err);process.exitCode=1;});
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_short_instruction_is_in_source_and_generated_markup(self):
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        for markup in (source, html):
            self.assertEqual(markup.count(COPY_CUE), 1)
            self.assertIn('id="brief-selection-cue" class="brief-selection-cue" hidden', markup)
            self.assertIn('id="brief-text" readonly rows="16" spellcheck="false" aria-describedby="brief-text-help"', markup)
        self.assertIn("output.setAttribute('aria-describedby', 'brief-selection-cue brief-text-help')", script)
        self.assertIn("output.setAttribute('aria-describedby', 'brief-text-help')", script)
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)


if __name__ == '__main__':
    unittest.main()
