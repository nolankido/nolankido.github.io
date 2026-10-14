"""Exact predecessor for the reviewed betting lesson and its discovery changes.

Only a complete reviewed digest permits reversal. Unrelated edits remain visible
to the existing historical contracts; no earlier golden hash is refreshed.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import checkpoint_history

ROOT = Path(__file__).resolve().parents[1]
ID = 'poker-betting-with-a-purpose'
OUTPUT = 'poker/betting-with-a-purpose/index.html'


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/betting-change.json').read_text())


def before(path, data):
    data = checkpoint_history.before(path, data)
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
    records = checkpoint_history.pages(records)
    return [p for p in records if p != change()['page']]


def outputs(records):
    records = checkpoint_history.outputs(records)
    return {p: before(p, value) for p, value in records.items()
            if change()['new_outputs'].get(str(p)) != sha256(value.encode()).hexdigest()}


def files(paths):
    paths = checkpoint_history.files(paths)
    def original(path):
        key = Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key) != sha256((ROOT / path).read_bytes()).hexdigest()
    return type(paths)(p for p in paths if original(p))
