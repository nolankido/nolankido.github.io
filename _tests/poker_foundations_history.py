"""Reverse only the exact reviewed learning-entrance release for old contracts."""
from base64 import b64decode
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/poker-foundations-change.json').read_text())


def before(path, data):
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode()
    item = change()['paths'].get(str(path))
    if not item or sha256(raw).hexdigest() != item['new_sha256']:
        return data
    if 'old_base64' in item:
        restored = b64decode(item['old_base64'])
    else:
        text = raw.decode()
        for edit in reversed(item['edits']):
            assert text[edit['start']:edit['end']] == edit['new']
            text = text[:edit['start']] + edit['old'] + text[edit['end']:]
        restored = text.encode()
    assert sha256(restored).hexdigest() == item['old_sha256']
    return restored if binary else restored.decode()


def pages(records):
    pairs = change()['pages']
    return [deepcopy(pairs[p['id']]['old'])
            if p['id'] in pairs and p == pairs[p['id']]['new'] else deepcopy(p)
            for p in records]


def outputs(records):
    return {path: before(path, text) for path, text in records.items()}


def files(paths):
    # This release adds no product source, asset or download files.
    return paths
