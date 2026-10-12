"""Expose existing everyday-work guides without duplicating articles or inventing outcomes.

Search metadata is presentation only. Original titles, prose, publication dates,
and feed records stay with the Living Well source. All worksheet bodies are
exported from the original visible starters, not independently maintained copies.
"""
from __future__ import annotations
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re
import living_well_utility as utility


def load(root: Path, pages: list[dict]) -> dict:
    config = json.loads((root / '_source/everyday-tasks.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict) or set(config) != {'hub', 'tasks'}:
        raise ValueError('Everyday tasks require hub and tasks')
    by_path = {page['path']: page for page in pages}
    tasks = config['tasks']
    if not isinstance(tasks, list) or not tasks:
        raise ValueError('Everyday tasks require a nonempty ordered list')
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {'slug', 'label', 'seo_title', 'description', 'cue'}:
            raise ValueError('Unexpected task fields')
        slug = task['slug']
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError('Invalid or duplicate task slug')
        seen.add(slug)
        page = by_path.get('/living-well/' + slug + '/')
        if not page or page.get('living_well_kind') != 'guide' or page.get('draft') or page.get('noindex'):
            raise ValueError('Task must lead to a published, indexable guide')
        for field in ('label', 'seo_title', 'description', 'cue'):
            value = task[field]
            if not isinstance(value, str) or not value.strip() or len(value) > 220:
                raise ValueError('Invalid task label or metadata: ' + field)
    hub = config['hub']
    if not isinstance(hub, dict) or set(hub) != {'path', 'seo_title', 'description'}:
        raise ValueError('Unexpected hub metadata')
    if hub['path'] != '/living-well/technology-for-real-life/' or hub['path'] not in by_path:
        raise ValueError('Use the existing canonical everyday-work hub')
    for field in ('seo_title', 'description'):
        if not isinstance(hub[field], str) or not hub[field].strip() or len(hub[field]) > 220:
            raise ValueError('Invalid hub metadata')
    return config


def metadata(pages: list[dict], root: Path) -> list[dict]:
    config = load(root, pages)
    overrides = {'/living-well/' + t['slug'] + '/': t for t in config['tasks']}
    overrides[config['hub']['path']] = config['hub']
    result = deepcopy(pages)
    for page in result:
        if page['path'] in overrides:
            entry = overrides[page['path']]
            for key in ('seo_title', 'description'):
                page[key] = entry[key]
    return result


def cards(config: dict, entries: list[dict], *, downloads: bool = False) -> str:
    by_slug = {entry['slug']: entry for entry in entries}
    cards = []
    for task in config['tasks']:
        entry = by_slug.get(task['slug'])
        if not entry or not entry.get('utility'):
            raise ValueError('Every task needs an existing visible worksheet')
        utility.validate(entry)
        route = '/living-well/' + entry['slug'] + '/'
        body = ('<h3><a href="' + route + '">' + escape(task['label']) + '</a></h3>'
                '<p>' + escape(task['cue']) + '</p>'
                '<p class="everyday-outcome"><strong>Leave with:</strong> ' + escape(entry['outcome']) + '</p>')
        if downloads:
            body += '<p><a href="/' + utility.worksheet_path(entry).as_posix() + '" download>Save ' + escape(task['label'].lower()) + ' worksheet (.txt)</a></p>'
        else:
            body += '<p class="everyday-format">Worked guide + free text worksheet</p>'
        cards.append('<article class="everyday-task">' + body + '</article>')
    return '<div class="everyday-task-grid">' + ''.join(cards) + '</div>'
