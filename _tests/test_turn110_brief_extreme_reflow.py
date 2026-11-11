"""Task Brief at extreme reflow: usable viewport and safe selected-text focus."""

from hashlib import sha256
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExtremeReflowTests(unittest.TestCase):
    def test_only_the_extremely_narrow_task_brief_header_loses_stickiness(self):
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        extreme = css.split('@media (max-width: 240px) {', 1)[1].split('@media print {', 1)[0]
        self.assertIn('.page-task-brief .site-header { position: static; }', extreme)
        self.assertIn('html:has(.page-task-brief) { scroll-padding-top: 20px; }', extreme)
        self.assertIn('#brief-next-check, #brief-next-check-title, #how-it-works { scroll-margin-top: 0; }', extreme)
        self.assertIn('@media (max-width: 620px) {', css)
        self.assertIn('html { scroll-padding-top: 180px; }',
                      (ROOT / 'assets/site.css').read_text(encoding='utf-8'))
        # The normal navigation stays sticky above the extreme-reflow threshold.
        self.assertNotIn('.site-header { position: static; }', css.split('@media (max-width: 240px) {', 1)[0])

    def test_manual_selection_handles_a_header_scrolled_out_of_view(self):
        script = r'''
const assert=require('node:assert/strict');
let labelTop=-90, active=null;
const scrollCalls=[], dom={};
function el(id) {
  const attributes=new Map();
  return {
    id, textContent:'', value:'', hidden:true, handlers:{}, children:[],
    addEventListener(name,handler) {this.handlers[name]=handler;},
    removeAttribute(name) {attributes.delete(name);},
    setAttribute(name,value) {attributes.set(name,value);},
    getAttribute(name) {return attributes.get(name);},
    focus() {active=id;if(id==='brief-text')labelTop=-90;},
    select() {this.selectionStart=0;this.selectionEnd=this.value.length;this.scrollTop=888;},
    getBoundingClientRect() {return {top:id==='brief-text-label'?labelTop:labelTop+190};},
    replaceChildren() {this.children=[];},
    append(...children) {this.children.push(...children);},
    appendChild(child) {this.children.push(child);},
    remove() {}
  };
}
const names=['editor','result','text','text-label','selection-cue','status','copy-status',
 'confirm','preview','confirm-title','confirm-message','confirm-yes','confirm-no',
 'build','clear','copy','select','print','download','result-title','unavailable',
 'quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for(const f of fields)names.push(f,f+'-error');
for(const n of names)dom['brief-'+n]=el('brief-'+n);
global.document={
  getElementById:id=>dom[id],querySelectorAll:()=>[],
  querySelector:selector=>selector==='.site-header'?{
    getBoundingClientRect:()=>({bottom:-20})}:null,
  createElement:tag=>el('created-'+tag)
};
global.location={hash:''};
global.window={
  addEventListener() {},scrollBy(opts) {scrollCalls.push(opts);labelTop-=opts.top;}
};
Object.defineProperty(global,'navigator',{value:{clipboard:{}},configurable:true});
require('./assets/task-brief.js');
for(const [key,value] of Object.entries({
  goal:'Fictional task',materials:'Generic notes',output:'A short list',
  review:'Compare with the notes',limits:'Invent no facts'
}))dom['brief-'+key].value=value;
dom['brief-build'].handlers.click();
dom['brief-select'].handlers.click();
const output=dom['brief-text'];
assert.equal(active,'brief-text');
assert.equal(dom['brief-selection-cue'].hidden,false);
assert.equal(output.getAttribute('aria-describedby'),'brief-selection-cue brief-text-help');
assert.equal(output.selectionStart,0);
assert.equal(output.selectionEnd,output.value.length);
assert.equal(output.scrollTop,0);
assert.equal(labelTop,20);
assert.deepEqual(scrollCalls,[{top:-110,behavior:'instant'}]);
console.log('Static-header selected-text clearance: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_generated_html_uses_versioned_local_stylesheet(self):
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.css?v=' + sha256(css.encode()).hexdigest()[:12], html)
        self.assertIn('id="brief-selection-cue"', source)
        self.assertIn('id="brief-selection-cue"', html)
        self.assertIn('aria-describedby="brief-text-help"', html)
        self.assertNotIn('<script src="https://', html)


if __name__ == '__main__':
    unittest.main()
