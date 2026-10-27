"""Undo exactly the reviewed AI Works Human Decides release for archival tests.

Never normalize an unrecognized mutation. SHA-gated edits protect the historical
contract while the current site can adopt a deliberately different public voice.
"""
from __future__ import annotations

import base64
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/brand-positioning-change.json'


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def change() -> dict:
    record = json.loads(CHANGE.read_text(encoding='utf-8'))
    if record.get('version') != 1 or record.get('base_commit') != '59781671d4b2722186195a9d3315da30add8ae6f':
        raise ValueError('Unknown brand history record')
    return record


def before(path: str | Path, data: bytes | str) -> bytes | str:
    item = change()['paths'].get(str(path))
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if item is None or digest(raw) != item['new_sha256']:
        return data
    if 'old_base64' in item:
        restored = base64.b64decode(item['old_base64'], validate=True)
    else:
        restored_text = raw.decode('utf-8')
        for edit in reversed(item['edits']):
            start, end = edit['start'], edit['end']
            if (type(start) is not int or type(end) is not int or
                    not 0 <= start <= end <= len(restored_text) or
                    restored_text[start:end] != edit['new']):
                raise ValueError('Invalid brand history offset: ' + str(path))
            restored_text = restored_text[:start] + edit['old'] + restored_text[end:]
        restored = restored_text.encode('utf-8')
    if digest(restored) != item['old_sha256']:
        raise ValueError('Invalid brand history predecessor: ' + str(path))
    return restored if binary else restored.decode('utf-8')


def pages(records: list[dict]) -> list[dict]:
    result = deepcopy(records)
    for page in result:
        mapping = change()['pages'].get(page.get('id'))
        if mapping and all(page.get(key) == value for key, value in mapping['new'].items()):
            page.update(mapping['old'])
    return result


def outputs(records: dict) -> dict:
    return {path: before(path, value) for path, value in records.items()}
