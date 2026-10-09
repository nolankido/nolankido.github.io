"""Editorial task-fit notes. Resource identity, access and reviews remain canonical."""
from __future__ import annotations
from datetime import date, datetime, timezone
from html import escape
import json
from pathlib import Path
import re

TEXT_FIELDS = ('fits', 'why', 'first_step', 'choose_other')
FIELDS = {'resource_id', 'alternative_id', *TEXT_FIELDS}
SHORTLISTS = {
    'cash': ('pokerbank-strategy', 'pot-odds', 'multiway-tips'),
    'free': ('pokerology-lessons', 'combinatorics', 'equity-realization'),
    'ranges': ('equilab', 'flopzilla'),
    'models': ('wizard-study-docs', 'pio-quick-start'),
}


def load(root: Path, resources: list[dict], *, as_of: date | None = None) -> dict:
    data = json.loads((root / '_source/poker/resource-selection.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'edited_on', 'entries'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Invalid resource-selection schema')
    edited = data['edited_on']
    if not isinstance(edited, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', edited):
        raise ValueError('Selection date must be YYYY-MM-DD')
    if date.fromisoformat(edited) > (as_of or datetime.now(timezone.utc).date()):
        raise ValueError('Cannot future-date selection editing')
    if not isinstance(data['entries'], list) or not data['entries']:
        raise ValueError('Selection notes must be a nonempty list')
    by_id = {r['id']: r for r in resources}
    seen = set()
    for item in data['entries']:
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise ValueError('Invalid selection fields')
        for key, value in item.items():
            if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value) or chr(0x2014) in value:
                raise ValueError('Selection fields require plain nonempty text')
            if len(value) > 240:
                raise ValueError('Keep selection notes concise')
        ident, alternative = item['resource_id'], item['alternative_id']
        if ident not in by_id or alternative not in by_id or ident == alternative or ident in seen:
            raise ValueError('Selection must reference distinct existing resources')
        seen.add(ident)
    for key, ids in SHORTLISTS.items():
        if not set(ids) <= seen or len(ids) != len(set(ids)):
            raise ValueError('Shortlist requires distinct annotated resources')
        if key in {'cash', 'free'} and any(by_id[i]['access'] != 'Free' for i in ids):
            raise ValueError('Free starting points must remain free at the linked destination')
    return data


def details(item: dict, resources: dict[str, dict]) -> str:
    fields = ''.join('<dt>' + label + '</dt><dd>' + escape(item[key]) + '</dd>' for key, label in
                     zip(TEXT_FIELDS, ('Fits this question', 'Why start here', 'First useful step', 'Choose another source when')))
    other = resources[item['alternative_id']]
    return ('<details class="poker-details resource-selection"><summary>Is this the right resource for me?</summary>'
            '<div><dl>' + fields + '</dl><p>Alternative: <a href="/poker/resources/#resource-' + escape(other['id'], quote=True)
            + '">' + escape(other['title']) + '</a>.</p></div></details>')


def directory_details(data: dict, resources: list[dict]) -> dict[str, str]:
    by_id = {r['id']: r for r in resources}
    return {item['resource_id']: details(item, by_id) for item in data['entries']}


def supplement(data: dict, resources: list[dict]) -> dict[str, str]:
    by_id = {r['id']: r for r in resources}
    notes = {item['resource_id']: item for item in data['entries']}
    values = {'selection_note_count': str(len(notes)), 'selection_edited_on': data['edited_on']}
    for key, ids in SHORTLISTS.items():
        cards = []
        for ident in ids:
            r, n = by_id[ident], notes[ident]
            method = 'Public page read' if r['review_method'] == 'page' else 'Search index only'
            cards.append('<article class="selection-option" data-selection-resource="' + ident + '">'
                         '<h3><a href="' + escape(r['url'], quote=True) + '" rel="external">' + escape(r['title']) + '</a></h3>'
                         '<p class="small-copy">' + escape(r['publisher'] + ' · ' + r['access'] + ' · ' + r['kind']) + '</p>'
                         '<p><strong>Use it for:</strong> ' + escape(n['fits']) + '</p>'
                         '<p><strong>First step:</strong> ' + escape(n['first_step']) + '</p>'
                         + ('<p class="small-copy"><strong>Before you use it:</strong> ' + escape(r['notes']) + '</p>' if r['notes'] else '')
                         + details(n, by_id)
                         + '<p class="small-copy">' + method + ' · <time datetime="' + r['reviewed_on'] + '">' + r['reviewed_on']
                         + '</time> · <a href="/poker/resources/#resource-' + ident + '">Full directory listing</a></p></article>')
        values['selection_' + key] = '<div class="selection-list">' + ''.join(cards) + '</div>'
    return values


def annotate(items: list[dict], data: dict) -> list[dict]:
    """Search original editorial fit notes without copying publisher articles."""
    by_id = {n['resource_id']: n for n in data['entries']}
    result = []
    for item in items:
        note = by_id.get(item['id'].removeprefix('external-')) if item['kind'] == 'resource' else None
        extra = ' '.join(note[field] for field in TEXT_FIELDS) if note else ''
        result.append({**item, 'keywords': (item['keywords'] + ' ' + extra).strip()})
    return result
