"""Reverse only five frozen search titles, never article identity or prose."""
from copy import deepcopy
from functools import lru_cache
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/study-titles-change.json').read_text())


def pages(records):
    result = deepcopy(records)
    for page in result:
        for entry in change()['entries']:
            if (page.get('id'), page.get('path'), page.get('seo_title')) == (entry['id'], entry['path'], entry['new']):
                page['seo_title'] = entry['old']
    return result


def before(path, data):
    path = str(path)
    entries = change()['entries']
    entry = next((e for e in entries if path == e['path'].lstrip('/') + 'index.html'), None)
    if path != '_source/pages.json' and entry is None:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    if path == '_source/pages.json':
        for old, new in change()['source_patches']:
            text = text.replace(new, old, 1)
    else:
        old, new = escape(entry['old'], quote=True), escape(entry['new'], quote=True)
        for prefix, suffix in [('<title>', '</title>'),
                               ('<meta property="og:title" content="', '">'),
                               ('<meta name="twitter:title" content="', '">')]:
            text = text.replace(prefix + new + suffix, prefix + old + suffix, 1)
        text = text.replace('"name": ' + json.dumps(entry['new'], ensure_ascii=False),
                            '"name": ' + json.dumps(entry['old'], ensure_ascii=False), 1)
    return text.encode() if binary else text
