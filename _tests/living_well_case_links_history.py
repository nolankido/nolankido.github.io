"""Exact PR150 predecessor for the six contextual case links, for tests only.

Only complete reviewed bytes and records are restored. Unknown changes remain
visible to the older contracts. The published visibility capsule is immutable;
this separate leaf describes the later editorial revision.
"""
from __future__ import annotations

import base64
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/living-well-case-links-change.json'
PARENT = '116359834b8b48dbd1526c68392d89f9dd7bf1a0'
PARENT_TREE = '7ce0f278d05e262af96a32f105a89397aa5213cb'
SLUGS = frozenset({
    'scattered-notes-to-next-step', 'rough-idea-to-small-creation',
    'did-the-tool-actually-help', 'ai-and-personal-productivity',
})
SOURCES = frozenset({
    '_source/living-well/discovery.json',
    '_source/living-well/productivity.json',
})
# Captured only after the final source and generated output are reviewed.
CAPSULE_SHA256 = 'd370b6a1a3c7d1abfb2f9b991f1cef772ebf05ad9109e9cf7cea2abad98faab8'


def digest(data: bytes | str) -> str:
    return sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()


def signature(record) -> str:
    """Keep JSON types distinct, including booleans, integers and floats."""
    return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def key(path: str | Path) -> str:
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def _hash(value) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(c in '0123456789abcdef' for c in value))


def _path(value) -> bool:
    return (isinstance(value, str) and bool(value) and not value.startswith('/')
            and not any(part in {'', '.', '..'} for part in value.split('/')))


@lru_cache(maxsize=1)
def change() -> dict:
    raw = CHANGE.read_bytes()
    if not _hash(CAPSULE_SHA256) or digest(raw) != CAPSULE_SHA256:
        raise ValueError('Unknown Living Well case-link capsule digest')
    record = json.loads(raw)
    if (not isinstance(record, dict) or set(record) != {
            'version', 'parent_commit', 'parent_tree', 'paths', 'pages',
            'entries', 'parent_outputs'}
            or type(record['version']) is not int or record['version'] != 1
            or record['parent_commit'] != PARENT or record['parent_tree'] != PARENT_TREE
            or not isinstance(record['paths'], dict)
            or not isinstance(record['parent_outputs'], dict)
            or not SOURCES <= set(record['paths'])):
        raise ValueError('Unknown Living Well case-link predecessor')
    for name, item in record['paths'].items():
        if (not _path(name) or not isinstance(item, dict) or set(item) != {
                'current_sha256', 'parent_sha256', 'parent_size', 'parent_zlib_base64'}
                or not _hash(item['current_sha256']) or not _hash(item['parent_sha256'])
                or item['current_sha256'] == item['parent_sha256']
                or type(item['parent_size']) is not int or item['parent_size'] < 0
                or not isinstance(item['parent_zlib_base64'], str)):
            raise ValueError('Invalid Living Well case-link file boundary: ' + str(name))
    if any(not _path(name) or not _hash(value)
           for name, value in record['parent_outputs'].items()):
        raise ValueError('Invalid Living Well case-link output inventory')
    for field, identity, expected, immutable, allowed in [
            ('pages', 'id', {'living-well-' + s for s in SLUGS},
             ('id', 'path', 'date'), {'updated', 'revision'}),
            ('entries', 'slug', SLUGS,
             ('slug', 'published'), {'sections', 'updated', 'revision'})]:
        pairs = record[field]
        if not isinstance(pairs, list) or len(pairs) != len(expected):
            raise ValueError('Invalid Living Well case-link record boundary: ' + field)
        found = set()
        for pair in pairs:
            if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                    or not isinstance(pair['old'], dict) or not isinstance(pair['new'], dict)):
                raise ValueError('Invalid Living Well case-link record pair: ' + field)
            old, new = pair['old'], pair['new']
            if (new.get(identity) not in expected or new[identity] in found
                    or any(old.get(k) != new.get(k) for k in immutable)
                    or signature(old) == signature(new)
                    or {k for k in old.keys() | new.keys()
                        if k not in old or k not in new
                        or signature(old[k]) != signature(new[k])} - allowed
                    or new.get('updated') != '2026-10-28'
                    or not isinstance(new.get('revision'), str) or not new['revision'].strip()):
                raise ValueError('Invalid Living Well case-link record identity: ' + field)
            found.add(new[identity])
        if found != expected:
            raise ValueError('Incomplete Living Well case-link record boundary: ' + field)
    return record


def before(path: str | Path, data: bytes | str) -> bytes | str:
    item = change()['paths'].get(key(path))
    if item is None or digest(data) != item['current_sha256']:
        return data
    try:
        original = zlib.decompress(base64.b64decode(item['parent_zlib_base64'], validate=True))
    except (ValueError, zlib.error) as exc:
        raise ValueError('Invalid Living Well case-link predecessor encoding: ' + key(path)) from exc
    if len(original) != item['parent_size'] or digest(original) != item['parent_sha256']:
        raise ValueError('Invalid Living Well case-link predecessor digest: ' + key(path))
    return original if isinstance(data, bytes) else original.decode('utf-8')


def _records(records: list[dict], field: str) -> list[dict]:
    pairs = {signature(pair['new']): pair['old'] for pair in change()[field]}
    return [deepcopy(pairs.get(signature(record), record)) for record in records]


def pages(records: list[dict]) -> list[dict]:
    return _records(records, 'pages')


def entries(records: list[dict]) -> list[dict]:
    return _records(records, 'entries')


def outputs(records: dict) -> dict:
    return {path: before(path, value) for path, value in records.items()}
