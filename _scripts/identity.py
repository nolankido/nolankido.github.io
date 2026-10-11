"""Small, explicit personal gateway. Published content stays in its original section."""
import html
import json

def load(root, pages):
    config = json.loads((root / '_source/identity.json').read_text(encoding='utf-8'))
    by_path = {page['path']: page for page in pages}
    nav = config['navigation']
    ids = [item['id'] for item in nav]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError('Identity navigation needs unique destinations')
    for item in nav:
        if '/' + item['id'] + '/' not in by_path or not isinstance(item['label'], str) or not item['label'].strip():
            raise ValueError('Identity navigation must point to a published page')
    selected = config['selected']
    paths = [item['path'] for item in selected]
    if len(paths) != 3 or len(paths) != len(set(paths)):
        raise ValueError('Choose exactly three distinct gateway readings')
    for item in selected:
        page = by_path.get(item['path'])
        if not page or page.get('noindex') or page.get('living_well_kind') == 'experiment':
            raise ValueError('Gateway readings must be public, published content')
        if not all(isinstance(item.get(key), str) and item[key].strip() for key in ('kind', 'description')):
            raise ValueError('Gateway readings need a kind and an honest description')
    return config

def navigation(config, page):
    section = page.get('section') or ('notes' if page.get('note') else page['id'])
    links = []
    for item in config['navigation']:
        route = '/' + item['id'] + '/'
        current = ''
        if section == item['id']:
            current = ' aria-current="page"' if page['path'] == route else ' aria-current="location"'
        links.append('<li><a href="' + html.escape(route, quote=True) + '"' + current + '>' + html.escape(item['label']) + '</a></li>')
    return ''.join(links)

def selected_reading(config, pages):
    by_path = {page['path']: page for page in pages}
    cards = []
    for item in config['selected']:
        page = by_path[item['path']]
        cards.append('<article class="identity-reading"><p class="note-category">' + html.escape(item['kind']) + '</p><h3><a href="' + html.escape(page['path'], quote=True) + '">' + html.escape(page['title']) + '</a></h3><p>' + html.escape(item['description']) + '</p></article>')
    return '<div class="identity-readings">' + ''.join(cards) + '</div>'
