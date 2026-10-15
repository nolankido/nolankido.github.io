"""Exact predecessor for the reviewed checkpoint and its discovery changes.

Only a complete reviewed digest permits reversal. Unrelated edits remain visible
to the existing historical contracts; no earlier golden hash is refreshed.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import poker_course_history
import productivity_history

ROOT = Path(__file__).resolve().parents[1]
ID = 'poker-beginner-checkpoint'
OUTPUT = 'poker/beginner-checkpoint/index.html'


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/checkpoint-change.json').read_text())


def before(path, data):
    data = productivity_history.before(path, data)
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
    records = productivity_history.pages(records)
    c = change()
    return [deepcopy(c['old_page']) if p == c['new_page'] else deepcopy(p)
            for p in records if p != c['page']]


def outputs(records):
    records = productivity_history.outputs(records)
    return {p: before(p, value) for p, value in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(value.encode()).hexdigest()}


def files(paths):
    paths = productivity_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256(poker_course_history.before(key, (ROOT / path).read_bytes())).hexdigest()
    return type(paths)(p for p in paths if original(p))
