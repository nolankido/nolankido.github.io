"""Source-backed public book pages for sitemap and local Find discovery."""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

ORIGIN = "https://nolankido.com"
PERSON = ORIGIN + "/about/#nolan-kido"
UPDATED = "2026-11-23"
BOOKS = [
    {"slug": "one-workflow-at-a-time", "title": "One Workflow at a Time",
     "seo": "One Workflow at a Time: Practical AI Book | Nolan Kido",
     "description": "Nolan Kido's One Workflow at a Time examines small-business AI pilots, complete workflow costs, verification, and human approvals. Read free companion methods.",
     "interest": "technology", "modified": "2026-11-22"},
    {"slug": "how-to-play-no-limit-texas-holdem",
     "title": "How to Play No-Limit Texas Hold’em",
     "seo": "How to Play No-Limit Texas Hold’em: Book | Nolan Kido",
     "description": "About How to Play No-Limit Texas Hold’em by Nolan Kido: a beginner poker book covering rules, position, betting, ranges and decision review, with free practice.",
     "interest": "poker", "modified": "2026-11-22"},
]

HUB_ROUTE = "/books/"
HUB_URL = ORIGIN + HUB_ROUTE
HUB_SOURCE = Path("_source/books/index.html")
HUB_OUTPUT = Path("books/index.html")
HUB_TITLE = "Books by Nolan Kido | Practical AI and Texas Hold’em"
HUB_DESCRIPTION = ("Explore three books by Nolan Kido: AI Works, Human Decides; One Workflow at a Time; "
                   "and How to Play No-Limit Texas Hold’em. Free companion exercises.")
THIRD_BOOK = {
    "@type": "Book",
    "@id": HUB_URL + "#book-ai-works-human-decides",
    "name": "AI Works, Human Decides",
    "url": HUB_URL + "#book-ai-works-human-decides",
    "description": "A book about using AI for practical tasks while retaining human judgment, verification, and responsibility.",
    "author": {"@id": PERSON},
}


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
        if (schema.get("@type") != "WebPage" or schema.get("url") != url or schema.get("dateModified") != item["modified"]
            or entity.get("@type") != "Book" or entity.get("@id") != url + "#book"
            or entity.get("author", {}).get("@id") != PERSON
            or schema.get("about", {}).get("@id") != url + "#book"
            or entity.get("mainEntityOfPage", {}).get("@id") != url + "#webpage"
            or entity.get("isbn") is not None or entity.get("offers") is not None or entity.get("datePublished") is not None):
            raise ValueError("Book identity or provenance schema invalid")
        for link in ("index.html", "creative/index.html"):
            if 'href="' + route(item) + '"' not in (root / link).read_text(encoding="utf-8"):
                raise ValueError("Book needs inbound link from " + link)
        items.append(item)
    return items

def hub_record(root: Path) -> dict | None:
    """Register an author catalog only when its full source and public page agree."""
    source, target = root / HUB_SOURCE, root / HUB_OUTPUT
    if not source.exists() and not target.exists():
        return None
    if not source.is_file() or not target.is_file():
        raise ValueError("Books catalog requires source and published HTML")
    html = target.read_text(encoding="utf-8")
    if not html or source.read_text(encoding="utf-8") != html:
        raise ValueError("Books catalog published HTML differs from source")
    if (html.count('<link rel="canonical" href="' + HUB_URL + '">') != 1
            or html.count('<meta property="og:url" content="' + HUB_URL + '">') != 1
            or len(re.findall(r'<h1\b', html)) != 1
            or len(re.findall(r'<main\b', html)) != 1
            or 'noindex' in html.lower() or '—' in html):
        raise ValueError("Books catalog requires one indexable canonical and accessible landmarks")
    metas = re.findall(r'<meta name="description" content="([^"]+)">', html)
    if len(metas) != 1 or metas[0].replace("&#x27;", "'") != HUB_DESCRIPTION:
        raise ValueError("Books catalog description must match reviewed metadata")
    schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if len(schemas) != 1:
        raise ValueError("Books catalog requires one JSON-LD record")
    data = json.loads(schemas[0])
    collection = data.get("mainEntity", {})
    items = collection.get("itemListElement", [])
    expected = published(root)
    if (len(expected) != len(BOOKS) or data.get("@type") != "CollectionPage"
            or data.get("url") != HUB_URL or data.get("@id") != HUB_URL + "#webpage"
            or data.get("description") != HUB_DESCRIPTION or data.get("dateModified") != UPDATED
            or data.get("about", {}).get("@id") != PERSON or collection.get("@type") != "ItemList"
            or collection.get("@id") != HUB_URL + "#book-list"
            or len(items) != len(expected)):
        raise ValueError("Books catalog must list the exact published author works")
    # A catalog work, not a new independently indexed author-book page.
    if (data.get("mentions") != THIRD_BOOK
            or html.count('id="book-ai-works-human-decides"') != 1
            or THIRD_BOOK["description"] not in html):
        raise ValueError("Books catalog third-title provenance or anchor mismatch")
    for position, (entry, book) in enumerate(zip(items, expected), start=1):
        item = entry.get("item", {})
        url = ORIGIN + route(book)
        if (entry.get("position") != position or item.get("@type") != "Book"
                or item.get("@id") != url + "#book" or item.get("url") != url
                or item.get("name") != book["title"] or item.get("author", {}).get("@id") != PERSON
                or any(key in item for key in ("isbn", "offers", "datePublished", "bookFormat", "aggregateRating"))
                or html.count('href="' + route(book) + '"') != 1):
            raise ValueError("Books catalog contains unsupported or duplicate work data")
        book_html = (root / "books" / book["slug"] / "index.html").read_text(encoding="utf-8")
        if 'href="' + HUB_ROUTE + '"' not in book_html:
            raise ValueError("Individual book pages must link back to the author catalog")
    for location in ("index.html", "creative/index.html", "about/index.html", "bio/index.html"):
        if 'href="' + HUB_ROUTE + '"' not in (root / location).read_text(encoding="utf-8"):
            raise ValueError("Books catalog needs a native link from " + location)
    return {"route": HUB_ROUTE, "url": HUB_URL, "modified": UPDATED}


def add_to_sitemap(root_sitemap: ET.Element, root: Path) -> None:
    hub = hub_record(root)
    if hub is not None:
        entry = ET.SubElement(root_sitemap, "url")
        ET.SubElement(entry, "loc").text = hub["url"]
        ET.SubElement(entry, "lastmod").text = hub["modified"]
    for book in published(root):
        url = ET.SubElement(root_sitemap, "url")
        ET.SubElement(url, "loc").text = ORIGIN + route(book)
        ET.SubElement(url, "lastmod").text = book["modified"]

def find_entries(root: Path) -> list[dict]:
    entries = [{"path": route(b), "title": b["title"], "search_title": b["seo"],
                "description": b["description"], "interests": [b["interest"], "creative"],
                "home": b["interest"], "kind": "book", "date": ""}
               for b in published(root)]
    if hub_record(root) is not None:
        entries.append({"path": HUB_ROUTE, "title": "Books by Nolan Kido",
                        "search_title": HUB_TITLE, "description": HUB_DESCRIPTION,
                        "interests": ["creative"], "home": "creative",
                        "kind": "collection", "date": ""})
    return entries
