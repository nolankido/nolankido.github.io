"""Reverse only the exact reviewed hub navigation for predecessor contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import poker_course_history
ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/poker-routes-change.json').read_text())


def before(path, data):
    data = poker_course_history.before(path, data)
    entry = change()['paths'].get(str(path))
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode()
    if not entry or sha256(raw).hexdigest() != entry['new_sha256']:
        return data
    value = raw.decode()
    for edit in reversed(entry['edits']):
        assert value[edit['start']:edit['end']] == edit['new']
        value = value[:edit['start']] + edit['old'] + value[edit['end']:]
    assert sha256(value.encode()).hexdigest() == entry['old_sha256']
    return value.encode() if binary else value


def pages(records):
    records = poker_course_history.pages(records)
    pairs = change()['pages']
    return [deepcopy(pairs[r['id']]['old']) if r['id'] in pairs and r == pairs[r['id']]['new'] else deepcopy(r) for r in records]


def outputs(records):
    records = poker_course_history.outputs(records)
    return {p: before(p, v) for p, v in records.items()}


def files(paths):
    paths = poker_course_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256(poker_course_history.before(key, (ROOT / path).read_bytes())).hexdigest()
    return type(paths)(p for p in paths if original(p))
