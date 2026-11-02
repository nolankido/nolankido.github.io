"""Add only a published, source-checked Poker video companion to Poker RSS.

No new story is invented, and no external feed or publishing service is used.
This uses the same date-only midnight-GMT convention as the existing site.
"""
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET
import build_poker_episode
import poker_episode


def add(feed: str, root: Path) -> str:
    info = poker_episode.record(root)
    if info is None:
        return feed
    original = ET.fromstring(feed)
    if original.tag != 'rss' or original.get('version') != '2.0':
        raise ValueError('Poker RSS requires valid RSS 2.0')
    channel = original.find('channel')
    if channel is None:
        raise ValueError('Poker RSS requires a channel')
    if any(e.findtext('link') == info['url'] or e.findtext('guid') == info['url']
           for e in channel.findall('item')):
        raise ValueError('Public episode cannot appear twice in the Poker feed')
    title = build_poker_episode.TITLE
    desc = build_poker_episode.DESCRIPTION
    if not title or not desc or len(desc) > 320:
        raise ValueError('Poker RSS episode needs a bounded public title and description')
    stamp = format_datetime(datetime.combine(date.fromisoformat(info['date']),
                                              datetime.min.time(), tzinfo=timezone.utc), usegmt=True)
    item = ('    <item>\n'
            '      <title>' + escape(title) + '</title>\n'
            '      <link>' + escape(info['url']) + '</link>\n'
            '      <description>' + escape(desc) + '</description>\n'
            '      <guid isPermaLink="true">' + escape(info['url']) + '</guid>\n'
            '      <pubDate>' + stamp + '</pubDate>\n'
            '    </item>\n')
    anchor = '    <item>\n' if '    <item>\n' in feed else '  </channel>\n'
    if feed.count(anchor) < 1:
        raise ValueError('Poker RSS insertion point missing')
    published = feed.replace(anchor, item + anchor, 1)
    parsed = ET.fromstring(published)
    rows = parsed.findall('./channel/item')
    if len(rows) != len(channel.findall('item')) + 1 or rows[0].findtext('link') != info['url']:
        raise ValueError('Poker RSS insertion did not produce exactly one new first item')
    return published
