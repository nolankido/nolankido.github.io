"""Search actual descriptive routes without changing content or broadening privacy."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import build, site_find
import search_addresses_history as history
import poker_titles_history


class SearchAddressesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = {p: poker_titles_history.before(p, value) for p, value in build.build_outputs().items()}
        cls.baseline = json.loads((ROOT / '_tests/search-addresses-baseline.json').read_text())

    def test_only_search_behavior_scope_copy_and_cache_token_change(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        b = self.baseline
        self.assertEqual(sha256(json.dumps(poker_titles_history.pages(beginner_history.pages(build.public_pages())), sort_keys=True, ensure_ascii=False).encode()).hexdigest(), b['pages_sha256'])
        self.assertEqual(set(map(str, historical_outputs)), set(b['outputs']))
        changed = []
        for p, expected in b['outputs'].items():
            value = historical_outputs[Path(p)]
            if sha256(value.encode()).hexdigest() != expected:
                changed.append(p)
            self.assertEqual(sha256(history.before(p, value).encode()).hexdigest(), expected, p)
        self.assertEqual(changed, ['find/index.html'])
        files = beginner_history.files({p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file()})
        self.assertEqual(files, set(b['files']))
        changed = []
        for p, expected in b['files'].items():
            value = poker_titles_history.before(p, (ROOT / p).read_bytes())
            if sha256(value).hexdigest() != expected:
                changed.append(p)
            self.assertEqual(sha256(history.before(p, value)).hexdigest(), expected, p)
        self.assertCountEqual(changed, ['assets/site-find.js', '_source/find.html'])

    def test_real_missed_destinations_ranking_and_conservative_address_scope(self):
        rows = site_find.entries(ROOT, build.public_pages())
        packed = json.loads(re.search(r'id="find-section-data">(.*?)</script>', (ROOT / 'find/index.html').read_text(), re.S)[1])
        sections = {('/'+g+'/'+s if g else '/'):[[v[i],packed['labels'][v[i+1]] if type(v[i+1]) is int else v[i+1]] for i in range(0,len(v),2)] for g,entries in packed['pages'].items() for s,v in entries.items()}
        for row in rows:
            row.update(subjects=' '.join(row['interests']), sections=sections[row['path']])
        old = history.before('assets/site-find.js', (ROOT / 'assets/site-find.js').read_text())
        code = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const {rows,old}=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const current=require('./assets/site-find.js'),context={module:{exports:{}}};vm.runInNewContext(old,context);
for(const [query,path] of [['AI time savings','/technology/ai-time-savings/'],['poker hand rankings','/poker/hand-rankings/'],['task brief','/technology/task-brief/']]){
 const row=rows.find(r=>r.path===path);assert(current.score(row,query)>=0,path);
 if(query!=='task brief')assert.equal(context.module.exports.score(row,query),-1,path);
}
// Keep every formerly discoverable match, and its rank, when no new address
// term is needed. Title/summary matches must outrank address-only matches.
for(const row of rows)for(const query of ['AI','family story','recovery','pot odds','weekly reset']){
 const prior=context.module.exports.score(row,query);if(prior>=1000)assert.equal(current.score(row,query),prior);
 if(prior>=0)assert(current.score(row,query)>=0);
}
const base={title:'Guide',description:'',subjects:'',sections:[]};
assert(current.score({...base,title:'Hand rankings'},'hand rankings')>current.score({...base,path:'/poker/hand-rankings/'},'hand rankings'));
assert(current.score({...base,path:'/poker/hand-rankings/'},'hand rankings')>current.score({...base,sections:[['ranks','Hand rankings']]},'hand rankings'));
for(const path of [undefined,'https://other.example/secret/','//other.example/secret/','/safe/?secret=x','/safe/#secret','/secret','/secret%2f/','/SECRET/'])assert.equal(current.score({...base,path},'secret'),-1);
assert.equal(current.score({...base,path:'/chair/'},'AI'),-1);
assert.equal(current.score({...base,path:'/technology/ai-time-savings/'},'savings football'),-1);
assert.equal(current.score({...base,path:'/poker/hand-rankings/'},'the and'),-1);
assert.equal(current.score({...base,path:'/poker/hand-rankings/'},'???'),-1);
assert.equal(current.matchingSections({...base,path:'/poker/hand-rankings/',sections:[['kicker','Compare the kicker']]},'hand rankings kicker')[0][0],'kicker');
assert.equal(current.score({...base,path:'/poker/hand-rankings/',sections:[['alpha','Alpha'],['beta','Beta']]},'alpha beta'),-1);
'''
        result = subprocess.run(['node', '-e', code], cwd=ROOT, input=json.dumps({'rows': rows, 'old': old}), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_frozen_adapter_cannot_hide_search_logic_or_source_edits(self):
        for path, old, new in [('assets/site-find.js', 'addressMatch ? 500', 'addressMatch ? 1500'),
                               ('assets/site-find.js', 'const stops =', 'const changed = 1; const stops ='),
                               ('_source/find.html', 'words in page addresses', 'private worksheet answers'),
                               ('find/index.html', 'words in page addresses', 'private worksheet answers'),
                               ('find/index.html', 'Keep access and recovery simple', 'Unexpected heading')]:
            value = (ROOT / path).read_text()
            modified = value.replace(old, new, 1)
            self.assertNotEqual(value, modified)
            self.assertNotEqual(history.before(path, value), history.before(path, modified))
        self.assertEqual(history.before('about/index.html', 'untouched'), 'untouched')
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
