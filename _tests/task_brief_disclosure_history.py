"""Reverse only this turn's two exact changes for frozen historic snapshots.

This is test-only. It never mutates or weakens the published build, and it
cannot silently reverse a page carrying an unrelated change.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = 'a6aa35f61f65f96bb18a632ac77a6008987421b7'
PATHS = {'assets/task-brief.css', 'technology/task-brief/index.html'}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/task-brief-disclosure-change.json').read_text(encoding='utf-8'))
    if (record.get('version') != 1 or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown Task Brief disclosure predecessor')
    return record


def before(path, data):
    import task_brief_print_history
    data = task_brief_print_history.before(path, data)
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    new, old = item['new'].encode(), item['old'].encode()
    if raw.count(new) != 1:
        raise ValueError('Ambiguous Task Brief predecessor: ' + str(path))
    previous = raw.replace(new, old, 1)
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt Task Brief predecessor: ' + str(path))
    return previous if binary else previous.decode('utf-8')
