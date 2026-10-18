"""Independent review of Turn 03's new examples, exact-source preservation and safety."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import task_brief_growth_history as history
import turn04_public_source_history

CHANGED = {'_source/pages.json','_source/technology/task-brief.html',
           'assets/task-brief.js','assets/task-brief.css',
           'find/index.html','sitemap.xml','technology/task-brief/index.html'}
EXAMPLES = {'meeting','article','website','writing','planning','learning'}
FIELDS = {'goal','materials','output','review','limits'}

class TaskBriefGrowthTests(unittest.TestCase):
    def test_only_reviewed_input_and_output_paths_are_reversible(self):
        record = history.change()
        self.assertEqual(set(record['paths']), CHANGED)
        for path,item in record['paths'].items():
            with self.subTest(path=path):
                raw=turn04_public_source_history.before(path, (ROOT / path).read_bytes())
                self.assertEqual(sha256(raw).hexdigest(),item['new_sha256'])
                old=history.before(path,raw)
                self.assertEqual(sha256(old).hexdigest(),item['old_sha256'])
                self.assertEqual(history.before(path,old),old)
                for changed in (raw+b'changed',b'changed'+raw,raw[1:]):
                    self.assertEqual(history.before(path,changed),changed)
        self.assertEqual(history.before('assets/contact.js',b'unchanged'),b'unchanged')

    def test_corrupted_snapshot_fails_and_wrong_input_cannot_be_reversed(self):
        record=history.change()
        raw=(ROOT/'assets/task-brief.js').read_bytes()
        for mode in ('wrong_digest','invalid_zlib','wrong_old_digest'):
            broken=deepcopy(record)
            item=broken['paths']['assets/task-brief.js']
            if mode=='wrong_digest': item['new_sha256']='0'*64
            if mode=='invalid_zlib': item['old_zlib_base64']='not a base64 string'
            if mode=='wrong_old_digest': item['old_sha256']='0'*64
            with patch.object(history,'change',return_value=broken):
                if mode=='wrong_digest': self.assertEqual(history.before('assets/task-brief.js',raw),raw)
                else:
                    with self.assertRaises(ValueError): history.before('assets/task-brief.js',raw)

    def test_metadata_is_bounded_and_does_not_relabel_other_pages(self):
        items=build.public_pages()
        newer=next(p for p in items if p['id']=='task-brief')
        self.assertEqual(newer,history.change()['page']['new'])
        self.assertEqual(newer['updated'],'2026-10-17')
        self.assertEqual(history.pages([newer]),[history.change()['page']['old']])
        altered=deepcopy(newer);altered['noindex']=True
        self.assertEqual(history.pages([altered]),[altered])
        self.assertEqual([p for p in items if p['id']!='task-brief'],
            history.pages([p for p in items if p['id']!='task-brief']))

    def test_six_static_examples_have_complete_reviewable_fields(self):
        source=(ROOT/'_source/technology/task-brief.html').read_text()
        self.assertEqual(source.count('data-brief-example='),6)
        for key in EXAMPLES:
            m=re.search(r'<details class="brief-example" data-brief-example="'+key+r'">(.*?)</details>',source,re.S)
            self.assertIsNotNone(m,key)
            values={k:unescape(v) for k,v in re.findall(r'<dd data-brief-field="([^"]+)">(.*?)</dd>',m[1],re.S)}
            self.assertEqual(set(values),FIELDS,key)
            for value in values.values(): self.assertNotIn('<',value)
            self.assertEqual(m[1].count('data-use-example="'+key+'"'),1)
        self.assertIn('not records of completed work',source)
        self.assertIn('Do not invent',source)

    def test_preview_is_literal_and_matches_text_export(self):
        code=r'''
const assert=require('node:assert/strict');
const {assemble}=require('./assets/task-brief.js');
const source={goal:'Text <img src=x onerror=alert(1)>',materials:'A\r\nB',output:'One plan',review:'Compare to source',limits:'No publication'};
const v=assemble(source);
assert.deepEqual(v.errors,{});
assert.equal(v.sections.length,6);
assert.equal(v.text,v.sections.map(s=>s.heading+'\n'+s.content).join('\n\n')+'\n');
assert.equal(v.sections[0].content,source.goal);
assert.equal(v.sections[1].content,'A\nB');
assert.equal(assemble(source).text,v.text);
assert.equal(assemble({...source,review:''}).sections,undefined);
console.log('PASS');
'''
        run=subprocess.run(['node','-e',code],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr+run.stdout)
        script=(ROOT/'assets/task-brief.js').read_text()
        self.assertIn('value.textContent = section.content',script)
        self.assertIn("preview.replaceChildren()",script)
        self.assertNotIn('innerHTML',script)
        for call in ('fetch(', 'localStorage', 'sessionStorage','XMLHttpRequest','sendBeacon','location.search'):
            self.assertNotIn(call,script)

    def test_static_template_unchanged_and_no_submissions(self):
        html=(ROOT/'_source/technology/task-brief.html').read_text()
        blank=unescape(re.search(r'<pre>(.*?)</pre>',html,re.S)[1]).strip()+'\n'
        self.assertEqual(blank,(ROOT/'downloads/ai-task-brief.txt').read_text())
        self.assertNotIn('<form',html)
        self.assertNotIn('data-umami-event',html)

if __name__=='__main__': unittest.main()
