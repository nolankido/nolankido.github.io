"""Reverse only declared path promotion and Technology search metadata."""
from copy import deepcopy
from functools import lru_cache
from html import escape
from pathlib import Path
import json
import re
import practical_navigation_history
import local_fonts_history

# Freeze this release's reviewed copy. Historical adapters must load before
# production modules, and future editorial changes must not rewrite history.
NEW_TITLE = 'Practical AI Workflow, Tools & Checklists | Nolan Kido'
NEW_DESCRIPTION = 'Decide whether AI fits, write a brief, check its answer and compare the full cost. Follow four useful steps with free tools, guides and one private-use workbook.'

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def baseline():
    return json.loads((ROOT / '_tests/practical-path-baseline.json').read_text())

def pages(records):
    result = local_fonts_history.pages(records)
    old = next(p for p in baseline()['pages'] if p['id'] == 'technology')
    for p in result:
        if p['id'] == 'technology':
            for field in ('seo_title', 'description'): p[field] = old[field]
    return result

def before(path, data):
    data = practical_navigation_history.before(path, data)
    path = str(path)
    if path not in {'technology/index.html', 'resources/index.html', 'find/index.html'}: return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    pattern = r'<!-- Practical AI path: start -->\n.*?<!-- Practical AI path: end -->\n'
    text = re.sub(pattern, lambda m: baseline()['technology_promos'] if path == 'technology/index.html' else '', text, flags=re.S)
    text = re.sub(r'\n  <link rel="stylesheet" href="/assets/practical-ai-path[.]css[?]v=[a-f0-9]{12}">', '', text)
    old = next(p for p in baseline()['pages'] if p['id'] == 'technology')
    text = text.replace(escape(NEW_DESCRIPTION, quote=True), escape(old['description'], quote=True))
    text = text.replace(escape(NEW_TITLE, quote=True), escape(old['seo_title'], quote=True))
    if path == 'technology/index.html':
        def original_schema(match):
            schema = json.loads(match[1])
            if schema.get('mainEntity', {}).get('@id') == 'https://nolankido.com/technology/#practical-ai-path': schema.pop('mainEntity')
            schema['name'] = old['seo_title']
            schema['description'] = old['description']
            return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', original_schema, text)
    return text.encode() if binary else text
