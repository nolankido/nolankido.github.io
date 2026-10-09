#!/usr/bin/env python3
"""Read-only HTTP diagnostics for curated Living Well links, not an editorial verdict.

Run separately from deterministic builds. This never edits the resource catalog.
A 200 response does not establish free access, suitability, or correct content.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import living_well_resources as resources
ROOT = Path(__file__).resolve().parents[1]


def classify_status(status: int) -> str:
    if 200 <= status < 300:
        return 'responded'
    if status in {404, 410}:
        return 'not-found'
    if status in {401, 403, 429}:
        return 'restricted-or-rate-limited'
    return 'needs-review'


def check(item: dict, timeout: float = 15) -> dict:
    url = resources.safe_url(item['entry_url'])
    result = {'id': item['id'], 'requested_url': url}
    try:
        request = Request(url, headers={'User-Agent': 'NolanKido-resource-link-review/1.0', 'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1'})
        with urlopen(request, timeout=timeout) as response:
            result.update(status=response.status, final_url=response.url, result=classify_status(response.status))
            kind = response.headers.get_content_type()
            result['content_type'] = kind
            if kind in {'text/html', 'application/xhtml+xml'}:
                text = response.read(524288).decode('utf-8', errors='replace')
                title = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
                result['title'] = html.unescape(re.sub(r'\s+', ' ', title.group(1))).strip()[:240] if title else ''
                if any(word in result['title'].lower() for word in ['domain parking', 'domain is for sale', 'buy this domain']):
                    result['result'] = 'possible-parked-domain'
            if urlsplit(url).hostname != urlsplit(response.url).hostname:
                result['host_changed'] = True
    except HTTPError as exc:
        result.update(status=exc.code, result=classify_status(exc.code), final_url=exc.url)
    except (URLError, TimeoutError, OSError) as exc:
        result.update(status=None, result='retrieval-unavailable', reason=str(exc)[:240])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, choices=range(1, 7), default=4)
    parser.add_argument('--report-only', action='store_true', help='Report all findings without treating a status as a release gate.')
    args = parser.parse_args()
    catalog = resources.load(ROOT)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(check, catalog['resources']))
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'GET transport checks of recommended entry URLs. No login, media playback, app installation, or free-access confirmation. No catalog edits.',
              'results': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    counts = {key: sum(r['result'] == key for r in results) for key in sorted({r['result'] for r in results})}
    print(json.dumps({'entry_points': len(results), 'status_summary': counts}, sort_keys=True))
    for row in results:
        if row['result'] != 'responded' or row.get('host_changed'):
            print(row['id'], row.get('status'), row['result'], row.get('final_url', row['requested_url']))
    return 0 if args.report_only or not any(r['result'] in {'not-found', 'possible-parked-domain'} for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
