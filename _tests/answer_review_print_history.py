"""Restore only the exact predecessor of the complete answer-review print copy.

Complete reviewed hashes gate every reversal. Unknown changes pass through,
and reconstructed bytes must match the independently captured parent hash.
This adapter is test-only and never runs in the published website.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = '2809bbf4a234331ab6413323f3d100ccc823bd0f'
PATHS = {
    '_source/technology/check-ai-answers.html',
    'assets/answer-review.css',
    'technology/check-ai-answers/index.html',
}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/answer-review-print-change.json').read_text(encoding='utf-8'))
    if (type(record.get('version')) is not int or record['version'] != 1
            or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown answer-review print predecessor')
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
            raise ValueError('Invalid answer-review print predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    previous = b''.join(parts)
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt answer-review print predecessor: ' + str(path))
    return previous if binary else previous.decode('utf-8')
