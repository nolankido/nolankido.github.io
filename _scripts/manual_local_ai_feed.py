"""Publish one source-verified practical local-AI article in the existing RSS feed.

No new feed, network requests, scraping, scheduled task, or future publication.
The separate guide has a real canonical Article and an explicit publication date.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

import local_laptop_case


def add(feed: str, root: Path) -> str:
    case = local_laptop_case.record(root)
    if case is None:
        return feed
    original = ET.fromstring(feed)
    if original.tag != 'rss' or original.get('version') != '2.0':
        raise ValueError('Practical AI feed must be RSS 2.0')
    channel = original.find('channel')
    if channel is None or channel.findtext('title') != 'Nolan Kido | Practical AI writing':
        raise ValueError('Practical AI feed channel is unexpected')
    if any(i.findtext('link') == case['url'] or i.findtext('guid') == case['url']
           for i in channel.findall('item')):
        raise ValueError('Gaming laptop guide must not be published twice')
    stamp = format_datetime(datetime.combine(date.fromisoformat(case['date']),
                                              datetime.min.time(), tzinfo=timezone.utc), usegmt=True)
    block = ('    <item>\n'
             '      <title>' + escape(case['title']) + '</title>\n'
             '      <link>' + escape(case['url']) + '</link>\n'
             '      <description>' + escape(case['description']) + '</description>\n'
             '      <guid isPermaLink="true">' + escape(case['url']) + '</guid>\n'
             '      <pubDate>' + stamp + '</pubDate>\n'
             '    </item>\n')
    anchor = '    <item>\n' if '    <item>\n' in feed else '  </channel>\n'
    if anchor not in feed:
        raise ValueError('Practical AI feed insertion point is missing')
    result = feed.replace(anchor, block + anchor, 1)
    rows = ET.fromstring(result).findall('./channel/item')
    if len(rows) != len(channel.findall('item')) + 1 or rows[0].findtext('link') != case['url']:
        raise ValueError('Exactly one new local AI guide must be listed first')
    return result
