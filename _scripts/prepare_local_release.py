#!/usr/bin/env python3
"""Prepare a local website release without CI, network calls or automatic merges.

By default, check the generated audit against the existing report without
writing it. --apply installs only the real, passing audit and runs the existing
full local release suite, restoring the old report if the suite fails.
Run from an isolated, complete checkout; do not edit the report concurrently.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = Path('_reports/search-audit.json')


class ReleaseError(RuntimeError):
    pass


def run(root: Path, *args: str) -> None:
    result = subprocess.run([sys.executable, *args], cwd=root, check=False)
    if result.returncode != 0:
        raise ReleaseError(f'Exit {result.returncode}: {" ".join(args)}')


def validate_report(path: Path) -> bytes:
    try:
        raw = path.read_bytes()
        data = json.loads(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ReleaseError(f'Cannot read generated search audit: {exc}') from exc
    if not isinstance(data, dict) or data.get('status') != 'pass' or data.get('errors') != []:
        raise ReleaseError('Generated search audit is not a passing report')
    if type(data.get('sitemap_urls')) is not int or data['sitemap_urls'] <= 0:
        raise ReleaseError('Generated search audit has no valid sitemap count')
    return raw


def atomic_write(path: Path, raw: bytes) -> None:
    # The temporary file shares the report filesystem, so replacement is atomic.
    mode = stat.S_IMODE(path.stat().st_mode)
    fd, name = tempfile.mkstemp(prefix='.search-audit-', dir=path.parent)
    staging = Path(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(staging, mode)
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)


def prepare(root: Path, *, apply: bool = False) -> int:
    """Return 0 on verified match/full checks, 2 for reviewed drift, raise on failure."""
    snapshot = root / SNAPSHOT
    if not snapshot.is_file() or snapshot.is_symlink():
        raise ReleaseError('A regular committed search-audit snapshot is required')
    if any(p.is_file() and p.suffix.lower() in {'.yaml', '.yml'}
           for p in (root / '.github/workflows').glob('*')):
        raise ReleaseError('Repository-authored GitHub Actions are prohibited')
    before = snapshot.read_bytes()
    # Both deterministic builders must pass before deriving a new report.
    run(root, '_scripts/build_books.py', '--check')
    run(root, '_scripts/build.py', '--check')
    run(root, '_tests/check_html5.py')
    with tempfile.TemporaryDirectory(prefix='site-release-audit-') as temp:
        candidate = Path(temp) / 'search-audit.json'
        run(root, '_scripts/check_search.py', '--json', str(candidate))
        raw = validate_report(candidate)
        run(root, '_scripts/check_search.py', '--verify-snapshot', str(candidate))
    if snapshot.read_bytes() != before:
        raise ReleaseError('Committed report changed during preparation; refusing to overwrite')
    changed = before != raw
    if not apply:
        if changed:
            print('Search audit drift: real candidate passed; no files changed. Re-run with --apply to validate the full local release.')
            return 2
        print('Generated search audit matches. Full release suite has not run.')
        return 0
    try:
        if changed:
            atomic_write(snapshot, raw)
        # The existing runner checks exact snapshot parity as part of its suite.
        run(root, '_scripts/local_release_checks.py', '--full', '--browser')
        if snapshot.read_bytes() != raw:
            raise ReleaseError('Report changed during release validation; inspect the checkout')
    except BaseException:
        if changed:
            # Do not overwrite concurrent changes by another process.
            if snapshot.is_file() and snapshot.read_bytes() == raw:
                atomic_write(snapshot, before)
                print('Release failed; original snapshot restored.', file=sys.stderr)
            elif snapshot.is_file() and snapshot.read_bytes() == before:
                print('Release failed; original snapshot is intact.', file=sys.stderr)
            else:
                print('Release failed; report changed externally, not overwritten.', file=sys.stderr)
        raise
    print('Local release checks passed; inspect and commit the reviewed snapshot diff. No merge or deployment was performed.')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Install the passing audit, run full local checks, and roll back on failure')
    args = parser.parse_args()
    try:
        return prepare(ROOT, apply=args.apply)
    except (ReleaseError, OSError) as exc:
        print(f'Local release blocked: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
