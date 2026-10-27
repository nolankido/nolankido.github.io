"""Rewind only the exact approved per-page social-card scoping release.

This adapter runs before the earlier brand positioning adapter. Unknown
mutations are not rewritten, even when they contain matching social copy.
"""
from __future__ import annotations

import base64
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/scoped-share-change.json'
GENERAL_ALT = 'Nolan Kido. Build useful things. Make room for a good life. nolankido.com.'
BRAND_ALT = 'Nolan Kido. AI Works Human Decides. Practical AI for real life. nolankido.com.'


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def change() -> dict:
    record = json.loads(CHANGE.read_text(encoding='utf-8'))
    if (record.get('version') != 1 or
            record.get('parent_commit') != '1de951bac87c767aaecd6eff2433353d17a44a62' or
            record.get('parent_tree') != '85839487e491aacd75c3978e47be17c5416b13d7'):
        raise ValueError('Unrecognized social-card scoping predecessor')
    return record


def before(path: str | Path, data: str | bytes) -> str | bytes:
    item = change()['paths'].get(str(path))
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if item is None or digest(raw) != item['current_sha256']:
        return data
    if item['mode'] == 'social-metadata':
        text = raw.decode('utf-8').replace(GENERAL_ALT, BRAND_ALT)
        if str(path) in {'index.html', 'about/index.html'}:
            text = text.replace('/assets/social/nolan-kido-ai.png', '/assets/social/nolan-kido.png')
        restored = text.encode('utf-8')
    elif item['mode'] == 'frozen-predecessor':
        restored = zlib.decompress(base64.b64decode(item['parent_zlib_base64'], validate=True))
    else:
        raise ValueError('Unknown social-card scoping mode: ' + str(path))
    if digest(restored) != item['parent_sha256']:
        raise ValueError('Invalid scoped social-card predecessor: ' + str(path))
    return restored if binary else restored.decode('utf-8')
