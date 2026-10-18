"""Offline search-discovery guard for seven published priority pages.

This is a check of committed site outputs, not evidence of search indexing,
rankings, search-engine citations, or traffic. No network requests are made.
"""
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://nolankido.com"
ROUTES = (
    "/technology/task-brief/",
    "/technology/check-ai-answers/",
    "/technology/ai-time-savings/",
    "/living-well/weekly-reset/",
    "/poker/first-live-tournament/",
    "/poker/hand-rankings/",
    "/poker/school/",
)
POKER_LINKS = ("/poker/hand-rankings/", "/poker/school/")


class Parsed(HTMLParser):
    """Collect only the HTML signals needed by this bounded guard."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_text = ""
        self.in_title = False
        self.meta = []
        self.links = []
        self.anchors = []
        self.h1 = 0
        self.schemas = []
        self.in_schema = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1 += 1
        if tag == "meta":
            self.meta.append(attrs)
        if tag == "link":
            self.links.append(attrs)
        if tag == "a":
            self.anchors.append(attrs)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_schema = True
            self.schemas.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_schema = False

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data
        if self.in_schema:
            self.schemas[-1] += data


def check(root=ROOT):
    """Raise ValueError on any broken priority-page discovery invariant."""
    root = Path(root)
    errors = []

    # Strip comments first: an inactive sitemap or commented block is not a rule.
    directives = [
        line.split("#", 1)[0].strip()
        for line in (root / "robots.txt").read_text(encoding="utf-8").splitlines()
    ]
    if not any(re.fullmatch(
            r"Sitemap:\s*https://nolankido\.com/sitemap\.xml", line, re.I)
            for line in directives):
        errors.append("robots.txt: missing active canonical sitemap declaration")
    if any(re.fullmatch(r"Disallow:\s*/(?:\*+)?\s*", line, re.I)
           for line in directives):
        errors.append("robots.txt: blanket root Disallow")

    tree = ET.fromstring((root / "sitemap.xml").read_text(encoding="utf-8"))
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = {}
    for url in tree.findall("s:url", namespace):
        loc = url.findtext("s:loc", default="", namespaces=namespace)
        lastmod = url.findtext("s:lastmod", default="", namespaces=namespace)
        sitemap.setdefault(loc, []).append(lastmod)

    for route in ROUTES:
        canonical = ORIGIN + route
        revisions = sitemap.get(canonical, [])
        if len(revisions) != 1:
            errors.append(route + ": sitemap entry count")
        else:
            try:
                date.fromisoformat(revisions[0])
            except (TypeError, ValueError):
                errors.append(route + ": invalid sitemap lastmod")

        file = root / route.lstrip("/") / "index.html"
        if not file.is_file():
            errors.append(route + ": missing generated page")
            continue

        parsed = Parsed()
        parsed.feed(file.read_text(encoding="utf-8"))
        if not 12 <= len(parsed.title_text.strip()) <= 100:
            errors.append(route + ": missing or implausible title")
        descriptions = [
            m.get("content", "") for m in parsed.meta
            if m.get("name", "").lower() == "description"
        ]
        if len(descriptions) != 1 or not 50 <= len(descriptions[0]) <= 300:
            errors.append(route + ": missing or implausible description")
        if parsed.h1 != 1:
            errors.append(route + ": expected exactly one h1")
        canonicals = [
            link.get("href")
            for link in parsed.links
            if "canonical" in link.get("rel", "").lower().split()
        ]
        if canonicals != [canonical]:
            errors.append(route + ": canonical mismatch")
        og_urls = [
            meta.get("content") for meta in parsed.meta
            if meta.get("property", "").lower() == "og:url"
        ]
        if og_urls != [canonical]:
            errors.append(route + ": Open Graph URL mismatch")
        if any(
            any(item.strip().split(":", 1)[0].lower() in ("noindex", "none")
                for item in m.get("content", "").split(","))
            for m in parsed.meta
            if m.get("name", "").lower() in ("robots", "googlebot")
        ):
            errors.append(route + ": noindex directive")

        found_schema_url = False
        for raw in parsed.schemas:
            try:
                schema = json.loads(raw)
            except json.JSONDecodeError:
                errors.append(route + ": malformed JSON-LD")
                continue
            if isinstance(schema, dict) and schema.get("url") == canonical:
                found_schema_url = True
        if not found_schema_url:
            errors.append(route + ": structured-data URL mismatch")

    poker = Parsed()
    poker.feed((root / "poker/index.html").read_text(encoding="utf-8"))
    navigation = {a.get("href") for a in poker.anchors}
    for route in POKER_LINKS:
        if route not in navigation:
            errors.append("/poker/: missing native link to " + route)

    if errors:
        raise ValueError("Discovery guard: " + "; ".join(errors))
    return {
        "status": "pass",
        "priority_pages": len(ROUTES),
        "sitemap_urls": len(sitemap),
        "scope": "committed local outputs only, not indexing or traffic",
    }


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
