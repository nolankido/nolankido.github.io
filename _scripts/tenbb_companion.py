"""Register one public, manually authored 10 BB video companion safely.

This page is already published as poker/10bb/index.html and is not owned by
the manifest generator. Only its exact canonical/Article identity may enter
the deterministic sitemap or read-only release inventory.
"""
from datetime import date
from pathlib import Path
import json
import re
from xml.etree import ElementTree as ET

ORIGIN = "https://nolankido.com"
ROUTE = "/poker/10bb/"
OUTPUT = Path("poker/10bb/index.html")
CODE = "downloads/ten-bb-playbook-icm-verify.py"


def inspect(html: str) -> dict:
    canonical = '<link rel="canonical" href="' + ORIGIN + ROUTE + '">'
    heading = '<h1 class="page-title">The 10 Big Blind Tournament Playbook</h1>'
    for marker, label in (
        (canonical, "canonical"), (heading, "heading"),
        ('<meta property="article:published_time" content="2026-11-19">', "original publication date"),
        ('id="icm-reproduce"', "reproducibility heading"),
        ('href="/' + CODE + '"', "exact offline checker"),
    ):
        if html.count(marker) != 1:
            raise ValueError("10 BB Playbook missing or duplicates " + label)
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not match or html.count('<script type="application/ld+json">') != 1:
        raise ValueError("10 BB Playbook requires exactly one Article identity")
    schema = json.loads(match.group(1))
    if schema.get("@type") != "Article" or schema.get("url") != ORIGIN + ROUTE:
        raise ValueError("10 BB Playbook schema must match its unique canonical URL")
    if schema.get("author", {}).get("@id") != ORIGIN + "/about/#nolan-kido":
        raise ValueError("10 BB Playbook author identity changed")
    if schema.get("datePublished") != "2026-11-19":
        raise ValueError("10 BB Playbook original publication date changed")
    modified = schema.get("dateModified")
    if not isinstance(modified, str) or date.fromisoformat(modified) < date(2026, 11, 19):
        raise ValueError("10 BB Playbook modification date missing or before publication")
    if html.count('<meta property="article:modified_time" content="' + modified + '">') != 1:
        raise ValueError("10 BB Playbook visible and structured revision dates disagree")
    if '<meta name="robots" content="noindex' in html or 'FAQPage' in html:
        raise ValueError("10 BB Playbook has an unexpected crawl/schema policy")
    return {"route": ROUTE, "url": ORIGIN + ROUTE, "lastmod": modified}


def record(root: Path):
    if not (root / OUTPUT).is_file() or not (root / CODE).is_file():
        raise ValueError("10 BB Playbook or its required checker is missing")
    return inspect((root / OUTPUT).read_text(encoding="utf-8"))


def add_to_sitemap(sitemap: ET.Element, root: Path):
    approved = record(root)
    element = ET.SubElement(sitemap, "url")
    ET.SubElement(element, "loc").text = approved["url"]
    ET.SubElement(element, "lastmod").text = approved["lastmod"]
