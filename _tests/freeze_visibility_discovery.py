#!/usr/bin/env python3
"""Capture the explicitly reviewed discovery delta from published PR151.

Read the actual fixed Git parent and require an exact production-path review.
This utility never rewrites earlier capsules, stages, commits, or deploys.
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

import visibility_discovery_history as history

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
import check_live
outputs = build.build_outputs()
drift = [str(p) for p, value in outputs.items()
         if not (Path.cwd() / p).is_file()
         or (Path.cwd() / p).read_bytes() != value.encode('utf-8')]
if drift:
    raise SystemExit('Unbuilt output: ' + ', '.join(drift))
print(json.dumps({
    'outputs': {str(p): value for p, value in outputs.items()},
    'pages': build.public_pages(),
    'catalog': json.loads((Path.cwd() / '_source/pages.json').read_text()),
    'targets': {route: {'status': pair[0], 'sha256': __import__('hashlib').sha256(pair[1]).hexdigest()}
                for route, pair in check_live.targets().items()},
}, ensure_ascii=False))
'''
    return json.loads(subprocess.check_output([sys.executable, '-I', '-c', code], cwd=root))


def freeze(baseline: Path, reviewed_paths: Path):
    if git('rev-parse', 'HEAD', root=baseline).decode().strip() != history.PARENT:
        raise ValueError('Baseline checkout is not the published PR151 merge')
    if git('rev-parse', history.PARENT + '^{tree}').decode().strip() != history.PARENT_TREE:
        raise ValueError('Unexpected published PR151 tree')
    if git('status', '--porcelain', root=baseline).strip():
        raise ValueError('The published PR151 baseline must remain clean')
    reviewed = json.loads(reviewed_paths.read_text())
    if (not isinstance(reviewed, list) or not reviewed
            or any(not isinstance(p, str) for p in reviewed)
            or len(reviewed) != len(set(reviewed))):
        raise ValueError('Reviewed paths must be an explicit, unique, nonempty JSON list')
    parent_paths = {p for p in git('ls-tree', '-r', '--name-only', history.PARENT).decode().splitlines()
                    if production(p)}
    current_paths = {p for p in git('ls-files', '--cached', '--others', '--exclude-standard', '-z')
                     .decode().split('\0') if p and production(p)}
    missing = [p for p in parent_paths if p not in current_paths or not (ROOT / p).is_file()]
    if missing:
        raise ValueError('This release cannot delete production files: ' + ', '.join(missing))
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
    added = {name: history.digest((ROOT / name).read_bytes())
             for name in sorted(current_paths - parent_paths)}
    actual = set(changed) | set(added)
    if actual != set(reviewed):
        raise ValueError('Reviewed scope mismatch. Unreviewed: ' + repr(sorted(actual - set(reviewed)))
                         + '; absent from change: ' + repr(sorted(set(reviewed) - actual)))
    old, new = snapshot(baseline), snapshot(ROOT)
    if set(old['outputs']) - set(new['outputs']):
        raise ValueError('The release must retain every previous generated output')
    if set(old['targets']) - set(new['targets']):
        raise ValueError('The release must retain every previous live target')
    output_additions = {name: history.digest(value) for name, value in new['outputs'].items()
                        if name not in old['outputs']}
    if any(added.get(name) != value for name, value in output_additions.items()):
        raise ValueError('Generated additions must be in the reviewed production inventory')
    page_pairs = []
    for view in ['catalog', 'pages']:
        old_pages = {p['id']: p for p in old[view]}
        new_pages = {p['id']: p for p in new[view]}
        if (set(old_pages) != set(new_pages) or len(old_pages) != len(old[view])
                or len(new_pages) != len(new[view])):
            raise ValueError('This discovery release must retain every page identity')
        for page_id, page in new_pages.items():
            previous = old_pages[page_id]
            pair = {'old': previous, 'new': page}
            if (history.signature(previous) != history.signature(page)
                    and history.signature(pair) not in {history.signature(p) for p in page_pairs}):
                page_pairs.append(pair)
    record = {
        'version': 1, 'parent_commit': history.PARENT, 'parent_tree': history.PARENT_TREE,
        'paths': changed, 'added_files': added, 'added_outputs': output_additions,
        'added_targets': {route: value for route, value in new['targets'].items()
                          if route not in old['targets']},
        'pages': page_pairs,
        'parent_outputs': {name: history.digest(value) for name, value in old['outputs'].items()},
    }
    rendered = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    capsule_hash = history.digest(rendered)
    helper = ROOT / '_tests/visibility_discovery_history.py'
    helper_text, count = re.subn(r"(?m)^CAPSULE_SHA256 = '[0-9a-f]*'$",
                                "CAPSULE_SHA256 = '" + capsule_hash + "'", helper.read_text())
    if count != 1:
        raise ValueError('Expected exactly one new capsule digest pin')
    history.CHANGE.write_text(rendered)
    helper.write_text(helper_text)
    history.CAPSULE_SHA256 = capsule_hash
    history.change.cache_clear()
    history.change()
    print(json.dumps({'capsule_sha256': capsule_hash, 'changed_files': len(changed),
                      'added_files': len(added), 'added_outputs': len(output_additions),
                      'added_targets': len(record['added_targets']), 'page_pairs': len(page_pairs),
                      'parent_outputs': len(old['outputs'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--reviewed-paths', type=Path, required=True)
    args = parser.parse_args()
    freeze(args.baseline.resolve(), args.reviewed_paths.resolve())
