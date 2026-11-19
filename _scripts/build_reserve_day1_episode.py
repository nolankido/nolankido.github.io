#!/usr/bin/env python3
"""Build one archived-source NolanPoker Reserve Day 1 companion locally.

The existing public Poker shell is reused. This page is not part of the main
manifest and must not be built by an automated remote workflow.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

import build_poker_episode
from build_standoff_episode import replace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/reserve-day-1.html"
OUTPUT = ROOT / "poker/episodes/reserve-day-1/index.html"
URL = "https://nolankido.com/poker/episodes/reserve-day-1/"
TITLE = "WSOP Circuit Reserve Day 1: 7 BB and a Three-Way A-K Pot | Nolan Kido"
DESCRIPTION = (
    "Nolan Kido's source-bounded Reserve Poker Club WSOP Circuit Day 1 account: "
    "seven big blinds near the money, an A-K three-way pot and 63rd for $800."
)
HEADLINE = "Seven Big Blinds and a Three-Way A-K Pot at the Reserve"
LABEL = "WSOP Circuit Reserve Day 1"
PUBLISHED = "2026-11-18"
MODIFIED = "2026-11-18"
VIDEO = "https://www.youtube.com/watch?v=edNSD5BjIV8"
MARKER = (
    "<!-- Reserve Day 1 companion: edit _source/poker/reserve-day-1.html; "
    "build with _scripts/build_reserve_day1_episode.py. -->"
)


def render() -> str:
    template = build_poker_episode.render()
    original = build_poker_episode.SOURCE.read_text(encoding="utf-8")
    authored = SOURCE.read_text(encoding="utf-8")
    if template.count(original) != 1 or not authored.strip():
        raise ValueError("Reserve companion source must fit the Poker shell once")
    if (any(token in authored.lower() for token in ("<iframe", "<script", "<form"))
            or "\u2014" in authored):
        raise ValueError("Reserve companion cannot embed media, forms, code or em dashes")
    if authored.count('id="reserve-intro"') != 1 or authored.count(VIDEO) != 1:
        raise ValueError("Reserve companion requires one introduction and one public video link")
    prefix, suffix = template.split(original, 1)
    prefix = replace(prefix, build_poker_episode.MANUAL_MARKER, MARKER, 1)
    prefix = replace(prefix, build_poker_episode.URL, URL)
    prefix = replace(prefix, build_poker_episode.TITLE, TITLE)
    prefix = replace(prefix, escape(build_poker_episode.DESCRIPTION, quote=True),
                     escape(DESCRIPTION, quote=True))
    prefix = replace(prefix, build_poker_episode.DESCRIPTION, DESCRIPTION)
    prefix = replace(prefix, "Portland Meadows: From 6.5 Big Blinds to a Trophy", HEADLINE)
    prefix = replace(prefix, "Portland Meadows Episode 1", LABEL)
    prefix = replace(prefix, "2026-11-02", PUBLISHED)
    prefix = replace(prefix, build_poker_episode.MODIFIED, MODIFIED)
    # The reused shell has a spacer line; keep generated HTML whitespace-clean.
    page = re.sub(r"(?m)^[ \t]+$", "", prefix + authored + suffix)
    if page.count("<h1 ") != 1 or page.count('aria-label="Breadcrumb"') != 1:
        raise ValueError("Reserve companion requires one H1 and breadcrumb")
    found = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page,
                       flags=re.S)
    if len(found) != 1:
        raise ValueError("Reserve companion requires one structured-data record")
    article = json.loads(found[0])
    if (article.get("@type") != "Article" or article.get("url") != URL
            or article.get("headline") != HEADLINE
            or article.get("datePublished") != PUBLISHED
            or article.get("dateModified") != MODIFIED
            or article.get("author", {}).get("@id") !=
            "https://nolankido.com/about/#nolan-kido"):
        raise ValueError("Reserve companion structured data is inconsistent")
    if ('<link rel="canonical" href="' + URL + '">' not in page
            or "JToB7upHqEM" in page):
        raise ValueError("Reserve companion canonical or video source failed")
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare without writing")
    args = parser.parse_args()
    try:
        html = render()
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != html:
                print("Reserve Day 1 companion differs from authored source", file=sys.stderr)
                return 1
            print("Reserve Day 1 companion: exact source match")
            return 0
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(html, encoding="utf-8", newline="")
        print("Built " + str(OUTPUT.relative_to(ROOT)))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("Reserve Day 1 build error: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
