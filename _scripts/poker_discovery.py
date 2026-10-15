"""Curated entry routes into existing Poker writing, rendered without JavaScript."""
from html import escape
import hashlib
import json
import re

HUBS = {'/poker/', '/poker/library/'}
CSS = 'assets/poker-discovery.css'


def load(root, entries):
    data = json.loads((root / '_source/poker/reading-routes.json').read_text(encoding='utf-8'))
    if set(data) != {'version', 'routes', 'in_depth'} or data['version'] != 1:
        raise ValueError('Invalid Poker reading routes')
    by_slug = {e['slug']: e for e in entries}
    ids = set()
    for route in data['routes']:
        if set(route) != {'id', 'title', 'description', 'links'}:
            raise ValueError('Invalid Poker route fields')
        if not re.fullmatch(r'[a-z]+', route['id']) or route['id'] in ids:
            raise ValueError('Invalid or duplicate Poker route ID')
        ids.add(route['id'])
        if not route['title'].strip() or not route['description'].strip() or not 2 <= len(route['links']) <= 3:
            raise ValueError('Poker routes need a purpose and two or three destinations')
        slugs = []
        for link in route['links']:
            if set(link) != {'slug', 'label'} or link['slug'] not in by_slug or not link['label'].strip():
                raise ValueError('Poker route must link to an existing guide')
            slugs.append(link['slug'])
        if len(set(slugs)) != len(slugs):
            raise ValueError('Duplicate guide in Poker route')
    if not data['routes'] or not data['in_depth']:
        raise ValueError('Poker discovery needs routes and substantial reading')
    slugs = set()
    for item in data['in_depth']:
        if set(item) != {'slug', 'kind', 'description'} or item['slug'] not in by_slug or item['slug'] in slugs:
            raise ValueError('Invalid or duplicate in-depth Poker guide')
        if not item['kind'].strip() or not item['description'].strip():
            raise ValueError('In-depth guides need a reader purpose')
        slugs.add(item['slug'])
    return data


def supplement(root, entries):
    data = load(root, entries)
    by_slug = {e['slug']: e for e in entries}
    routes = []
    for route in data['routes']:
        links = ''.join(f'<li><a href="{by_slug[link["slug"]]["route"]}">{escape(link["label"])}</a></li>' for link in route['links'])
        routes.append(f'<article class="poker-goal" aria-labelledby="goal-{route["id"]}">'
                      f'<h3 id="goal-{route["id"]}">{escape(route["title"])}</h3>'
                      f'<p>{escape(route["description"])}</p><ul>{links}</ul></article>')
    reads = []
    for item in data['in_depth']:
        guide = by_slug[item['slug']]
        reads.append('<article class="poker-long-read">'
                     f'<p class="reader-eyebrow">{escape(item["kind"])}</p>'
                     f'<h3><a href="{guide["route"]}">{escape(guide["title"])}</a></h3>'
                     f'<p>{escape(item["description"])}</p>'
                     f'<p class="poker-reading-time">About {guide["minutes"]} min read</p></article>')
    return {'poker_goal_routes': '<div class="poker-goal-grid" role="group" aria-label="Ways to explore Poker">' + ''.join(routes) + '</div>',
            'poker_in_depth': '<div class="poker-long-read-grid">' + ''.join(reads) + '</div>'}


def head(page, root):
    if page['path'] not in HUBS:
        return ''
    version = hashlib.sha256((root / CSS).read_bytes()).hexdigest()[:12]
    return f'\n  <link rel="stylesheet" href="/{CSS}?v={version}">'
