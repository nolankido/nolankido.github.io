#!/usr/bin/env python3
"""Freeze the audited social-card scoping edit against its pinned parent.

The 84 generated HTML edits have one reversible metadata transformation.
Store both SHA-256 values, and retain exact compressed predecessors for the
two authoring files and original card. CI does not need Git history to replay.
"""
from __future__ import annotations

import base64
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_PARENT = '1de951bac87c767aaecd6eff2433353d17a44a62'
LOCAL_EQUIVALENT = 'b37428cc98c25207d58f40664d29d453919e9f06'
PARENT_TREE = '85839487e491aacd75c3978e47be17c5416b13d7'
TARGET = ROOT / '_tests/scoped-share-change.json'
NEW_ASSET = 'assets/social/nolan-kido-ai.png'
GENERAL_ALT = 'Nolan Kido. Build useful things. Make room for a good life. nolankido.com.'
BRAND_ALT = 'Nolan Kido. AI Works Human Decides. Practical AI for real life. nolankido.com.'


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def pinned_parent() -> str:
    for commit in (PUBLISHED_PARENT, LOCAL_EQUIVALENT):
        probe = subprocess.run(['git', 'rev-parse', commit + '^{tree}'], cwd=ROOT,
                               capture_output=True, text=True)
        if probe.returncode == 0 and probe.stdout.strip() == PARENT_TREE:
            return commit
    raise ValueError('Published parent tree unavailable or inconsistent')


def reverse_html(path: str, raw: bytes) -> bytes:
    value = raw.decode('utf-8').replace(GENERAL_ALT, BRAND_ALT)
    if path in {'index.html', 'about/index.html'}:
        value = value.replace('/assets/social/nolan-kido-ai.png', '/assets/social/nolan-kido.png')
    return value.encode('utf-8')


def main() -> None:
    parent = pinned_parent()
    changed = git('diff', '--name-only', parent).decode().splitlines()
    # The capsule describes published-byte changes. Other test files may be
    # revised while repairing the historical suite and are audited separately.
    files = [p for p in changed if not p.startswith('_tests/')]
    record = {'version': 1, 'parent_commit': PUBLISHED_PARENT, 'parent_tree': PARENT_TREE, 'paths': {},
              'new_asset': {'path': NEW_ASSET, 'sha256': digest((ROOT / NEW_ASSET).read_bytes())}}
    for path in files:
        previous = git('show', parent + ':' + path)
        current = (ROOT / path).read_bytes()
        if previous == current:
            raise ValueError('Unchanged file in scope: ' + path)
        item = {'parent_sha256': digest(previous), 'current_sha256': digest(current)}
        if path.endswith('.html'):
            item['mode'] = 'social-metadata'
            restored = reverse_html(path, current)
        else:
            item['mode'] = 'frozen-predecessor'
            item['parent_zlib_base64'] = base64.b64encode(zlib.compress(previous, 9)).decode('ascii')
            restored = previous
        if restored != previous:
            raise ValueError('Non-reversible scoped share edit: ' + path)
        record['paths'][path] = item
    if len(files) != 87 or len([p for p in files if p.endswith('.html')]) != 84:
        raise ValueError('Unexpected share-card change set')
    TARGET.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'Frozen {len(files)} scoped social-card edits and 1 new asset')


if __name__ == '__main__':
    main()
