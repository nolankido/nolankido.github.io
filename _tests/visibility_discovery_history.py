"""Exact published PR151 predecessor for the next discovery release.

This test-only leaf restores complete reviewed bytes and page records. It
removes an added file or live response only when its full digest matches the
reviewed release. Unrecognized changes remain visible to older contracts.
"""
from __future__ import annotations

import base64
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from hashlib import sha1
import zlib

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/visibility-discovery-change.json'
PARENT = '1f315095cef741bd1afe6fe3bcba8b11216b0d0e'
PARENT_TREE = '0755a76bd631e9fec24950f4a14eed242f7f6d01'
# Captured after all production changes and generated output are reviewed.
CAPSULE_SHA256 = 'cf839b940bb1b01e374dc218c5355500b8af0357cf049bf468e2c67121d8ce14'


def digest(data: bytes | str) -> str:
    return sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()


def signature(record) -> str:
    """Distinguish JSON types and missing fields from explicit null values."""
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
        raise ValueError('Unknown visibility-discovery capsule digest')
    record = json.loads(raw)
    if (not isinstance(record, dict) or set(record) != {
            'version', 'parent_commit', 'parent_tree', 'paths', 'added_files',
            'added_outputs', 'added_targets', 'pages', 'parent_outputs'}
            or type(record['version']) is not int or record['version'] != 1
            or record['parent_commit'] != PARENT or record['parent_tree'] != PARENT_TREE
            or any(not isinstance(record[field], dict) for field in
                   ['paths', 'added_files', 'added_outputs', 'added_targets', 'parent_outputs'])
            or not isinstance(record['pages'], list)):
        raise ValueError('Unknown visibility-discovery predecessor')
    for name, item in record['paths'].items():
        if (not _path(name) or not isinstance(item, dict) or set(item) != {
                'current_sha256', 'parent_sha256', 'parent_size', 'parent_zlib_base64'}
                or not _hash(item['current_sha256']) or not _hash(item['parent_sha256'])
                or item['current_sha256'] == item['parent_sha256']
                or type(item['parent_size']) is not int or item['parent_size'] < 0
                or not isinstance(item['parent_zlib_base64'], str)):
            raise ValueError('Invalid visibility-discovery file boundary: ' + str(name))
    for field in ['added_files', 'added_outputs', 'parent_outputs']:
        if any(not _path(name) or not _hash(value) for name, value in record[field].items()):
            raise ValueError('Invalid visibility-discovery inventory: ' + field)
    if (set(record['paths']) & set(record['added_files'])
            or any(record['added_files'].get(name) != value
                   for name, value in record['added_outputs'].items())):
        raise ValueError('Conflicting visibility-discovery additions')
    for route, item in record['added_targets'].items():
        if (not isinstance(route, str) or not route.startswith('/') or route.startswith('//')
                or '?' in route or '#' in route or not isinstance(item, dict)
                or set(item) != {'status', 'sha256'} or type(item['status']) is not int
                or item['status'] != 200 or not _hash(item['sha256'])):
            raise ValueError('Invalid visibility-discovery live target')
    seen = set()
    for pair in record['pages']:
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not isinstance(pair['old'], dict) or not isinstance(pair['new'], dict)):
            raise ValueError('Invalid visibility-discovery page pair')
        old, new = pair['old'], pair['new']
        if (not isinstance(new.get('id'), str) or not isinstance(new.get('path'), str)
                or any(signature(old.get(k)) != signature(new.get(k)) for k in ['id', 'path'])
                or signature(old) == signature(new)
                or {k for k in old.keys() | new.keys()
                    if k not in old or k not in new or signature(old[k]) != signature(new[k])}
                    - {'title', 'seo_title', 'description', 'updated', 'revision', 'entry_summary'}
                or signature(new) in seen):
            raise ValueError('Invalid visibility-discovery page identity')
        seen.add(signature(new))
    return record



# October 29, 2026: deliberate long-form update to one already-published
# practical-AI article. Restore only exact recognized blobs before applying
# the frozen PR152 predecessor. Unknown edits must remain visible. Both
# original blobs occur at the pinned, CI-fetched PR151 commit (PARENT).
STUDY_NEW_BLOBS = {
    '_source/technology/local-ai-review-replies.html': '0f18088f086c70dd03016104f22afc1353dc5b34',
    'technology/local-ai-review-replies/index.html': '5e7557339494a52140df0a646f54b99146af4ed5',
    'find/index.html': '58378f58f7f531c18b2feb5eec852e835a7df86a',
}
STUDY_OLD_BLOBS = {
    '_source/technology/local-ai-review-replies.html': '1034845cba7b9627fe8e2de1074c04249caaff39',
    'technology/local-ai-review-replies/index.html': '31d72d70965ec623eb0fdd6674972ebec3789f89',
    'find/index.html': '88d402570c19e1e4e266410a5b7e74234b38194c',
}


def _blob_sha(raw: bytes) -> str:
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()



# Only the search-section entry for this page changes. The index's other
# 194 or more canonical page records and all shared label IDs stay intact.
# The two arrays are fixed snapshots; do not infer a restoration from any
# unknown or unreviewed text. Check both complete Git blob IDs.
_STUDY_SECTION_OLD = [
    'reply-task', "Use AI to draft a customer reply, with the owner's policy beside it.",
    'reply-example', 'Keep the double charge and the unanswered question visible.',
    'reply-boundary', 'Separate writing, authorization, and approval.',
    'reply-failure', 'A checker rejected harmless wording and accepted a missing detail.',
    'reply-try', 'Start with the fictional example.',
    'reply-sources', 'What this project demonstrates.',
    'case-return-title', 15,
]
_STUDY_SECTION_NEW = [
    *_STUDY_SECTION_OLD[:8],
    'reply-evaluation', 'Can a draft be polite and still get the important facts wrong?',
    'reply-evaluation-results', 'The 30-case run returned 29 templates and blocked one.',
    'reply-evaluation-lessons', 'Five examples make the distinction visible.',
    'reply-evaluation-gemma', 'What the archived Gemma tests actually showed.',
    'reply-evaluation-method', 'How to repeat the offline study, and what to check yourself.',
    'reply-evaluation-limits', 'The strongest conclusion is about human control, not AI productivity.',
    *_STUDY_SECTION_OLD[8:],
]


def _restore_find_index(raw: bytes) -> bytes:
    token = '"local-ai-review-replies/":'
    new = (token + json.dumps(_STUDY_SECTION_NEW, ensure_ascii=False, separators=(',', ':'))).encode('utf-8')
    old = (token + json.dumps(_STUDY_SECTION_OLD, ensure_ascii=False, separators=(',', ':'))).encode('utf-8')
    if raw.count(new) != 1:
        raise ValueError('Unrecognized review reply search index successor')
    previous = raw.replace(new, old, 1)
    if _blob_sha(previous) != STUDY_OLD_BLOBS['find/index.html']:
        raise ValueError('Review reply search index restoration did not match predecessor')
    return previous


def _before_review_reply_study(path: str | Path, data: bytes | str) -> bytes | str:
    name = key(path)
    expected = STUDY_NEW_BLOBS.get(name)
    if expected is None:
        return data
    raw = data if isinstance(data, bytes) else data.encode('utf-8')
    if _blob_sha(raw) != expected:
        return data
    if name == 'find/index.html':
        restored = _restore_find_index(raw)
        return restored if isinstance(data, bytes) else restored.decode('utf-8')
    original = subprocess.check_output(['git', 'show', PARENT + ':' + name], cwd=ROOT)
    if _blob_sha(original) != STUDY_OLD_BLOBS[name]:
        raise ValueError('Unrecognized review reply study predecessor: ' + name)
    return original if isinstance(data, bytes) else original.decode('utf-8')


def before(path: str | Path, data: bytes | str) -> bytes | str:
    data = _before_review_reply_study(path, data)
    item = change()['paths'].get(key(path))
    if item is None or digest(data) != item['current_sha256']:
        return data
    try:
        original = zlib.decompress(base64.b64decode(item['parent_zlib_base64'], validate=True))
    except (ValueError, zlib.error) as exc:
        raise ValueError('Invalid visibility-discovery predecessor encoding: ' + key(path)) from exc
    if len(original) != item['parent_size'] or digest(original) != item['parent_sha256']:
        raise ValueError('Invalid visibility-discovery predecessor digest: ' + key(path))
    return original if isinstance(data, bytes) else original.decode('utf-8')


def pages(records: list[dict]) -> list[dict]:
    pairs = {signature(pair['new']): pair['old'] for pair in change()['pages']}
    return [deepcopy(pairs.get(signature(record), record)) for record in records]


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
    additions = change()['added_targets']
    def keep(route, response):
        item = additions.get(route)
        if (item is None or not isinstance(response, tuple) or len(response) != 2
                or type(response[0]) is not int or not isinstance(response[1], bytes)):
            return True
        return response[0] != item['status'] or digest(response[1]) != item['sha256']
    return {route: response for route, response in records.items() if keep(route, response)}
