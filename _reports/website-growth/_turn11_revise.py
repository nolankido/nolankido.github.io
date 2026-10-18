"""Temporary Turn 11 follow-up: regenerate tracked outputs and exact historical signature."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,zlib
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[2]
BASE='e6d61d4070bae76c54e1b676422e716ff8adaac6'
PATHS=['_source/start-here.html','_source/resources.html','_source/find.html','_source/pages.json','_source/search-entrypoints.json','start-here/index.html','resources/index.html','find/index.html','sitemap.xml']
def call(*xs):subprocess.run(list(xs),cwd=ROOT,check=True)
def old(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def patch(path,before,after):
 file=ROOT/path;s=file.read_text()
 if s.count(before)!=1:raise ValueError('Unexpected patch source '+path+':'+before[:60])
 file.write_text(s.replace(before,after,1),encoding='utf-8')
call(sys.executable,'_scripts/build.py')
sys.path.insert(0,str(ROOT/'_scripts'))
import build
now={p['id']:p for p in build.public_pages() if p['id'] in ('start-here','resources','find')}
previous=deepcopy(now)
manifest={p['id']:p for p in json.loads(old('_source/pages.json'))}
config=json.loads(old('_source/search-entrypoints.json'))['entries']
for name,p in previous.items():
 for key in ('description','updated'):p[key]=(manifest if name=='find' else config)[name][key]
 if name!='find':p['entry_summary']=config[name]['description']
digest=lambda value:hashlib.sha256(value).hexdigest()
record={'version':1,'base_commit':BASE,'paths':{},'pages':{}}
for path in PATHS:
 prior=old(path);new=(ROOT/path).read_bytes()
 if new==prior:raise ValueError('Unchanged expected source '+path)
 record['paths'][path]={'old_sha256':digest(prior),'new_sha256':digest(new),'old_zlib_base64':base64.b64encode(zlib.compress(prior,9)).decode('ascii')}
for name in now:
 if now[name]!=previous[name]:record['pages'][name]={'old':previous[name],'new':now[name]}
assert len(record['pages'])==3
(ROOT/'_tests/turn11-task-navigation-change.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
patch('_tests/homepage_growth_history.py','import task_brief_growth_history','import task_brief_growth_history\nimport turn11_task_navigation_history as task_nav_history')
patch('_tests/homepage_growth_history.py','def pages(records):\n    records = task_brief_growth_history.pages(records)','def pages(records):\n    records = task_nav_history.pages(records)\n    records = task_brief_growth_history.pages(records)')
patch('_tests/test_homepage_growth.py','import task_brief_growth_history as task_growth','import task_brief_growth_history as task_growth\nimport turn11_task_navigation_history as task_nav_history')
patch('_tests/test_homepage_growth.py',"""        for page in records:
            if page['id'] not in {'home', 'task-brief'}:
                self.assertEqual(history.pages([page]), [page])""","""        for page in records:
            if page['id'] not in {'home', 'task-brief'}:
                expected = task_nav_history.pages([page]) if page['id'] in {'start-here', 'resources', 'find'} else [page]
                self.assertEqual(history.pages([page]), expected)""")
patch('_tests/test_turn04_public_source.py','import turn04_public_source_history as history','import turn04_public_source_history as history\nimport turn11_task_navigation_history as task_nav_history')
patch('_tests/test_turn04_public_source.py','original=(ROOT/path).read_bytes()','original=task_nav_history.before(path,(ROOT/path).read_bytes())')
call(sys.executable,'_scripts/build.py','--check')
call(sys.executable,'_scripts/check_search.py')
for pattern in ('test_turn11_task_navigation.py','test_entrypoints.py','test_search_entrypoints.py','test_search_addresses.py','test_preflop.py','test_turn04_public_source.py','test_poker_school_history.py'):
 call(sys.executable,'-m','unittest','discover','-s','_tests','-p',pattern,'-q')
print('TURN11_REVISED_PASS')
