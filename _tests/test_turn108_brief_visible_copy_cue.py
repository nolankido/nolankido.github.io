"""The manual-copy cue stays visible with selected text below mobile navigation."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class VisibleCopyCueTests(unittest.TestCase):
    def test_actual_export_handlers_keep_cue_and_label_visible_only_when_needed(self):
        script = r'''
const assert=require('node:assert/strict');
let labelTop=-77, focused=null, selections=0, downloads=0, printCalls=0;
const pageScrolls=[];
function el(id) {
  return {
    id, value:'', textContent:'', hidden:true, handlers:{}, children:[],
    addEventListener(name,handler) {this.handlers[name]=handler;},
    focus() {focused=id; if(id==='brief-text') labelTop=-77;},
    select() {
      selections++; this.selectionStart=0; this.selectionEnd=this.value.length;
      this.scrollTop=900;
    },
    getBoundingClientRect() {return {top:id==='brief-text-label'?labelTop:
      id==='brief-text'?labelTop+(dom['brief-selection-cue'].hidden?28:112):0};},
    removeAttribute() {}, setAttribute() {}, remove() {},
    replaceChildren() {this.children=[];},
    appendChild(child) {this.children.push(child);},
    append(...children) {this.children.push(...children);},
    click() {downloads++;}
  };
}
const names=['editor','result','text','text-label','selection-cue',
 'status','copy-status','confirm','preview','confirm-title','confirm-message',
 'confirm-yes','confirm-no','build','clear','copy','select','print','download',
 'result-title','unavailable','quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for(const f of fields)names.push(f,f+'-error');
const dom=Object.fromEntries(names.map(n=>['brief-'+n,el('brief-'+n)]));
const cue=dom['brief-selection-cue'];
const output=dom['brief-text'];
const status=dom['brief-copy-status'];
global.document={
  getElementById:id=>dom[id], querySelectorAll:()=>[],
  querySelector:selector=>selector==='.site-header'?{
    getBoundingClientRect:()=>({bottom:153})}:null,
  createElement:tag=>el('created-'+tag)
};
global.window={
  addEventListener() {}, setTimeout() {},
  scrollBy(options) {pageScrolls.push(options);labelTop-=options.top;},
  print() {printCalls++;}
};
global.location={hash:''};
let clipboardPromise=Promise.resolve();
Object.defineProperty(global,'navigator',{value:{clipboard:{
  writeText() {return clipboardPromise;}
}},configurable:true});
URL.createObjectURL=()=> 'blob:fictional'; URL.revokeObjectURL=()=>{};
require('./assets/task-brief.js');
const values={goal:'Fictional purpose',materials:'Anonymized notes',
 output:'Concise list',review:'Check against notes',limits:'No invention'};
for(const [k,v] of Object.entries(values)) dom['brief-'+k].value=v;
dom['brief-build'].handlers.click();
assert.equal(cue.hidden,true);

function checkSelected(message) {
  assert.equal(cue.hidden,false);
  assert.equal(focused,'brief-text');
  assert.equal(output.selectionStart,0);
  assert.equal(output.selectionEnd,output.value.length);
  assert.equal(output.scrollTop,0);
  assert.equal(labelTop,173); // Header bottom 153 plus 20px clearance.
  assert.ok(output.getBoundingClientRect().top>labelTop);
  assert.match(status.textContent,message);
}
(async()=>{
  dom['brief-select'].handlers.click();
  checkSelected(/Complete text selected, but not copied/);
  assert.deepEqual(pageScrolls.at(-1),{top:-250,behavior:'instant'});

  // A successful copy hides the cue rather than leaving stale instructions.
  await dom['brief-copy'].handlers.click();
  assert.equal(cue.hidden,true);
  assert.match(status.textContent,/Brief copied to the clipboard/);

  // Clipboard rejection returns to visible manual selection.
  clipboardPromise=Promise.reject(Error('Denied'));
  await dom['brief-copy'].handlers.click();
  checkSelected(/Automatic copy is unavailable/);

  // Print and download requests hide the manual-only cue.
  dom['brief-print'].handlers.click();
  assert.equal(cue.hidden,true);
  assert.equal(printCalls,1);
  dom['brief-download'].handlers.click();
  assert.equal(cue.hidden,true);
  assert.equal(downloads,1);

  window.print=()=>{throw Error('Unavailable');};
  dom['brief-print'].handlers.click();
  checkSelected(/Printing is unavailable/);
  URL.createObjectURL=()=>{throw Error('Unavailable');};
  dom['brief-download'].handlers.click();
  checkSelected(/Download unavailable/);

  // Edits and a fresh assembly remove a no-longer-applicable cue.
  dom['brief-goal'].value='Revised fictional purpose';
  dom['brief-goal'].handlers.input();
  assert.equal(cue.hidden,true);
  dom['brief-build'].handlers.click();
  assert.equal(cue.hidden,true);
  assert.equal(dom['brief-result'].hidden,false);
  console.log('Visible copy cue and action transitions: PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        result = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_cue_is_hidden_by_default_and_only_the_site_builder_owns_markup(self):
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        public = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        for html in (source, public):
            self.assertIn('id="brief-text-label" for="brief-text"', html)
            self.assertIn('id="brief-selection-cue" class="brief-selection-cue" hidden', html)
            self.assertIn('Selected, not copied. Press Ctrl+C or Command+C; on touch, choose Copy.', html)
            self.assertEqual(html.count('id="brief-selection-cue"'), 1)
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        self.assertIn('.brief-selection-cue {', css)
        self.assertIn('.page-task-brief [hidden] { display: none !important; }', css)

    def test_cue_uses_versioned_assets_without_new_data_channels_or_date(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        self.assertIn('task-brief.css?v=' + sha256(css.encode()).hexdigest()[:12], html)
        self.assertIn('const anchor = label', script)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertGreaterEqual(brief['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
