"""Reverse only the exact reviewed short-lesson release for earlier contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/short-lessons-change.json').read_text())


def before(path, data):
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
    pairs = change()['pages']
    return [deepcopy(pairs[p['id']]['old']) if p['id'] in pairs and p == pairs[p['id']]['new'] else deepcopy(p) for p in records]


def outputs(records):
    return {path: before(path, text) for path, text in records.items()}


def files(paths):
    def keep(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256((ROOT / path).read_bytes()).hexdigest()
    return type(paths)(p for p in paths if keep(p))
