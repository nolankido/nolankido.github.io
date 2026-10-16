"""Reverse only the SHA-bound card-foundation release for earlier contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import round_practice_history
ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/hand-lab-change.json').read_text())


def before(path, data):
    data = round_practice_history.before(path, data)
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
    records = round_practice_history.pages(records)
    return [deepcopy(change()['pages'][p['id']]['old']) if p['id'] in change()['pages'] and p == change()['pages'][p['id']]['new'] else deepcopy(p) for p in records]


def outputs(records):
    records = round_practice_history.outputs(records)
    return {path: before(path, text) for path, text in records.items()}


def files(paths):
    paths = round_practice_history.files(paths)
    def keep(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256(round_practice_history.before(key, (ROOT / path).read_bytes())).hexdigest()
    return type(paths)(path for path in paths if keep(path))
