"""Reverse only the frozen local-address search change on its three paths."""
from functools import lru_cache
import json
from pathlib import Path
import turn10_profile_history
from poker_titles_history import before as before_poker_titles

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/search-addresses-change.json').read_text())


def before(path, data):
    data = before_poker_titles(path,turn10_profile_history.before(path,data))
    path = str(path)
    if path not in {'assets/site-find.js', '_source/find.html', 'find/index.html'}:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    source = '_source/find.html' if path == 'find/index.html' else path
    for old, new in reversed(change()['patches'][source]):
        text = text.replace(new, old, 1)
    if path == 'find/index.html':
        old, new = change()['script_versions']
        text = text.replace('/assets/site-find.js?v=' + new, '/assets/site-find.js?v=' + old, 1)
    return text.encode() if binary else text
