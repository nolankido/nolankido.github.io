"""Reverse only frozen public-title search metadata and its runtime patches."""
from functools import lru_cache
import json
from pathlib import Path
from beginner_history import before as before_beginner

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/search-public-titles-change.json').read_text())


def before(path, data):
    data = before_beginner(path, data)
    path = str(path)
    if path not in change()['patches']:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    for old, new in reversed(change()['patches'][path]):
        text = text.replace(new, old, 1)
    if path == 'find/index.html':
        old, new = change()['script_versions']
        text = text.replace('/assets/site-find.js?v=' + new, '/assets/site-find.js?v=' + old, 1)
    return text.encode() if binary else text
