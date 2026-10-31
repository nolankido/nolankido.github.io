#!/usr/bin/env python3
"""Bounded public GET diagnostics for priority routes or the full release.

This supplements the frozen production verifier. It never submits forms or
uses private credentials. Network failures remain failures, not inferred 404s.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import check_live

PRIORITY = (
    '/', '/about/', '/bio/', '/technology/', '/poker/',
    '/technology/local-ai-review-replies/',
    '/technology/ai-book-continuity-checker/',
    '/technology/dinner-on-time/',
    '/technology/task-brief/', '/technology/check-ai-answers/',
    '/robots.txt', '/sitemap.xml',
    '/assets/social/nolan-kido-ai.png',
    '/review-no-such-page-20261005/',
)


def inspect_transport(route: str) -> str:
    """Retry a failed transport once with a readable, bounded reason.

    This is diagnostic only. It cannot replace an exact-byte pass from the
    production verifier, even if the endpoint now responds with HTTP 200.
    """
    request = urllib.request.Request(
        check_live.ORIGIN + route + '?diagnostic=' + str(time.time_ns()),
        headers={'Cache-Control': 'no-cache', 'Accept-Encoding': 'identity',
                 'User-Agent': 'NolanKidoReleaseCheck/1.0'}, method='GET')
    try:
        opener = urllib.request.build_opener(check_live.SameOriginRedirect())
        with opener.open(request, timeout=12) as response:
            return 'separate diagnostic HTTP ' + str(response.code) + ' (bytes not compared)'
    except urllib.error.HTTPError as error:
        return 'separate diagnostic HTTP ' + str(error.code) + ' (bytes not compared)'
    except (OSError, urllib.error.URLError) as error:
        reason = str(getattr(error, 'reason', error)).replace('\n', ' ').strip()
        return type(error).__name__ + ': ' + reason[:160]


def audit(scope: str, attempts: int, interval: int, workers: int) -> dict:
    all_targets = check_live.targets()
    targets = {route: all_targets[route] for route in PRIORITY} if scope == 'priority' else all_targets
    pending = dict(targets)
    failures = {}
    for index in range(attempts):
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda item: (item[0], *check_live.check(*item)), pending.items()))
        for route, passed, message in results:
            if passed:
                pending.pop(route)
                failures.pop(route, None)
            else:
                failures[route] = message
        if not pending:
            break
        if index + 1 < attempts:
            time.sleep(interval)
    diagnostics = {}
    for route, message in failures.items():
        if message in {'URLError', 'OSError'}:
            diagnostics[route] = inspect_transport(route)
    return {'scope': scope, 'total': len(targets), 'passed': len(targets) - len(pending),
            'failed': len(pending), 'failures': failures, 'transport_diagnostics': diagnostics,
            'read_only': True, 'exact_byte_comparison': True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=('priority', 'all'), default='priority')
    parser.add_argument('--attempts', type=int, choices=range(1, 5), default=2)
    parser.add_argument('--interval', type=int, choices=range(0, 11), default=2)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=2)
    args = parser.parse_args(argv)
    report = audit(args.scope, args.attempts, args.interval, args.workers)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 1 if report['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
