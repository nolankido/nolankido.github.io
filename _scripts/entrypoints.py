"""Small reader routes reuse published destinations, never a second content catalog."""
from __future__ import annotations
import html
import json
import search_visibility
from pathlib import Path
import re
import identity
from presentation import publication

SUBJECTS = ('technology', 'living-well', 'poker', 'creative')
LABELS = {'technology': 'Technology', 'living-well': 'Living Well', 'poker': 'Poker', 'creative': 'Creative Work'}


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load(root: Path, pages: list[dict]) -> dict:
    config = json.loads((root / '_source/entrypoints.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict) or set(config) != {'interests', 'resources', 'next_reading'}:
        raise ValueError('Entry points need interests, resources, and next_reading')
    by_path = {p['path']: p for p in pages}
    def destination(path):
        if not isinstance(path, str) or not re.fullmatch(r'/(?:[a-z0-9-]+/)+', path):
            raise ValueError('Reader destinations must be local canonical page routes')
        page = by_path.get(path)
        if not page or (page.get('noindex') and page['id'] not in search_visibility.UTILITY_IDS) or page.get('living_well_kind') == 'experiment':
            raise ValueError('Reader destination is missing, hidden, or a proposal: ' + path)
        return page
    for name in ('interests', 'resources'):
        groups = config[name]
        if not isinstance(groups, list) or len(groups) != len(SUBJECTS):
            raise ValueError('Entry points need four ordered subject routes')
        for expected, group in zip(SUBJECTS, groups):
            if not isinstance(group, dict) or group.get('id') != expected or not all(_text(group.get(k)) for k in ('title', 'description')):
                raise ValueError('Entry points need named routes in the established subject order')
            if name == 'resources':
                links = group.get('links')
                if not isinstance(links, list) or len(links) != 2 or any(not isinstance(v, dict) or not _text(v.get('kind')) for v in links):
                    raise ValueError('Resource routes need two clearly labelled destinations')
                paths = [v.get('path') for v in links]
            else:
                paths = group.get('paths')
                if not isinstance(paths, list) or len(paths) != 2:
                    raise ValueError('Interest routes need two starting points')
            for path in paths:
                destination(path)
            if len(set(paths)) != len(paths):
                raise ValueError('A reader route cannot repeat a destination')
    next_reading = config['next_reading']
    notes = {p['id']: p for p in pages if p.get('note')}
    if not isinstance(next_reading, dict) or set(next_reading) != set(notes):
        raise ValueError('Every original note needs a deliberate next-reading choice')
    for slug, entries in next_reading.items():
        if not isinstance(entries, list) or len(entries) != 2:
            raise ValueError('Choose exactly two next readings per note')
        paths = []
        for entry in entries:
            if not isinstance(entry, dict) or not _text(entry.get('reason')):
                raise ValueError('Each next reading needs a reason')
            path = entry.get('path')
            page = destination(path)
            if not identity._reading(page) or path == notes[slug]['path']:
                raise ValueError('Next readings must be editorial content, not hubs or self-links')
            paths.append(path)
        if len(set(paths)) != len(paths):
            raise ValueError('Next readings must be distinct')
    return config


def interest_cards(config: dict, pages: list[dict]) -> str:
    by_path = {p['path']: p for p in pages}
    cards = []
    for group in config['interests']:
        slug = group['id']
        links = ''.join('<li><a href="' + html.escape(path, quote=True) + '">' + html.escape(by_path[path]['title']) + '</a></li>' for path in group['paths'])
        cards.append('<article class="entry-card" id="start-' + slug + '" aria-labelledby="start-' + slug + '-title"><p class="note-category">' + LABELS[slug] + '</p><h3 id="start-' + slug + '-title">' + html.escape(group['title']) + '</h3><p>' + html.escape(group['description']) + '</p><ul class="entry-links">' + links + '</ul></article>')
    return '<div class="entry-grid">' + ''.join(cards) + '</div>'


def resource_cards(config: dict, pages: list[dict]) -> str:
    by_path = {p['path']: p for p in pages}
    cards = []
    for group in config['resources']:
        slug = group['id']
        links = []
        for link in group['links']:
            path = link['path']
            links.append('<li><span class="entry-link-kind">' + html.escape(link['kind']) + '</span><a href="' + html.escape(path, quote=True) + '">' + html.escape(by_path[path]['title']) + '</a></li>')
        cards.append('<article class="entry-card" id="resources-' + slug + '" aria-labelledby="resources-' + slug + '-title"><p class="note-category">' + LABELS[slug] + '</p><h3 id="resources-' + slug + '-title">' + html.escape(group['title']) + '</h3><p>' + html.escape(group['description']) + '</p><ul class="entry-links">' + ''.join(links) + '</ul></article>')
    return '<div class="entry-grid">' + ''.join(cards) + '</div>'


def next_reading(config: dict, pages: list[dict], page: dict) -> str:
    if not page.get('note'):
        return ''
    by_path = {p['path']: p for p in pages}
    cards = []
    for choice in config['next_reading'][page['id']]:
        target = by_path[choice['path']]
        cards.append('<div class="reader-next-item"><h3><a href="' + html.escape(target['path'], quote=True) + '">' + html.escape(target['title']) + '</a></h3><p>' + html.escape(choice['reason']) + '</p>' + publication(target) + '</div>')
    return '<nav class="reader-next" aria-labelledby="reader-next-title"><h2 id="reader-next-title">Take the idea further.</h2><p class="reader-next-intro">Two related pieces, each for a different next step.</p><div class="reader-next-links">' + ''.join(cards) + '</div></nav>'
