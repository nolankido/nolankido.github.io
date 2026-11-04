"""Add source-checked manually owned Poker companions to the existing Poker feed.

No private drafts, automatic polling, external feeds or scheduled publishing.
Every item is tied to a complete approved source and standalone public HTML.
"""
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

import build_poker_episode
import build_standoff_episode
import poker_episode
import poker_standoff_episode


def _add_one(feed: str, root: Path, registry, title: str, desc: str) -> str:
    info = registry.record(root)
    if info is None:
        return feed
    original = ET.fromstring(feed)
    if original.tag != "rss" or original.get("version") != "2.0":
        raise ValueError("Poker RSS requires valid RSS 2.0")
    channel = original.find("channel")
    if channel is None:
        raise ValueError("Poker RSS requires a channel")
    if any(
        e.findtext("link") == info["url"] or e.findtext("guid") == info["url"]
        for e in channel.findall("item")
    ):
        raise ValueError("Public episode cannot appear twice in the Poker feed")
    if not title or not desc or len(desc) > 320:
        raise ValueError("Poker RSS episode needs a bounded public title and description")
    stamp = format_datetime(
        datetime.combine(date.fromisoformat(info["date"]), datetime.min.time(),
                         tzinfo=timezone.utc), usegmt=True
    )
    item = (
        "    <item>\n"
        "      <title>" + escape(title) + "</title>\n"
        "      <link>" + escape(info["url"]) + "</link>\n"
        "      <description>" + escape(desc) + "</description>\n"
        '      <guid isPermaLink="true">' + escape(info["url"]) + "</guid>\n"
        "      <pubDate>" + stamp + "</pubDate>\n"
        "    </item>\n"
    )
    anchor = "    <item>\n" if "    <item>\n" in feed else "  </channel>\n"
    if anchor not in feed:
        raise ValueError("Poker RSS insertion point missing")
    published = feed.replace(anchor, item + anchor, 1)
    parsed = ET.fromstring(published)
    items = parsed.findall("./channel/item")
    if len(items) != len(channel.findall("item")) + 1 or items[0].findtext("link") != info["url"]:
        raise ValueError("Poker RSS insertion did not produce one new canonical first item")
    return published


def add(feed: str, root: Path) -> str:
    first = _add_one(feed, root, poker_episode,
                     build_poker_episode.TITLE, build_poker_episode.DESCRIPTION)
    return _add_one(first, root, poker_standoff_episode,
                    build_standoff_episode.TITLE, build_standoff_episode.DESCRIPTION)
