"""Static Poker discovery and reader metadata. No third-party dependencies."""
from html import escape
from html.parser import HTMLParser
from math import ceil
from pathlib import Path
from datetime import datetime
import json
import re

TOPICS = {'basics': 'Learn the basics', 'hands': 'Read a hand', 'tournaments': 'Tournament study',
          'practice': 'Try a decision', 'results': 'Results and review', 'creative': 'Make a vlog'}
LEVELS = {'Start here', 'Build understanding', 'Go deeper', 'Practice', 'Creator workflow'}

class PlainText(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.parts = []; self.ignored = 0
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.ignored += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.ignored = max(0, self.ignored - 1)
    def handle_data(self, value):
        if not self.ignored: self.parts.append(value)

def minutes(source):
    """Editorial estimate, not a measured reader speed; include disclosure answers."""
    clean = re.sub(r'\$\{[a-z_]+\}', '', ' '.join(PlainText(source).parts))
    return max(1, ceil(len(clean.split()) / 225))

def load(root, pages):
    data = json.loads((root / '_source/poker/library.json').read_text(encoding='utf-8'))
    if set(data) != {'version', 'entries'} or data['version'] != 1 or not isinstance(data['entries'], list):
        raise ValueError('Invalid Poker library schema')
    by_path = {p['path']: p for p in pages}
    expected = {p['path'] for p in pages if p.get('poker_guide')} | {'/poker/reviewing-a-hand/'}
    result = []; seen = set()
    for item in data['entries']:
        if not isinstance(item, dict) or set(item) != {'slug', 'title', 'description', 'topic', 'level', 'keywords'}:
            raise ValueError('Invalid Poker library entry fields')
        if not all(isinstance(v, str) and v.strip() for v in item.values()):
            raise ValueError('Library fields must be nonempty strings')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item['slug']):
            raise ValueError('Invalid library slug')
        route = '/poker/' + item['slug'] + '/'
        if route not in expected or route in seen or item['topic'] not in TOPICS or item['level'] not in LEVELS:
            raise ValueError('Unknown or duplicate library route/category: ' + route)
        page = by_path[route]
        source = (root / '_source' / page['source']).resolve()
        if not source.is_relative_to((root / '_source').resolve()):
            raise ValueError('Library source outside source directory')
        result.append({**item, 'route': route, 'minutes': minutes(source.read_text(encoding='utf-8'))})
        seen.add(route)
    if seen != expected:
        raise ValueError('Library missing published guides: ' + ', '.join(sorted(expected - seen)))
    return result

def card(item):
    topic = TOPICS[item['topic']]
    search = ' '.join([item['title'], item['description'], item['keywords'], topic, item['level']])
    return (f'<article class="reader-card" data-library-card data-topic="{item["topic"]}" data-search="{escape(search, quote=True)}">'
            f'<p class="reader-eyebrow">{escape(topic)}</p><h3><a href="{item["route"]}">{escape(item["title"])}</a></h3>'
            f'<p>{escape(item["description"])}</p><p class="reader-card-meta"><span>{escape(item["level"])}</span>'
            f'<span>About {item["minutes"]} min read</span></p></article>')

def supplement(entries):
    buttons = [f'<button type="button" data-filter="all" aria-pressed="true">All ({len(entries)})</button>']
    for key, title in TOPICS.items():
        count = sum(item['topic'] == key for item in entries)
        buttons.append(f'<button type="button" data-filter="{key}" aria-pressed="false">{escape(title)} ({count})</button>')
    controls = ('<div class="reader-controls" id="library-controls" hidden>'
                '<label for="library-search">Search titles, topics and summaries</label>'
                '<div class="reader-search-row"><input type="search" id="library-search" maxlength="160" autocomplete="off" spellcheck="false" aria-describedby="library-search-help">'
                '<button type="button" id="library-reset">Clear filters</button></div>'
                '<p class="reader-help" id="library-search-help">Try “side pots”, “ICM” or “vlog”. Search terms stay on this page: no search requests, saved history or analytics events.</p>'
                '<div class="reader-filters" role="group" aria-label="Filter by topic">' + ''.join(buttons) + '</div></div>')
    index = ('<div id="poker-library">' + controls +
             f'<p class="reader-result-count" id="library-count" role="status" aria-live="polite" aria-atomic="true">{len(entries)} guides available.</p>'
             '<p class="reader-empty" id="library-empty" hidden>No guides match these filters. Try fewer words, choose another topic, or clear the filters.</p>'
             '<div class="reader-grid" id="library-grid">' + ''.join(card(item) for item in entries) + '</div></div>')
    return {'poker_library': index, 'poker_library_count': str(len(entries))}

def reader_meta(page, entries):
    item = next((e for e in entries if e['route'] == page['path']), None)
    if item is None: return ''
    parts = [escape(item['level']), f'<a href="/poker/library/#reading-times">About {item["minutes"]} min read</a>']
    date = page.get('date') or page.get('updated')
    if date:
        dt = datetime.strptime(date, '%Y-%m-%d')
        parts.append(f'<time datetime="{date}">{dt.strftime("%B")} {dt.day}, {dt.year}</time>')
    return '<p class="reader-meta">' + ''.join('<span>' + part + '</span>' for part in parts) + '</p>'

def related(page, entries):
    item = next((e for e in entries if e['route'] == page['path']), None)
    if item is None: return ''
    peers = [e for e in entries if e['route'] != item['route'] and e['topic'] == item['topic']]
    if len(peers) < 2:
        peers += [e for e in entries if e['route'] != item['route'] and e not in peers]
    return ('<aside class="shell reader-related" aria-labelledby="reader-next-heading"><p class="reader-eyebrow">Keep exploring</p>'
            '<h2 id="reader-next-heading">Take the next useful step.</h2><div class="reader-related-grid">' +
            ''.join(card(e) for e in peers[:2]) + '</div><nav class="reader-tools" aria-label="Reading tools">'
            '<a href="/poker/library/">All Poker guides</a><a href="#main">Back to top</a></nav></aside>')
