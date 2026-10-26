"""Exact test-only predecessor for the public-page feedback handoff.

Never normalize an unrecognized edit or rewrite an older release baseline.
This adapter is not imported by public build or runtime code.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json
import task_brief_error_history

ROOT = Path(__file__).resolve().parents[1]
BASE = '9ada5f1041f54a311f5142cb520d5f75edf3e2cd'


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/feedback-context-change.json').read_text(encoding='utf-8'))
    if record.get('version') != 1 or record.get('base_commit') != BASE:
        raise ValueError('Unknown feedback context predecessor')
    return record


def before(path, data):
    import study_inquiry_history
    data = study_inquiry_history.before(path, data)
    data = task_brief_error_history.before(path, data)
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
            raise ValueError('Invalid feedback predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    original = b''.join(parts)
    if sha256(original).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt feedback context predecessor: ' + str(path))
    return original if binary else original.decode('utf-8')
