"""Short mobile viewports show export actions and selected text together."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BriefShortViewportTests(unittest.TestCase):
    def test_selection_scroll_reveals_text_without_hiding_first_export_action(self):
        script = r'''
const assert=require('node:assert/strict');
const fs=require('node:fs');
const src=fs.readFileSync('assets/task-brief.js','utf8');
const start=src.indexOf('  function selectVisibleText(message) {');
const end=src.indexOf("  get('copy').addEventListener",start);
assert.ok(start>0 && end>start);
const factory=new Function('output','copyStatus','document','window','SELECTED_CUE',
  src.slice(start,end)+'\nreturn selectVisibleText;');
const cue={hidden:true,textContent:''};
const alternatives={hidden:false};
const save={hidden:false,getBoundingClientRect:()=>({top:labelTop+210})};
const print={hidden:false,getBoundingClientRect:()=>({top:labelTop+270})};
const label={getBoundingClientRect:()=>({top:labelTop})};
let labelTop=-80, selections=0, focusCount=0;
const scrolls=[];
const output={
  value:'PURPOSE\n'+'Fictional text and a check. '.repeat(60),
  focus(){focusCount++;labelTop=-80;},
  select(){selections++;this.selectionStart=0;this.selectionEnd=this.value.length;this.scrollTop=600;},
  setAttribute(name,value){this[name]=value;},
  getBoundingClientRect(){return {top:labelTop+445};}
};
const feedback={textContent:''};
const elements={
  'brief-selection-cue':cue,'brief-export-alternatives':alternatives,
  'brief-save-alternative':save,'brief-print-alternative':print,
  'brief-text-label':label
};
const document={
  getElementById:id=>elements[id]??null,
  querySelector:q=>q==='.site-header'?{getBoundingClientRect:()=>({bottom:153})}:null
};
const window={
  innerHeight:568,
  scrollBy(options){scrolls.push(options);labelTop-=options.top;}
};
const SELECTED_CUE='Selected, not copied. Press Ctrl+C or Command+C; on touch, choose Copy.';
const selectVisibleText=factory(output,feedback,document,window,SELECTED_CUE);
selectVisibleText('Selected, not copied.');
assert.equal(scrolls.length,2,JSON.stringify(scrolls));
assert.deepEqual(scrolls[0],{top:-253,behavior:'instant'});
assert.ok(scrolls[1].top>0,'must correct the short-viewport text clipping');
assert.ok(output.getBoundingClientRect().top<568-80,'opening text remains visible');
assert.ok(save.getBoundingClientRect().top>=165,'first export action remains below header');
assert.equal(output.selectionStart,0);
assert.equal(output.selectionEnd,output.value.length);
assert.equal(output.scrollTop,0);
assert.equal(focusCount,1);
assert.equal(selections,1);
assert.equal(cue.hidden,false);
assert.equal(output['aria-describedby'],'brief-selection-cue brief-text-help');

// Tall screens must preserve the existing label-first handoff, not jump down.
scrolls.length=0;
window.innerHeight=900;
selectVisibleText('Selected again.');
assert.equal(scrolls.length,1);
assert.equal(labelTop,173);
assert.equal(output.getBoundingClientRect().top,618);

// When text becomes extremely tall at higher zoom, never hide the only
// surviving export button underneath a sticky mobile header.
scrolls.length=0;
window.innerHeight=568;
save.hidden=true; // A download failed and only Print remains available.
selectVisibleText('Print remains.');
assert.equal(scrolls.length,2);
assert.ok(print.getBoundingClientRect().top>=165);
assert.equal(output.selectionEnd,output.value.length);
console.log('Short viewport selection and export visibility: PASS');
'''
        result = subprocess.run(
            ['node', '-e', script], cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_compact_buttons_remain_accessible_with_unchanged_export_contract(self):
        source = (ROOT / '_source/technology/task-brief.html').read_text(encoding='utf-8')
        public = (ROOT / 'technology/task-brief/index.html').read_text(encoding='utf-8')
        for html in (source, public):
            self.assertIn('id="brief-export-alternatives" class="brief-export-alternatives" role="group"', html)
            self.assertIn('id="brief-save-alternative" aria-label="Save full brief as .txt">Save .txt</button>', html)
            self.assertIn('id="brief-print-alternative" aria-label="Print / Save as PDF">Print / PDF</button>', html)
            self.assertIn('Check the download or PDF before leaving. A request does not confirm a save.', html)
        css = (ROOT / 'assets/task-brief.css').read_text(encoding='utf-8')
        self.assertIn('.brief-fallback-actions button { padding: 8px 10px; font-size: .88rem; }', css)
        self.assertIn('.page-task-brief button { cursor: pointer; padding: 12px 18px; min-height: 44px;', css)
        self.assertIn('overflow-wrap: anywhere;', css)
        script = (ROOT / 'assets/task-brief.js').read_text(encoding='utf-8')
        self.assertIn('const needed = textTop - (window.innerHeight - minText);', script)
        self.assertIn('const available = actionTop - (inset + 12);', script)
        self.assertIn('window.scrollBy({top: shift, behavior: \'instant\'});', script)
        self.assertIn('task-brief.js?v=' + sha256(script.encode()).hexdigest()[:12], public)
        self.assertIn('task-brief.css?v=' + sha256(css.encode()).hexdigest()[:12], public)
        for forbidden in ('fetch(', 'sendBeacon', 'localStorage', 'sessionStorage',
                          'innerHTML', 'preventDefault(', 'execCommand('):
            self.assertNotIn(forbidden, script)
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        entry = next(page for page in pages if page.get('id') == 'task-brief')
        self.assertGreaterEqual(entry['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
