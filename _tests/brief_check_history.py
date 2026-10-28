"""Restore the exact published brief-to-check predecessor, for tests.

Whole successor hashes gate checked reverse character spans, and restored
bytes must match the independently captured whole parent hashes. Unknown
bytes and metadata stay visible. The later visibility sprint is reversed first.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/brief-check-change.json'
PARENT = '427f258ad895cfc736d3d29944347ea584f04826'
PARENT_TREE = 'f51ffdb98ccb618896e25d6d729cc7919536a92d'
PATHS = frozenset({
    '_source/pages.json', '_source/technology/task-brief.html',
    'assets/task-brief.css', 'assets/task-brief.js',
    'find/index.html', 'sitemap.xml', 'technology/task-brief/index.html',
})
PAGE_ID = 'task-brief'
# Complete manifest records captured from the actual parent and successor.
PAGE_HASHES = {
    'old': '1bd2f556b03ec17ac4f63839306624c422ec7eb34eab5fabdee4201dde95952d',
    'new': 'e79677b673c839648dc3f02b8e8b69710867cf4a028439d53b9a18e96e5764a6',
}


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def change() -> dict:
    record = json.loads(CHANGE.read_text(encoding='utf-8'))
    if (not isinstance(record, dict) or
            set(record) != {'version', 'parent_commit', 'parent_tree', 'paths', 'pages'} or
            type(record['version']) is not int or record['version'] != 1 or
            record['parent_commit'] != PARENT or
            record['parent_tree'] != PARENT_TREE or
            not isinstance(record['paths'], dict) or set(record['paths']) != PATHS or
            not isinstance(record['pages'], dict) or set(record['pages']) != {PAGE_ID}):
        raise ValueError('Unknown brief-check predecessor')
    for name, item in record['paths'].items():
        if (not isinstance(item, dict) or
                set(item) != {'current_sha256', 'parent_sha256', 'edits'} or
                any(not isinstance(item[field], str) or len(item[field]) != 64 or
                    any(c not in '0123456789abcdef' for c in item[field])
                    for field in ('current_sha256', 'parent_sha256'))):
            raise ValueError('Unknown brief-check file boundary: ' + name)
    pair = record['pages'][PAGE_ID]
    if (not isinstance(pair, dict) or set(pair) != {'old', 'new'} or
            not isinstance(pair['old'], dict) or not isinstance(pair['new'], dict)):
        raise ValueError('Unknown brief-check metadata boundary')
    current = pair['new']
    expected_old = {**current, 'updated': '2026-10-21'}
    if (current.get('id') != PAGE_ID or
            current.get('path') != '/technology/task-brief/' or
            current.get('updated') != '2026-10-27' or
            pair['old'] != expected_old or
            any(digest(json.dumps(pair[side], sort_keys=True, separators=(',', ':'),
                                  ensure_ascii=False).encode('utf-8')) != expected
                for side, expected in PAGE_HASHES.items())):
        raise ValueError('Unknown brief-check metadata boundary')
    return record


def key(path: str | Path) -> str:
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def before(path: str | Path, data: bytes | str) -> bytes | str:
    import visibility_sprint_history
    data = visibility_sprint_history.before(path, data)
    name = key(path)
    item = change()['paths'].get(name)
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if digest(raw) != item['current_sha256']:
        return data
    current = raw.decode('utf-8')
    edits = item['edits']
    if type(edits) is not list or not edits:
        raise ValueError('Invalid brief-check edits: ' + name)
    previous_end = 0
    for edit in edits:
        if (not isinstance(edit, dict) or
                set(edit) != {'start', 'end', 'current_sha256', 'old'} or
                type(edit['start']) is not int or type(edit['end']) is not int or
                not previous_end <= edit['start'] <= edit['end'] <= len(current) or
                not isinstance(edit['old'], str) or
                digest(current[edit['start']:edit['end']].encode('utf-8')) != edit['current_sha256']):
            raise ValueError('Invalid brief-check edit span: ' + name)
        previous_end = edit['end']
    restored = current
    for edit in reversed(edits):
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    original = restored.encode('utf-8')
    if digest(original) != item['parent_sha256']:
        raise ValueError('Invalid brief-check predecessor digest: ' + name)
    return original if binary else restored


def pages(records: list[dict]) -> list[dict]:
    """Restore only the complete approved task-brief record without mutation."""
    import visibility_sprint_history
    records = visibility_sprint_history.pages(records)
    pair = change()['pages'][PAGE_ID]
    return [deepcopy(pair['old'] if page == pair['new'] else page) for page in records]
