"""Restore only the exact reviewed rules-reference delta for older contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import poker_school_history
import poker_search_history
import poker_progress_history

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/rules-reference-change.json').read_text())


def before(path, data):
    data = poker_search_history.before(path, data)
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode()
    item = change()['paths'].get(str(path))
    if not item or sha256(raw).hexdigest() != item['new_sha256']:
        return data
    text = raw.decode()
    for edit in reversed(item['edits']):
        assert text[edit['start']:edit['end']] == edit['new']
        text = text[:edit['start']] + edit['old'] + text[edit['end']:]
    assert sha256(text.encode()).hexdigest() == item['old_sha256']
    return text.encode() if binary else text


def pages(records):
    records = poker_progress_history.pages(records)
    pairs = change()['pages']
    return [deepcopy(pairs[p['id']]['old']) if p['id'] in pairs and p == pairs[p['id']]['new'] else deepcopy(p) for p in records]


def outputs(records):
    records = poker_school_history.outputs(records)
    return {path: before(path, value) for path, value in records.items()}


def resources(records):
    pairs = change()['resources']
    return [deepcopy(pairs[r['id']]['old']) if r['id'] in pairs and r == pairs[r['id']]['new'] else deepcopy(r) for r in records]
