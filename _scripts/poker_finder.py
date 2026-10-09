"""Build one local-only Poker search from published pages, glossary and resources."""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import poker_library
import poker_resources
import poker_content


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



class GuideText(HTMLParser):
    """Extract original article prose and existing section anchors, never answer spoilers."""
    VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'wbr', 'area', 'base', 'embed', 'param', 'track', 'col'}

    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.sections = []
        self.current = {'anchor': '', 'title': 'Introduction', 'parts': []}
        self.skip = 0
        self.heading = False
        self.feed(re.sub(r'\$\{[a-z_]+\}', '', source))
        self.finish()

    def finish(self):
        text = ' '.join(' '.join(self.current['parts']).split())
        if text:
            self.sections.append({'anchor': self.current['anchor'], 'title': self.current['title'].strip(), 'text': text})

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.skip:
            if tag not in self.VOID:
                self.skip += 1
            return
        if tag in {'script', 'style', 'nav', 'details', 'noscript'} or 'hidden' in attrs or attrs.get('aria-hidden') == 'true':
            if tag not in self.VOID:
                self.skip = 1
            return
        if tag == 'h2':
            self.finish()
            anchor = attrs.get('id', '')
            if anchor and not re.fullmatch(r'[a-zA-Z0-9_-]+', anchor):
                raise ValueError('Unsafe search section anchor')
            self.current = {'anchor': anchor, 'title': '', 'parts': []}
            self.heading = True
        elif tag in {'p', 'li', 'td', 'th', 'h3', 'br'}:
            self.current['parts'].append(' ')

    def handle_startendtag(self, tag, attrs):
        if not self.skip and tag == 'br':
            self.current['parts'].append(' ')

    def handle_endtag(self, tag):
        if self.skip:
            if tag not in self.VOID:
                self.skip -= 1
            return
        if tag == 'h2':
            self.heading = False
        elif tag in {'p', 'li', 'td', 'th', 'h3'}:
            self.current['parts'].append(' ')

    def handle_data(self, text):
        if self.skip:
            return
        if self.heading:
            self.current['title'] += text
        else:
            self.current['parts'].append(text)


def guide_sections(root: Path, page: dict, catalog: dict) -> list[dict]:
    if not page.get('poker_guide') and not page.get('poker_entry') and page['path'] != '/poker/reviewing-a-hand/':
        return []
    if page.get('poker_entry'):
        record = next(e for e in catalog['entries'] if e['slug'] == page['poker_entry'])
        source = poker_content.render(record, catalog)
    else:
        path = (root / '_source' / page['source']).resolve()
        if not path.is_relative_to((root / '_source').resolve()):
            raise ValueError('Search sources must be public manifest sources')
        source = path.read_text(encoding='utf-8')
    return GuideText(source).sections


def entries(root: Path, pages: list[dict], guides: list[dict], resources: list[dict]) -> list[dict]:
    by_route = {g['route']: g for g in guides}
    catalog = poker_content.load(root)
    result = []
    for page in pages:
        if not page['path'].startswith('/poker/') or page.get('noindex') or page['path'] == '/poker/find/':
            continue
        g = by_route.get(page['path'])
        label = poker_library.TOPICS[g['topic']] if g else 'Section overview'
        result.append({'id': page['id'], 'kind': 'guide', 'title': page['title'], 'description': page['description'],
                       'url': page['path'], 'access': 'Free', 'meta': 'On this site · ' + label,
                       'keywords': (g['keywords'] + ' ' + g['level']) if g else page.get('kicker', ''),
                       'notes': '', 'context': '', 'reviewed': '', 'sections': guide_sections(root, page, catalog)})
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
        sections = e.get('sections', [])
        passages = ''.join('<p data-finder-passage data-anchor="' + escape(s['anchor'], quote=True) + '" data-heading="' + escape(s['title'], quote=True) + '">' + escape(s['text']) + '</p>' for s in sections)
        cards.append(f'<article class="reader-card finder-card" data-finder-card data-id="{escape(e["id"], quote=True)}" '
                     f'data-kind="{e["kind"]}" data-free="{str(e["access"] == "Free").lower()}" '
                     f'data-topics="{escape(" ".join(e.get("topics", [])), quote=True)}" '
                     f'data-search="{search}" tabindex="-1">'
                     f'<p class="reader-eyebrow">{escape(e["meta"])}</p>'
                     f'<h3><a href="{escape(e["url"], quote=True)}"' + (' rel="external"' if e['kind'] == 'resource' else '') + f'>{title}</a></h3>'
                     f'<p>{escape(e["description"])}</p>'
                     + ('<p class="finder-excerpt" hidden></p><p class="finder-jump" hidden><a href="' + escape(e['url'], quote=True) + '">Read matching section</a></p><details class="finder-text"><summary>Searchable article text, without exercise answers</summary><div>' + passages + '</div></details>' if sections else '')
                     + (f'<p class="small-copy"><strong>Before you use it:</strong> {escape(e["notes"])}</p>' if e['notes'] else '')
                     + (f'<p class="small-copy">{escape(e["method"])} · <time datetime="{e["reviewed"]}">{e["reviewed"]}</time>'
                        f' · <a href="{e["context"]}">Full directory listing</a></p>' if e['context'] else '') + '<button type="button" class="finder-save" aria-pressed="false" hidden>Add to study list</button></article>')
    counts = {k: sum(e['kind'] == k for e in items) for k in ('guide', 'resource', 'glossary')}
    return {'poker_finder_cards': '\n'.join(cards), 'poker_finder_count': str(len(items)),
            'poker_finder_scope': f'{counts["guide"]} on-site pages, {counts["resource"]} external resources and {counts["glossary"]} glossary entries. '
            'Guide prose and section headings are searchable; exercise answers, navigation and external article bodies are excluded. ' +
            'An overview or glossary entry is not an additional guide.'}
