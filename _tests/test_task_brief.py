"""Local utility contracts: deterministic output, honest scope, and fixed boundaries."""
import choice_history
from html import unescape
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'_scripts'))
import beginner_history
import build
import check_live
import site_find
from test_site import Page

class TaskBriefTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.html = cls.outputs[Path('technology/task-brief/index.html')]
        cls.page = Page(cls.html)

    def test_tool_is_not_a_personal_result_or_new_feed_article(self):
        item = next(p for p in self.pages if p['id'] == 'task-brief')
        self.assertEqual(item['section'], 'technology')
        self.assertFalse(item.get('note') or item.get('poker_guide') or item.get('living_well_entry'))
        self.assertIn('No AI runs here.', self.html)
        self.assertIn('fixed template', self.html)
        self.assertIn('No personal results', self.html)
        self.assertIn('not a security control', self.html)
        for feed in ['feed.xml', 'writing.xml', 'living-well/feed.xml', 'poker/feed.xml']:
            self.assertNotIn('/technology/task-brief/', self.outputs[Path(feed)])
        self.assertIn('/technology/task-brief/', self.outputs[Path('sitemap.xml')])

    def test_routes_and_search_are_connected_without_global_script(self):
        for route in ['technology/index.html','start-here/index.html','resources/index.html','find/index.html']:
            self.assertIn('href="/technology/task-brief/"', self.outputs[Path(route)])
        matches = [e for e in site_find.entries(ROOT,self.pages) if e['path']=='/technology/task-brief/']
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0]['home'],'technology')
        for p in self.pages:
            content = self.outputs[build.output_path(p['path'])]
            for asset in ['task-brief.css','task-brief.js']:
                self.assertEqual('/assets/'+asset in content, p['id']=='task-brief')
        targets=check_live.targets()
        for path in ['assets/task-brief.css','assets/task-brief.js','downloads/ai-task-brief.txt']:
            self.assertEqual(targets['/'+path],(200,(ROOT/path).read_bytes()))

    def test_fixed_private_boundaries_are_unchanged(self):
        fixed=json.loads((ROOT/'_tests/task-brief-baseline.json').read_text())
        for path,digest in fixed.items():
            with self.subTest(path=path):
                target=ROOT/path
                if target.is_dir():
                    h=hashlib.sha256()
                    for file in sorted(beginner_history.files([f for f in target.rglob('*') if f.is_file()])):
                        if file.is_file():
                            h.update(str(file.relative_to(ROOT)).encode()+b'\0'+hashlib.sha256(beginner_history.before(file.relative_to(ROOT), file.read_bytes())).hexdigest().encode()+b'\0')
                    actual=h.hexdigest()
                else:
                    actual=hashlib.sha256(choice_history.before(path,target.read_bytes())).hexdigest()
                self.assertEqual(actual,digest)

    def test_native_controls_have_labels_limits_and_no_submission(self):
        self.assertNotIn('<form',self.html)
        self.assertNotIn('data-umami-event',self.html)
        fields={a['id']:a for a in self.page.tags('textarea')}
        labels={a.get('for') for a in self.page.tags('label')}
        for key,limit in [('goal',600),('materials',800),('output',600),('review',800),('limits',600)]:
            name='brief-'+key
            self.assertIn(name,labels)
            self.assertEqual(fields[name]['maxlength'],str(limit))
            self.assertEqual(fields[name]['autocomplete'],'off')
            self.assertNotIn('name',fields[name])
            self.assertIn(name+'-error',fields[name]['aria-describedby'])
        editor=next(a for a in self.page.tags('div') if a.get('id')=='brief-editor')
        self.assertIn('hidden',editor)
        self.assertTrue(all(b.get('type')=='button' for b in self.page.tags('button')))
        self.assertIn('readonly',fields['brief-text'])

    def test_static_template_matches_download_and_survives_script_failure(self):
        source=(ROOT/'_source/technology/task-brief.html').read_text()
        blank=unescape(re.search(r'<pre>(.*?)</pre>',source,re.S)[1]).strip()+'\n'
        self.assertEqual(blank,(ROOT/'downloads/ai-task-brief.txt').read_text())
        self.assertEqual(source.count('data-brief-example='),6)
        self.assertEqual(source.count('Illustrative starting point, not a personal case study.'),5)
        self.assertIn('Illustrative starting point, not a personal development claim.', source)
        for example in ['meeting', 'article', 'website', 'writing', 'planning', 'learning']:
            self.assertIn('data-brief-example="' + example + '"', source)
        self.assertIn('work without it',source)
        self.assertIn('do not paste confidential',source.lower())

    def test_assembly_validation_and_literal_input(self):
        code=r'''
const assert=require('node:assert/strict');
const {assemble, FIELDS, INSTRUCTIONS}=require('./assets/task-brief.js');
const values={goal:'A useful task',materials:'A short draft',output:'One paragraph',review:'Compare with the source',limits:''};
const first=assemble(values); assert.deepEqual(first.errors,{});
assert.equal(first.text,assemble(values).text); assert(first.text.includes(INSTRUCTIONS));
assert.equal(values.limits,'');
assert(first.text.startsWith('PURPOSE\nA useful task\n'));
assert(first.text.includes('No additional task-specific constraints supplied.'));
for(const field of Object.keys(FIELDS)) {
 const tooLong=assemble({...values,[field]:'x'.repeat(FIELDS[field]+1)});
 assert(tooLong.errors[field]);assert.equal(tooLong.text,'');
 const exact=assemble({...values,[field]:'x'.repeat(FIELDS[field])});assert.deepEqual(exact.errors,{});
 if(field!=='limits')assert(assemble({...values,[field]:' \n '}).errors[field]);
}
assert.equal(Object.keys(assemble(null).errors).length,4);
assert.equal(Object.keys(assemble({}).errors).length,4);
const literal='<img src=x onerror=alert(1)> & "quoted"';
assert(assemble({...values,goal:literal}).text.includes(literal));
assert(assemble({...values,goal:' First\r\nSecond '}).text.includes('First\nSecond'));
console.log('PASS deterministic assembly, validation, optional boundary, literal text, CRLF');
'''
        result=subprocess.run(['node','-e',code],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_page_uses_existing_design_tokens_and_unique_ids(self):
        css=(ROOT/'assets/task-brief.css').read_text()
        declared=set(re.findall(r'(--[a-z-]+)\s*:', (ROOT/'styles.css').read_text()))
        used=set(re.findall(r'var\((--[a-z-]+)\)',css))
        self.assertLessEqual(used, declared)
        ids=[a['id'] for _,a in self.page.elements if 'id' in a]
        self.assertEqual(len(ids),len(set(ids)))

    def test_no_network_persistence_or_untrusted_html_sink(self):
        code=(ROOT/'assets/task-brief.js').read_text()
        for bad in ['fetch(', 'XMLHttpRequest','WebSocket','sendBeacon','localStorage','sessionStorage','indexedDB','document.cookie','innerHTML','outerHTML','insertAdjacentHTML','eval(', 'readText(', 'pushState','replaceState','location.search']:
            self.assertNotIn(bad,code)
        self.assertIn('navigator.clipboard.writeText(snapshot)',code)
        self.assertIn("window.addEventListener('pagehide', clearAll)",code)
        self.assertIn("window.addEventListener('pageshow'",code)
        self.assertIn('not a security control',code)
        self.assertIn('URL.revokeObjectURL(url)',code)

if __name__=='__main__': unittest.main()
