"""Exact test-only predecessor for the optional meeting walkthrough."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json
import resource_review_history

ROOT = Path(__file__).resolve().parents[1]
BASE = '564a9d7eaf634497767ade3db4bcb6a3b2bd9c61'
PATHS = {'_source/pages.json', '_source/technology/task-brief.html',
         'sitemap.xml', 'technology/task-brief/index.html'}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/task-brief-walkthrough-change.json').read_text(encoding='utf-8'))
    if (record.get('version') != 1 or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown task brief walkthrough predecessor')
    return record


def before(path, data):
    data = resource_review_history.before(path, data)
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
            raise ValueError('Invalid walkthrough predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    old = b''.join(parts)
    if sha256(old).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt walkthrough predecessor: ' + str(path))
    return old if binary else old.decode('utf-8')


def pages(records):
    # This metadata entry point is also called directly by older contracts.
    # Rewind only the exact later Task Brief record before matching its pair.
    import brief_check_history
    records = brief_check_history.pages(records)
    pair = change()['page']
    return [deepcopy(pair['old'] if page == pair['new'] else page) for page in records]
