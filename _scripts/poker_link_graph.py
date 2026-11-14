#!/usr/bin/env python3
"""Audit actual published Poker links, separating prose links from site navigation.

Read-only. The existing check_internal_links.py remains responsible for
validating target routes and fragments. Counts here are editorial diagnostics,
not search ranking or crawler observations.
"""
from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import poker_library
import poker_resources
import poker_topics

ORIGIN = 'https://nolankido.com'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
CHROME = {'page-hero', 'poker-breadcrumb', 'reader-outline', 'topic-context',
          'reader-related', 'page-share-wrap', 'page-share-print-origin'}
NON_PROSE = {'nav', 'header', 'footer', 'script', 'style'}
ENTRYPOINTS = ('/poker/', '/poker/library/', '/poker/topics/')


def local_route(href: str, current: str) -> str | None:
    """Resolve authored anchors without treating another origin as local."""
    url = urlsplit(urljoin(ORIGIN + current, href))
    if url.hostname not in {'nolankido.com', 'www.nolankido.com'}:
        return None
    return unquote(url.path)


class PokerLinks(HTMLParser):
    """Record links in main, and the stricter subset in visible guide prose."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.main_links: list[str] = []
        self.prose_links: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        chain = [item[0] for item in self.stack]
        classes = set().union(*(item[1] for item in self.stack)) if self.stack else set()
        if tag == 'a' and attributes.get('href') and 'main' in chain:
            href = attributes['href']
            self.main_links.append(href)
            if ('p' in chain or 'li' in chain) and not NON_PROSE.intersection(chain) and not CHROME.intersection(classes):
                self.prose_links.append(href)
        if tag not in VOID:
            self.stack.append((tag, set(attributes.get('class', '').split())))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


def links(source: bytes) -> PokerLinks:
    parser = PokerLinks()
    parser.feed(source.decode('utf-8'))
    return parser


def scan(root: Path = ROOT) -> dict:
    pages = build.public_pages(root)
    guides = poker_library.load(root, pages)
    resources = poker_resources.load(root)
    topics = poker_topics.load(root, pages, guides, resources)
    inventory = check_live.targets(root)
    html = {route: body for route, (status, body) in inventory.items()
            if route.startswith('/poker/') and status == 200
            and body.lstrip().lower().startswith(b'<!doctype html')}
    guide_by_route = {guide['route']: guide for guide in guides}
    all_edges: dict[str, set[str]] = {}
    prose_edges: dict[str, set[str]] = {}
    for route, body in html.items():
        parsed = links(body)
        all_edges[route] = {target for href in parsed.main_links
                            if (target := local_route(href, route)) in html and target != route}
        prose_edges[route] = {target for href in parsed.prose_links
                              if (target := local_route(href, route)) in guide_by_route and target != route}

    reachable = set(route for route in ENTRYPOINTS if route in html)
    queue = deque(reachable)
    while queue:
        for target in all_edges[queue.popleft()] - reachable:
            reachable.add(target)
            queue.append(target)

    records = []
    for route, guide in sorted(guide_by_route.items()):
        incoming = sorted(source for source in guide_by_route
                          if route in prose_edges.get(source, set()))
        outgoing = sorted(prose_edges.get(route, set()))
        primary = next(topic['id'] for topic in topics if guide['slug'] in topic['primary_guides'])
        records.append({'slug': guide['slug'], 'title': guide['title'], 'topic': primary,
                        'route': route, 'prose_inbound_guides': incoming,
                        'prose_outbound_guides': outgoing,
                        'inbound_count': len(incoming), 'outbound_count': len(outgoing),
                        'reachable_from_poker_entrypoints': route in reachable})

    weak = [record for record in records if record['inbound_count'] <= 1]
    return {'scope': 'links in locally generated public Poker HTML; no remote crawl, ranking or user behavior',
            'poker_html_pages': len(html), 'guides': len(guides),
            'guide_prose_edges': sum(len(prose_edges.get(route, set())) for route in guide_by_route),
            'weak_guides_at_most_one_inbound': len(weak),
            'unreachable_guides': sorted(item['slug'] for item in records
                                         if not item['reachable_from_poker_entrypoints']),
            'records': records}


def main() -> int:
    result = scan()
    summary = {key: value for key, value in result.items() if key != 'records'}
    print(json.dumps(summary, indent=2, sort_keys=True))
    print('Lowest guide-to-guide prose inlinks:')
    for item in sorted(result['records'], key=lambda row: (row['inbound_count'], row['slug']))[:20]:
        print(f"  {item['inbound_count']:2} in / {item['outbound_count']:2} out: {item['slug']} ({item['topic']})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
