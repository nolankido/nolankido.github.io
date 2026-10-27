"""Reconstruct only the reviewed Turn 02 homepage delta for older contracts.

Whole-file matching prevents this adapter from concealing later changes. This
module is used by tests only; deployed page generation does not invoke it.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import creative_print_history
import task_brief_growth_history
import turn04_public_source_history

ROOT = Path(__file__).resolve().parents[1]
BASE = '8f63c0436a45256cb2987cd93f77a9ef6e85df1b'


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/homepage-growth-change.json').read_text(encoding='utf-8'))
    if record.get('version') != 1 or record.get('base_commit') != BASE:
        raise ValueError('Unknown homepage predecessor')
    return record


def before(path, data):
    data = creative_print_history.before(path, data)
    import answer_review_growth_history as growth_history
    data = growth_history.before(path, data)
    data = turn04_public_source_history.before(path, data)
    data = task_brief_growth_history.before(path, data)
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    item = change()['paths'].get(str(path))
    if item is None or sha256(raw).hexdigest() != item['new_sha256']:
        return data
    restored = raw.decode('utf-8')
    for edit in reversed(item['edits']):
        start, end = edit['start'], edit['end']
        if (type(start) is not int or type(end) is not int
                or not 0 <= start <= end <= len(restored)
                or restored[start:end] != edit['new']):
            raise ValueError('Corrupt homepage change offset: ' + str(path))
        restored = restored[:start] + edit['old'] + restored[end:]
    result = restored.encode('utf-8')
    if sha256(result).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt homepage predecessor: ' + str(path))
    return result if binary else restored


def pages(records):
    import answer_review_growth_history as growth_history
    records = growth_history.pages(records)
    records = task_brief_growth_history.pages(records)
    pairs = change()['pages']
    return [deepcopy(pairs[p['id']]['old'])
            if p['id'] in pairs and p == pairs[p['id']]['new'] else deepcopy(p)
            for p in records]


def outputs(records):
    import later_release_history
    records = later_release_history.outputs(records)
    return {path: before(path, value) for path, value in records.items()}


def source_records(records):
    import later_release_history
    records = later_release_history.source_records(records)
    return {path: before(path, value) for path, value in records.items()}
