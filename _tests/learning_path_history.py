"""Reverse only the exact reviewed beginner-route addition for older contracts."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import poker_course_history
import ranges_history

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/learning-path-change.json').read_text())


def before(path, data):
    data = ranges_history.before(path, data)
    entry = change()['paths'].get(str(path))
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode()
    if not entry or sha256(raw).hexdigest() != entry['new_sha256']:
        return data
    text = raw.decode()
    for edit in reversed(entry['edits']):
        assert text[edit['start']:edit['end']] == edit['new']
        text = text[:edit['start']] + edit['old'] + text[edit['end']:]
    assert sha256(text.encode()).hexdigest() == entry['old_sha256']
    return text.encode() if binary else text


def pages(records):
    records = ranges_history.pages(records)
    c = change()
    return [deepcopy(c['old_page']) if p == c['new_page'] else deepcopy(p) for p in records]


def outputs(records):
    records = ranges_history.outputs(records)
    return {p: before(p, value) for p, value in records.items()}


def files(paths):
    paths = ranges_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256(poker_course_history.before(key, (ROOT / path).read_bytes())).hexdigest()
    return type(paths)(p for p in paths if original(p))
