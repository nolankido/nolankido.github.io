#!/usr/bin/env python3
"""Offline discovery regression gate. Valid HTML does not prove indexing or ranking."""
import argparse
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://nolankido.com"
PRIORITIES = (
    "/technology/task-brief/", "/technology/check-ai-answers/",
    "/technology/ai-time-savings/", "/living-well/weekly-reset/",
    "/poker/first-live-tournament/", "/poker/hand-rankings/",
    "/poker/school/",
)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.jsonld = []
        self.in_jsonld = False
        self.metas = []
        self.links = []
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "meta":
            self.metas.append(a)
        if tag in ("link", "a"):
            self.links.append(a)
        if tag == "script" and a.get("type") == "application/ld+json":
            self.jsonld.append("")
            self.in_jsonld = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_jsonld = False

    def handle_data(self, value):
        if self.in_title:
            self.title += value
        if self.in_jsonld:
            self.jsonld[-1] += value


def check(root=ROOT):
    root = Path(root)
    problems = []
    robots = (root / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://nolankido.com/sitemap.xml" not in robots:
        problems.append("canonical sitemap absent from robots.txt")
    if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
        problems.append("robots.txt blanket Disallow: /")
    tree = ET.fromstring((root / "sitemap.xml").read_text(encoding="utf-8"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries = {}
    for node in tree.findall("s:url", ns):
        loc = node.findtext("s:loc", default="", namespaces=ns)
        modified = node.findtext("s:lastmod", default="", namespaces=ns)
        entries.setdefault(loc, []).append(modified)
    for route in PRIORITIES:
        canonical = ORIGIN + route
        lastmods = entries.get(canonical, [])
        if len(lastmods) != 1:
            problems.append(f"{route}: sitemap URL count is {len(lastmods)}, expected 1")
        else:
            try:
                date.fromisoformat(lastmods[0])
            except ValueError:
                problems.append(f"{route}: invalid sitemap lastmod")
        file = root / route.lstrip("/") / "index.html"
        if not file.is_file():
            problems.append(f"{route}: generated page absent")
            continue
        p = Page()
        p.feed(file.read_text(encoding="utf-8"))
        if not 12 <= len(p.title.strip()) <= 100:
            problems.append(f"{route}: title missing or implausible")
        descriptions = [m.get("content", "") for m in p.metas if m.get("name") == "description"]
        if len(descriptions) != 1 or not 50 <= len(descriptions[0]) <= 300:
            problems.append(f"{route}: description absent or implausible")
        if p.h1 != 1:
            problems.append(f"{route}: found {p.h1} H1 headings")
        if [a.get("href") for a in p.links if a.get("rel") == "canonical"] != [canonical]:
            problems.append(f"{route}: canonical mismatch")
        if [m.get("content") for m in p.metas if m.get("property") == "og:url"] != [canonical]:
            problems.append(f"{route}: Open Graph URL mismatch")
        if any(re.search(r"\bnoindex\b", m.get("content", ""), re.I)
               for m in p.metas if m.get("name", "").lower() in ("robots", "googlebot")):
            problems.append(f"{route}: noindex directive")
        schema_ok = False
        for raw in p.jsonld:
            try:
                value = json.loads(raw)
                if isinstance(value, dict) and value.get("url") == canonical:
                    schema_ok = True
            except json.JSONDecodeError:
                problems.append(f"{route}: malformed JSON-LD")
        if not schema_ok:
            problems.append(f"{route}: structured-data URL mismatch")
    poker = Page()
    poker.feed((root / "poker/index.html").read_text(encoding="utf-8"))
    hrefs = [a.get("href", "") for a in poker.links]
    for route in ("/poker/hand-rankings/", "/poker/school/"):
        if route not in hrefs:
            problems.append(f"/poker/: missing native link to {route}")
    if problems:
        raise ValueError("Discovery gate failed:\n- " + "\n- ".join(problems))
    return {"status": "pass", "priority_pages": len(PRIORITIES), "sitemap_urls": len(entries),
            "scope": "local output integrity, not third-party indexation"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    print(json.dumps(check(parser.parse_args().root), sort_keys=True))
