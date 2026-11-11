"""Nearby full-brief exports remain usable when clipboard or selection fails."""

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExportAlternativesTests(unittest.TestCase):
    def test_actual_handlers_offer_and_reset_independent_export_routes(self):
        script = r'''
const assert=require('node:assert/strict');
const dom={};
let downloads=0, prints=0, clipboardWrites=0, exportedBlob=null;
function el(id) {
  return {
    id,value:'',textContent:'',hidden:true,children:[],handlers:{},
    addEventListener(name,handler) {this.handlers[name]=handler;},
    focus() {},
    select() {this.selectionStart=0;this.selectionEnd=this.value.length;},
    getBoundingClientRect() {return {top:250,bottom:300};},
    setAttribute() {},removeAttribute() {},remove() {},
    replaceChildren() {this.children=[];},
    append(...items) {this.children.push(...items);},
    appendChild(item) {this.children.push(item);},
    click() {downloads++;}
  };
}
const names=['editor','result','text','text-label','selection-cue',
  'export-alternatives','save-alternative','print-alternative',
  'status','copy-status','confirm','preview','confirm-title','confirm-message',
  'confirm-yes','confirm-no','build','clear','copy','select','print','download',
  'result-title','unavailable','quick-meeting'];
for(const key of ['goal','materials','output','review','limits']) names.push(key,key+'-error');
for(const name of names) dom['brief-'+name]=el('brief-'+name);
global.document={
  getElementById:id=>dom[id],querySelectorAll:()=>[],
  querySelector:()=>null,createElement:tag=>el('created-'+tag)
};
global.window={addEventListener() {},scrollBy() {},setTimeout() {},print() {prints++;}};
global.location={hash:''};
let copyMode='resolve';
Object.defineProperty(global,'navigator',{configurable:true,value:{clipboard:{
  writeText() {
    clipboardWrites++;
    return copyMode==='resolve'?Promise.resolve():Promise.reject(Error('Denied'));
  }
}}});
URL.createObjectURL=blob=>{exportedBlob=blob;return 'blob:fictional';};
URL.revokeObjectURL=()=>{};
require('./assets/task-brief.js');
const d=name=>dom['brief-'+name];
for(const [key,value] of Object.entries({goal:'Fictional goal',
  materials:'Anonymized public notes',output:'A short draft',
  review:'Check against the notes',limits:'Do not invent facts'})) d(key).value=value;
d('build').handlers.click();
assert.equal(d('result').hidden,false);
assert.equal(d('export-alternatives').hidden,true);
assert.equal(d('save-alternative').hidden,true); // Mock default, reset on reveal.

(async()=>{
  // A confirmed clipboard write does not display unnecessary alternatives.
  await d('copy').handlers.click();
  assert.equal(d('export-alternatives').hidden,true);
  assert.match(d('copy-status').textContent,/Brief copied to the clipboard/);

  // Clipboard rejection selects the full brief and puts usable actions nearby.
  copyMode='reject';
  await d('copy').handlers.click();
  assert.equal(d('export-alternatives').hidden,false);
  assert.equal(d('save-alternative').hidden,false);
  assert.equal(d('print-alternative').hidden,false);
  assert.equal(d('text').selectionStart,0);
  assert.equal(d('text').selectionEnd,d('text').value.length);
  assert.match(d('copy-status').textContent,/Automatic copy is unavailable/);
  assert.match(d('copy-status').textContent,/Save full brief as .txt/);
  assert.equal(downloads,0); // A clipboard failure never starts another export.
  assert.equal(prints,0);

  // The nearby Save action exports the complete brief without clipboard access.
  d('save-alternative').handlers.click();
  assert.equal(downloads,1);
  assert.equal(d('export-alternatives').hidden,true);
  assert.equal(await exportedBlob.text(),d('text').value);
  assert.match(d('copy-status').textContent,/Text download requested/);
  assert.match(d('copy-status').textContent,/confirm the file was saved/);
  assert.doesNotMatch(d('copy-status').textContent,/Successfully saved|Brief saved/);

  // Manual selection also makes the independent actions available.
  d('select').handlers.click();
  assert.equal(d('export-alternatives').hidden,false);
  assert.equal(d('save-alternative').hidden,false);
  assert.equal(d('print-alternative').hidden,false);
  d('print-alternative').handlers.click();
  assert.equal(prints,1);
  assert.equal(d('export-alternatives').hidden,true);
  assert.match(d('copy-status').textContent,/Print requested/);

  // If printing fails, do not offer the failing action again in the panel.
  window.print=()=>{throw Error('Unusable print dialog');};
  d('select').handlers.click();
  d('print-alternative').handlers.click();
  assert.equal(d('export-alternatives').hidden,false);
  assert.equal(d('print-alternative').hidden,true);
  assert.equal(d('save-alternative').hidden,false);
  assert.match(d('copy-status').textContent,/Printing is unavailable/);

  // If saving fails, point to Print instead, with no false save confirmation.
  URL.createObjectURL=()=>{throw Error('Blocked download');};
  d('save-alternative').handlers.click();
  assert.equal(d('export-alternatives').hidden,false);
  assert.equal(d('save-alternative').hidden,true);
  assert.equal(d('print-alternative').hidden,false);
  assert.match(d('copy-status').textContent,/Download unavailable/);
  assert.match(d('copy-status').textContent,/not copied or saved/);

  // Changing the draft removes stale controls and prevents old exports.
  d('goal').value='Different fictional goal';
  d('goal').handlers.input();
  assert.equal(d('result').hidden,true);
  assert.equal(d('export-alternatives').hidden,true);
  const count=downloads;
  d('save-alternative').handlers.click();
  assert.equal(downloads,count);
  assert.equal(clipboardWrites,2);
  console.log('Contextual Save/Print actions, failures and reset: PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_source_and_generated_page_keep_accessible_nearby_actions(self):
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        public = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        for html in (source, public):
            self.assertEqual(html.count('id="brief-export-alternatives"'), 1)
            self.assertIn('id="brief-export-alternatives" class="brief-export-alternatives" role="group" aria-labelledby="brief-export-alternatives-title" hidden', html)
            self.assertIn('id="brief-save-alternative"', html)
            self.assertIn('id="brief-print-alternative"', html)
            self.assertIn('without the clipboard', html)
            self.assertIn('A request does not confirm a save.', html)
            self.assertLess(html.index('id="brief-selection-cue"'), html.index('id="brief-export-alternatives"'))
            self.assertLess(html.index('id="brief-export-alternatives"'), html.index('id="brief-text" readonly'))
            self.assertEqual(len(re.findall(r'id="brief-save-alternative"', html)), 1)
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        self.assertIn('.brief-export-alternatives {', css)
        self.assertIn('.brief-fallback-actions {', css)
        self.assertIn('.page-task-brief [hidden] { display: none !important; }', css)

    def test_no_new_transport_or_publication_date_change(self):
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        html = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], html)
        self.assertIn('task-brief.css?v=' + sha256(css.encode()).hexdigest()[:12], html)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage',
                          'innerHTML', 'preventDefault(', 'execCommand('):
            self.assertNotIn(forbidden, script)
        self.assertIn("get('print-alternative')?.addEventListener('click', printBrief)", script)
        self.assertIn("get('save-alternative')?.addEventListener('click', downloadBrief)", script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(item for item in pages if item.get('id') == 'task-brief')
        self.assertEqual(brief['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
