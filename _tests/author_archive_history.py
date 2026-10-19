"""Reverse only the declared archive additions for historical integrity checks."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json
import re
import turn10_profile_history
import practical_path_history

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def baseline():
    return json.loads((ROOT / '_tests/author-archive-baseline.json').read_text())

def pages(records):
    records = practical_path_history.pages(records)
    result = deepcopy(records)
    old = {p['id']: p for p in baseline()['pages']}
    for p in result:
        if p['id'] == 'about': p['updated'] = old['about']['updated']
    return result

def before(path, data):
    data = practical_path_history.before(path, turn10_profile_history.before(path,data))
    path = str(path)
    if path not in {'notes/index.html', 'about/index.html', 'sitemap.xml'}:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    if path in {'notes/index.html', 'about/index.html'}:
        text = re.sub(r'<!-- Author archive: start -->.*?<!-- Author archive: end -->', '', text, flags=re.S)
        text = re.sub(r'\n  <link rel="stylesheet" href="/assets/author-archive[.]css[?]v=[a-f0-9]{12}">', '', text)
        def original_schema(match):
            schema = json.loads(match[1])
            if path == 'notes/index.html':
                schema.pop('creator', None)
                schema.pop('mainEntity', None)
            else:
                old = next(p for p in baseline()['pages'] if p['id'] == 'about')
                schema['dateModified'] = old['updated']
            return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', original_schema, text)
    if path == 'sitemap.xml':
        old = next(p for p in baseline()['pages'] if p['id'] == 'about')
        text = re.sub(r'(<loc>https://nolankido.com/about/</loc>\s*<lastmod>)[^<]+(</lastmod>)', lambda m: m[1] + old['updated'] + m[2], text)
    return text.encode() if binary else text
