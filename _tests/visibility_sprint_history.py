"""Exact predecessor views for the reviewed visibility sprint, for tests only.

The capsule is tied to one Git parent and one complete capsule digest. Only
whole recognized successor files, additions, and page records are rewound.
Unknown changes remain visible to older contracts. Runtime code never imports
this module; current behavior is tested without this historical view.
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
CHANGE = ROOT / '_tests/visibility-sprint-change.json'
PARENT = '2aae4923318c0028d98266d78f6e4aabea295387'
PARENT_TREE = '5cb303f7aec831e6f02f152455dbb2306e83fb37'
# Set only after the completed source and generated output have been reviewed.
CAPSULE_SHA256 = '0b2018bdcf934a2dc6e2b843cb47dd9f28a7f7c754ff26a7209f269b4ec93525'


def digest(data: bytes | str) -> str:
    return sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()


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
        raise ValueError('Unknown visibility-sprint capsule digest')
    record = json.loads(raw)
    if (not isinstance(record, dict) or set(record) != {
            'version', 'parent_commit', 'parent_tree', 'paths', 'added_files',
            'added_outputs', 'added_targets', 'pages', 'parent_outputs'}
            or type(record['version']) is not int or record['version'] != 1
            or record['parent_commit'] != PARENT or record['parent_tree'] != PARENT_TREE
            or any(not isinstance(record[field], dict) for field in
                   ['paths', 'added_files', 'added_outputs', 'added_targets', 'parent_outputs'])
            or not isinstance(record['pages'], list)):
        raise ValueError('Unknown visibility-sprint predecessor')
    for name, item in record['paths'].items():
        if (not _path(name) or not isinstance(item, dict) or set(item) != {
                'current_sha256', 'parent_sha256', 'parent_size', 'parent_zlib_base64'}
                or not _hash(item['current_sha256']) or not _hash(item['parent_sha256'])
                or item['current_sha256'] == item['parent_sha256']
                or type(item['parent_size']) is not int or item['parent_size'] < 0
                or not isinstance(item['parent_zlib_base64'], str)):
            raise ValueError('Invalid visibility-sprint file boundary: ' + str(name))
    for field in ['added_files', 'added_outputs', 'parent_outputs']:
        if any(not _path(name) or not _hash(value) for name, value in record[field].items()):
            raise ValueError('Invalid visibility-sprint inventory: ' + field)
    if (set(record['paths']) & set(record['added_files'])
            or any(record['added_files'].get(name) != value
                   for name, value in record['added_outputs'].items())):
        raise ValueError('Conflicting visibility-sprint additions')
    for route, item in record['added_targets'].items():
        if (not isinstance(route, str) or not route.startswith('/') or route.startswith('//')
                or '?' in route or '#' in route or not isinstance(item, dict)
                or set(item) != {'status', 'sha256'} or type(item['status']) is not int
                or item['status'] != 200 or not _hash(item['sha256'])):
            raise ValueError('Invalid visibility-sprint live target')
    seen = set()
    for pair in record['pages']:
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not isinstance(pair['new'], dict)
                or (pair['old'] is not None and not isinstance(pair['old'], dict))
                or not isinstance(pair['new'].get('id'), str)
                or not isinstance(pair['new'].get('path'), str)
                or pair['old'] == pair['new']):
            raise ValueError('Invalid visibility-sprint metadata boundary')
        if pair['old'] is not None and any(
                pair['old'].get(field) != pair['new'][field] for field in ['id', 'path']):
            raise ValueError('Visibility-sprint metadata cannot rename existing identities')
        signature = json.dumps(pair['new'], sort_keys=True, ensure_ascii=False)
        if signature in seen:
            raise ValueError('Duplicate visibility-sprint metadata boundary')
        seen.add(signature)
    return record


def before(path: str | Path, data: bytes | str) -> bytes | str:
    import living_well_case_links_history
    data = living_well_case_links_history.before(path, data)
    item = change()['paths'].get(key(path))
    if item is None or digest(data) != item['current_sha256']:
        return data
    try:
        original = zlib.decompress(base64.b64decode(item['parent_zlib_base64'], validate=True))
    except (ValueError, zlib.error) as exc:
        raise ValueError('Invalid visibility-sprint predecessor encoding: ' + key(path)) from exc
    if len(original) != item['parent_size'] or digest(original) != item['parent_sha256']:
        raise ValueError('Invalid visibility-sprint predecessor digest: ' + key(path))
    return original if isinstance(data, bytes) else original.decode('utf-8')


def pages(records: list[dict]) -> list[dict]:
    """Restore complete records only; a duplicate added record stays detectable."""
    import living_well_case_links_history
    records = living_well_case_links_history.pages(records)
    result = []
    removed = set()
    pairs = change()['pages']
    # JSON signatures distinguish booleans from equal-valued integers, unlike
    # Python dict equality. A type mutation must remain an unreviewed record.
    signatures = {json.dumps(pair['new'], sort_keys=True, ensure_ascii=False): i
                  for i, pair in enumerate(pairs)}
    for page in records:
        match = signatures.get(json.dumps(page, sort_keys=True, ensure_ascii=False))
        if match is None:
            result.append(deepcopy(page))
        elif pairs[match]['old'] is not None:
            result.append(deepcopy(pairs[match]['old']))
        elif match in removed:
            result.append(deepcopy(page))
        else:
            removed.add(match)
    return result


def _records(records: dict, additions: dict) -> dict:
    return {path: before(path, value) for path, value in records.items()
            if additions.get(key(path)) != digest(value)}


def outputs(records: dict) -> dict:
    return _records(records, change()['added_outputs'])


def source_records(records: dict) -> dict:
    return _records(records, change()['added_files'])


def files(paths):
    additions = change()['added_files']
    def keep(path):
        name = key(path)
        expected = additions.get(name)
        return expected is None or digest((ROOT / name).read_bytes()) != expected
    return type(paths)(path for path in paths if keep(path))


def live_targets(records: dict) -> dict:
    """Remove only the exact newly added successful release responses."""
    additions = change()['added_targets']
    def keep(route, response):
        item = additions.get(route)
        if (item is None or not isinstance(response, tuple) or len(response) != 2
                or type(response[0]) is not int or not isinstance(response[1], bytes)):
            return True
        return response[0] != item['status'] or digest(response[1]) != item['sha256']
    return {route: response for route, response in records.items() if keep(route, response)}
