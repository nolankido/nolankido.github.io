"""Exact test-only predecessor for the integrated Weekly Reset release.

The six reviewed production changes restore the actual published parent only
when their complete hashes match. Unknown edits and partial metadata remain
visible. Published historical baseline records are never refreshed here.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json
import zlib

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b5cfbd5d6abee0ce1082cf14deecb508f0996e6e'


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/turn09-weekly-reset-change.json').read_text(encoding='utf-8'))
    if record.get('version') != 2 or record.get('base_commit') != BASE:
        raise ValueError('Unknown integrated weekly-reset predecessor')
    return record


def before(path, data):
    import profile_datetime_history
    data = profile_datetime_history.before(path, data)
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    restored = zlib.decompress(base64.b64decode(item['old_zlib_base64'], validate=True))
    if sha256(restored).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt Weekly Reset predecessor: ' + str(path))
    return restored if binary else restored.decode('utf-8')


def pages(records):
    pairs = change()['page_pairs']
    result = []
    for page in records:
        match = next((pair for pair in pairs if page == pair['new']), None)
        result.append(deepcopy(match['old'] if match else page))
    return result


def original_entry(entry):
    pair = change()['entry_pair']
    return deepcopy(pair['old'] if entry == pair['new'] else entry)


def outputs(records):
    return {path: before(path, value) for path, value in records.items()}
