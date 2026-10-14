"""Undo only frozen font URLs, one preconnect and the reviewed privacy disclosure.

No old golden hashes are refreshed. The independent local-fonts baseline pins
all pre-release outputs and files directly from production Git objects.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import search_sections_history
import poker_titles_history

ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def baseline():return json.loads((ROOT/'_tests/local-fonts-baseline.json').read_text())

@lru_cache(maxsize=1)
def change():return json.loads((ROOT/'_tests/local-fonts-change.json').read_text())

def pages(records):
    result=poker_titles_history.pages(records)
    for p in result:
        if p['id']=='privacy' and p.get('updated')=='2026-10-13':p['updated']='2026-10-12'
    return result

def before(path,data):
    data=search_sections_history.before(path,data)
    path=str(path);b=baseline();c=change()
    if path not in b['outputs'] and path not in {'_source/pages.json','_source/privacy.html'}:return data
    binary=isinstance(data,bytes);text=data.decode() if binary else data
    if path=='assets/site-fonts.css':
        for old,new in c['urls'].items():text=text.replace('url('+new+')','url('+old+')')
    if path.endswith('.html') and path in b['outputs']:
        new='<link rel="stylesheet" href="/assets/site-fonts.css?v='+c['new_css_sha256'][:12]+'">'
        old='<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link rel="stylesheet" href="/assets/site-fonts.css?v='+b['outputs']['assets/site-fonts.css'][:12]+'">'
        text=text.replace(new,old,1)
    if path in {'_source/privacy.html','privacy/index.html'}:
        text=text.replace(c['privacy_new'],c['privacy_old'],1).replace(c['providers_new'],c['providers_old'],1)
        text=text.replace('Updated October 13, 2026','Updated October 12, 2026',1)
        text=text.replace('"dateModified": "2026-10-13"','"dateModified": "2026-10-12"',1)
    if path=='_source/pages.json':text=json.dumps(pages(json.loads(text)),indent=2,ensure_ascii=False)+'\n'
    if path=='sitemap.xml':text=text.replace('<loc>https://nolankido.com/privacy/</loc>\n    <lastmod>2026-10-13</lastmod>','<loc>https://nolankido.com/privacy/</loc>\n    <lastmod>2026-10-12</lastmod>',1)
    return text.encode() if binary else text
