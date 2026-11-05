"""Register exactly one archived-source Stand Off companion, not live video proof.

The separate source file and static HTML must match before this route can be
advertised in sitemap, Poker discovery and manual public-byte verification.
No remote requests, private uploads, scheduled checks or video embeds.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path

ROUTE = "/poker/episodes/portland-meadows-standoff/"
URL = "https://nolankido.com" + ROUTE
SOURCE = Path("_source/poker/portland-meadows-standoff.html")
OUTPUT = Path("poker/episodes/portland-meadows-standoff/index.html")
VIDEO = "https://www.youtube.com/watch?v=I75GOBVXij4"
TITLE = "Portland Meadows Stand Off: A-K Facing Two Shoves"
PUBLISHED = "2026-11-04"
MODIFIED = "2026-11-04"
PERSON_ID = "https://nolankido.com/about/#nolan-kido"


class _Document(HTMLParser):
    def __init__(self, markup: str):
        super().__init__(convert_charrefs=True)
        self.canonical = []
        self.og_url = []
        self.robots = []
        self.video_links = []
        self.schema = []
        self._schema_text = []
        self._in_schema = False
        self.h1_count = 0
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical.append(values.get("href"))
        if tag == "meta":
            if values.get("property") == "og:url":
                self.og_url.append(values.get("content"))
            if values.get("name") == "robots":
                self.robots.append(values.get("content", ""))
        if tag == "a" and values.get("href") == VIDEO:
            self.video_links.append(values)
        if tag == "script" and values.get("type") == "application/ld+json":
            self._in_schema = True
            self._schema_text = []

    def handle_data(self, data):
        if self._in_schema:
            self._schema_text.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_schema:
            self.schema.append(json.loads("".join(self._schema_text)))
            self._in_schema = False


def record(root: Path) -> dict | None:
    """Return metadata only for a complete, source-checked public article."""
    source = root / SOURCE
    page = root / OUTPUT
    if not source.exists() and not page.exists():
        return None
    if not source.is_file() or not page.is_file():
        raise ValueError("Stand Off publication requires source and public HTML")
    authored = source.read_text(encoding="utf-8")
    published = page.read_text(encoding="utf-8")
    if not authored.strip() or published.count(authored) != 1:
        raise ValueError("Stand Off public page must include the exact approved source")
    if any(value in authored.lower() for value in ("<script", "<form", "<iframe")):
        raise ValueError("Stand Off companion must not contain executable or private forms")
    if "\u2014" in published or "JToB7upHqEM" in published:
        raise ValueError("Stand Off companion contains disallowed private or superseded details")
    if "have not independently compared" not in authored or "not a solver output" not in authored:
        raise ValueError("Stand Off source must preserve current-cut and solver limits")
    doc = _Document(published)
    if (doc.canonical != [URL] or doc.og_url != [URL]
            or doc.h1_count != 1 or len(doc.schema) != 1 or not doc.video_links):
        raise ValueError("Stand Off page needs canonical URL, one H1, one schema and video link")
    if any("noindex" in x.lower() or "none" in x.lower() for x in doc.robots):
        raise ValueError("Stand Off public companion must be indexable")
    schema = doc.schema[0]
    if (schema.get("@type") != "Article" or schema.get("url") != URL
            or schema.get("@id") != URL + "#article"
            or schema.get("headline") != TITLE
            or schema.get("datePublished") != PUBLISHED
            or schema.get("dateModified") != MODIFIED
            or schema.get("author", {}).get("@id") != PERSON_ID
            or schema.get("mainEntityOfPage", {}).get("url") != URL):
        raise ValueError("Stand Off Article metadata does not match reviewed source")
    for token in ("46,000", "K-K", "Q-Q", "15,000", "November 4, 2026"):
        if token not in authored:
            raise ValueError("Stand Off source is missing a required documented distinction")
    return {"route": ROUTE, "url": URL, "title": TITLE,
            "date": PUBLISHED, "modified": MODIFIED, "video_url": VIDEO}
