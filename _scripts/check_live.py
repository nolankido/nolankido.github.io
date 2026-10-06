#!/usr/bin/env python3
"""Read-only public release verification. GET requests only; no form submissions or credentials."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import build
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nolankido.com'
LIMIT = 2 * 1024 * 1024


def targets(root: Path = ROOT) -> dict[str, tuple[int, bytes]]:
    pages = json.loads((root / '_source/pages.json').read_text(encoding='utf-8')) + build.poker_content.manifest(build.poker_content.load(root))
    result = {}
    for page in pages:
        route = page['path']
        relative = route.lstrip('/') + ('index.html' if route.endswith('/') else '')
        result[route] = (200, (root / relative).read_bytes())
    assets = ['downloads/poker-watch-along.md', 'downloads/poker-viewer-reference.md', 'assets/poker.css', 'poker/feed.xml', 'downloads/poker-session-debrief.md', 'assets/hubs.css', 'downloads/poker-hand-review.md', 'assets/contact.js', 'assets/site.css', 'styles.css', 'favicon.svg', 'robots.txt', 'feed.xml', 'sitemap.xml', 'nolan-kido.vcf', 'card/qr.svg', '.well-known/security.txt']
    assets += ['downloads/' + name + '.md' for name in ['decision-record', 'tool-trust-check', 'learning-loop']]
    catalog = build.poker_content.load(root)
    assets += sorted({e['image']['src'].lstrip('/') for e in catalog['entries'] if e.get('image')})
    for path in assets:
        result['/' + path] = (200, (root / path).read_bytes())
    not_found = (root / '404.html').read_bytes()
    for route in ['/review-no-such-page-20261005/', '/SITE_REVIEW.md', '/_source/site.json', '/_scripts/build.py']:
        result[route] = (404, not_found)
    return result


class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urlsplit(newurl)
        if url.scheme != 'https' or url.netloc != 'nolankido.com':
            raise urllib.error.URLError('Unexpected cross-origin redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check(route: str, expected: tuple[int, bytes]) -> tuple[bool, str]:
    if not route.startswith('/') or route.startswith('//') or '?' in route or '#' in route:
        return False, 'Invalid local route'
    request = urllib.request.Request(ORIGIN + route + '?release-check=' + str(time.time_ns()), headers={
        'Cache-Control': 'no-cache', 'Accept-Encoding': 'identity', 'User-Agent': 'NolanKidoReleaseCheck/1.0'
    }, method='GET')
    opener = urllib.request.build_opener(SameOriginRedirect())
    try:
        try:
            response = opener.open(request, timeout=12)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            status, body = response.code, response.read(LIMIT + 1)
        if status != expected[0]:
            return False, 'HTTP ' + str(status) + ', expected ' + str(expected[0])
        if body != expected[1]:
            return False, 'Response bytes do not match the checked-out release'
        return True, 'HTTP ' + str(status) + '; exact release bytes'
    except (OSError, urllib.error.URLError) as error:
        return False, type(error).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempts', type=int, default=1)
    parser.add_argument('--interval', type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.attempts <= 12 or not 0 <= args.interval <= 30:
        parser.error('attempts must be 1..12 and interval must be 0..30 seconds')
    pending = targets()
    total = len(pending)
    failures = {}
    for attempt in range(args.attempts):
        def run(item):
            route, value = item
            return route, *check(route, value)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(run, list(pending.items())))
        for route, ok, message in results:
            if ok:
                print('PASS ' + route + ': ' + message, flush=True)
                pending.pop(route)
                failures.pop(route, None)
            else:
                failures[route] = message
        if not pending:
            print(f'PASS {total}/{total} live targets. Public GET requests only; no form submissions.', flush=True)
            return 0
        if attempt + 1 < args.attempts:
            print(f'Waiting for {len(pending)} live targets; attempt {attempt + 1}.', flush=True)
            time.sleep(args.interval)
    for route, message in failures.items():
        print('FAIL ' + route + ': ' + message, flush=True)
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
