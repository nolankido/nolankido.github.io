"""Exact predecessor for removing a stale accessible field error, test-only."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json
import task_brief_walkthrough_history

ROOT = Path(__file__).resolve().parents[1]
BASE = '82c0a82df9969c2255e3c3ebbaacf290faeef78e'
PATHS = {'assets/task-brief.js', 'technology/task-brief/index.html'}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/task-brief-error-change.json').read_text(encoding='utf-8'))
    if (record.get('version') != 1 or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown task brief error predecessor')
    return record


def before(path, data):
    data = task_brief_walkthrough_history.before(path, data)
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
                or not offset <= start <= end <= len(raw)):
            raise ValueError('Invalid task brief error predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    original = b''.join(parts)
    if sha256(original).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt task brief error predecessor: ' + str(path))
    return original if binary else original.decode('utf-8')
