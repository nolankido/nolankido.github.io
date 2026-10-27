#!/usr/bin/env python3
"""Freeze one independently verifiable brand release delta for legacy test replay.

Run only while the two pinned commits are locally available. The generated
record is committed, so CI and later audits need neither a parent Git object
nor network access. This never modifies website content or old snapshots.
"""
from __future__ import annotations

import ast
import base64
from difflib import SequenceMatcher
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '59781671d4b2722186195a9d3315da30add8ae6f'
PUBLISHED_RELEASE = '1a62b90dd278b82a2716a429b1265b6dea5ab203'
LOCAL_EQUIVALENT = 'b798277d990c7dd60c02bf14ee2dff8eefaba2cf'
RELEASE_TREE = 'ab7bf3d812752dcdc320cc0fd4784e5ac43d3778'
TARGET = ROOT / '_tests/brand-positioning-change.json'


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def pinned_release() -> str:
    for commit in (PUBLISHED_RELEASE, LOCAL_EQUIVALENT):
        probe = subprocess.run(['git', 'rev-parse', commit + '^{tree}'], cwd=ROOT,
                               capture_output=True, text=True)
        if probe.returncode == 0 and probe.stdout.strip() == RELEASE_TREE:
            return commit
    raise ValueError('Published positioning release tree unavailable or inconsistent')


def edits(new: str, old: str) -> list[dict]:
    current_lines = new.splitlines(keepends=True)
    prior_lines = old.splitlines(keepends=True)
    starts = [0]
    for line in current_lines:
        starts.append(starts[-1] + len(line))
    result = []
    for operation, i1, i2, j1, j2 in SequenceMatcher(
            None, current_lines, prior_lines, autojunk=False).get_opcodes():
        if operation == 'equal':
            continue
        result.append({'start': starts[i1], 'end': starts[i2],
                       'new': ''.join(current_lines[i1:i2]),
                       'old': ''.join(prior_lines[j1:j2])})
    restored = new
    for item in reversed(result):
        assert restored[item['start']:item['end']] == item['new']
        restored = restored[:item['start']] + item['old'] + restored[item['end']:]
    if restored != old:
        raise ValueError('Non-reversible text delta')
    return result


def frozen_page_fields(commit: str) -> dict:
    pages = json.loads(git('show', commit + ':_source/pages.json'))
    result = {}
    for page in pages:
        if page['id'] in {'home', 'about', 'technology'}:
            result[page['id']] = {key: page[key]
                                  for key in ('seo_title', 'description', 'updated')}
    practical_source = git('show', commit + ':_scripts/practical_path.py').decode()
    for variable, field in [('SEO_TITLE', 'seo_title'), ('DESCRIPTION', 'description')]:
        value = re.search('^' + variable + r' = (.+)$', practical_source, re.M)
        if not value:
            raise ValueError('Missing pinned Technology SEO override')
        result['technology'][field] = ast.literal_eval(value.group(1))
    return result


def main() -> None:
    release = pinned_release()
    paths = git('diff', '--name-only', BASE, release).decode().splitlines()
    record = {'version': 1, 'base_commit': BASE, 'release_commit': PUBLISHED_RELEASE,
              'release_tree': RELEASE_TREE,
              'paths': {}, 'pages': {}}
    for path in paths:
        old = git('show', BASE + ':' + path)
        new = git('show', release + ':' + path)
        if old == new:
            raise ValueError('Unchanged path in release diff: ' + path)
        item = {'old_sha256': digest(old), 'new_sha256': digest(new)}
        if path.endswith('.png'):
            item['old_base64'] = base64.b64encode(old).decode('ascii')
        else:
            item['edits'] = edits(new.decode('utf-8'), old.decode('utf-8'))
        record['paths'][path] = item
    old_pages, new_pages = frozen_page_fields(BASE), frozen_page_fields(release)
    record['pages'] = {key: {'old': old_pages[key], 'new': new_pages[key]}
                       for key in old_pages if old_pages[key] != new_pages[key]}
    TARGET.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Frozen {len(record["paths"])} exact paths and {len(record["pages"])} metadata records in {TARGET}')


if __name__ == '__main__':
    main()
