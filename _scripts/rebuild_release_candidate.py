#!/usr/bin/env python3
"""Rebuild and validate a committed site release in a new local Git worktree.

The existing checkout is not edited. The new detached worktree is retained on
success or failure for inspection. No fetch, push, merge, or deployment.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class RebuildError(RuntimeError):
    pass


def git(root: Path, *args: str, capture: bool = False) -> str:
    done = subprocess.run(['git', '-C', str(root), *args], check=False,
                          text=True, stdout=subprocess.PIPE if capture else None)
    if done.returncode:
        raise RebuildError(f'Git exit {done.returncode}: {" ".join(args)}')
    return (done.stdout or '').strip()


def python(root: Path, *args: str) -> None:
    done = subprocess.run([sys.executable, *args], cwd=root, check=False)
    if done.returncode:
        raise RebuildError(f'Python exit {done.returncode}: {" ".join(args)}')


def rebuild(root: Path, destination: Path, *, expected_head: str | None = None,
            receipt: Path | None = None) -> Path:
    root = root.resolve(strict=True)
    if destination.exists() or destination.is_symlink():
        raise RebuildError('Worktree destination must not exist')
    destination = destination.resolve()
    if destination.is_relative_to(root) or root.is_relative_to(destination):
        raise RebuildError('Worktree must be outside the existing checkout')
    if not destination.parent.is_dir():
        raise RebuildError('Worktree parent directory must already exist')
    top = Path(git(root, 'rev-parse', '--show-toplevel', capture=True)).resolve()
    if top != root:
        raise RebuildError('Run from the repository root')
    head = git(root, 'rev-parse', '--verify', 'HEAD^{commit}', capture=True)
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', head):
        raise RebuildError('Expected an exact committed Git revision')
    if expected_head is not None and expected_head != head:
        raise RebuildError(f'Reviewed commit mismatch: expected {expected_head}, found {head}')
    if receipt is not None:
        if receipt.exists() or receipt.is_symlink():
            raise RebuildError('Receipt must be a new file')
        receipt = receipt.resolve()
        if (receipt.is_relative_to(root) or receipt.is_relative_to(destination)
                or not receipt.parent.is_dir()):
            raise RebuildError('Receipt must be outside both checkouts with an existing parent')
    if git(root, 'status', '--porcelain', capture=True):
        print('Local edits are excluded; validating the committed revision only.', flush=True)
    print(f'Release candidate: {head}\nIsolated worktree: {destination}', flush=True)
    # Append-only JSON lines retain completed steps even if a later check fails.
    # A missing final pass event is never a successful validation receipt.
    context = receipt.open('x', encoding='utf-8', newline='\n') if receipt else nullcontext(None)
    with context as log:
        def record(event, **fields):
            if log is not None:
                log.write(json.dumps({'event': event, **fields}, ensure_ascii=True) + '\n')
                log.flush()

        record('started', version=1, head=head, worktree=str(destination),
               scope='local release validation only; no deployment')
        step = 'create detached worktree'
        try:
            git(root, 'worktree', 'add', '--detach', str(destination), head)
            if git(destination, 'rev-parse', 'HEAD', capture=True) != head:
                raise RebuildError('Worktree revision does not match the selected commit')
            record('step_pass', step=step)
            for command in (('_scripts/build_books.py',), ('_scripts/build.py',),
                            ('_scripts/prepare_local_release.py', '--apply')):
                step = ' '.join(command)
                record('step_started', step=step)
                python(destination, *command)
                record('step_pass', step=step)
            step = 'review generated changes'
            if git(destination, 'rev-parse', 'HEAD', capture=True) != head:
                raise RebuildError('Unexpected commit movement during validation')
            status = git(destination, 'status', '--porcelain=v1', capture=True)
            record('finished', status='pass', head=head, worktree_status=status,
                   deployment_verified=False)
        except BaseException as exc:
            record('finished', status='blocked', head=head, step=step,
                   reason=f'{type(exc).__name__}: {exc}', deployment_verified=False)
            print(f'Release blocked. Inspect the retained worktree at {destination}', file=sys.stderr)
            raise
    print('Local release checks passed. Review the generated changes:', flush=True)
    if status:
        print(status, flush=True)
    print('No commit, push, merge, or deployment was performed.', flush=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worktree', type=Path, required=True,
                        help='New directory outside this checkout')
    parser.add_argument('--expected-head', help='Exact reviewed commit; refuse a different HEAD')
    parser.add_argument('--receipt', type=Path,
                        help='New JSONL validation receipt outside both checkouts')
    args = parser.parse_args()
    try:
        rebuild(ROOT, args.worktree, expected_head=args.expected_head, receipt=args.receipt)
    except (OSError, RebuildError) as exc:
        print(f'Rebuild blocked: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
