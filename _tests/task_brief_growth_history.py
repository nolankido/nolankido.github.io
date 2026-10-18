"""Exact pre-Turn 03 view for legacy release contracts, test-only.

An entire-file SHA must match the approved candidate before any reversal. No
fuzzy source replacement or schema-level downgrade can conceal later changes.
This does not run in the published website.
"""
import turn09_weekly_reset_history
import base64
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
BASE = '9a9eaba7359cd9c3e4e7a92fffdd34f991a303df'

@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/task-brief-growth-change.json').read_text(encoding='utf-8'))
    if record.get('version') != 1 or record.get('base_commit') != BASE:
        raise ValueError('Unknown task-brief growth predecessor')
    return record


def before(path, data):
    data = turn09_weekly_reset_history.before(path,data)
    item = change()['paths'].get(str(path))
    if not item:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    try:
        restored = zlib.decompress(base64.b64decode(item['old_zlib_base64'], validate=True))
    except (ValueError, zlib.error) as exc:
        raise ValueError('Invalid task-brief predecessor snapshot: ' + str(path)) from exc
    if sha256(restored).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt task-brief predecessor: ' + str(path))
    return restored if binary else restored.decode('utf-8')


def pages(records):
    records = turn09_weekly_reset_history.pages(records)
    pair = change()['page']
    return [deepcopy(pair['old']) if page == pair['new'] else deepcopy(page)
            for page in records]


def outputs(records):
    return {p: before(p, v) for p, v in records.items()}
