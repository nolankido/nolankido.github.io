"""The Task Brief selection stays complete while the textarea opens at line one."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'assets/task-brief.js'


class TaskBriefSelectionStartTests(unittest.TestCase):
    def test_real_selection_helper_opens_at_start_without_collapsing_selection(self):
        script = r'''
const assert=require('node:assert/strict');
const fs=require('node:fs');
const src=fs.readFileSync('assets/task-brief.js','utf8');
const start=src.indexOf('  function selectVisibleText(message) {');
const end=src.indexOf("  get('copy').addEventListener",start);
assert.ok(start>0 && end>start);
const factory=new Function('output','copyStatus','document','window',
  src.slice(start,end)+'\nreturn selectVisibleText;');
const events=[];
let innerScroll=0;
let rectTop=43;
const output={
  value:'PURPOSE\n'+'A deliberately long fictional brief. '.repeat(50),
  focus() {events.push('focus'); this.focused=true;},
  select() {
    events.push('select'); this.selectionStart=0;
    this.selectionEnd=this.value.length;
    this.scrollTop=1265; // Native behavior observed at 320px.
  },
  getBoundingClientRect() {return {top:rectTop};}
};
Object.defineProperty(output,'scrollTop',{
  get() {return innerScroll;},
  set(value) {innerScroll=value; events.push('inner:'+value);}
});
const copyStatus={textContent:''};
const document={querySelector:selector=>selector==='.site-header'?
  {getBoundingClientRect:()=>({bottom:153})}:null};
const window={scrollBy:options=>{
  events.push('page-scroll');
  assert.deepEqual(options,{top:-130,behavior:'instant'});
  rectTop-=options.top;
}};
const selectVisibleText=factory(output,copyStatus,document,window);
selectVisibleText('Selected; use your device Copy command.');
assert.equal(output.focused,true);
assert.equal(output.selectionStart,0);
assert.equal(output.selectionEnd,output.value.length);
assert.equal(output.scrollTop,0);
assert.equal(rectTop,173);
assert.equal(copyStatus.textContent,'Selected; use your device Copy command.');
assert.ok(events.indexOf('inner:0')>events.indexOf('select'));
assert.ok(events.indexOf('page-scroll')>events.indexOf('inner:0'));

// A second selection that is already below the header still opens at line one.
rectTop=240;
const priorPageScrolls=events.filter(e=>e==='page-scroll').length;
selectVisibleText('Selected again.');
assert.equal(output.scrollTop,0);
assert.equal(output.selectionEnd,output.value.length);
assert.equal(events.filter(e=>e==='page-scroll').length,priorPageScrolls);

// Missing page geometry or scroll APIs must not prevent text selection.
delete output.getBoundingClientRect;
delete window.scrollBy;
selectVisibleText('Fallback selected.');
assert.equal(output.scrollTop,0);
assert.equal(output.selectionStart,0);
assert.equal(output.selectionEnd,output.value.length);
console.log('Selection opens at start: PASS');
'''
        proc = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_reset_is_only_after_explicit_selection_and_keeps_data_local(self):
        script = SCRIPT.read_text(encoding='utf-8')
        start = script.index('function selectVisibleText(message) {')
        end = script.index("get('copy').addEventListener", start)
        helper = script[start:end]
        self.assertEqual(script.count('output.scrollTop = 0;'), 1)
        self.assertLess(helper.index('output.focus(); output.select();'), helper.index('output.scrollTop = 0;'))
        self.assertLess(helper.index('output.scrollTop = 0;'), helper.index("window.scrollBy({top:"))
        self.assertEqual(script.count('selectVisibleText('), 5)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML'):
            self.assertNotIn(forbidden, script)

    def test_generated_fingerprint_and_article_date_are_stable(self):
        fingerprint = sha256(SCRIPT.read_bytes()).hexdigest()[:12]
        page = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        self.assertIn('task-brief.js?v=' + fingerprint, page)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        brief = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertEqual(brief['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
