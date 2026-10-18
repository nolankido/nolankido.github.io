"""One-shot feature-branch builder. Remove before release."""
from pathlib import Path
from copy import deepcopy
import base64,hashlib,json,subprocess,sys,zlib
ROOT=Path(__file__).resolve().parents[2]
BASE='e6d61d4070bae76c54e1b676422e716ff8adaac6'
paths=['_source/start-here.html','_source/resources.html','_source/find.html','_source/pages.json','_source/search-entrypoints.json','start-here/index.html','resources/index.html','find/index.html','sitemap.xml']
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def patch(path,old,new):
 p=ROOT/path;s=p.read_text()
 if s.count(old)!=1:raise ValueError('Patch failed '+path+':'+old[:35])
 p.write_text(s.replace(old,new,1),encoding='utf8')
def run(*args):subprocess.run(list(args),cwd=ROOT,check=True)
run(sys.executable,'_scripts/build.py')
sys.path.insert(0,str(ROOT/'_scripts'))
import build
now={p['id']:p for p in build.public_pages() if p['id'] in {'start-here','resources','find'}}
previous=deepcopy(now)
old_manifest={p['id']:p for p in json.loads(original('_source/pages.json'))}
old_config=json.loads(original('_source/search-entrypoints.json'))['entries']
for k,entry in previous.items():
 for field in ('description','updated'):entry[field]=(old_manifest if k=='find' else old_config)[k][field]
 if k!='find':entry['entry_summary']=old_config[k]['description']
sha=lambda b:hashlib.sha256(b).hexdigest()
record={'version':1,'base_commit':BASE,'paths':{},'pages':{}}
for path in paths:
 old=original(path);new=(ROOT/path).read_bytes()
 if old==new:raise ValueError('Unchanged expected release path: '+path)
 record['paths'][path]={'old_sha256':sha(old),'new_sha256':sha(new),'old_zlib_base64':base64.b64encode(zlib.compress(old,9)).decode('ascii')}
for k in now:
 if now[k]!=previous[k]:record['pages'][k]={'old':previous[k],'new':now[k]}
if len(record['pages'])!=3:raise ValueError('Wrong manifest delta')
(ROOT/'_tests/turn11-task-navigation-change.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
patch('_tests/beginner_history.py','import poker_course_history','import turn11_task_navigation_history as task_nav_history\nimport poker_course_history')
patch('_tests/beginner_history.py','def before(path, data):\n    data = preflop_history.before(path, data)','def before(path, data):\n    data = task_nav_history.before(path, data)\n    data = preflop_history.before(path, data)')
patch('_tests/beginner_history.py','def pages(records):\n    records = preflop_history.pages(records)','def pages(records):\n    records = task_nav_history.pages(records)\n    records = preflop_history.pages(records)')
patch('_tests/choice_history.py','import answer_review_history','import turn11_task_navigation_history as task_nav_history\nimport answer_review_history')
patch('_tests/choice_history.py','def before(path,data):\n    data=answer_review_history.before(path,data)','def before(path,data):\n    data=task_nav_history.before(path,data)\n    data=answer_review_history.before(path,data)')
patch('_tests/search_entry_history.py','import author_archive_history','import turn11_task_navigation_history as task_nav_history\nimport author_archive_history')
patch('_tests/search_entry_history.py',"return json.loads(poker_progress_history.before(path, (ROOT / path).read_text()))['entries']","return json.loads(poker_progress_history.before(path, task_nav_history.before(path, (ROOT / path).read_text())))['entries']")
patch('_tests/search_entry_history.py','def pages(records):\n    records = author_archive_history.pages(records)','def pages(records):\n    records = task_nav_history.pages(records)\n    records = author_archive_history.pages(records)')
patch('_tests/search_entry_history.py','def before(path, data):\n    data = author_archive_history.before(path, data)','def before(path, data):\n    data = task_nav_history.before(path, data)\n    data = author_archive_history.before(path, data)')
patch('_tests/turn04_public_source_history.py','from pathlib import Path','from pathlib import Path\nimport turn11_task_navigation_history as task_nav_history')
patch('_tests/turn04_public_source_history.py','def before(path,data):\n    entry=change()','def before(path,data):\n    data=task_nav_history.before(path,data)\n    entry=change()')
patch('_tests/test_search_entrypoints.py',"expected_date = {'poker-library': '2026-10-15', 'poker-study': '2026-10-16'}.get(p['id'], '2026-10-12')","expected_date = {'poker-library': '2026-10-15', 'poker-study': '2026-10-16', 'start-here': '2026-10-17', 'resources': '2026-10-17'}.get(p['id'], '2026-10-12')")
for path in ('_source/find.html','find/index.html'):
 patch('_tests/test_search_addresses.py',"('"+path+"', 'words in page addresses', 'private worksheet answers')","('"+path+"', 'visible section headings', 'private worksheet answers')")
run(sys.executable,'_scripts/build.py','--check')
run(sys.executable,'_scripts/check_search.py')
for t in ('test_turn11_task_navigation.py','test_entrypoints.py','test_search_entrypoints.py','test_search_sections.py','test_search_addresses.py'):
 run(sys.executable,'-m','unittest','discover','-s','_tests','-p',t,'-q')
print('TURN11_CANDIDATE_PASS',len(record['paths']),len(record['pages']))
