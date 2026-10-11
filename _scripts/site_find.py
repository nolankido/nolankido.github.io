"""Build one privacy-preserving discovery surface from published page metadata.

No crawl, remote source content, hidden answers or personal records enter this
index. Titles and summaries are always reused from the public page manifest.
"""
from __future__ import annotations
from datetime import date
from html import escape
import json
from pathlib import Path
import re

INTERESTS = {'technology': 'Technology', 'living-well': 'Living Well', 'poker': 'Poker', 'creative': 'Creative Work'}
EXCLUDED = {'home', 'find', 'follow', 'about', 'bio', 'contact', 'privacy', 'card', '404', 'start-here', 'notes', 'resources',
            'living-well-field-notes', 'living-well-editorial-standards', 'living-well-sources', 'poker-find', 'living-well-find'}


def eligible(page: dict) -> bool:
    return (page['id'] not in EXCLUDED and not page.get('noindex')
            and page.get('living_well_kind') != 'experiment'
            and bool(page.get('note') or page.get('section', page['id']) in INTERESTS))


def entries(root: Path, pages: list[dict]) -> list[dict]:
    config = json.loads((root / '_source/discovery.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict) or set(config) != {'note_interests', 'also_in'}:
        raise ValueError('Discovery needs note_interests and also_in mappings')
    notes, extra = config['note_interests'], config['also_in']
    if not isinstance(notes, dict) or not isinstance(extra, dict):
        raise ValueError('Discovery mappings must be objects')
    if set(notes) != {p['id'] for p in pages if p.get('note')}:
        raise ValueError('Every original note needs explicit discovery interests')
    by_path = {p['path']: p for p in pages}
    if len(by_path) != len(pages):
        raise ValueError('Discovery page routes must be unique')
    for path in extra:
        if path not in by_path or not eligible(by_path[path]):
            raise ValueError('Extra discovery interests must reference eligible public pages')
    for labels in [*notes.values(), *extra.values()]:
        if not isinstance(labels, list) or not labels or any(not isinstance(k, str) or k not in INTERESTS for k in labels) or len(set(labels)) != len(labels):
            raise ValueError('Discovery interests must be a nonempty list of unique known labels')
    result = []
    for page in pages:
        if not eligible(page):
            continue
        if not re.fullmatch(r'/(?:[a-z0-9-]+/)+', page['path']):
            raise ValueError('Discovery destinations must be local canonical pages')
        if not all(isinstance(page.get(k), str) and page[k].strip() for k in ('title', 'description')):
            raise ValueError('Searchable pages need a title and summary')
        interests = list(notes[page['id']] if page.get('note') else [page.get('section', page['id'])])
        interests.extend(k for k in extra.get(page['path'], []) if k not in interests)
        kind = ('essay' if page.get('note') or page.get('living_well_kind') == 'essay' else
                'guide' if page.get('poker_guide') or page.get('living_well_kind') == 'guide' else 'collection')
        published = page.get('date', '') if kind != 'collection' else ''
        if published:
            date.fromisoformat(published)
        result.append({'path': page['path'], 'title': page['title'], 'description': page['description'],
                       'interests': interests, 'home': interests[0], 'kind': kind, 'date': published})
    return sorted(result, key=lambda e: (list(INTERESTS).index(e['home']), e['title'].casefold(), e['path']))


def render(items: list[dict]) -> str:
    groups = []
    names = {'essay': 'Essay', 'guide': 'Guide', 'collection': 'Collection / reference'}
    for key, label in INTERESTS.items():
        group = [item for item in items if item['home'] == key]
        cards = []
        for item in group:
            subjects = ' · '.join(INTERESTS[k] for k in item['interests'])
            published = ''
            if item['date']:
                dt = date.fromisoformat(item['date'])
                published = f'<p class="find-date">Published <time datetime="{escape(item["date"], quote=True)}">{dt.strftime("%B")} {dt.day}, {dt.year}</time></p>'
            cards.append(f'<li class="find-item" data-kind="{item["kind"]}" data-interests="{" ".join(item["interests"])}">'
                         f'<p class="find-kind">{names[item["kind"]]} <span aria-hidden="true">/</span> <span class="find-subjects">{escape(subjects)}</span></p>'
                         f'<h3><a href="{escape(item["path"], quote=True)}">{escape(item["title"])}</a></h3>'
                         f'<p class="find-description">{escape(item["description"])}</p>{published}</li>')
        groups.append(f'<details class="find-group" id="browse-{key}"><summary>{label} <span class="find-group-count" hidden>({len(group)})</span></summary>'
                      f'<ul class="find-items">{"".join(cards)}</ul></details>')
    return '\n'.join(groups)
