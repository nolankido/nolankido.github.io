"""Reviewed independent reply acceptance case and its public discovery metadata.

This helper is deliberately read-only and stdlib-only. It never contacts a
model, tries to detect the owner's hardware, or creates a scheduled workflow.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROUTE = "/technology/review-reply-evidence-audit/"
URL = "https://nolankido.com" + ROUTE
SOURCE = Path("_source/technology/review-reply-evidence-audit.html")
OUTPUT = Path("technology/review-reply-evidence-audit/index.html")
TOOL = Path("downloads/review-reply-independent-audit.py")
PUBLISHED = "2026-11-03"
PERSON = "https://nolankido.com/about/#nolan-kido"


class Document(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.in_title = False
        self.h1 = []
        self.in_h1 = False
        self.canonical = []
        self.og_url = []
        self.robots = []
        self.description = []
        self.article_dates = []
        self.schemas = []
        self.in_json = False
        self.jsontext = ''
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'h1':
            self.in_h1 = True
            self.h1.append('')
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canonical.append(values.get('href'))
        if tag == 'meta':
            if values.get('name') == 'description':
                self.description.append(values.get('content'))
            if values.get('name') == 'robots':
                self.robots.append(values.get('content', ''))
            if values.get('property') == 'og:url':
                self.og_url.append(values.get('content'))
            if values.get('property') == 'article:published_time':
                self.article_dates.append(values.get('content'))
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_json = True
            self.jsontext = ''

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_h1:
            self.h1[-1] += data
        if self.in_json:
            self.jsontext += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'script' and self.in_json:
            self.schemas.append(json.loads(self.jsontext))
            self.in_json = False


def record(root: Path) -> dict | None:
    source, published, script = root / SOURCE, root / OUTPUT, root / TOOL
    if not source.exists() and not published.exists():
        return None
    if not source.is_file() or not published.is_file() or not script.is_file():
        raise ValueError("Independent reply case requires source, article, and original offline script")
    body = source.read_text(encoding='utf-8')
    html = published.read_text(encoding='utf-8')
    if not body.strip() or body not in html:
        raise ValueError("Independent reply case must preserve the complete approved source")
    if '—' in body or '<iframe' in html.lower():
        raise ValueError("Independent reply case must remain static and without em dashes")
    page = Document(html)
    if (page.canonical != [URL] or page.og_url != [URL] or len(page.h1) != 1
            or len(page.title) == 0 or len(page.description) != 1
            or page.article_dates != [PUBLISHED] or len(page.schemas) != 1):
        raise ValueError("Independent reply case canonical, title, description or article dates disagree")
    if any('noindex' in value.lower() or 'none' in value.lower() for value in page.robots):
        raise ValueError("Independent reply case must remain indexable")
    schema = page.schemas[0]
    if (schema.get('@type') != 'Article' or schema.get('url') != URL
            or schema.get('@id') != URL + '#article'
            or schema.get('datePublished') != PUBLISHED
            or schema.get('dateModified') != PUBLISHED
            or schema.get('author', {}).get('@id') != PERSON
            or schema.get('mainEntityOfPage', {}).get('url') != URL):
        raise ValueError("Independent reply case must match the shared author identity and date")
    if schema.get('name') != ''.join(page.title) or schema.get('description') != page.description[0]:
        raise ValueError("Independent reply case visible metadata and Article schema must agree")
    if (len(page.description[0]) > 190 or len(page.description[0]) < 80
            or '<a href="/downloads/local-ai-loopback-check.py"' not in body):
        raise ValueError("Independent reply case needs a bounded description and tool link")
    code = script.read_text(encoding='utf-8')
    if not all(token in code for token in ("SOURCE", "EXAMPLES", "NEGATIVE", "human_approval", "--self-test")):
        raise ValueError("Independent audit script must preserve offline inputs, checks, and human review boundary")
    if ('href="' + ROUTE + '"') not in (root / 'technology/index.html').read_text(encoding='utf-8'):
        raise ValueError("Technology hub must link to the independent reply audit")
    return {
        'path': ROUTE, 'url': URL, 'date': PUBLISHED,
        'title': ''.join(page.h1),
        'seo_title': ''.join(page.title),
        'description': page.description[0],
    }


def add_to_sitemap(sitemap: ET.Element, root: Path) -> None:
    item = record(root)
    if item is None:
        return
    row = ET.SubElement(sitemap, 'url')
    ET.SubElement(row, 'loc').text = item['url']
    ET.SubElement(row, 'lastmod').text = item['date']


def find_entry(root: Path) -> dict | None:
    item = record(root)
    if item is None:
        return None
    return {'path': item['path'], 'title': item['title'],
            'search_title': item['seo_title'], 'description': item['description'],
            'interests': ['technology'], 'home': 'technology',
            'kind': 'guide', 'date': item['date']}
