import os,json,subprocess,hashlib,base64,urllib.request
from pathlib import Path
root=Path.cwd()
base='fbfd99915d6b11332b0bf771c8ad7103d8be0d93'
tree='5813b88bf927256f8aba942952511741527a85f5'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==base
assert subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip()==tree
assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
p=root/'_source/poker/resources.json';s=p.read_text();original=json.loads(s);byid={e['id']:e for e in original['entries']}
mods={
'nj-dge-information':{'notes':'Official information page reviewed: approved-site and permit-holder listings, best-practice links, and the requirement to complain to the operator before filing an Internet gaming dispute with DGE. Linked lists, forms, individual approvals and eligibility were not checked.','reviewed_on':'2026-10-24','review_method':'page'},
'wynn-poker':{'notes':'Official Wynn poker landing page reviewed for cash games, tournament series, daily tournament information and schedule/structure links. Linked schedules and structures, registration details and live game availability were not independently checked.','reviewed_on':'2026-10-24'}}
for name,fields in mods.items():
    oldline=next(x for x in s.splitlines() if '"id": "'+name+'"' in x);new=oldline
    for k,v in fields.items():
        old='"'+k+'": '+json.dumps(byid[name][k],ensure_ascii=False)
        assert old in new
        new=new.replace(old,'"'+k+'": '+json.dumps(v,ensure_ascii=False),1)
    assert s.count(oldline)==1
    s=s.replace(oldline,new,1)
p.write_text(s)
subprocess.run(['python','_scripts/build.py'],check=True)
paths=['_source/poker/resources.json','downloads/poker-resource-directory.json','downloads/poker-resource-directory.md','poker/find/index.html','poker/poker-access-and-protection/index.html','poker/resource-quality/index.html','poker/resources/index.html']
assert sorted(subprocess.check_output(['git','diff','--name-only'],text=True).splitlines())==sorted(paths)
hist={'version':1,'base_commit':base,'resources':{},'paths':{}}
for ident in mods:
    old=byid[ident];new=next(x for x in json.loads(s)['entries'] if x['id']==ident)
    hist['resources'][ident]={'old':old,'new':new}
for f in paths:
    a=subprocess.check_output(['git','show','HEAD:'+f]);b=(root/f).read_bytes()
    al=a.splitlines(keepends=True);bl=b.splitlines(keepends=True)
    assert len(al)==len(bl),f
    hist['paths'][f]={'old_sha256':hashlib.sha256(a).hexdigest(),
       'new_sha256':hashlib.sha256(b).hexdigest(),
       'old_lines':[[i,x.decode('utf-8')] for i,(x,y) in enumerate(zip(al,bl)) if x!=y]}
(root/'_tests/resource-followup-change.json').write_text(json.dumps(hist,ensure_ascii=False,separators=(',',':'))+'\n')
(root/'_tests/resource_followup_history.py').write_text('''"""Hash-gated preservation of the October 23 source records."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
BASE='fbfd99915d6b11332b0bf771c8ad7103d8be0d93'
IDS={'nj-dge-information','wynn-poker'}
@lru_cache(maxsize=1)
def change():
    r=json.loads((ROOT/'_tests/resource-followup-change.json').read_text())
    if r.get('version')!=1 or r.get('base_commit')!=BASE or set(r['resources'])!=IDS:
        raise ValueError('Unknown exact review predecessor')
    return r
def before(path,data):
    item=change()['paths'].get(str(path))
    if item is None:return data
    binary=isinstance(data,bytes);raw=data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest()!=item['new_sha256']:return data
    lines=raw.decode('utf-8').splitlines(keepends=True)
    for n,prior in item['old_lines']:
        if type(n)!=int or n<0 or n>=len(lines):raise ValueError('Invalid historical line')
        lines[n]=prior
    old=''.join(lines).encode('utf-8')
    if sha256(old).hexdigest()!=item['old_sha256']:raise ValueError('Corrupted predecessor')
    return old if binary else old.decode('utf-8')
def resources(records):
    p=change()['resources']
    return [deepcopy(p[r['id']]['old']) if r['id'] in p and r==p[r['id']]['new'] else deepcopy(r) for r in records]
''')
p=root/'_tests/resource_review_history.py';txt=p.read_text()
assert txt.count('import json\n')==1
txt=txt.replace('import json\n','import json\nimport resource_followup_history\n',1)
txt=txt.replace('def before(path, data):\n','def before(path, data):\n    data = resource_followup_history.before(path, data)\n',1)
txt=txt.replace('def resources(records):\n','def resources(records):\n    records = resource_followup_history.resources(records)\n',1)
p.write_text(txt)
p=root/'_tests/test_resource_review_20261023.py';txt=p.read_text()
txt=txt.replace('import resource_review_history as history\n','import resource_review_history as history\nimport resource_followup_history as followup\n',1)
txt=txt.replace("cls.raw = (ROOT / '_source/poker/resources.json').read_text()","cls.raw = followup.before('_source/poker/resources.json', (ROOT / '_source/poker/resources.json').read_text())",1)
txt=txt.replace('cls.entries = poker_resources.load(ROOT)','cls.entries = followup.resources(poker_resources.load(ROOT))',1)
txt=txt.replace("payload = json.loads(self.outputs[Path('downloads/poker-resource-directory.json')])",
"payload = json.loads(followup.before('downloads/poker-resource-directory.json', self.outputs[Path('downloads/poker-resource-directory.json')]))",1)
txt=txt.replace("raw = (ROOT / name).read_bytes()\n            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])",
"raw = followup.before(name, (ROOT / name).read_bytes())\n            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])",1)
p.write_text(txt)
(root/'_tests/test_resource_followup_20261024.py').write_text('''"""Bounded followup for two previously inconclusive public sources."""
from datetime import date
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,poker_resources,resource_followup_history as history
class FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/'_source/poker/resources.json').read_text()
        cls.current=json.loads(cls.raw)['entries']
        cls.prior=json.loads(history.before('_source/poker/resources.json',cls.raw))['entries']
        cls.entries=poker_resources.load(ROOT)
    def test_exactly_two_changes_and_all_links_preserved(self):
        self.assertEqual(len(self.current),146)
        self.assertEqual([e['id'] for e in self.current],[e['id'] for e in self.prior])
        diffs=[(a,b) for a,b in zip(self.prior,self.current) if a!=b]
        self.assertEqual({b['id'] for a,b in diffs},history.IDS)
        for a,b in diffs:
            self.assertEqual(a['url'],b['url'])
            self.assertEqual(a['description'],b['description'])
            self.assertEqual(b['reviewed_on'],'2026-10-24')
            self.assertEqual({k for k in b if a[k]!=b[k]},
             {'notes','review_method','reviewed_on'} if b['id']=='nj-dge-information' else {'notes','reviewed_on'})
    def test_limits_and_review_queue(self):
        e={r['id']:r for r in self.entries}
        self.assertEqual(e['nj-dge-information']['review_method'],'page')
        self.assertIn('eligibility were not checked',e['nj-dge-information']['notes'])
        self.assertIn('real-time',e['wynn-poker']['notes'].replace('live game','real-time'))
        self.assertEqual({r['id'] for r in poker_resources.review_queue(history.resources(self.entries),date(2026,10,24))},history.IDS)
        self.assertEqual(poker_resources.review_queue(self.entries,date(2026,10,24)),[])
    def test_export_exact_and_predecessor_bytes(self):
        out=build.build_outputs()
        r=json.loads(out[Path('downloads/poker-resource-directory.json')])['entries']
        self.assertEqual({e['id']:e for e in r},{e['id']:e for e in self.entries})
        for f,v in history.change()['paths'].items():
            raw=(ROOT/f).read_bytes();old=history.before(f,raw)
            self.assertEqual(sha256(raw).hexdigest(),v['new_sha256'])
            self.assertEqual(sha256(old).hexdigest(),v['old_sha256'])
            self.assertEqual(history.before(f,raw+b'x'),raw+b'x')
    def test_corrupt_history_rejected(self):
        x=deepcopy(history.change());x['paths']['_source/poker/resources.json']['old_sha256']='0'*64
        with patch.object(history,'change',return_value=x),self.assertRaises(ValueError):
            history.before('_source/poker/resources.json',(ROOT/'_source/poker/resources.json').read_bytes())
    def test_scope(self):
        self.assertEqual(set(history.change()['paths']),{
          '_source/poker/resources.json','downloads/poker-resource-directory.json',
          'downloads/poker-resource-directory.md','poker/find/index.html',
          'poker/poker-access-and-protection/index.html',
          'poker/resource-quality/index.html','poker/resources/index.html'})
if __name__=='__main__':unittest.main()
''')
rp=root/'_reports/website-growth'
(rp/'turn-18-resource-review-followup.md').write_text('''# Turn 18: two checked directory sources

Reviewed October 24, 2026. New Jersey DGE's Internet Gaming Information page and Wynn Las Vegas Poker's official room page were readable through a second permitted public extractor, although the initial URL fetch returned HTTP 403. The DGE landing page describes approved-site information, permit holders, and filing a complaint with the operator before escalating an Internet-gaming dispute. Wynn's landing page describes cash games, tournament series, daily tournament information and schedule/structure links.

The listed reviews cover only those original public pages, not their linked documents, specific licenses, event schedules, eligibility, payments or live availability. Exactly two review records changed; 144 other records and all 146 destination URLs/IDs remain unchanged. Generated directory, finder and export surfaces were rebuilt from one catalogue. No website scripting, Task Brief interface, tracking, storage, stylesheet, sitemap or publication date changed. These are editorial checks, not real visitor observations or growth data.
''')
(rp/'turn-18-resource-review-followup.json').write_text(json.dumps({'date':'2026-10-24','base_commit':base,'ids':sorted(mods),'source_checks':'two direct public landing-page text reads','limits':'linked files, status, schedules, approvals and eligibility not verified','status':'candidate, not yet published'},indent=2)+'\n')
subprocess.run(['python','_scripts/build.py','--check'],check=True)
for name in ['test_resource_followup_20261024.py','test_resource_review_20261023.py']:
    subprocess.run(['python','-m','unittest','discover','-s','_tests','-p',name,'-v'],check=True)
files=paths+['_tests/resource-followup-change.json','_tests/resource_followup_history.py',
 '_tests/resource_review_history.py','_tests/test_resource_review_20261023.py','_tests/test_resource_followup_20261024.py',
 '_reports/website-growth/turn-18-resource-review-followup.md','_reports/website-growth/turn-18-resource-review-followup.json']
subprocess.run(['git','add','--',*files],check=True)
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(files)
token=os.environ['GH_TOKEN']
def post(t,d):
 req=urllib.request.Request('https://api.github.com/repos/nolankido/nolankido.github.io/git/'+t,data=json.dumps(d).encode(),method='POST',headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'nk-resource-stage'})
 with urllib.request.urlopen(req,timeout=80) as r:return json.load(r)
items=[]
for f in sorted(files):
 b=(root/f).read_bytes();sha=post('blobs',{'encoding':'base64','content':base64.b64encode(b).decode()})['sha']
 assert sha==hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 items.append({'path':f,'mode':'100644','type':'blob','sha':sha})
newtree=post('trees',{'base_tree':tree,'tree':items})['sha']
assert newtree==subprocess.check_output(['git','write-tree'],text=True).strip()
print('CANDIDATE_TREE='+newtree,flush=True)
