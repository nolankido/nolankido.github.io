"""One-off source migration for the owner-approved local utility; remove before release."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import sys
R=Path.cwd()
def put(path,s):
    p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf-8')
def replace(path,a,b):
    s=(R/path).read_text();assert s.count(a)==1,(path,a[:80],s.count(a));put(path,s.replace(a,b))
protected=['_source/site.json','_source/about.html','_source/bio.html','_source/contact.html','_source/privacy.html','_source/layout.html','styles.css','assets/site.css','assets/hubs.css','assets/contact.js','assets/site-find.js','assets/site-find.css','nolan-kido.vcf','card/qr.svg','feed.xml','writing.xml','living-well/feed.xml','poker/feed.xml','CNAME','_config.yml']
fixed={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in protected}
for root in ['_source/notes','_source/living-well','_source/poker']:
    h=hashlib.sha256()
    for file in sorted((R/root).rglob('*')):
        if file.is_file():
            h.update(str(file.relative_to(R)).encode()+b'\0'+hashlib.sha256(file.read_bytes()).hexdigest().encode()+b'\0')
    fixed[root]=h.hexdigest()
put('_tests/task-brief-baseline.json',json.dumps(fixed,indent=2))
pages=json.loads((R/'_source/pages.json').read_text())
assert not any(p['id']=='task-brief' for p in pages)
pages.append({'id':'task-brief','section':'technology','path':'/technology/task-brief/','title':'Build a clearer AI task brief.','seo_title':'AI Task Brief Builder | Nolan Kido','description':'A free local tool for turning an everyday task into a clear AI brief: purpose, inputs, deliverable, checks, and boundaries. No account or AI connection.','kicker':'Technology / A practical tool','source':'technology/task-brief.html','updated':'2026-10-11'})
put('_source/pages.json',json.dumps(pages,ensure_ascii=False,indent=2))
needle="        if p['id'] == 'contact':\n"
replace('_scripts/build.py',needle,"        if p['id'] == 'task-brief':\n            for asset, kind in [('task-brief.css', 'style'), ('task-brief.js', 'script')]:\n                version = hashlib.sha256((ROOT / 'assets' / asset).read_bytes()).hexdigest()[:12]\n                extra += (f'\\n  <link rel=\"stylesheet\" href=\"/assets/{asset}?v={version}\">' if kind == 'style' else f'\\n  <script defer src=\"/assets/{asset}?v={version}\"></script>')\n"+needle)
replace('_scripts/check_live.py',"    assets += ['assets/entrypoints.css',", "    assets += ['assets/task-brief.css', 'assets/task-brief.js', 'downloads/ai-task-brief.txt']\n    assets += ['assets/entrypoints.css',")
replace('_source/technology/home.html','Start with selected writing on useful tools, then follow a practical guide or try a small check of your own.','Build a brief for one task, read the argument behind it, or follow a practical guide. The small tool below is a working starting point, not a promise of what AI can do.')
replace('_source/technology/home.html','<a class="button" href="#technology-path">Find a useful starting point <span aria-hidden="true">↓</span></a>','<a class="button" href="/technology/task-brief/">Build an AI task brief <span aria-hidden="true">→</span></a><a class="text-link" href="#technology-path">Explore the reading <span aria-hidden="true">↓</span></a>')
replace('_source/technology/home.html','<h3>Where should AI fit?</h3>','<h3>Have a task in mind?</h3><p><a href="/technology/task-brief/">Build a clearer AI task brief</a>. Define the purpose, inputs, output, boundaries, and checks, then copy or save the result. Three examples help you start. No AI service or account is connected.</p>\n<h3>Where should AI fit?</h3>')
replace('_source/resources.html','${resource_entrypoints}','${resource_entrypoints}\n<p class="small-copy"><strong>Something to use now:</strong> <a href="/technology/task-brief/">Build an AI task brief</a> locally, with a blank template and three illustrative starting points.</p>')
replace('_source/start-here.html','${interest_entrypoints}','${interest_entrypoints}\n<p class="small-copy">Have a task to try? <a href="/technology/task-brief/">Build a clear AI brief</a> before choosing what to delegate.</p>')
replace('_tests/test_content.py',"            if path == Path('find/index.html'):","            if path == Path('technology/task-brief/index.html'):\n                expected.insert(0, '/assets/task-brief.js?v=' + hashlib.sha256((ROOT / 'assets/task-brief.js').read_bytes()).hexdigest()[:12])\n            if path == Path('find/index.html'):")
replace('_tests/test_site.py',"allowed = {Path('find/index.html'):","allowed = {Path('technology/task-brief/index.html'): '/assets/task-brief.js', Path('find/index.html'):")
replace('_tests/test_gateway.py',"self.assertIn('Start with selected writing on useful tools', technology)","self.assertIn('Build a brief for one task', technology)\n        self.assertIn('href=\"/technology/task-brief/\"', technology)")
subprocess.run([sys.executable,'_scripts/build.py'],check=True)
p=R/'_tests/test_viewer_next.py';s=p.read_text();digest=hashlib.sha256((R/'technology/index.html').read_bytes()).hexdigest()
s,n=re.subn(r"('technology/index.html'\s*:\s*')[a-f0-9]{64}(')",lambda m:m[1]+digest+m[2],s);assert n==1;p.write_text(s)
p=R/'_tests/test_poker_content.py';s=p.read_text();paths=ast.literal_eval(re.search(r'^BASELINE_PATHS = (.+)$',s,re.M)[1]);h=hashlib.sha256()
for path in paths:h.update(path.encode()+b'\0'+(R/path).read_bytes()+b'\0')
s,n=re.subn(r"BASELINE_DIGEST = '[a-f0-9]{64}'",f"BASELINE_DIGEST = '{h.hexdigest()}'",s);assert n==1;p.write_text(s)
print('Task brief sources and output prepared; original protected content is unchanged.')
