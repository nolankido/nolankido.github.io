#!/usr/bin/env python3
"""Compile a source-backed Stand Off companion using the reviewed Poker shell.

This is a separate, manually owned publication, not a catalog draft or a
transcript of the current YouTube cut. Never run this from GitHub Actions.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

import build_poker_episode

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/portland-meadows-standoff.html"
OUTPUT = ROOT / "poker/episodes/portland-meadows-standoff/index.html"
URL = "https://nolankido.com/poker/episodes/portland-meadows-standoff/"
TITLE = "Portland Meadows Stand Off: A-K and Two Shoves | Nolan Kido"
DESCRIPTION = (
    "Nolan Kido reviews a Portland Meadows Stand Off A-K hand, a 15,000 flat, "
    "two shoves, a 46,000 call, K-K versus Q-Q, and a later rethink."
)
HEADLINE = "Portland Meadows Stand Off: A-K Facing Two Shoves"
LABEL = "Portland Meadows Stand Off"
PUBLISHED = "2026-11-04"
MODIFIED = "2026-11-04"
VIDEO = "https://www.youtube.com/watch?v=I75GOBVXij4"
MARKER = (
    "<!-- Stand Off companion: edit _source/poker/portland-meadows-standoff.html; "
    "build with _scripts/build_standoff_episode.py. -->"
)


def replace(text: str, old: str, new: str, count: int | None = None) -> str:
    found = text.count(old)
    if found == 0 or (count is not None and found != count):
        raise ValueError("Reviewed Poker shell changed: " + old[:80])
    return text.replace(old, new)


def render() -> str:
    template = build_poker_episode.render()
    original = build_poker_episode.SOURCE.read_text(encoding="utf-8")
    body = SOURCE.read_text(encoding="utf-8")
    if template.count(original) != 1 or not body.strip():
        raise ValueError("Standalone Poker source cannot be placed exactly once")
    if any(value in body.lower() for value in ("<iframe", "<form", "<script")) or "\u2014" in body:
        raise ValueError("Public companion contains a script, form, embed or em dash")
    if body.count('id="standoff-intro"') != 1 or body.count(VIDEO) != 1:
        raise ValueError("Public companion needs an introduction and one direct video link")
    prefix, suffix = template.split(original, 1)
    prefix = replace(prefix, build_poker_episode.MANUAL_MARKER, MARKER, 1)
    prefix = replace(prefix, build_poker_episode.URL, URL)
    prefix = replace(prefix, build_poker_episode.TITLE, TITLE)
    prefix = replace(prefix, escape(build_poker_episode.DESCRIPTION, quote=True),
                     escape(DESCRIPTION, quote=True))
    prefix = replace(prefix, build_poker_episode.DESCRIPTION, DESCRIPTION)
    prefix = replace(prefix, "Portland Meadows: From 6.5 Big Blinds to a Trophy",
                     HEADLINE)
    prefix = replace(prefix, "Portland Meadows Episode 1", LABEL)
    prefix = replace(prefix, "2026-11-02", PUBLISHED)
    published = prefix + body + suffix
    if published.count("<h1 ") != 1 or published.count('aria-label="Breadcrumb"') != 1:
        raise ValueError("Companion requires one H1 and one breadcrumb")
    match = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                       published, flags=re.S)
    if len(match) != 1:
        raise ValueError("Companion requires one structured-data record")
    structured = json.loads(match[0])
    if (structured.get("@type") != "Article" or structured.get("url") != URL
            or structured.get("datePublished") != PUBLISHED
            or structured.get("dateModified") != MODIFIED
            or structured.get("author", {}).get("@id") !=
            "https://nolankido.com/about/#nolan-kido"):
        raise ValueError("Standalone companion metadata is inconsistent")
    if ('<link rel="canonical" href="' + URL + '">' not in published
            or "JToB7upHqEM" in published):
        raise ValueError("Companion canonical or public video source failed")
    return published


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare published page; do not write")
    args = parser.parse_args()
    try:
        value = render()
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != value:
                print("Stand Off companion differs from authored source", file=sys.stderr)
                return 1
            print("Stand Off companion: exact source match")
            return 0
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(value, encoding="utf-8", newline="")
        print("Built " + str(OUTPUT.relative_to(ROOT)))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("Stand Off companion build error: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
