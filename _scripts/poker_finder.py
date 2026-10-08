"""Build one local-only Poker search from published pages, glossary and resources."""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import poker_library
import poker_resources


class Glossary(HTMLParser):
    """Read existing definition markup instead of maintaining duplicate definitions."""
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.entries = []
        self.inside = False
        self.item = None
        self.field = None
        self.feed(source)
        ids = [e['id'] for e in self.entries]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError('Glossary search needs distinct definitions')

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'dl' and 'poker-glossary' in attrs.get('class', '').split():
            self.inside = True
        if self.inside and tag == 'div':
            ident = attrs.get('id', '')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident):
                raise ValueError('Glossary definition needs a safe anchor')
            self.item = {'id': ident, 'title': '', 'description': ''}
        if self.item is not None and tag in ('dt', 'dd'):
            self.field = 'title' if tag == 'dt' else 'description'

    def handle_data(self, data):
        if self.item is not None and self.field:
            self.item[self.field] += data

    def handle_endtag(self, tag):
        if tag in ('dt', 'dd'):
            self.field = None
        if tag == 'div' and self.item is not None:
            if not self.item['title'].strip() or not self.item['description'].strip():
                raise ValueError('Glossary definition must include a term and explanation')
            self.entries.append(self.item)
            self.item = None
        if tag == 'dl':
            self.inside = False


def entries(root: Path, pages: list[dict], guides: list[dict], resources: list[dict]) -> list[dict]:
    by_route = {g['route']: g for g in guides}
    result = []
    for page in pages:
        if not page['path'].startswith('/poker/') or page.get('noindex') or page['path'] == '/poker/find/':
            continue
        g = by_route.get(page['path'])
        label = poker_library.TOPICS[g['topic']] if g else 'Section overview'
        result.append({'id': page['id'], 'kind': 'guide', 'title': page['title'], 'description': page['description'],
                       'url': page['path'], 'access': 'Free', 'meta': 'On this site · ' + label,
                       'keywords': (g['keywords'] + ' ' + g['level']) if g else page.get('kicker', ''),
                       'notes': '', 'context': '', 'reviewed': ''})
    for r in resources:
        result.append({'id': 'external-' + r['id'], 'kind': 'resource', 'title': r['title'], 'description': r['description'],
                       'url': r['url'], 'access': r['access'],
                       'meta': 'External · ' + ' · '.join([r['publisher'], r['kind'], r['level'], r['access']]),
                       'keywords': poker_resources.CATEGORIES[r['category']][0], 'notes': r['notes'],
                       'context': '/poker/resources/#resource-' + r['id'], 'reviewed': r['reviewed_on'],
                       'method': 'Public page read' if r['review_method'] == 'page' else 'Search index only'})
    for e in Glossary((root / '_source/poker/glossary.html').read_text(encoding='utf-8')).entries:
        result.append({'id': 'term-' + e['id'], 'kind': 'glossary', 'title': e['title'], 'description': e['description'],
                       'url': '/poker/glossary/#' + e['id'], 'access': 'Free', 'meta': 'Glossary · Hold’em terminology',
                       'keywords': '', 'notes': '', 'context': '', 'reviewed': ''})
    if len({r['id'] for r in result}) != len(result) or len({r['url'] for r in result}) != len(result):
        raise ValueError('Finder IDs and destinations must be unique')
    return result


def render(items: list[dict]) -> dict[str, str]:
    cards = []
    for e in items:
        title = escape(e['title'])
        search = escape(' '.join([e['title'], e['description'], e['keywords'], e['meta']]), quote=True)
        cards.append(f'<article class="reader-card finder-card" data-finder-card data-id="{escape(e["id"], quote=True)}" '
                     f'data-kind="{e["kind"]}" data-free="{str(e["access"] == "Free").lower()}" '
                     f'data-topics="{escape(" ".join(e.get("topics", [])), quote=True)}" '
                     f'data-search="{search}" tabindex="-1">'
                     f'<p class="reader-eyebrow">{escape(e["meta"])}</p>'
                     f'<h3><a href="{escape(e["url"], quote=True)}"' + (' rel="external"' if e['kind'] == 'resource' else '') + f'>{title}</a></h3>'
                     f'<p>{escape(e["description"])}</p>'
                     + (f'<p class="small-copy"><strong>Before you use it:</strong> {escape(e["notes"])}</p>' if e['notes'] else '')
                     + (f'<p class="small-copy">{escape(e["method"])} · <time datetime="{e["reviewed"]}">{e["reviewed"]}</time>'
                        f' · <a href="{e["context"]}">Full directory listing</a></p>' if e['context'] else '') + '</article>')
    counts = {k: sum(e['kind'] == k for e in items) for k in ('guide', 'resource', 'glossary')}
    return {'poker_finder_cards': '\n'.join(cards), 'poker_finder_count': str(len(items)),
            'poker_finder_scope': f'{counts["guide"]} on-site pages, {counts["resource"]} external resources and {counts["glossary"]} glossary entries. '
            'An overview or a glossary entry is not counted as an additional guide in the guide library.'}
