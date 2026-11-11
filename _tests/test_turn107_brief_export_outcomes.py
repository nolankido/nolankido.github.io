"""Task Brief export feedback reflects the current action, not a stale result."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'assets/task-brief.js'
SOURCE = ROOT / '_source/technology/task-brief.html'
PAGE = ROOT / 'technology/task-brief/index.html'


class BriefExportOutcomeTests(unittest.TestCase):
    def test_real_handlers_keep_newer_export_feedback_and_state_what_is_done(self):
        script = r'''
const assert = require('node:assert/strict');
let focused = null, selected = 0, downloadClicks = 0, printCalls = 0;
function element(id) {
  return {
    id, value:'', textContent:'', hidden:true, handlers:{}, children:[],
    addEventListener(name, handler) {this.handlers[name]=handler;},
    focus() {focused=id;},
    select() {selected++; this.selectionStart=0; this.selectionEnd=this.value.length;},
    getBoundingClientRect() {return {top:230};},
    removeAttribute() {}, setAttribute() {}, remove() {},
    replaceChildren() {this.children=[];},
    appendChild(node) {this.children.push(node);},
    append(...items) {this.children.push(...items);},
    click() {downloadClicks++;}
  };
}
const names=['editor','result','text','status','copy-status','confirm','preview',
 'confirm-title','confirm-message','confirm-yes','confirm-no','build','clear',
 'copy','select','print','download','result-title','unavailable','quick-meeting'];
const fields=['goal','materials','output','review','limits'];
for (const name of fields) names.push(name,name+'-error');
const dom=Object.fromEntries(names.map(n=>['brief-'+n,element('brief-'+n)]));
global.document={
  getElementById:id=>dom[id], querySelectorAll:()=>[],
  querySelector:selector=>selector==='.site-header'?{
    getBoundingClientRect:()=>({bottom:153})}:null,
  createElement:tag=>element('created-'+tag)
};
global.window={
  addEventListener() {}, scrollBy() {}, setTimeout() {},
  print() {printCalls++;}
};
global.location={hash:''};
const calls=[];
let nextCopy;
Object.defineProperty(global,'navigator',{value:{clipboard:{
  writeText(text) {calls.push(text); return nextCopy.promise;}
}},configurable:true});
URL.createObjectURL=()=> 'blob:fictional-local-brief';
URL.revokeObjectURL=()=>{};
function deferred() {
  let resolve, reject;
  const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});
  return {promise,resolve,reject};
}
require('./assets/task-brief.js');
const values={goal:'A fictional meeting',materials:'Anonymized meeting notes',
 output:'One action list',review:'Check against source',limits:'No unsupported names'};
for (const [name,value] of Object.entries(values)) dom['brief-'+name].value=value;
dom['brief-build'].handlers.click();
const result=dom['brief-result'], text=dom['brief-text'], feedback=dom['brief-copy-status'];
assert.equal(result.hidden,false);
assert.ok(text.value.includes('A fictional meeting'));

(async()=>{
  // Only a resolved clipboard promise earns a confirmed-copy message.
  nextCopy=deferred();
  const copied=dom['brief-copy'].handlers.click();
  assert.equal(feedback.textContent,'');
  nextCopy.resolve(); await copied;
  assert.match(feedback.textContent,/Brief copied to the clipboard/);
  assert.equal(calls.at(-1),text.value);

  // New manual selection wins over a late successful clipboard response.
  nextCopy=deferred();
  const staleSuccess=dom['brief-copy'].handlers.click();
  dom['brief-select'].handlers.click();
  const manualMessage=feedback.textContent;
  assert.match(manualMessage,/selected, but not copied/);
  const manualSelected=selected;
  nextCopy.resolve(); await staleSuccess;
  assert.equal(feedback.textContent,manualMessage);
  assert.equal(selected,manualSelected);
  assert.equal(focused,'brief-text');
  assert.equal(text.selectionEnd,text.value.length);

  // Download is only requested, never described as a verified file save.
  nextCopy=deferred();
  const staleFailure=dom['brief-copy'].handlers.click();
  dom['brief-download'].handlers.click();
  assert.equal(downloadClicks,1);
  const downloadMessage=feedback.textContent;
  assert.match(downloadMessage,/Text download requested/);
  assert.match(downloadMessage,/confirm the file was saved/);
  const selectedBeforeReject=selected;
  nextCopy.reject(Error('Clipboard denied')); await staleFailure;
  assert.equal(feedback.textContent,downloadMessage);
  assert.equal(selected,selectedBeforeReject);

  // Rebuilding even the same output cancels old clipboard feedback.
  nextCopy=deferred();
  const staleRebuild=dom['brief-copy'].handlers.click();
  dom['brief-build'].handlers.click();
  assert.equal(feedback.textContent,'');
  nextCopy.resolve(); await staleRebuild;
  assert.equal(feedback.textContent,'');

  // Editing while the clipboard is pending never selects an obsolete brief.
  nextCopy=deferred();
  const staleEdit=dom['brief-copy'].handlers.click();
  dom['brief-goal'].value='A different fictional task';
  dom['brief-goal'].handlers.input();
  const selectedBeforeEditReject=selected;
  nextCopy.reject(Error('Clipboard denied')); await staleEdit;
  assert.equal(result.hidden,true);
  assert.equal(feedback.textContent,'');
  assert.equal(selected,selectedBeforeEditReject);

  dom['brief-build'].handlers.click();
  nextCopy=deferred();
  const failedCopy=dom['brief-copy'].handlers.click();
  nextCopy.reject(Error('Clipboard denied')); await failedCopy;
  assert.match(feedback.textContent,/Automatic copy is unavailable/);
  assert.match(feedback.textContent,/selected, not copied/);
  assert.equal(text.selectionEnd,text.value.length);

  dom['brief-print'].handlers.click();
  assert.equal(printCalls,1);
  assert.match(feedback.textContent,/Print requested/);
  assert.match(feedback.textContent,/confirm the result yourself/);
  window.print=()=>{throw Error('Printer unavailable');};
  dom['brief-print'].handlers.click();
  assert.match(feedback.textContent,/Printing is unavailable/);
  assert.match(feedback.textContent,/selected, not copied/);

  URL.createObjectURL=()=>{throw Error('Download unavailable');};
  dom['brief-download'].handlers.click();
  assert.match(feedback.textContent,/Download unavailable/);
  assert.match(feedback.textContent,/selected, not copied or saved/);
  assert.equal(text.selectionEnd,text.value.length);
  assert.equal(calls.length,6);
  console.log('Export outcomes and stale-clipboard races: PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        proc = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_export_help_explains_selection_and_unconfirmed_requests(self):
        source = SOURCE.read_text(encoding='utf-8')
        page = PAGE.read_text(encoding='utf-8')
        for expected in (
            'Selecting text does not copy it',
            'check your browser’s downloads to confirm the file exists',
            'cannot confirm printing or saving',
            'role="status" aria-live="polite" aria-atomic="true"',
        ):
            self.assertIn(expected, source)
            self.assertIn(expected, page)

    def test_changed_script_is_versioned_without_advancing_content_date(self):
        script = SCRIPT.read_text(encoding='utf-8')
        page = PAGE.read_text(encoding='utf-8')
        fingerprint = sha256(SCRIPT.read_bytes()).hexdigest()[:12]
        self.assertIn('task-brief.js?v=' + fingerprint, page)
        self.assertIn('attempt === exportAttempt', script)
        self.assertIn('attempt !== exportAttempt', script)
        self.assertEqual(script.count('exportAttempt++;') + script.count('++exportAttempt'), 6)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(item for item in pages if item.get('id') == 'task-brief')
        self.assertGreaterEqual(brief['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
