"""The manual-copy UI must not mistake a changed selection for a full brief."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PartialSelectionTests(unittest.TestCase):
    def test_mouse_keyboard_copy_and_reselect_produce_truthful_messages(self):
        script = r'''
const assert=require('node:assert/strict');
const dom={};
let focused=null, clipboardWrites=0, eventPrevented=false;
function el(id) {
  const attrs=new Map(id==='brief-text'?[['aria-describedby','brief-text-help']]:[]);
  return {
    id,value:'',textContent:'',hidden:true,children:[],handlers:{},
    addEventListener(name,fn) {this.handlers[name]=fn;},
    setAttribute(name,value) {attrs.set(name,value);},
    getAttribute(name) {return attrs.get(name);},
    removeAttribute(name) {attrs.delete(name);},
    focus() {focused=id;},
    select() {
      this.selectionStart=0;this.selectionEnd=this.value.length;this.scrollTop=800;
      if(this.handlers.select)this.handlers.select();
    },
    getBoundingClientRect() {return {top:210,bottom:290};},
    append(...items) {this.children.push(...items);},
    appendChild(item) {this.children.push(item);},
    replaceChildren() {this.children=[];},
    click() {},remove() {}
  };
}
const names=['editor','result','text','text-label','selection-cue','status',
  'copy-status','confirm','preview','confirm-title','confirm-message',
  'confirm-yes','confirm-no','build','clear','copy','select','print','download',
  'result-title','unavailable','quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for(const f of fields)names.push(f,f+'-error');
for(const n of names)dom['brief-'+n]=el('brief-'+n);
global.document={
  getElementById:id=>dom[id],querySelectorAll:()=>[],querySelector:()=>null,
  createElement:tag=>el('created-'+tag)
};
global.window={addEventListener() {},setTimeout() {},scrollBy() {},print() {}};
global.location={hash:''};
Object.defineProperty(global,'navigator',{value:{clipboard:{
  writeText(){clipboardWrites++;return Promise.resolve();}
}},configurable:true});
URL.createObjectURL=()=> 'blob:fictional';
URL.revokeObjectURL=()=>{};
require('./assets/task-brief.js');
const output=dom['brief-text'],cue=dom['brief-selection-cue'];
const feedback=dom['brief-copy-status'];
const selected='Selected, not copied. Press Ctrl+C or Command+C; on touch, choose Copy.';
const partial='Full brief no longer selected. Choose Select text manually again.';
const copyAttempt='Copy command detected. Paste to check the result.';
const nativeCopy={preventDefault(){eventPrevented=true;}};
for(const [key,value] of Object.entries({
  goal:'Fictional goal',materials:'Generic notes',output:'A short summary',
  review:'Compare with supplied notes',limits:'Invent no facts'
}))dom['brief-'+key].value=value;
dom['brief-build'].handlers.click();
dom['brief-select'].handlers.click();
assert.equal(focused,'brief-text');
assert.equal(cue.textContent,selected);
assert.equal(output.selectionStart,0);
assert.equal(output.selectionEnd,output.value.length);

// Keyboard arrow or selection handle removes the complete range.
output.selectionStart=4;
output.handlers.keyup();
assert.equal(cue.textContent,partial);
assert.match(feedback.textContent,/complete brief is no longer selected/);
const firstWarning=feedback.textContent;
output.selectionStart=9;
output.handlers.keyup();
assert.equal(feedback.textContent,firstWarning); // No repeated live announcement.

// A native Copy with only part selected still copies normally, but warns.
output.handlers.copy(nativeCopy);
assert.equal(cue.textContent,partial);
assert.match(feedback.textContent,/Copy command detected with only part/);
assert.match(feedback.textContent,/Re-select the full text/);
assert.equal(eventPrevented,false);
assert.equal(clipboardWrites,0);

// Ctrl+A in the text field restores a full selection and resets the warning.
output.selectionStart=0;
output.selectionEnd=output.value.length;
output.handlers.select();
assert.equal(cue.textContent,selected);
assert.match(feedback.textContent,/Complete text selected, not copied/);
output.handlers.copy(nativeCopy);
assert.equal(cue.textContent,copyAttempt);
assert.match(feedback.textContent,/cannot confirm clipboard contents/);
assert.equal(eventPrevented,false);

// A pointer-adjusted selection becomes partial even after a Copy attempt.
output.selectionEnd=output.value.length-2;
output.handlers.pointerup();
assert.equal(cue.textContent,partial);
assert.match(feedback.textContent,/complete brief is no longer selected/);

// Explicit reselect restores the full range and cue; rebuilding hides it.
dom['brief-select'].handlers.click();
assert.equal(cue.textContent,selected);
assert.equal(output.selectionStart,0);
assert.equal(output.selectionEnd,output.value.length);
dom['brief-build'].handlers.click();
assert.equal(cue.hidden,true);
assert.equal(cue.textContent,selected);
assert.equal(feedback.textContent,'');
output.selectionEnd=1;
output.handlers.keyup();
output.handlers.copy(nativeCopy);
assert.equal(cue.hidden,true);
assert.equal(feedback.textContent,'');
assert.equal(output.getAttribute('aria-describedby'),'brief-text-help');
console.log('Manual full/partial selection transitions: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_generated_script_keeps_local_only_copy_and_fingerprints(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        self.assertIn("['select', 'keyup', 'pointerup']", script)
        self.assertIn("output.addEventListener('copy', () => {", script)
        for forbidden in ('preventDefault(', 'navigator.clipboard.readText(', 'execCommand(',
                          'fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)


if __name__ == '__main__':
    unittest.main()
