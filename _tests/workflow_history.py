"""Reverse only reviewed workflow changes for existing historical contracts.

The independent production baseline and new feature tests ensure this adapter
cannot hide changes to article text, identity or existing behavior.
"""
from copy import deepcopy
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
BASE=json.loads((ROOT/'_tests/workflow-path-baseline.json').read_text())
HUBS={'technology','resources','start-here'}
OLD={p['id']:p for p in BASE['manifest']}
PATTERN=r'<!-- AI workflow path: start -->\n.*?<!-- AI workflow path: end -->\n'
NEW_TITLE='Practical AI Workflow, Tools & Checklists | Nolan Kido'
NEW_DESCRIPTION='Decide whether AI fits, write a task brief, check a summary, and compare the full effort. Free tools, worked guides, and one downloadable workflow workbook.'

def original_pages(pages):
    result=deepcopy(pages)
    for p in result:
        if p['id'] in HUBS:p['updated']=OLD[p['id']]['updated']
        if p['id']=='technology':
            p['seo_title']=OLD[p['id']]['seo_title']
            p['description']=OLD[p['id']]['description']
    return result

def before(path,data):
    from html import escape
    path=str(path);binary=isinstance(data,bytes)
    if not (path.endswith('.html') or path in {'_source/pages.json','sitemap.xml'}):return data
    text=data.decode() if binary else data
    if path=='_source/pages.json':text=json.dumps(original_pages(json.loads(text)),indent=2,ensure_ascii=False)+'\n'
    elif path=='sitemap.xml':
        for route in ['/technology/','/start-here/','/resources/']:
            pattern=r'(<loc>https://nolankido\.com'+re.escape(route)+r'</loc>\s*<lastmod>)2026-10-12(</lastmod>)'
            text=re.sub(pattern,lambda m:m[1]+'2026-10-11'+m[2],text)
    elif path.endswith('.html'):
        if path=='technology/index.html':text=re.sub(PATTERN,lambda m:BASE['original_technology_panel'],text,flags=re.S)
        else:text=re.sub(PATTERN,'',text,flags=re.S)
        text=re.sub(r'\n  <link rel="stylesheet" href="/assets/workflow-path\.css\?v=[a-f0-9]{12}">','',text)
        if path in {'technology/index.html','find/index.html'}:
            for new,old in [(NEW_TITLE,OLD['technology']['seo_title']),(NEW_DESCRIPTION,OLD['technology']['description'])]:
                text=text.replace(escape(new,quote=True),escape(old,quote=True)).replace(new,old)
        if path=='technology/index.html':text=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda m:BASE['technology_schema'],text,count=1,flags=re.S)
        elif path in {'resources/index.html','start-here/index.html'}:text=text.replace('"dateModified": "2026-10-12"','"dateModified": "2026-10-11"')
    return text.encode() if binary else text
