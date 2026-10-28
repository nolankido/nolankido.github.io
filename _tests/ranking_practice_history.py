"""Restore the exact published ranking-to-practice predecessor, for tests.

Whole successor hashes gate checked reverse character spans, and restored
bytes must match the independently captured whole parent hashes. Unknown
bytes and metadata stay visible. This leaf has no build or history imports.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/ranking-practice-change.json'
PARENT = 'dfdcdc64dd096f7bdcab0569f19d6cc466c5584b'
PARENT_TREE = 'bfce9e3713ff4413450aff2dccb1a0b326f38748'
PATHS = frozenset({
    '_source/pages.json', '_source/poker/hand-rankings.html',
    'assets/poker-hand-lab.css', 'find/index.html', 'poker/find/index.html',
    'poker/free-poker-learning-path/index.html',
    'poker/hand-rankings/index.html', 'sitemap.xml',
})
PAGE_ID = 'poker-hand-rankings'
REVISION = ('Connected the showdown explanations to the existing card-building '
            'practice and a private correction note.')
# Canonical complete records captured from the actual parent and successor
# manifests, so coordinated changes to both metadata sides also fail closed.
PAGE_HASHES = {
    'old': '5f74c41b73824704c9aade17691f6ef16425f593461baa0457245ce3aee5cf9c',
    'new': '9510786356074de150f5cca88f9c14febadb86acb23b89bd66df8df8d6d16cd7',
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
        raise ValueError('Unknown ranking-practice predecessor')
    for name, item in record['paths'].items():
        if (not isinstance(item, dict) or
                set(item) != {'current_sha256', 'parent_sha256', 'edits'} or
                any(not isinstance(item[field], str) or len(item[field]) != 64 or
                    any(c not in '0123456789abcdef' for c in item[field])
                    for field in ('current_sha256', 'parent_sha256'))):
            raise ValueError('Unknown ranking-practice file boundary: ' + name)
    pair = record['pages'][PAGE_ID]
    if (not isinstance(pair, dict) or set(pair) != {'old', 'new'} or
            not isinstance(pair['old'], dict) or not isinstance(pair['new'], dict)):
        raise ValueError('Unknown ranking-practice metadata boundary')
    current = pair['new']
    expected_old = {key: value for key, value in current.items()
                    if key not in {'updated', 'revision'}}
    expected_old['updated'] = '2026-10-05'
    if (current.get('id') != PAGE_ID or
            current.get('path') != '/poker/hand-rankings/' or
            current.get('date') != '2026-10-05' or
            current.get('updated') != '2026-10-27' or
            current.get('revision') != REVISION or pair['old'] != expected_old or
            any(digest(json.dumps(pair[side], sort_keys=True, separators=(',', ':'),
                                  ensure_ascii=False).encode('utf-8')) != expected
                for side, expected in PAGE_HASHES.items())):
        raise ValueError('Unknown ranking-practice metadata boundary')
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
        raise ValueError('Invalid ranking-practice edits: ' + name)
    previous_end = 0
    for edit in edits:
        if (not isinstance(edit, dict) or
                set(edit) != {'start', 'end', 'current_sha256', 'old'} or
                type(edit['start']) is not int or type(edit['end']) is not int or
                not previous_end <= edit['start'] <= edit['end'] <= len(current) or
                not isinstance(edit['old'], str) or
                digest(current[edit['start']:edit['end']].encode('utf-8')) != edit['current_sha256']):
            raise ValueError('Invalid ranking-practice edit span: ' + name)
        previous_end = edit['end']
    restored = current
    for edit in reversed(edits):
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    original = restored.encode('utf-8')
    if digest(original) != item['parent_sha256']:
        raise ValueError('Invalid ranking-practice predecessor digest: ' + name)
    return original if binary else restored


def pages(records: list[dict]) -> list[dict]:
    """Restore only the complete approved guide record without mutation."""
    pair = change()['pages'][PAGE_ID]
    return [deepcopy(pair['old'] if page == pair['new'] else page) for page in records]
