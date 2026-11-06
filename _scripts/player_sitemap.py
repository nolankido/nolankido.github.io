"""Register one independently reviewed manual Poker page in the main sitemap.

The player page is built by build_player_profile.py, not by the manifest loop.
This bounded registration never guesses URLs or dates and does not create a
second sitemap, search landing page, or publishing workflow.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import poker_episode
import poker_standoff_episode

ROUTE = '/poker/nolan-kido/'
URL = 'https://nolankido.com' + ROUTE
RELATIVE = Path('poker/nolan-kido/index.html')
SOURCE = Path('_source/poker/nolan-kido-profile.html')
MODIFIED = '2026-11-06'
PERSON = 'https://nolankido.com/about/#nolan-kido'


class _Document(HTMLParser):
    def __init__(self, content: str):
        super().__init__(convert_charrefs=True)
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.open_graph: list[str] = []
        self.jsonld: list[dict] = []
        self.in_schema = False
        self.schema_data = ''
        self.h1 = 0
        self.feed(content)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canonicals.append(values.get('href', ''))
        if tag == 'meta':
            if values.get('name', '').lower() == 'robots':
                self.robots.append(values.get('content', ''))
            if values.get('property') == 'og:url':
                self.open_graph.append(values.get('content', ''))
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema_data = ''

    def handle_data(self, content: str) -> None:
        if self.in_schema:
            self.schema_data += content

    def handle_endtag(self, tag: str) -> None:
        if tag == 'script' and self.in_schema:
            try:
                self.jsonld.append(json.loads(self.schema_data))
            except ValueError as exc:
                raise ValueError('Invalid player profile structured data') from exc
            self.in_schema = False


def record(root: Path) -> tuple[str, str] | None:
    """Require a canonical, indexable, source-backed manual profile if present.

    Minimal temporary build fixtures that have neither source nor page may
    omit this independently published route. A partial or invalid publication
    always fails instead of advertising a broken canonical.
    """
    source = root / SOURCE
    published = root / RELATIVE
    if not source.exists() and not published.exists():
        return None
    if not source.is_file() or not published.is_file():
        raise ValueError('Player sitemap entry requires source and published HTML')
    body = source.read_text(encoding='utf-8')
    html = published.read_text(encoding='utf-8')
    if not body.strip() or body not in html:
        raise ValueError('Player sitemap source must appear verbatim in the public page')
    document = _Document(html)
    if document.canonicals != [URL] or document.open_graph != [URL] or document.h1 != 1:
        raise ValueError('Player sitemap entry needs exactly one matching canonical, share URL and H1')
    if any('noindex' in directive.lower() or 'none' in directive.lower()
           for directive in document.robots):
        raise ValueError('Player sitemap entry must not point to a noindex page')
    if len(document.jsonld) != 1:
        raise ValueError('Player sitemap entry needs one structured-data record')
    schema = document.jsonld[0]
    if (schema.get('@type') != 'WebPage' or schema.get('url') != URL or
            schema.get('@id') != URL + '#webpage' or
            schema.get('dateModified') != MODIFIED or
            schema.get('about', {}).get('@id') != PERSON):
        raise ValueError('Player sitemap record disagrees with public identity or review date')
    for link in ('poker/index.html', 'about/index.html'):
        if 'href="' + ROUTE + '"' not in (root / link).read_text(encoding='utf-8'):
            raise ValueError('Player sitemap entry must have a native internal discovery link: ' + link)
    return URL, MODIFIED


def add_to_sitemap(sitemap: ET.Element, root: Path) -> None:
    item = record(root)
    if item is not None:
        url, modified = item
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = url
        ET.SubElement(entry, 'lastmod').text = modified
    episode = poker_episode.record(root)
    if episode is not None:
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = episode['url']
        ET.SubElement(entry, 'lastmod').text = episode['modified']
    standoff = poker_standoff_episode.record(root)
    if standoff is not None:
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = standoff['url']
        ET.SubElement(entry, 'lastmod').text = standoff['modified']
