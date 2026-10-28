#!/usr/bin/env python3
"""Capture one explicitly reviewed visibility-sprint predecessor capsule.

This developer-only command reads the actual Git parent, verifies both rendered
trees, and requires an exact reviewed production-path list. It never stages,
commits, deploys, or updates older golden snapshots.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
PARENT = '2aae4923318c0028d98266d78f6e4aabea295387'
PARENT_TREE = '5cb303f7aec831e6f02f152455dbb2306e83fb37'


def digest(raw):
    return sha256(raw if isinstance(raw, bytes) else raw.encode('utf-8')).hexdigest()


def git(*args, root=ROOT):
    return subprocess.check_output(['git', *args], cwd=root)


def production(path):
    # This existing deterministic audit is itself pinned by older releases.
    # Other reports remain outside this sprint's production boundary.
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
    if git('rev-parse', 'HEAD', root=baseline).decode().strip() != PARENT:
        raise ValueError('Baseline checkout is not the fixed visibility-sprint parent')
    if git('rev-parse', PARENT + '^{tree}').decode().strip() != PARENT_TREE:
        raise ValueError('Unexpected visibility-sprint parent tree')
    if git('status', '--porcelain', root=baseline).strip():
        raise ValueError('Baseline checkout must remain clean')
    reviewed = json.loads(reviewed_paths.read_text())
    if (not isinstance(reviewed, list) or not reviewed
            or any(not isinstance(p, str) for p in reviewed)
            or len(reviewed) != len(set(reviewed))):
        raise ValueError('Reviewed paths must be an explicit, unique, nonempty JSON list')
    parent_paths = {p for p in git('ls-tree', '-r', '--name-only', PARENT).decode().splitlines()
                    if production(p)}
    current_paths = {p for p in git('ls-files', '--cached', '--others', '--exclude-standard', '-z')
                     .decode().split('\0') if p and production(p)}
    missing = [p for p in parent_paths if not (ROOT / p).is_file()]
    if missing:
        raise ValueError('This sprint capsule does not authorize deletions: ' + ', '.join(missing))
    changed = {}
    for name in sorted(parent_paths):
        previous = git('show', PARENT + ':' + name)
        current = (ROOT / name).read_bytes()
        if current != previous:
            changed[name] = {
                'current_sha256': digest(current), 'parent_sha256': digest(previous),
                'parent_size': len(previous),
                'parent_zlib_base64': base64.b64encode(zlib.compress(previous, 9)).decode('ascii'),
            }
    added = {name: digest((ROOT / name).read_bytes()) for name in sorted(current_paths - parent_paths)}
    actual = set(changed) | set(added)
    if actual != set(reviewed):
        raise ValueError('Reviewed scope mismatch. Unreviewed: ' + repr(sorted(actual - set(reviewed)))
                         + '; absent from change: ' + repr(sorted(set(reviewed) - actual)))
    old = snapshot(baseline)
    new = snapshot(ROOT)
    if set(old['outputs']) - set(new['outputs']):
        raise ValueError('This sprint must retain every previous output')
    output_additions = {name: digest(value) for name, value in new['outputs'].items()
                        if name not in old['outputs']}
    if any(added.get(name) != value for name, value in output_additions.items()):
        raise ValueError('Generated additions must be in the reviewed production inventory')
    page_pairs = []
    for view in ['catalog', 'pages']:
        old_pages = {p['id']: p for p in old[view]}
        new_pages = {p['id']: p for p in new[view]}
        if set(old_pages) - set(new_pages):
            raise ValueError('This sprint must retain every previous page identity')
        for page_id, page in new_pages.items():
            previous = old_pages.get(page_id)
            pair = {'old': previous, 'new': page}
            if previous != page and pair not in page_pairs:
                page_pairs.append(pair)
    record = {
        'version': 1, 'parent_commit': PARENT, 'parent_tree': PARENT_TREE,
        'paths': changed, 'added_files': added, 'added_outputs': output_additions,
        'added_targets': {route: value for route, value in new['targets'].items()
                          if route not in old['targets']},
        'pages': page_pairs,
        'parent_outputs': {name: digest(value) for name, value in old['outputs'].items()},
    }
    rendered = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    target = ROOT / '_tests/visibility-sprint-change.json'
    helper = ROOT / '_tests/visibility_sprint_history.py'
    helper_text = helper.read_text()
    expression = r"(?m)^CAPSULE_SHA256 = '[0-9a-f]*'$"
    if len(re.findall(expression, helper_text)) != 1:
        raise ValueError('Capsule helper must declare exactly one digest')
    helper_text = re.sub(expression, "CAPSULE_SHA256 = '" + digest(rendered) + "'", helper_text)
    target.write_text(rendered)
    helper.write_text(helper_text)
    print(json.dumps({'capsule': str(target), 'sha256': digest(rendered),
                      'changed_files': len(changed), 'added_files': len(added),
                      'added_outputs': len(output_additions), 'page_pairs': len(page_pairs),
                      'parent_outputs': len(old['outputs'])}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--reviewed-paths', required=True, type=Path)
    args = parser.parse_args()
    freeze(args.baseline.resolve(), args.reviewed_paths.resolve())


if __name__ == '__main__':
    main()
