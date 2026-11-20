"""Source-backed public book pages for sitemap and local Find discovery."""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

ORIGIN = "https://nolankido.com"
PERSON = ORIGIN + "/about/#nolan-kido"
UPDATED = "2026-11-20"
BOOKS = [
    {"slug": "one-workflow-at-a-time", "title": "One Workflow at a Time",
     "seo": "One Workflow at a Time: Practical AI Book | Nolan Kido",
     "description": "Nolan Kido's One Workflow at a Time examines small-business AI pilots, complete workflow costs, verification, and human approvals. Read free companion methods.",
     "interest": "technology"},
    {"slug": "how-to-play-no-limit-texas-holdem",
     "title": "How to Play No-Limit Texas Hold’em",
     "seo": "How to Play No-Limit Texas Hold’em: Book | Nolan Kido",
     "description": "About How to Play No-Limit Texas Hold’em by Nolan Kido: a beginner poker book covering rules, position, betting, ranges and decision review, with free practice.",
     "interest": "poker"},
]

def route(item):
    return "/books/" + item["slug"] + "/"

def published(root: Path) -> list[dict]:
    items = []
    for item in BOOKS:
        path = Path("books") / item["slug"] / "index.html"
        src = Path("_source/books") / (item["slug"] + ".html")
        source, target = root / src, root / path
        if not source.exists() and not target.exists():
            continue
        if not source.is_file() or not target.is_file() or source.read_text(encoding="utf-8") != target.read_text(encoding="utf-8"):
            raise ValueError("Book page must match exact public source: " + item["slug"])
        html = target.read_text(encoding="utf-8")
        url = ORIGIN + route(item)
        if html.count('<link rel="canonical" href="' + url + '">') != 1 or html.count('<meta property="og:url" content="' + url + '">') != 1:
            raise ValueError("Book canonical and Open Graph URL must match")
        if len(re.findall(r"<h1\b", html)) != 1 or 'content="noindex' in html.lower() or "—" in html:
            raise ValueError("Book must be indexable, accessible and free of em dashes")
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        if not match or len(re.findall(r'<script type="application/ld\+json">', html)) != 1:
            raise ValueError("Book must have one schema record")
        schema = json.loads(match.group(1))
        entity = schema.get("mainEntity", {})
        if (schema.get("@type") != "WebPage" or schema.get("url") != url or schema.get("dateModified") != UPDATED
            or entity.get("@type") != "Book" or entity.get("@id") != url + "#book"
            or entity.get("author", {}).get("@id") != PERSON
            or entity.get("isbn") is not None or entity.get("offers") is not None or entity.get("datePublished") is not None):
            raise ValueError("Book identity or provenance schema invalid")
        for link in ("index.html", "creative/index.html"):
            if 'href="' + route(item) + '"' not in (root / link).read_text(encoding="utf-8"):
                raise ValueError("Book needs inbound link from " + link)
        items.append(item)
    return items

def add_to_sitemap(root_sitemap: ET.Element, root: Path) -> None:
    for book in published(root):
        url = ET.SubElement(root_sitemap, "url")
        ET.SubElement(url, "loc").text = ORIGIN + route(book)
        ET.SubElement(url, "lastmod").text = UPDATED

def find_entries(root: Path) -> list[dict]:
    return [{"path": route(b), "title": b["title"], "search_title": b["seo"],
             "description": b["description"], "interests": [b["interest"], "creative"],
             "home": b["interest"], "kind": "book", "date": ""}
            for b in published(root)]
