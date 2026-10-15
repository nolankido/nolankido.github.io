"""Exact predecessor view for one published postflop guide and its discovery.

Reversal requires the complete reviewed new-file digest before applying frozen
edits at their exact offsets. Any unrelated change remains visible to old golden
checks. The independent beginner tests pin both inventories and new behavior.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import river_history

ROOT = Path(__file__).resolve().parents[1]
ID = 'poker-first-flop-decisions'
OUTPUT = 'poker/first-flop-decisions/index.html'


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/flop-change.json').read_text())


def before(path, data):
    data = river_history.before(path, data)
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
    records = river_history.pages(records)
    return [p for p in records if p != change()['page']]


def outputs(records):
    records = river_history.outputs(records)
    return {p: before(p, value) for p, value in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(value.encode()).hexdigest()}


def files(paths):
    paths = river_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256(river_history.before(key, (ROOT / path).read_bytes())).hexdigest()
    return type(paths)(p for p in paths if original(p))
