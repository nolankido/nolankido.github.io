#!/usr/bin/env python3
"""Audit the 19 Technology reader routes against locally built public files.

No network, analytics, search rankings, automated publication, or private data.
The editorial intent matrix is an explicit input, not inferred search demand.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import csv
import json
import re

from build import output_path
from audit_ai_reader_paths import MainLinks, local_path


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nolankido.com'
MATRIX = Path('_reports/visibility-sprint/seo-geo-turn11-technology-intent-matrix-2026-11-18.csv')
FIELDS = ('route', 'task', 'reader_question', 'answer', 'distinct_artifact',
          'evidence_type', 'next_action', 'related_paths')
TASKS = {'hub', 'deciding', 'briefing', 'checking', 'measuring', 'local_execution',
         'writing_continuity', 'practical_operations', 'project_demonstrations'}
MANUAL = {
    '/technology/local-ai-gaming-laptop/': ('_source/technology/local-ai-gaming-laptop.html', '2026-11-02'),
    '/technology/review-reply-evidence-audit/': ('_source/technology/review-reply-evidence-audit.html', '2026-11-03'),
}


class Canonicals(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            fields = dict(attrs)
            if 'canonical' in fields.get('rel', '').split():
                self.urls.append(fields.get('href', ''))


def load_matrix(root: Path = ROOT) -> list[dict]:
    with (root / MATRIX).open(newline='', encoding='utf-8') as handle:
        table = csv.DictReader(handle)
        if tuple(table.fieldnames or ()) != FIELDS:
            raise ValueError('The intent matrix columns changed')
        return list(table)


def page_links(body: str, route: str) -> set[str]:
    parser = MainLinks()
    parser.feed(body)
    return {path for href in parser.links if (path := local_path(route, href)) is not None}


def canonical_urls(body: str) -> list[str]:
    parser = Canonicals()
    parser.feed(body)
    return parser.urls


def find_routes(body: str) -> list[str]:
    """Get actual Find result links, excluding nav and supplemental-section links."""
    return re.findall(r'<li class="find-item"[^>]*>\s*.*?<h3><a href="([^"]+)"', body, re.S)


def task_routes(body: str) -> tuple[set[str], int]:
    match = re.search(r'<section\b[^>]*\bid="technology-by-task"[^>]*>(.*?)</section>', body, re.S)
    if not match:
        return set(), 0
    block = match.group(1)
    routes = {urlsplit(href).path for href in re.findall(r'<a\s+href="([^"]+)"', block)
              if href.startswith('/technology/')}
    return routes, len(re.findall(r'<li\b', block))


def audit(root: Path = ROOT) -> dict:
    issues: list[str] = []
    matrix = load_matrix(root)
    routes = [row['route'] for row in matrix]
    manifest = json.loads((root / '_source/pages.json').read_text(encoding='utf-8'))
    manifest_cases = {p['path']: p for p in manifest if p['path'].startswith('/technology/')}
    expected = set(manifest_cases) | set(MANUAL)

    if len(matrix) != 19 or len(routes) != len(set(routes)) or set(routes) != expected:
        issues.append('Matrix must cover exactly the 19 distinct Technology routes')
    if set(manifest_cases) & set(MANUAL):
        issues.append('Manually built cases must not be adopted into the main page manifest')
    groups = Counter(row['task'] for row in matrix)
    if set(groups) != TASKS or groups['hub'] != 1 or routes.count('/technology/') != 1:
        issues.append('Expected eight reader task groups plus one hub')
    if len(set(row['reader_question'].casefold() for row in matrix)) != len(matrix):
        issues.append('Each reader question needs a distinct intent')

    page_graph: dict[str, set[str]] = {}
    for row in matrix:
        route = row['route']
        if not all(isinstance(row.get(field), str) and row[field].strip() for field in FIELDS):
            issues.append(f'Incomplete intent record: {route}')
            continue
        if row['task'] not in TASKS:
            issues.append(f'Unexpected reader task: {route}')
        if '\u2014' in ' '.join(row.values()):
            issues.append(f'Prohibited dash in matrix: {route}')
        neighbors = row['related_paths'].split('|')
        if not 2 <= len(neighbors) <= 3 or len(set(neighbors)) != len(neighbors) or route in neighbors:
            issues.append(f'Expected two or three distinct neighboring pages: {route}')

        output = root / output_path(route)
        if not output.is_file():
            issues.append(f'Missing generated article: {route}')
            continue
        body = output.read_text(encoding='utf-8')
        page_graph[route] = page_links(body, route)
        if canonical_urls(body) != [ORIGIN + route]:
            issues.append(f'Broken or duplicate canonical: {route}')
        for neighbor in neighbors:
            if neighbor not in page_graph[route]:
                issues.append(f'Missing contextual reader link: {route} -> {neighbor}')
        if route in MANUAL and not (root / MANUAL[route][0]).is_file():
            issues.append(f'Manual case source missing: {route}')

    hub_body = (root / 'technology/index.html').read_text(encoding='utf-8')
    linked_tasks, task_count = task_routes(hub_body)
    if task_count != 8 or (expected - {'/technology/'}) - linked_tasks:
        issues.append('The eight hub task rows must link to all 18 distinct article and tool routes')

    for supporting in ('/projects/', '/resources/'):
        content = (root / output_path(supporting)).read_text(encoding='utf-8')
        links = page_links(content, supporting)
        if not set(MANUAL).issubset(links):
            issues.append(f'{supporting} must lead to both independently built case pages')

    find = find_routes((root / 'find/index.html').read_text(encoding='utf-8'))
    find_counts = Counter(find)
    for route in expected:
        if find_counts[route] != 1:
            issues.append(f'Find must list the canonical route exactly once: {route}')

    sitemap = ET.parse(root / 'sitemap.xml')
    locs = [e.text or '' for e in sitemap.iter() if e.tag.rsplit('}', 1)[-1] == 'loc']
    site_counts = Counter(locs)
    for route in expected:
        if site_counts[ORIGIN + route] != 1:
            issues.append(f'Sitemap must list the canonical route exactly once: {route}')

    canonical_sites: list[str] = []
    for loc in locs:
        parsed = urlsplit(loc)
        if parsed.scheme != 'https' or parsed.netloc != 'nolankido.com':
            issues.append('Unexpected noncanonical site URL in sitemap: ' + loc)
            continue
        output = root / output_path(parsed.path)
        if not output.is_file():
            issues.append('Sitemap page missing locally: ' + loc)
            continue
        values = canonical_urls(output.read_text(encoding='utf-8'))
        if values != [loc]:
            issues.append('Missing or mismatched sitemap self-canonical: ' + loc)
        canonical_sites.extend(values)
    if any(count != 1 for count in Counter(canonical_sites).values()):
        issues.append('Different indexed pages share a canonical URL')

    feed = ET.parse(root / 'technology/feed.xml')
    items = feed.findall('./channel/item')
    feed_links = [item.findtext('link') for item in items]
    feed_count = Counter(feed_links)
    expected_feed_dates = {p['path']: p['date'] for p in manifest_cases.values()
                           if p.get('worked_guide') or p.get('evidence_article')}
    expected_feed_dates.update({route: date for route, (_, date) in MANUAL.items()})
    for route in expected:
        present = feed_count[ORIGIN + route]
        wanted = 1 if route in expected_feed_dates else 0
        if present != wanted:
            issues.append(f'Wrong practical-AI feed ownership or duplicate: {route}')
        if wanted and present:
            item = next(item for item in items if item.findtext('link') == ORIGIN + route)
            pub = item.findtext('pubDate')
            if not pub or parsedate_to_datetime(pub).date() != date.fromisoformat(expected_feed_dates[route]):
                issues.append(f'Feed changed an original publication date: {route}')

    return {
        'status': 'pass' if not issues else 'fail',
        'scope': 'committed local HTML, sitemap, Find and Technology RSS; no external search performance',
        'technology_routes': len(expected),
        'task_groups': len(TASKS) - 1,
        'sitemap_urls_checked': len(locs),
        'find_routes_checked': len(find),
        'technology_feed_items': len(items),
        'technology_article_feed_items': len(expected_feed_dates),
        'manual_source_routes': sorted(MANUAL),
        'issues': issues,
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
