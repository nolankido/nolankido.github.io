"""Restore only the exact parent files before this region-routing UI and CI change.

This historical adapter is test-only. Unknown bytes are never rewritten.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = '4bf860988f903a11becaf008bc6446c6bbde34bb'
PATHS = {'_scripts/poker_resources.py', '_source/poker/resources.html', 'poker/resources/index.html', '.github/workflows/site-checks.yml'}

@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/regional-link-change.json').read_text(encoding='utf-8'))
    if (type(record.get('version')) is not int or record['version'] != 1
            or record.get('base_commit') != BASE or set(record.get('paths', {})) != PATHS):
        raise ValueError('Unknown regional-link predecessor')
    return record

def before(path, data):
    import later_release_history
    data = later_release_history.before(path, data)
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    restored = raw.decode('utf-8')
    for edit in item['edits']:
        if (not isinstance(edit, dict) or set(edit) != {'new', 'old', 'count'}
                or not isinstance(edit['new'], str) or not edit['new']
                or not isinstance(edit['old'], str) or type(edit['count']) is not int
                or edit['count'] < 1 or restored.count(edit['new']) != edit['count']):
            raise ValueError('Corrupt regional-link reversal')
        restored = restored.replace(edit['new'], edit['old'])
    previous = restored.encode('utf-8')
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt regional-link parent digest')
    return previous if binary else restored
