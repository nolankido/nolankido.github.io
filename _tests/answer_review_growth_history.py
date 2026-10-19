"""Exact predecessor for the integrated AI answer-checking revision.

Test-only: recognize complete approved byte snapshots, then restore the actual
published main that immediately preceded this guide release. Unknown versions
and altered metadata remain visible to the older preservation tests.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '2f124944fe27569521382d06965b7dff8e5f618a'


@lru_cache(maxsize=1)
def change():
    data = json.loads((ROOT / '_tests/answer-review-growth-change.json').read_text(encoding='utf-8'))
    if data.get('version') != 2 or data.get('base_commit') != BASE:
        raise ValueError('Unknown integrated answer-checking predecessor')
    return data


def record():
    return change()['paths']


def before(path, data):
    item = record().get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    value = raw.decode('utf-8')
    for edit in reversed(item['edits']):
        start, end = edit['start'], edit['end']
        if (type(start) is not int or type(end) is not int
                or not 0 <= start <= end <= len(value)
                or value[start:end] != edit['new']):
            raise ValueError('Corrupt answer-checking predecessor edit')
        value = value[:start] + edit['old'] + value[end:]
    previous = value.encode('utf-8')
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt answer-checking predecessor digest')
    return previous if binary else value



def pages(records):
    """Restore only an exactly matching approved guide metadata record."""
    pairs = change()['page_pairs']
    result = []
    for page in records:
        matching = next((pair for pair in pairs if page == pair['new']), None)
        result.append(deepcopy(matching['old'] if matching else page))
    return result
