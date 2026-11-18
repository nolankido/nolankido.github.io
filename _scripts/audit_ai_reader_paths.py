#!/usr/bin/env python3
"""Audit practical-AI reader links against locally built public HTML.

Uses only committed HTML and the existing public-target inventory. It does
not fetch the site, contact Search Console, or estimate search rankings.
"""
from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import check_live


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nolankido.com'
TARGETS = (
    '/technology/local-ai-gaming-laptop/',
    '/technology/local-ai-test-record/',
    '/technology/ai-workflow-pilot/',
    '/technology/ai-time-savings/',
    '/technology/review-reply-evidence-audit/',
    '/downloads/local-hosted-ai-comparison-protocol.md',
    '/downloads/local-hosted-ai-comparison-blank.csv',
    '/downloads/ai-operations-exception-source.json',
    '/downloads/ai-operations-exception-worksheet.md',
)
REQUIRED_CONTENT_LINKS = {
    '/technology/': (
        '/technology/local-ai-gaming-laptop/',
        '/downloads/local-hosted-ai-comparison-protocol.md',
        '/technology/ai-time-savings/',
    ),
    '/technology/local-ai-gaming-laptop/': (
        '/downloads/local-hosted-ai-comparison-protocol.md',
        '/downloads/local-hosted-ai-comparison-blank.csv',
    ),
    '/technology/local-ai-test-record/': (
        '/downloads/local-hosted-ai-comparison-protocol.md',
        '/downloads/local-hosted-ai-comparison-blank.csv',
    ),
    '/technology/ai-workflow-pilot/': (
        '/downloads/local-hosted-ai-comparison-protocol.md',
        '/downloads/ai-operations-exception-source.json',
        '/downloads/ai-operations-exception-worksheet.md',
    ),
    '/technology/ai-time-savings/': (
        '/downloads/local-hosted-ai-comparison-protocol.md',
    ),
}


class MainLinks(HTMLParser):
    """Collect anchors inside a page's <main>, excluding the sitewide header."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.links: set[str] = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'main':
            self.in_main = True
        if self.in_main and tag == 'a' and values.get('href'):
            self.links.add(values['href'])

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main = False


def local_path(route: str, href: str) -> str | None:
    dest = urlsplit(urljoin(ORIGIN + route, href))
    if dest.scheme != 'https' or dest.hostname not in {'nolankido.com', 'www.nolankido.com'}:
        return None
    if dest.query:
        return None
    return unquote(dest.path)


def shortest_path(graph: dict[str, set[str]], start: str, goal: str) -> list[str] | None:
    if start == goal:
        return [start]
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        current, route = queue.popleft()
        for neighbor in sorted(graph.get(current, ())):
            if neighbor in seen:
                continue
            if neighbor == goal:
                return route + [neighbor]
            if neighbor in graph:
                seen.add(neighbor)
                queue.append((neighbor, route + [neighbor]))
    return None


def scan(root: Path = ROOT) -> dict:
    public = check_live.targets(root)
    graph: dict[str, set[str]] = {}
    for route, (status, body) in public.items():
        if status != 200 or not body.lstrip().lower().startswith(b'<!doctype html'):
            continue
        links = MainLinks()
        links.feed(body.decode('utf-8'))
        graph[route] = {
            path for href in links.links
            if (path := local_path(route, href)) is not None and path in public
        }

    missing = []
    for source, destinations in REQUIRED_CONTENT_LINKS.items():
        for target in destinations:
            if target not in graph.get(source, set()):
                missing.append({'source': source, 'target': target})

    rows = []
    for target in TARGETS:
        home = shortest_path(graph, '/', target)
        technology = shortest_path(graph, '/technology/', target)
        rows.append({
            'route': target,
            'registered': target in public and public[target][0] == 200,
            'content_pages_linking_here': sum(target in links for links in graph.values()),
            'clicks_from_home': len(home) - 1 if home else None,
            'clicks_from_technology': len(technology) - 1 if technology else None,
            'home_path': home,
        })

    inaccessible = [row['route'] for row in rows if not row['registered']
                    or row['clicks_from_home'] is None or row['clicks_from_technology'] is None]
    return {
        'status': 'pass' if not missing and not inaccessible else 'fail',
        'scope': 'locally built HTML main-content links and registered public targets only',
        'public_html_pages': len(graph),
        'expected_links_missing': missing,
        'inaccessible_targets': inaccessible,
        'targets': rows,
    }


def main() -> int:
    report = scan()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
