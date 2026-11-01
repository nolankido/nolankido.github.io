"""Add one source-verified, manually published poker player to local Find.

The ordinary Find inventory still projects only the public page manifest.
This bounded extension reads the independently reviewed player HTML, never a
user query, local files outside the public page, or a third-party source.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re

import player_sitemap
import site_find


class _PublicMetadata(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.description: list[str] = []
        self.title_depth = 0
        self.h1_depth = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'title':
            self.title_depth += 1
        if tag == 'h1':
            self.h1_depth += 1
        if tag == 'meta' and values.get('name') == 'description':
            self.description.append(values.get('content', ''))

    def handle_data(self, data):
        if self.title_depth:
            self.title_parts.append(data)
        if self.h1_depth:
            self.h1_parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.title_depth -= 1
        if tag == 'h1':
            self.h1_depth -= 1


def entry(root: Path) -> dict | None:
    """Return Find metadata copied from one verified public profile only."""
    if player_sitemap.record(root) is None:
        return None
    html = (root / player_sitemap.RELATIVE).read_text(encoding='utf-8')
    meta = _PublicMetadata(html)
    title = ' '.join(''.join(meta.h1_parts).split())
    seo_title = ' '.join(''.join(meta.title_parts).split())
    if len(meta.description) != 1:
        raise ValueError('Player Find needs exactly one public meta description')
    description = meta.description[0]
    if not (title and seo_title and description and len(seo_title) <= 100
            and 80 <= len(description) <= 190):
        raise ValueError('Player Find needs bounded, nonempty public titles and description')
    matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if len(matches) != 1:
        raise ValueError('Player Find requires one structured public record')
    schema = json.loads(matches[0])
    if schema.get('name') != seo_title or schema.get('description') != description:
        raise ValueError('Player Find metadata must match reviewed structured data')
    return {'path': player_sitemap.ROUTE, 'title': title,
            'search_title': seo_title, 'description': description,
            'interests': ['poker'], 'home': 'poker', 'kind': 'profile', 'date': ''}


def add(root: Path, manifest_items: list[dict]) -> list[dict]:
    """Include exactly one additional real page in the existing Find groups."""
    record = entry(root)
    if record is None:
        return manifest_items
    if any(item['path'] == record['path'] for item in manifest_items):
        raise ValueError('Player Find must not duplicate a manifest-owned page')
    result = [*manifest_items, record]
    order = list(site_find.INTERESTS)
    return sorted(result, key=lambda e: (
        order.index(e['home']), e['title'].casefold(), e['path']))
