"""Validate committed title cards against current public content. No image markup."""
from hashlib import sha256
from pathlib import Path
import json
import re

SOURCE = Path('_source/reader-previews.json')
HUB_IDS = frozenset({'poker', 'living-well', 'creative'})


def eligible(page: dict) -> bool:
    return not page.get('noindex') and bool(page['id'] in HUB_IDS or page.get('note') or page.get('poker_entry') or
        page.get('poker_guide') or page.get('living_well_entry') or page.get('evidence_article') or page.get('worked_guide'))


def label(page: dict) -> str:
    if page['id'] in HUB_IDS:
        return {'poker': 'POKER / LEARN, FIND & STUDY', 'living-well': 'LIVING WELL / IDEAS & PRACTICE', 'creative': 'CREATIVE WORK / WRITING & STORYTELLING'}[page['id']]
    if page.get('living_well_kind') == 'experiment':
        return 'LIVING WELL / PROPOSED EXPERIMENT'
    if page.get('living_well_entry'):
        return 'LIVING WELL / ' + ('ESSAY' if page.get('living_well_kind') == 'essay' else 'PRACTICAL GUIDE')
    if page.get('note'):
        return 'WRITING / ESSAY'
    if page.get('evidence_article'):
        return 'PRACTICAL AI / RECORDED CASE'
    if page.get('worked_guide'):
        return 'PRACTICAL AI / WORKED GUIDE'
    if page.get('poker_entry'):
        return 'POKER / PUBLISHED ACCOUNT'
    return 'POKER / PRACTICAL GUIDE'


def load(root: Path, pages: list[dict], retained: set[str]) -> dict:
    path = root / SOURCE
    if not path.exists():
        return {}  # Standalone legacy presentation fixtures have no extra catalogue.
    catalog = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(catalog, dict) or set(catalog) != {'version', 'pages'} or catalog['version'] != 1 or not isinstance(catalog['pages'], dict):
        raise ValueError('Reader previews need a versioned page catalogue')
    by_id = {p['id']: p for p in pages}
    result = {}
    for key, record in catalog['pages'].items():
        page = by_id.get(key)
        if key in retained or not page or not eligible(page):
            raise ValueError('Reader previews must not replace retained cards or describe unpublished work')
        if not isinstance(record, dict) or set(record) != {'path', 'title', 'label', 'src', 'sha256', 'layout'}:
            raise ValueError('Unexpected reader preview field')
        if (record['path'], record['title'], record['label']) != (page['path'], page['title'], label(page)):
            raise ValueError('Reader preview is stale for ' + key + '; regenerate after changing its title or status')
        expected = '/assets/social/reader-' + key + '.png'
        if record['src'] != expected or not re.fullmatch(r'/assets/social/reader-[a-z0-9-]+[.]png', expected):
            raise ValueError('Reader preview needs its stable local PNG address')
        raw = (root / expected.lstrip('/')).read_bytes()
        if sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Reader preview bytes do not match the reviewed catalogue')
        layout = record['layout']
        if not isinstance(layout, dict) or set(layout) != {'lines', 'font_size', 'bounds'} or not isinstance(layout['lines'], list) or not 1 <= len(layout['lines']) <= 3:
            raise ValueError('Invalid title-card line layout')
        if ' '.join(layout['lines']) != ' '.join(page['title'].split()) or not 42 <= layout['font_size'] <= 64:
            raise ValueError('The full current title must fit the reader preview')
        bounds = layout['bounds']
        if not isinstance(bounds, list) or len(bounds) != 4 or not all(isinstance(v, int) for v in bounds) or not (90 <= bounds[0] < bounds[2] <= 1124 and 155 <= bounds[1] < bounds[3] <= 445):
            raise ValueError('Reader preview exceeds the safe title area')
        result[key] = {'src': expected, 'alt': record['label'] + '. ' + record['title'] + ' Nolan Kido. nolankido.com.'}
    return result
