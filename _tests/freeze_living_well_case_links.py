#!/usr/bin/env python3
"""Capture a separate, explicitly reviewed successor to published PR150.

This test-only utility never rewrites the visibility-sprint capsule or an older
golden file. It accepts no added/deleted production files and changes only the
new capsule and its pinned digest after both committed output trees validate.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import re
import subprocess
import sys
import zlib

import living_well_case_links_history as history

ROOT = Path(__file__).resolve().parents[1]


def git(*args, root=ROOT):
    return subprocess.check_output(['git', *args], cwd=root)


def production(path):
    return (path == '_reports/search-audit.json'
            or (not path.startswith(('_tests/', '_reports/'))
                and '__pycache__' not in Path(path).parts))


def snapshot(root):
    code = r'''
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / '_scripts'))
import build
import living_well
outputs = build.build_outputs()
drift = [str(p) for p, value in outputs.items()
         if not (Path.cwd() / p).is_file()
         or (Path.cwd() / p).read_bytes() != value.encode('utf-8')]
if drift:
    raise SystemExit('Unbuilt output: ' + ', '.join(drift))
print(json.dumps({'outputs': {str(p): value for p, value in outputs.items()},
                  'pages': build.public_pages(),
                  'entries': living_well.load(Path.cwd())}, ensure_ascii=False))
'''
    return json.loads(subprocess.check_output([sys.executable, '-I', '-c', code], cwd=root))


def pairs(old, new, field, identity):
    previous = {r[identity]: r for r in old[field]}
    current = {r[identity]: r for r in new[field]}
    if set(previous) != set(current) or len(previous) != len(old[field]) or len(current) != len(new[field]):
        raise ValueError('Case links must retain every record identity: ' + field)
    result = [{'old': previous[name], 'new': current[name]} for name in sorted(current)
              if history.signature(previous[name]) != history.signature(current[name])]
    expected = history.SLUGS if field == 'entries' else {'living-well-' + s for s in history.SLUGS}
    if {pair['new'][identity] for pair in result} != expected:
        raise ValueError('Only the four reviewed articles may change: ' + field)
    return result


def freeze(baseline: Path, reviewed_paths: Path):
    if git('rev-parse', 'HEAD', root=baseline).decode().strip() != history.PARENT:
        raise ValueError('Baseline checkout is not the published PR150 merge')
    if git('rev-parse', history.PARENT + '^{tree}').decode().strip() != history.PARENT_TREE:
        raise ValueError('Unexpected published PR150 tree')
    if git('status', '--porcelain', root=baseline).strip():
        raise ValueError('The published PR150 baseline must remain clean')
    reviewed = json.loads(reviewed_paths.read_text())
    if (not isinstance(reviewed, list) or not reviewed
            or any(not isinstance(p, str) for p in reviewed)
            or len(reviewed) != len(set(reviewed))):
        raise ValueError('Reviewed paths must be an explicit, unique, nonempty JSON list')
    parent_paths = {p for p in git('ls-tree', '-r', '--name-only', history.PARENT).decode().splitlines()
                    if production(p)}
    current_paths = {p for p in git('ls-files', '--cached', '--others', '--exclude-standard', '-z')
                     .decode().split('\0') if p and production(p)}
    if current_paths != parent_paths or any(not (ROOT / p).is_file() for p in parent_paths):
        raise ValueError('Case links cannot add or delete production files')
    changed = {}
    for name in sorted(parent_paths):
        previous = git('show', history.PARENT + ':' + name)
        current = (ROOT / name).read_bytes()
        if current != previous:
            changed[name] = {
                'current_sha256': history.digest(current),
                'parent_sha256': history.digest(previous), 'parent_size': len(previous),
                'parent_zlib_base64': base64.b64encode(zlib.compress(previous, 9)).decode('ascii'),
            }
    if set(changed) != set(reviewed):
        raise ValueError('Reviewed scope mismatch. Unreviewed: ' + repr(sorted(set(changed) - set(reviewed)))
                         + '; absent from change: ' + repr(sorted(set(reviewed) - set(changed))))
    old, new = snapshot(baseline), snapshot(ROOT)
    if set(old['outputs']) != set(new['outputs']):
        raise ValueError('Case links cannot add or delete generated outputs')
    record = {
        'version': 1, 'parent_commit': history.PARENT, 'parent_tree': history.PARENT_TREE,
        'paths': changed, 'pages': pairs(old, new, 'pages', 'id'),
        'entries': pairs(old, new, 'entries', 'slug'),
        'parent_outputs': {name: history.digest(value) for name, value in old['outputs'].items()},
    }
    rendered = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    capsule_hash = history.digest(rendered)
    helper = ROOT / '_tests/living_well_case_links_history.py'
    helper_text, count = re.subn(r"CAPSULE_SHA256 = '[^']*'", "CAPSULE_SHA256 = '" + capsule_hash + "'", helper.read_text())
    if count != 1:
        raise ValueError('Expected exactly one new capsule digest pin')
    history.CHANGE.write_text(rendered)
    helper.write_text(helper_text)
    history.CAPSULE_SHA256 = capsule_hash
    history.change.cache_clear()
    history.change()
    print(json.dumps({'capsule_sha256': capsule_hash, 'changed_files': len(changed),
                      'page_pairs': len(record['pages']), 'entry_pairs': len(record['entries']),
                      'parent_outputs': len(record['parent_outputs'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--reviewed-paths', type=Path, required=True)
    args = parser.parse_args()
    freeze(args.baseline.resolve(), args.reviewed_paths.resolve())
