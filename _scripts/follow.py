"""Combine the generated public feeds without rewriting their source records.

No network, clock-based publication dates, subscriptions, or tracking. Items keep
canonical identity and original publication dates. Invalid source records stop
the build instead of manufacturing missing metadata.
"""
from copy import deepcopy
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from search_visibility import LEGACY_FEED_IDS

LEGACY_SOURCES = (Path('feed.xml'), Path('living-well/feed.xml'), Path('poker/feed.xml'))
SOURCES = (*LEGACY_SOURCES, Path('technology/feed.xml'))
OUTPUT = Path('writing.xml')
ATOM = 'http://www.w3.org/2005/Atom'


def combined(outputs: dict, pages: list[dict], origin: str) -> str:
    parsed_origin = urlsplit(origin)
    if parsed_origin.scheme != 'https' or not parsed_origin.netloc or parsed_origin.path or parsed_origin.query or parsed_origin.fragment:
        raise ValueError('Combined feed requires a canonical HTTPS origin')
    published = {origin + p['path']: p for p in pages}
    if len(published) != len(pages):
        raise ValueError('Feed manifest contains duplicate routes')
    items = {}
    for path in SOURCES:
        rss = ET.fromstring(outputs[path])
        if rss.tag != 'rss' or rss.get('version') != '2.0':
            raise ValueError('Expected an RSS 2.0 source: ' + str(path))
        channel = rss.find('channel')
        if channel is None or not channel.findtext('title'):
            raise ValueError('Feed source needs a channel and title')
        for item in channel.findall('item'):
            url = item.findtext('link', '')
            page = published.get(url)
            if (not page or (page.get('noindex') and page['id'] not in LEGACY_FEED_IDS)
                    or page.get('living_well_kind') == 'experiment' or not page.get('date')):
                raise ValueError('Feed entry must identify a dated, public, non-proposed page: ' + url)
            guid = item.find('guid')
            if guid is None or guid.text != url or guid.get('isPermaLink', 'true') != 'true':
                raise ValueError('Feed entries need canonical permalink GUIDs: ' + url)
            if not item.findtext('title') or not item.findtext('description'):
                raise ValueError('Feed entry needs a title and summary: ' + url)
            try:
                date = parsedate_to_datetime(item.findtext('pubDate', ''))
                expected = datetime.strptime(page['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                if date.tzinfo is None or date.astimezone(timezone.utc) != expected:
                    raise ValueError('Feed publication date disagrees with the page: ' + url)
            except (TypeError, IndexError, OverflowError) as exc:
                raise ValueError('Invalid feed publication date: ' + url) from exc
            # Whitespace is formatting, not feed identity. Compare semantic records.
            signature = [(child.tag, sorted(child.attrib.items()), child.text) for child in item]
            if url in items:
                if signature != items[url][2]:
                    raise ValueError('Conflicting records for one canonical page: ' + url)
                continue
            copy = deepcopy(item)
            ET.SubElement(copy, 'source', {'url': origin + '/' + path.as_posix()}).text = channel.findtext('title')
            items[url] = (date, copy, signature)
    ET.register_namespace('atom', ATOM)
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    for key, value in [('title', 'Nolan Kido | Writing across the site'), ('link', origin + '/notes/'),
                       ('description', 'Published writing from Notes, Living Well, Poker, and Technology. Original dates and links, in one feed. Proposed experiments and directory changes are not included.'),
                       ('language', 'en-us')]:
        ET.SubElement(channel, key).text = value
    ET.SubElement(channel, '{' + ATOM + '}link', {'href': origin + '/writing.xml', 'rel': 'self', 'type': 'application/rss+xml'})
    if items:
        ET.SubElement(channel, 'pubDate').text = format_datetime(max(value[0] for value in items.values()), usegmt=True)
    for url, (date, item, signature) in sorted(items.items(), key=lambda entry: (-entry[1][0].timestamp(), entry[0])):
        channel.append(item)
    ET.indent(rss, space='  ')
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode') + '\n'
