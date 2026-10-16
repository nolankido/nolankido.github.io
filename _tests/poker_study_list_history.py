"""Reverse only the exact reviewed study-list controls, styles and export delta."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import poker_progress_history

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/poker-study-list-change.json').read_text())


def before(path, data):
    data = poker_progress_history.before(path, data)
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
