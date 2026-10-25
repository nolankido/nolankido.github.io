"""Restore this print repair's exact predecessor for frozen release tests.

Only complete files with the reviewed new hash can be reversed. Unknown
changes pass through, and the reconstructed predecessor must match its hash.
This adapter is test-only and does not run in the published website.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f3067cc36286eb4adbe7aa15024f49a414008d4d'
PATHS = {'_source/technology/task-brief.html', 'assets/task-brief.css',
         'assets/task-brief.js', 'technology/task-brief/index.html'}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/task-brief-print-change.json').read_text(encoding='utf-8'))
    if (record.get('version') != 1 or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown Task Brief print predecessor')
    return record


def before(path, data):
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    parts, offset = [], 0
    for start, end, replacement in item['edits']:
        if (type(start) is not int or type(end) is not int
                or not offset <= start <= end <= len(raw)
                or not isinstance(replacement, str)):
            raise ValueError('Invalid Task Brief print predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    previous = b''.join(parts)
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt Task Brief print predecessor: ' + str(path))
    return previous if binary else previous.decode('utf-8')
