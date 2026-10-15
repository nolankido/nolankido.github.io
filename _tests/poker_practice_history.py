"""Reverse only this reviewed practice-room release for older contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/poker-practice-change.json').read_text())


def before(path, data):
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
    pairs = change()['pages']
    return [deepcopy(pairs[r['id']]['old']) if r['id'] in pairs and r == pairs[r['id']]['new'] else deepcopy(r)
            for r in records if r != change()['new_pages'].get(r['id'])]


def outputs(records):
    return {p: before(p, value) for p, value in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(value.encode()).hexdigest()}


def files(paths):
    def retained(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256((ROOT / path).read_bytes()).hexdigest()
    return type(paths)(path for path in paths if retained(path))
