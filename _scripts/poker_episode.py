"""Public-only registration for the manually authored Portland Meadows companion.

The source and committed HTML must agree before the Poker hub may advertise the
episode as published. No live network call, private media, or video embed.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path

ROUTE = '/poker/episodes/portland-meadows-ep1/'
URL = 'https://nolankido.com' + ROUTE
SOURCE = Path('_source/poker/portland-meadows-ep1.html')
OUTPUT = Path('poker/episodes/portland-meadows-ep1/index.html')
VIDEO = 'https://www.youtube.com/watch?v=qABaiIcvvpU'
TITLE = 'Portland Meadows: From 6.5 Big Blinds to a Trophy'
PUBLISHED = '2026-11-02'
PERSON_ID = 'https://nolankido.com/about/#nolan-kido'


class Document(HTMLParser):
    def __init__(self, content: str):
        super().__init__(convert_charrefs=True)
        self.canons = []
        self.og_urls = []
        self.robots = []
        self.schemas = []
        self.in_schema = False
        self.schema_text = ''
        self.h1_count = 0
        self.video_links = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canons.append(values.get('href'))
        if tag == 'meta':
            if values.get('property') == 'og:url':
                self.og_urls.append(values.get('content'))
            if values.get('name') == 'robots':
                self.robots.append(values.get('content', ''))
        if tag == 'a' and values.get('href') == VIDEO:
            self.video_links.append(values)
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema_text = ''

    def handle_data(self, data):
        if self.in_schema:
            self.schema_text += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_schema:
            self.schemas.append(json.loads(self.schema_text))
            self.in_schema = False


def record(root: Path) -> dict | None:
    source = root / SOURCE
    output = root / OUTPUT
    if not source.exists() and not output.exists():
        return None
    if not source.is_file() or not output.is_file():
        raise ValueError('Public poker video companion needs both source and output')
    authored = source.read_text(encoding='utf-8')
    published = output.read_text(encoding='utf-8')
    if not authored.strip() or authored not in published:
        raise ValueError('Poker companion publication must contain the exact approved source')
    if 'JToB7upHqEM' in authored or 'JToB7upHqEM' in published:
        raise ValueError('Private superseded video must not be linked from the companion')
    if '<iframe' in published.lower() or '<form' in authored.lower() or '\u2014' in published:
        raise ValueError('Poker companion must remain static and respect editorial boundaries')
    doc = Document(published)
    if doc.canons != [URL] or doc.og_urls != [URL] or doc.h1_count != 1 or len(doc.schemas) != 1:
        raise ValueError('Companion requires one canonical, matching Open Graph URL, one H1 and one schema')
    if not doc.video_links or any('noindex' in value.lower() or 'none' in value.lower() for value in doc.robots):
        raise ValueError('Companion must have verified public-video address and be indexable')
    schema = doc.schemas[0]
    if (schema.get('@type') != 'Article'
            or schema.get('url') != URL
            or schema.get('@id') != URL + '#article'
            or schema.get('datePublished') != PUBLISHED
            or schema.get('author', {}).get('@id') != PERSON_ID
            or schema.get('mainEntityOfPage', {}).get('url') != URL):
        raise ValueError('Companion structured data needs reviewed article identity and date')
    required = ('6.5 big blinds', '$2,900', '$5,100', 'gross tournament payment', 'A-K suited', 'A-T')
    if any(value not in authored for value in required):
        raise ValueError('Companion missing the reviewed hand/deal distinction')
    return {'route': ROUTE, 'url': URL, 'title': TITLE,
            'date': PUBLISHED, 'video_url': VIDEO}
