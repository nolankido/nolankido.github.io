"""Exact predecessor view for one published beginner guide and its discovery.

Reversal requires the complete reviewed new-file digest before applying frozen
edits at their exact offsets. Any unrelated change remains visible to old golden
checks. The independent beginner tests pin both inventories and new behavior.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import turn11_task_navigation_history as task_nav_history
import poker_course_history
import preflop_history

ROOT = Path(__file__).resolve().parents[1]
ID = 'poker-first-decisions'
OUTPUT = 'poker/first-decisions/index.html'


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/beginner-decisions-change.json').read_text())


def before(path, data):
    data = task_nav_history.before(path, data)
    data = preflop_history.before(path, data)
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
    records = task_nav_history.pages(records)
    records = preflop_history.pages(records)
    return [p for p in records if p != change()['page']]


def outputs(records):
    records = preflop_history.outputs(records)
    return {p: before(p, value) for p, value in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(value.encode()).hexdigest()}


def files(paths):
    paths = preflop_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256(poker_course_history.before(key, (ROOT / path).read_bytes())).hexdigest()
    return type(paths)(p for p in paths if original(p))
