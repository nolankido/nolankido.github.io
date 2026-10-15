"""Reverse only the exact reviewed tournament-budget publication for old contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'poker/tournament-trip-budget/index.html'

@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/tournament-budget-change.json').read_text())

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
    c = change()
    result = []
    for record in records:
        if record == c['page']:
            continue
        pair = c['pages'].get(record['id'])
        result.append(deepcopy(pair['old']) if pair and record == pair['new'] else deepcopy(record))
    return result

def outputs(records):
    return {p: before(p, v) for p, v in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(v.encode()).hexdigest()}

def files(paths):
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256((ROOT / path).read_bytes()).hexdigest()
    return type(paths)(p for p in paths if original(p))
