#!/usr/bin/env python3
"""Bounded public GET diagnostics for priority routes or the full release.

This supplements the frozen production verifier. It never submits forms or
uses private credentials. Network errors are inconclusive and must never
be reported as observed HTTP 404s. Only public GET responses are checked.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
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
    '/', '/about/', '/bio/', '/start-here/', '/technology/',
    '/technology/checking-ai-website-changes/',
    '/technology/ai-website-visibility/', '/technology/ai-workflow-pilot/',
    '/ai-in-real-life/', '/poker/', '/poker/free-poker-learning-path/', '/poker/10bb/', '/books/',
    '/books/one-workflow-at-a-time/',
    '/books/how-to-play-no-limit-texas-holdem/',
    '/technology/local-ai-review-replies/',
    '/technology/ai-book-continuity-checker/',
    '/technology/dinner-on-time/',
    '/technology/task-brief/', '/technology/check-ai-answers/',
    '/downloads/one-workflow-ai-pilot-worksheet.md',
    '/downloads/holdem-river-call-check-worksheet.md',
    '/downloads/website-check-offline-runbook.md',
    '/downloads/ten-bb-tournament-checklist.md',
    '/downloads/ten-bb-playbook-icm-verify.py',
    '/downloads/gsc-period-compare.py',
    '/downloads/gsc-download-verify.py',
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


def classify_failure(message: str) -> str:
    """Only actual HTTP errors or byte differences establish a release mismatch.

    DNS, TLS, timeout and unrecognized tool failures remain inconclusive.
    A later diagnostic GET is not an exact-byte comparison of the failed GET.
    """
    if message.startswith('HTTP ') or message == 'Response bytes do not match the checked-out release':
        return 'observed_mismatch'
    return 'inconclusive'


def exit_code(report: dict) -> int:
    return {'pass': 0, 'fail': 1, 'inconclusive': 2}[report['status']]


def audit(scope: str, attempts: int, interval: int, workers: int,
          only: list[str] | None = None) -> dict:
    all_targets = check_live.targets()
    if scope == 'priority':
        missing = [route for route in PRIORITY if route not in all_targets]
        if missing:
            raise ValueError('Priority release targets are not registered: ' + ', '.join(missing))
    targets = {route: all_targets[route] for route in PRIORITY} if scope == 'priority' else all_targets
    if only:
        if len(only) != len(set(only)):
            raise ValueError('Duplicate --only route')
        unknown = [route for route in only if route not in targets]
        if unknown:
            raise ValueError('Unknown selected release route: ' + ', '.join(unknown))
        targets = {route: targets[route] for route in only}
    pending = dict(targets)
    failures = {}
    verified = {}
    for index in range(attempts):
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda item: (item[0], *check_live.check(*item)), pending.items()))
        for route, passed, message in results:
            if passed:
                # This is a completed status-bearing GET and exact-byte
                # comparison from check_live.check(), not a cached HTML extract.
                expected_status, expected_body = targets[route]
                verified[route] = {
                    'http_status': expected_status,
                    'source_sha256': sha256(expected_body).hexdigest(),
                    'verified_attempt': index + 1,
                    'evidence': message,
                }
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
    observed = sorted(route for route, message in failures.items()
                      if classify_failure(message) == 'observed_mismatch')
    inconclusive = sorted(route for route, message in failures.items()
                          if classify_failure(message) == 'inconclusive')
    state = 'fail' if observed else ('inconclusive' if inconclusive else 'pass')
    return {'scope': scope, 'selection': 'explicit' if only else scope,
            'status': state, 'total': len(targets),
            'attempts_configured': attempts, 'attempts_used': index + 1,
            'retry_interval_seconds': interval,
            'passed': len(verified), 'failed': len(pending),
            'verified_routes': {route: verified[route] for route in sorted(verified)},
            'observed_failed': len(observed), 'inconclusive_count': len(inconclusive),
            'observed_failure_routes': observed, 'inconclusive_routes': inconclusive,
            'failures': failures, 'transport_diagnostics': diagnostics,
            'read_only': True, 'exact_byte_comparison': True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=('priority', 'all'), default='priority')
    # Manual long-window checks can outlast GitHub Pages propagation after
    # a successful build. Keep the original fast defaults and a hard ceiling.
    parser.add_argument('--attempts', type=int, choices=range(1, 9), default=2,
                        help='Attempts per remaining target, 1..8 (default: 2)')
    parser.add_argument('--interval', type=int, choices=range(0, 31), default=2,
                        help='Seconds between attempts, 0..30 (default: 2)')
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=2)
    parser.add_argument('--only', action='append', metavar='/PATH',
                        help='Check only named registered routes; repeat to select multiple')
    args = parser.parse_args(argv)
    try:
        report = audit(args.scope, args.attempts, args.interval, args.workers,
                       only=args.only)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True, indent=2))
    return exit_code(report)


if __name__ == '__main__':
    raise SystemExit(main())
