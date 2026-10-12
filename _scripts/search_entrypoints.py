"""Reviewed search copy and visible purpose summaries for existing reader hubs."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
from html import escape
from pathlib import Path
import json

SOURCE = Path('_source/search-entrypoints.json')
ASSET = Path('assets/search-entrypoints.css')
BEGIN = '<!-- Reader entry summary: start -->'
END = '<!-- Reader entry summary: end -->'
HUBS = frozenset({'living-well', 'living-well-ideas', 'living-well-guides',
                 'living-well-topics', 'living-well-worksheets', 'living-well-free-resources',
                 'poker-library', 'poker-study', 'notes', 'resources', 'start-here', 'creative'})


def load(root: Path, pages: list[dict]) -> dict:
    config = json.loads((root / SOURCE).read_text(encoding='utf-8'))
    if not isinstance(config, dict) or set(config) != {'entries'} or not isinstance(config['entries'], dict):
        raise ValueError('Reader entry copy needs an entries object')
    entries = config['entries']
    if set(entries) != HUBS:
        raise ValueError('Reader entry copy is limited to twelve reviewed hubs')
    by_id = {p['id']: p for p in pages}
    for key, entry in entries.items():
        page = by_id.get(key)
        if not page or page.get('date') or page.get('noindex'):
            raise ValueError('Reader entry copy must not republish an article or index a utility')
        if not isinstance(entry, dict) or set(entry) not in ({'seo_title', 'description', 'updated'}, {'title', 'seo_title', 'description', 'updated'}):
            raise ValueError('Unexpected reader entry field')
        for field, value in entry.items():
            if not isinstance(value, str) or not value.strip() or value != value.strip() or '\n' in value or chr(0x2014) in value:
                raise ValueError('Reader entry fields need plain, nonempty text')
        date.fromisoformat(entry['updated'])
        if not entry['seo_title'].endswith(' | Nolan Kido'):
            raise ValueError('Reader entry titles need the existing concise author identity')
        if len(entry['seo_title']) > 90 or not 80 <= len(entry['description']) <= 190:
            raise ValueError('Reader entry copy needs a concise, specific summary')
    return entries


def metadata(pages: list[dict], root: Path) -> list[dict]:
    entries = load(root, pages)
    result = deepcopy(pages)
    for page in result:
        if page['id'] in entries:
            page.update(entries[page['id']])
            page['entry_summary'] = entries[page['id']]['description']
    return result


def header(page: dict, content: str) -> str:
    if 'entry_summary' not in page:
        return content
    if BEGIN in content or '</section>' not in content:
        raise ValueError('Reader entry summary must be inserted once in the existing header')
    summary = BEGIN + '<p class="entry-summary">' + escape(page['entry_summary']) + '</p>' + END
    return content.replace('</section>', summary + '</section>', 1)


def head(page: dict, root: Path) -> str:
    if 'entry_summary' not in page:
        return ''
    version = sha256((root / ASSET).read_bytes()).hexdigest()[:12]
    return '\n  <link rel="stylesheet" href="/assets/search-entrypoints.css?v=' + version + '">'
