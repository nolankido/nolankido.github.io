#!/usr/bin/env python3
"""Verify public HTML links against local routes and real fragment targets.

The Poker Finder stores whitelisted filter settings in URL fragments rather
than element IDs. These are distinguished from actual anchors. No network calls.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import check_live

PUBLIC_ORIGIN = 'https://nolankido.com'
FINDER_ROUTE = '/poker/find/'
FINDER_SCRIPT_MARKER = 'new URLSearchParams(window.location.hash.slice(1))'


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if 'id' in attributes:
            self.ids[attributes['id']] += 1
        if tag == 'a' and 'href' in attributes:
            self.links.append(attributes['href'])


def finder_options(source: str, control: str) -> set[str]:
    """Use the generated public controls, not a guessed value list."""
    found = re.search(r'<select id="' + re.escape(control) + r'"[^>]*>(.*?)</select>',
                      source, flags=re.S)
    if found is None:
        raise ValueError('Missing Poker Finder control: ' + control)
    values = set(re.findall(r'<option value="([^"]+)"', found.group(1)))
    if 'all' not in values or len(values) < 2:
        raise ValueError('Incomplete Poker Finder control: ' + control)
    return values


def is_finder_state(fragment: str, source: str, script: str) -> bool:
    """Accept only linkable states the on-site filter script can restore."""
    if FINDER_SCRIPT_MARKER not in script:
        return False
    try:
        pairs = parse_qsl(fragment, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return False
    if not pairs or len(pairs) != len({key for key, _ in pairs}):
        return False
    try:
        allowed = {'topic': finder_options(source, 'finder-topic'),
                   'kind': finder_options(source, 'finder-kind'), 'free': {'1'}}
    except ValueError:
        return False
    return all(key in allowed and value in allowed[key] for key, value in pairs)


def scan(root: Path = ROOT) -> dict:
    inventory = check_live.targets(root)
    pages = {}
    for route, (status, body) in inventory.items():
        if status == 200 and body.lstrip().lower().startswith(b'<!doctype html'):
            parser = Page()
            parser.feed(body.decode('utf-8'))
            pages[route] = parser

    finder = (root / 'poker/find/index.html').read_text(encoding='utf-8')
    script = (root / 'assets/poker-finder.js').read_text(encoding='utf-8')
    issues = []
    internal = fragments = states = 0
    for route, parser in pages.items():
        for ident, count in parser.ids.items():
            if count > 1:
                issues.append({'page': route, 'id': ident, 'reason': 'duplicate-id', 'count': count})
        for href in parser.links:
            dest = urlsplit(urljoin(PUBLIC_ORIGIN + route, href))
            if dest.hostname not in {'nolankido.com', 'www.nolankido.com'}:
                continue
            internal += 1
            path = unquote(dest.path)
            if path not in inventory or inventory[path][0] != 200:
                issues.append({'page': route, 'href': href, 'reason': 'unregistered-public-target'})
                continue
            if not dest.fragment:
                continue
            fragments += 1
            anchor = unquote(dest.fragment)
            if path in pages and anchor in pages[path].ids:
                continue
            if path == FINDER_ROUTE and is_finder_state(anchor, finder, script):
                states += 1
                continue
            issues.append({'page': route, 'href': href,
                           'reason': 'missing-fragment' if path in pages else 'fragment-on-non-html'})

    return {'status': 'pass' if not issues else 'fail', 'html_pages': len(pages),
            'internal_links': internal, 'fragment_links': fragments,
            'finder_state_links': states, 'issues': issues,
            'scope': 'public HTML and registered GET targets; no network or browser requests'}


def main() -> int:
    report = scan()
    summary = {key: value for key, value in report.items() if key != 'issues'}
    summary['issue_count'] = len(report['issues'])
    print(json.dumps(summary, indent=2, sort_keys=True))
    for issue in report['issues'][:25]:
        print(json.dumps(issue, sort_keys=True))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
