"""Register one independently listed, archived-source Reserve Day 1 video page.

The private production source remains private. The public route is accepted
only when its separate authored body and generated Article agree exactly.
"""
from __future__ import annotations

import json
from pathlib import Path

from poker_standoff_episode import _Document

ROUTE = "/poker/episodes/reserve-day-1/"
URL = "https://nolankido.com" + ROUTE
SOURCE = Path("_source/poker/reserve-day-1.html")
OUTPUT = Path("poker/episodes/reserve-day-1/index.html")
LEDGER = Path("downloads/reserve-day1-public-source-ledger.json")
VIDEO = "https://www.youtube.com/watch?v=edNSD5BjIV8"
TITLE = "Seven Big Blinds and a Three-Way A-K Pot at the Reserve"
PUBLISHED = "2026-11-18"
MODIFIED = "2026-11-18"
PERSON_ID = "https://nolankido.com/about/#nolan-kido"


def record(root: Path) -> dict | None:
    source = root / SOURCE
    output = root / OUTPUT
    if not source.exists() and not output.exists():
        return None
    if not source.is_file() or not output.is_file() or not (root / LEDGER).is_file():
        raise ValueError("Reserve companion requires approved source, output and ledger")
    authored = source.read_text(encoding="utf-8")
    html = output.read_text(encoding="utf-8")
    if not authored.strip() or html.count(authored) != 1:
        raise ValueError("Reserve published page must contain the exact authored source once")
    if (any(value in authored.lower() for value in ("<iframe", "<form", "<script"))
            or "\u2014" in html):
        raise ValueError("Reserve source must be static and free of em dashes")
    if ("have not independently compared" not in authored
            or "not asserted as current public-video chapter" not in authored
            or "not" not in authored):
        raise ValueError("Reserve source must retain current-cut evidence limits")
    doc = _Document(html)
    if (doc.canonical != [URL] or doc.og_url != [URL]
            or doc.h1_count != 1 or len(doc.schema) != 1
            or html.count('href="' + VIDEO + '"') != 1):
        raise ValueError("Reserve companion must have one canonical, H1, schema, video")
    if any("noindex" in directive.lower() or "none" in directive.lower()
           for directive in doc.robots):
        raise ValueError("Reserve companion must be indexable")
    article = doc.schema[0]
    if (article.get("@type") != "Article" or article.get("url") != URL
            or article.get("@id") != URL + "#article"
            or article.get("headline") != TITLE
            or article.get("datePublished") != PUBLISHED
            or article.get("dateModified") != MODIFIED
            or article.get("author", {}).get("@id") != PERSON_ID
            or article.get("mainEntityOfPage", {}).get("url") != URL):
        raise ValueError("Reserve Article metadata disagrees with registered source")
    for token in ("527 entries", "80 paid", "63rd", "$800", "A♣K♥",
                  "Q-J offsuit", "9♦10♦", "28 − 18 = 10 BB"):
        if token not in authored:
            raise ValueError("Reserve source lost a checked fact or arithmetic boundary")
    ledger = json.loads((root / LEDGER).read_text(encoding="utf-8"))
    if (ledger.get("event", {}).get("entries") != 527
            or ledger.get("finish", {}).get("place") != 63
            or ledger.get("finish", {}).get("gross_cash_usd") != 800
            or ledger.get("video", {}).get("current_youtube_cut_compared_with_archive") is not False):
        raise ValueError("Reserve evidence ledger must stay bounded and internally coherent")
    return {"route": ROUTE, "url": URL, "title": TITLE,
            "date": PUBLISHED, "modified": MODIFIED, "video_url": VIDEO}
