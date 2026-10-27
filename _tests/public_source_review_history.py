"""Rewind exactly the October 27 public-source case review, for tests only.

The four complete successor hashes bind the reviewed change. Every replacement
span and restored predecessor is checked independently. Unknown edits remain
visible, and no public build code imports this historical view.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/public-source-review-change.json'
PARENT = 'a64bc51b6a39405a1ba59fbc589a9e190fce6229'
PARENT_TREE = '3fb7c1bb414db847c972516b5c558ce38712592c'
PATHS = frozenset({
    '_source/pages.json', '_source/technology/home.html',
    'technology/index.html', 'sitemap.xml',
})


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def change() -> dict:
    record = json.loads(CHANGE.read_text(encoding='utf-8'))
    if (set(record) != {'version', 'parent_commit', 'parent_tree', 'paths', 'page'} or
            type(record['version']) is not int or record['version'] != 1 or
            record['parent_commit'] != PARENT or record['parent_tree'] != PARENT_TREE or
            set(record['paths']) != PATHS):
        raise ValueError('Unknown public-source review predecessor')
    pair = record['page']
    if (set(pair) != {'old', 'new'} or
            pair['old'].get('id') != 'technology' or
            pair['old'].get('path') != '/technology/' or
            pair['old'].get('updated') != '2026-10-26' or
            pair['new'].get('updated') != '2026-10-27' or
            pair['old'] != {**pair['new'], 'updated': '2026-10-26'}):
        raise ValueError('Unknown public-source review metadata boundary')
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
        raise ValueError('Invalid public-source review edits: ' + name)
    previous_end = 0
    for edit in edits:
        if (not isinstance(edit, dict) or
                set(edit) != {'start', 'end', 'current_sha256', 'old'} or
                type(edit['start']) is not int or type(edit['end']) is not int or
                not previous_end <= edit['start'] <= edit['end'] <= len(current) or
                not isinstance(edit['old'], str) or
                digest(current[edit['start']:edit['end']].encode('utf-8')) != edit['current_sha256']):
            raise ValueError('Invalid public-source review edit span: ' + name)
        previous_end = edit['end']
    restored = current
    for edit in reversed(edits):
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    original = restored.encode('utf-8')
    if digest(original) != item['parent_sha256']:
        raise ValueError('Invalid public-source review predecessor digest: ' + name)
    return original if binary else restored


def pages(records: list[dict]) -> list[dict]:
    """Restore only the complete approved Technology record, without mutation."""
    pair = change()['page']
    return [deepcopy(pair['old'] if page == pair['new'] else page) for page in records]
