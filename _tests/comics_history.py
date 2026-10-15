"""Reverse only the exact comic publication for earlier content contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import getting_started_history

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/comics-change.json').read_text())

def before(path, data):
    data = getting_started_history.before(path, data)
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
    records = getting_started_history.pages(records)
    return [deepcopy(p) for p in records if p not in change()['pages']]

def outputs(records):
    records = getting_started_history.outputs(records)
    return {p: before(p, v) for p, v in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(v.encode()).hexdigest()}

def files(paths):
    paths = getting_started_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        raw = getting_started_history.before(key, (ROOT / path).read_bytes())
        return change()['new_files'].get(key) != sha256(raw).hexdigest()
    return type(paths)(p for p in paths if original(p))
