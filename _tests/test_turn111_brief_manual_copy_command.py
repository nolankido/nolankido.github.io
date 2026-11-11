"""A native Copy attempt updates the manual cue without claiming success."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ManualCopyCommandTests(unittest.TestCase):
    def test_copy_event_feedback_is_truthful_and_resets_without_interception(self):
        script = r'''
const assert=require('node:assert/strict');
let focused=null, clipboardCalls=0, printCalls=0, downloadClicks=0;
const dom={};
function element(id) {
  const attrs=new Map(id==='brief-text'?[['aria-describedby','brief-text-help']]:[]);
  return {
    id,value:'',textContent:'',hidden:true,children:[],handlers:{},
    addEventListener(name,handler) {this.handlers[name]=handler;},
    setAttribute(name,value) {attrs.set(name,value);},
    getAttribute(name) {return attrs.get(name)??null;},
    removeAttribute(name) {attrs.delete(name);},
    focus() {focused=id;},
    select() {this.selectionStart=0;this.selectionEnd=this.value.length;this.scrollTop=999;},
    getBoundingClientRect() {return {top:220,bottom:300};},
    replaceChildren() {this.children=[];},
    append(...children) {this.children.push(...children);},
    appendChild(child) {this.children.push(child);},
    click() {downloadClicks++;},
    remove() {}
  };
}
const names=['editor','result','text','text-label','selection-cue','status','copy-status',
  'confirm','preview','confirm-title','confirm-message','confirm-yes','confirm-no',
  'build','clear','copy','select','print','download','result-title','unavailable',
  'quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for(const name of fields)names.push(name,name+'-error');
for(const name of names)dom['brief-'+name]=element('brief-'+name);
global.document={
  getElementById:id=>dom[id],querySelectorAll:()=>[],
  querySelector:()=>null,createElement:tag=>element('created-'+tag)
};
global.window={addEventListener() {},setTimeout() {},scrollBy() {},
  print() {printCalls++;}
};
global.location={hash:''};
Object.defineProperty(global,'navigator',{value:{clipboard:{
  writeText() {clipboardCalls++;return Promise.resolve();}
}},configurable:true});
URL.createObjectURL=()=> 'blob:fictional';
URL.revokeObjectURL=()=>{};
require('./assets/task-brief.js');
const output=dom['brief-text'],cue=dom['brief-selection-cue'];
const feedback=dom['brief-copy-status'], selectedCue='Selected, not copied. Use your device’s Copy command.';
const attemptedCue='Copy command detected. Paste to check the result.';
for(const [key,value] of Object.entries({
  goal:'Fictional purpose',materials:'Generic notes',output:'Short summary',
  review:'Check against notes',limits:'Do not invent facts'
}))dom['brief-'+key].value=value;
dom['brief-build'].handlers.click();
assert.equal(cue.hidden,true);
assert.equal(cue.textContent,selectedCue);
assert.equal(typeof output.handlers.copy,'function');
const event={preventDefault(){throw Error('Native copy must not be prevented');}};

(async()=>{
  // No manual selection: copy on the read-only field must not invent an outcome.
  output.handlers.copy(event);
  assert.equal(feedback.textContent,'');
  assert.equal(cue.hidden,true);

  dom['brief-select'].handlers.click();
  assert.equal(cue.hidden,false);
  assert.equal(cue.textContent,selectedCue);
  assert.equal(focused,'brief-text');
  assert.equal(output.selectionStart,0);
  assert.equal(output.selectionEnd,output.value.length);
  assert.equal(output.scrollTop,0);
  output.handlers.copy(event);
  assert.equal(cue.textContent,attemptedCue);
  assert.match(feedback.textContent,/Copy command detected, but this page cannot confirm/);
  assert.match(feedback.textContent,/Paste to verify/);
  assert.doesNotMatch(feedback.textContent,/Brief copied to the clipboard/);
  assert.equal(clipboardCalls,0); // Native handler did not call the clipboard API.
  assert.equal(output.getAttribute('aria-describedby'),'brief-selection-cue brief-text-help');

  // A new Select action must restore the instruction for another attempt.
  dom['brief-select'].handlers.click();
  assert.equal(cue.textContent,selectedCue);
  output.selectionEnd=output.value.length-1;
  output.handlers.copy(event);
  assert.match(cue.textContent,/Full brief no longer selected/);
  assert.match(feedback.textContent,/Copy command detected with only part/);

  // Successful automatic copy has separate, stronger evidence.
  await dom['brief-copy'].handlers.click();
  assert.equal(cue.hidden,true);
  assert.equal(cue.textContent,selectedCue);
  assert.equal(output.getAttribute('aria-describedby'),'brief-text-help');
  assert.match(feedback.textContent,/Brief copied to the clipboard/);
  assert.equal(clipboardCalls,1);
  output.selectionEnd=output.value.length;
  output.handlers.copy(event); // A hidden cue must not overwrite copy success.
  assert.match(feedback.textContent,/Brief copied to the clipboard/);

  dom['brief-select'].handlers.click();
  output.handlers.copy(event);
  dom['brief-print'].handlers.click();
  assert.equal(cue.hidden,true);
  assert.equal(cue.textContent,selectedCue);
  assert.equal(printCalls,1);
  dom['brief-download'].handlers.click();
  assert.equal(downloadClicks,1);
  assert.equal(cue.hidden,true);

  dom['brief-select'].handlers.click();
  output.handlers.copy(event);
  dom['brief-goal'].handlers.input();
  assert.equal(dom['brief-result'].hidden,true);
  assert.equal(cue.hidden,true);
  assert.equal(cue.textContent,selectedCue);
  assert.equal(feedback.textContent,'');
  console.log('Native copy attempt and state reset: PASS');
})().catch(err=>{console.error(err);process.exitCode=1;});
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_static_instruction_and_versioned_script_remain_aligned(self):
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        self.assertIn('Selected, not copied. Use your device’s Copy command.', source)
        self.assertIn('id="brief-selection-cue" class="brief-selection-cue" hidden', html)
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        self.assertIn("output.addEventListener('copy', () => {", script)
        for forbidden in ('preventDefault(', 'execCommand(', 'navigator.clipboard.readText(',
                          'fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)


if __name__ == '__main__':
    unittest.main()
