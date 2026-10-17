"""Replay the exact pre-School release, without hiding subsequent edits.

This test-only view accepts a reversal only for an entire byte-identical reviewed
file or page record. Unknown bytes, altered additions and unrelated files remain
visible. It is not a transformation of the deployed site or a test bypass.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import homepage_growth_history
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '9021d4604c9427c37dc6c788753ddf9675dfc7ba'


@lru_cache(maxsize=1)
def change():
    value = json.loads((ROOT / '_tests/poker-school-change.json').read_text())
    if value.get('version') != 1 or value.get('base_commit') != BASE:
        raise ValueError('Unknown Poker School predecessor')
    return value


def before(path, data):
    data = homepage_growth_history.before(path, data)
    item = change()['paths'].get(str(path))
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if not item or sha256(raw).hexdigest() != item['new_sha256']:
        return data
    restored = raw.decode('utf-8')
    for edit in reversed(item['edits']):
        if restored[edit['start']:edit['end']] != edit['new']:
            raise ValueError('Corrupt Poker School change offset: ' + str(path))
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    restored = restored.encode('utf-8')
    if sha256(restored).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt Poker School predecessor: ' + str(path))
    return restored if binary else restored.decode('utf-8')


def pages(records):
    records = homepage_growth_history.pages(records)
    return [deepcopy(p) for p in records if p not in change()['new_pages']]


def _keep(path, data, additions):
    raw = data if isinstance(data, bytes) else data.encode('utf-8')
    return additions.get(str(path)) != sha256(raw).hexdigest()


def outputs(records):
    added = change()['new_outputs']
    return {p: before(p, data) for p, data in records.items() if _keep(p, data, added)}


def source_records(records):
    added = change()['new_files']
    return {p: before(p, data) for p, data in records.items() if _keep(p, data, added)}


def files(paths):
    def keep(path):
        p = Path(path)
        key = p.relative_to(ROOT).as_posix() if p.is_absolute() else p.as_posix()
        return _keep(key, (ROOT / p).read_bytes(), change()['new_files'])
    return type(paths)(p for p in paths if keep(p))
