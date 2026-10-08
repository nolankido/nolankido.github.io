"""Reviewed resource collections and portable exports, derived from one catalogue."""
from __future__ import annotations
from collections import Counter
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

FIELDS = {'id', 'slug', 'title', 'description', 'resource_ids'}


def load(root: Path, resources: list[dict], pages: list[dict]) -> list[dict]:
    data = json.loads((root / '_source/poker/collections.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'entries'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Invalid resource collections schema')
    if not isinstance(data['entries'], list) or not data['entries']:
        raise ValueError('Collections require a nonempty entry list')
    by_id = {e['id']: e for e in resources}
    routes = {p['path'] for p in pages if p.get('poker_guide')}
    seen_ids, seen_routes = set(), set()
    for item in data['entries']:
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise ValueError('Invalid collection fields')
        for key in ('id', 'slug', 'title', 'description'):
            value = item[key]
            if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
                raise ValueError('Collection text must be nonempty plain text')
        if not re.fullmatch(r'[a-z]+(?:_[a-z]+)*', item['id']) or item['id'] in seen_ids:
            raise ValueError('Invalid or duplicate collection ID')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item['slug']):
            raise ValueError('Invalid collection slug')
        route = '/poker/' + item['slug'] + '/'
        if route not in routes or route in seen_routes:
            raise ValueError('Collection must have one distinct published guide')
        ids = item['resource_ids']
        if (not isinstance(ids, list) or not 3 <= len(ids) <= 8
                or not all(isinstance(i, str) for i in ids)
                or len(set(ids)) != len(ids) or any(i not in by_id for i in ids)):
            raise ValueError('Collections need 3 to 8 distinct reviewed resource IDs')
        if item['id'] == 'free' and any(by_id[i]['access'] != 'Free' for i in ids):
            raise ValueError('Free learning path cannot contain paid or mixed resources')
        seen_ids.add(item['id']); seen_routes.add(route)
    return data['entries']


def supplement(collections: list[dict], resources: list[dict]) -> dict[str, str]:
    """Render current access, dates and cautions without duplicating their source data."""
    by_id = {e['id']: e for e in resources}
    values, hub = {}, []
    for item in collections:
        cards = []
        for ident in item['resource_ids']:
            e = by_id[ident]
            review = 'Public page read' if e['review_method'] == 'page' else 'Search index only'
            cards.append(
                '<article class="reader-card" data-collection-resource="' + ident + '">'
                '<p class="reader-eyebrow">' + escape(e['publisher']) + '</p>'
                '<h3><a href="' + escape(e['url'], quote=True) + '" rel="external">' + escape(e['title']) + '</a></h3>'
                '<p class="reader-card-meta">' + escape(e['access'] + ' · ' + e['kind'] + ' · ' + e['level']) + '</p>'
                '<p>' + escape(e['description']) + '</p>'
                + ('<p class="small-copy"><strong>Before you use it:</strong> ' + escape(e['notes']) + '</p>' if e['notes'] else '')
                + '<p class="small-copy">' + review + ' · <time datetime="' + e['reviewed_on'] + '">' + e['reviewed_on'] + '</time>'
                + ' · <a href="/poker/resources/#resource-' + ident + '">Full directory listing</a></p></article>')
        values['collection_' + item['id']] = '<div class="reader-grid">' + ''.join(cards) + '</div>'
        hub.append('<article class="reader-card"><h3><a href="/poker/' + item['slug'] + '/">' + escape(item['title']) + '</a></h3>'
                   '<p>' + escape(item['description']) + '</p><p class="small-copy">' + str(len(item['resource_ids'])) + ' selected sources with context</p></article>')
    values['poker_collections'] = '<div class="reader-grid">' + ''.join(hub) + '</div>'
    counts = Counter(e['access'] for e in resources)
    domains = {urlsplit(e['url']).hostname.lower().removeprefix('www.') for e in resources}
    values['poker_resource_summary'] = (f'{len(resources)} unique destinations on {len(domains)} hostnames. '
        + ', '.join(f'{counts[k]} {k.lower()}' for k in ('Free', 'Mixed', 'Paid'))
        + '. Hostnames are not a count of independent owners. Collection links reuse these listings and do not inflate the total.')
    return values


def exports(resources: list[dict]) -> dict[Path, str]:
    """Stable offline reference. It is a dated snapshot, never a new review claim."""
    entries = sorted(resources, key=lambda e: (e['category'], e['title'].casefold(), e['id']))
    latest = max(e['reviewed_on'] for e in entries)
    scope = ('Public-resource directory snapshot. Individual review dates and limitations remain attached. '
             'Access and destinations can change. Inclusion is not a product test, partnership or permission to use tools during play.')
    payload = {'version': 1, 'directory': 'https://nolankido.com/poker/resources/',
               'latest_listing_review': latest, 'scope': scope, 'entries': entries}
    lines = ['# Nolan Kido Poker resource directory', '', scope, '',
             f'{len(entries)} unique resources. Most recent individual listing review: {latest}.', '',
             'This is not a claim that all resources were rechecked on that date.', '']
    for e in entries:
        lines += ['## ' + e['title'], '', e['url'], '',
                  e['publisher'] + ' | ' + e['category'] + ' | ' + e['kind'] + ' | ' + e['access'] + ' | ' + e['level'],
                  '', e['description'], '', 'Before you use it: ' + (e['notes'] or 'Check the current publisher terms.'), '',
                  'Listing review: ' + e['reviewed_on'] + ' (' + e['review_method'] + ').',
                  'Directory context: https://nolankido.com/poker/resources/#resource-' + e['id'], '']
    return {Path('downloads/poker-resource-directory.json'): json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
            Path('downloads/poker-resource-directory.md'): '\n'.join(lines)}
