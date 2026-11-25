#!/usr/bin/env python3
"""Rebuild and validate a committed site release in a new local Git worktree.

The existing checkout is not edited. The new detached worktree is retained on
success or failure for inspection. No fetch, push, merge, or deployment.
"""
from __future__ import annotations

import argparse
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


def rebuild(root: Path, destination: Path) -> Path:
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
    if git(root, 'status', '--porcelain', capture=True):
        print('Local edits are excluded; validating the committed revision only.', flush=True)
    print(f'Release candidate: {head}\nIsolated worktree: {destination}', flush=True)
    git(root, 'worktree', 'add', '--detach', str(destination), head)
    try:
        if git(destination, 'rev-parse', 'HEAD', capture=True) != head:
            raise RebuildError('Worktree revision does not match the selected commit')
        # Regenerate from reviewed sources before checking generated parity.
        python(destination, '_scripts/build_books.py')
        python(destination, '_scripts/build.py')
        python(destination, '_scripts/prepare_local_release.py', '--apply')
        if git(destination, 'rev-parse', 'HEAD', capture=True) != head:
            raise RebuildError('Unexpected commit movement during validation')
    except BaseException:
        print(f'Release blocked. Inspect the retained worktree at {destination}', file=sys.stderr)
        raise
    print('Local release checks passed. Review the generated changes:', flush=True)
    git(destination, 'status', '--short')
    print('No commit, push, merge, or deployment was performed.', flush=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worktree', type=Path, required=True,
                        help='New directory outside this checkout')
    args = parser.parse_args()
    try:
        rebuild(ROOT, args.worktree)
    except (OSError, RebuildError) as exc:
        print(f'Rebuild blocked: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
