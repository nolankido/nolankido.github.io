"""Personal gateways select published writing without moving or duplicating articles."""
from __future__ import annotations
import html
import json
from presentation import publication
from practical_discovery import article_cards
from pathlib import Path


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _reading(page: dict | None) -> bool:
    """Do not promote a hub, private draft, or proposed experiment as evidence."""
    return bool(page and not page.get('noindex') and page.get('date') and (
        page.get('note') or page.get('poker_guide')
        or page.get('id') == 'poker-hand-review'
        or (page.get('living_well_entry') and page.get('living_well_kind') in {'essay', 'guide'})
    ))


def load(root: Path, pages: list[dict]) -> dict:
    config = json.loads((root / '_source/identity.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict):
        raise ValueError('Identity configuration must be an object')
    by_path = {page['path']: page for page in pages}
    nav = config.get('navigation')
    if not isinstance(nav, list) or not nav or any(
        not isinstance(item, dict) or not _nonempty(item.get('id'))
        or not _nonempty(item.get('label')) for item in nav
    ):
        raise ValueError('Identity navigation needs named destinations')
    ids = [item['id'] for item in nav]
    if len(ids) != len(set(ids)):
        raise ValueError('Identity navigation needs unique destinations')
    for item in nav:
        if '/' + item['id'] + '/' not in by_path:
            raise ValueError('Identity navigation must point to a published page')
    selected = config.get('selected')
    if not isinstance(selected, list) or len(selected) != 3 or any(
        not isinstance(item, dict) or not all(_nonempty(item.get(key)) for key in ('path', 'kind', 'description'))
        for item in selected
    ):
        raise ValueError('Choose three named and accurately described gateway readings')
    paths = [item['path'] for item in selected]
    if len(paths) != len(set(paths)) or any(not _reading(by_path.get(path)) for path in paths):
        raise ValueError('Gateway readings must be distinct, published editorial content')
    routes = config.get('reading_routes')
    if not isinstance(routes, list) or len(routes) != 4:
        raise ValueError('Writing needs four curated subject routes')
    seen = set()
    for expected, route in zip(['technology', 'living-well', 'poker', 'creative'], routes):
        if not isinstance(route, dict) or route.get('id') != expected or not all(
            _nonempty(route.get(key)) for key in ('label', 'title', 'description')
        ):
            raise ValueError('Writing routes must follow the established subject order')
        paths = route.get('paths')
        if not isinstance(paths, list) or len(paths) != 2 or any(not _nonempty(path) for path in paths):
            raise ValueError('Choose two published readings per writing route')
        for path in paths:
            if path in seen or not _reading(by_path.get(path)):
                raise ValueError('Writing routes need distinct published readings, not hubs or proposed results')
            seen.add(path)
    return config


def navigation(config: dict, page: dict) -> str:
    section = page.get('section') or ('notes' if page.get('note') else page['id'])
    links = []
    for item in config['navigation']:
        route = '/' + item['id'] + '/'
        current = ''
        if section == item['id']:
            current = ' aria-current="page"' if page['path'] == route else ' aria-current="location"'
        links.append('<li><a href="' + html.escape(route, quote=True) + '"' + current + '>' + html.escape(item['label']) + '</a></li>')
    return ''.join(links)


def selected_reading(config: dict, pages: list[dict]) -> str:
    by_path = {page['path']: page for page in pages}
    cards = []
    for item in config['selected']:
        page = by_path[item['path']]
        cards.append('<article class="identity-reading"><p class="note-category">' + html.escape(item['kind']) + '</p><h3><a href="' + html.escape(page['path'], quote=True) + '">' + html.escape(page['title']) + '</a></h3><p>' + html.escape(item['description']) + '</p>' + publication(page) + '</article>')
    return '<div class="identity-readings">' + ''.join(cards) + '</div>'


def reading_routes(config: dict, pages: list[dict]) -> str:
    """Use canonical titles/descriptions. Curated placement does not change authorship or dates."""
    by_path = {page['path']: page for page in pages}
    sections = []
    for route in config['reading_routes']:
        cards = []
        for path in route['paths']:
            page = by_path[path]
            kind = 'Essay / worked explanation'
            if page.get('living_well_kind'):
                kind = 'Practical guide' if page['living_well_kind'] == 'guide' else 'Essay'
            elif page.get('poker_guide'):
                kind = 'Poker study guide'
            elif page['id'] == 'poker-hand-review':
                kind = 'Fictional hand review'
            cards.append('<article class="note-entry"><p class="note-category">' + kind + '</p><h3><a href="' + html.escape(path, quote=True) + '">' + html.escape(page['title']) + '</a></h3><p>' + html.escape(page['description']) + '</p>' + publication(page) + '</article>')
        if route['id'] == 'technology':
            cards.append(article_cards(pages))
        sections.append('<section class="section folio-row writing-route" id="' + route['id'] + '" aria-labelledby="writing-' + route['id'] + '-title"><div class="section-meta"><p class="section-label">' + html.escape(route['label']) + '</p></div><div class="section-content"><h2 class="section-title" id="writing-' + route['id'] + '-title">' + html.escape(route['title']) + '</h2><p class="section-deck">' + html.escape(route['description']) + '</p><div class="notes-list">' + ''.join(cards) + '</div></div></section>')
    return '\n'.join(sections)
