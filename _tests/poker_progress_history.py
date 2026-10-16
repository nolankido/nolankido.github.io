"""Replay the exact pre-progress release without hiding unreviewed changes."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/poker-progress-change.json').read_text())


def before(path, data):
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode()
    item = change()['paths'].get(str(path))
    if not item or sha256(raw).hexdigest() != item['new_sha256']:
        return data
    value = raw.decode()
    for edit in reversed(item['edits']):
        assert value[edit['start']:edit['end']] == edit['new']
        value = value[:edit['start']] + edit['old'] + value[edit['end']:]
    assert sha256(value.encode()).hexdigest() == item['old_sha256']
    return value.encode() if binary else value


def pages(records):
    pairs = change()['pages']
    return [deepcopy(pairs[p['id']]['old'])
            if p['id'] in pairs and p == pairs[p['id']]['new'] else deepcopy(p)
            for p in records]


def source_records(records):
    added = change()['new_files']
    return {p: raw for p, raw in records.items()
            if added.get(str(p)) != sha256(raw).hexdigest()}


def files(paths):
    def keep(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256((ROOT / path).read_bytes()).hexdigest()
    return type(paths)(p for p in paths if keep(p))
