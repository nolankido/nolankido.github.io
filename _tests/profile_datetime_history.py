"""Reverse only the two approved ProfilePage datetime-repair byte snapshots.

Test-only compatibility: historical baselines stay untouched and altered files
remain visible. Never use this adapter in the site renderer.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json
import zlib

ROOT = Path(__file__).resolve().parents[1]
BASE = '3d58eef8d5d878885bfbcfe67b6565a17cd9defb'


@lru_cache(maxsize=1)
def change():
    data = json.loads((ROOT / '_tests/profile-datetime-change.json').read_text())
    if data.get('version') != 1 or data.get('base_commit') != BASE:
        raise ValueError('Unknown profile datetime predecessor')
    return data


def before(path, data):
    import feedback_context_history
    data = feedback_context_history.before(path, data)
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    old = zlib.decompress(base64.b64decode(item['old_zlib_base64'], validate=True))
    if sha256(old).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt profile datetime predecessor: ' + str(path))
    return old if binary else old.decode('utf-8')
