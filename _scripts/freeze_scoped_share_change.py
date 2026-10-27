#!/usr/bin/env python3
"""Freeze the audited social-card scoping edit against its pinned parent.

The 84 generated HTML edits have one reversible metadata transformation.
Read the two pinned Git trees, never the working tree, so this capsule remains
reproducible after later edits. Retain exact compressed predecessors for the
two authoring files and original card. Replay needs no Git history; rebuilding
the capsule requires the pinned objects. Use --check for non-writing validation.
"""
from __future__ import annotations

import argparse
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
PUBLISHED_RELEASE = 'd1764c0d43caa3e88eaf0ce5cb8d48eaa5ab30cb'
LOCAL_RELEASE = '1455b5b7419b5ab502bf59b957626a9479bc83dc'
RELEASE_TREE = 'ff70b08fc552a6e65268be3e8ffb8d00f3cd1eb1'
TARGET = ROOT / '_tests/scoped-share-change.json'
NEW_ASSET = 'assets/social/nolan-kido-ai.png'
AUTHORING_PATHS = frozenset({
    '_scripts/render_social_cards.py',
    '_source/presentation.json',
    'assets/social/nolan-kido.png',
})
REVIEW_TOOLS = frozenset({
    '_scripts/freeze_brand_positioning_delta.py',
    '_scripts/freeze_scoped_share_change.py',
})
GENERAL_ALT = 'Nolan Kido. Build useful things. Make room for a good life. nolankido.com.'
BRAND_ALT = 'Nolan Kido. AI Works Human Decides. Practical AI for real life. nolankido.com.'


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def pinned_revision(published: str, equivalent: str, tree: str, label: str) -> str:
    for commit in (published, equivalent):
        probe = subprocess.run(['git', 'rev-parse', commit + '^{tree}'], cwd=ROOT,
                               capture_output=True, text=True)
        if probe.returncode == 0 and probe.stdout.strip() == tree:
            return commit
    raise ValueError(f'Published {label} tree unavailable or inconsistent')


def pinned_parent() -> str:
    return pinned_revision(PUBLISHED_PARENT, LOCAL_EQUIVALENT, PARENT_TREE, 'parent')


def pinned_release() -> str:
    return pinned_revision(PUBLISHED_RELEASE, LOCAL_RELEASE, RELEASE_TREE, 'release')


def reverse_html(path: str, raw: bytes) -> bytes:
    value = raw.decode('utf-8').replace(GENERAL_ALT, BRAND_ALT)
    if path in {'index.html', 'about/index.html'}:
        value = value.replace('/assets/social/nolan-kido-ai.png', '/assets/social/nolan-kido.png')
    return value.encode('utf-8')


def production_paths(changed: list[str]) -> list[str]:
    """Keep only the reviewed capsule scope; never absorb other production edits."""
    ignored = REVIEW_TOOLS | {NEW_ASSET}
    files = [p for p in changed if not p.startswith('_tests/') and p not in ignored]
    unexpected = [p for p in files if not p.endswith('.html') and p not in AUTHORING_PATHS]
    if unexpected:
        raise ValueError('Unexpected production changes: ' + ', '.join(sorted(unexpected)))
    if (len(set(changed)) != len(changed) or NEW_ASSET not in changed or
            set(files) & AUTHORING_PATHS != AUTHORING_PATHS or
            len(files) != 87 or sum(p.endswith('.html') for p in files) != 84):
        raise ValueError('Unexpected share-card change set')
    return sorted(files)


def build_record() -> dict:
    parent = pinned_parent()
    release = pinned_release()
    changed = git('diff', '--name-only', parent, release).decode().splitlines()
    files = production_paths(changed)
    record = {'version': 1, 'parent_commit': PUBLISHED_PARENT, 'parent_tree': PARENT_TREE, 'paths': {},
              'new_asset': {'path': NEW_ASSET, 'sha256': digest(git('show', release + ':' + NEW_ASSET))}}
    for path in files:
        previous = git('show', parent + ':' + path)
        current = git('show', release + ':' + path)
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
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='verify the committed capsule without writing files')
    args = parser.parse_args(argv)
    record = build_record()
    serialized = json.dumps(record, indent=2) + '\n'
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding='utf-8') != serialized:
            print('Scoped social-card capsule differs from the pinned release')
            return 1
        print('Verified 87 scoped social-card edits and 1 new asset against pinned trees')
    else:
        TARGET.write_text(serialized, encoding='utf-8')
        print('Frozen 87 scoped social-card edits and 1 new asset')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
