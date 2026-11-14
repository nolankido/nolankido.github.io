"""Ensure the Resources hub links original tools without overstating their evidence."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/resources.html"
PAGE = ROOT / "resources/index.html"
BEGIN = '<div class="resource-kit-index"'
END = '<!-- AI task choice: start -->'

DOWNLOADS = (
    "downloads/ai-workflow-pilot-blank.csv",
    "downloads/ai-workflow-pilot-example.csv",
    "downloads/ai-workflow-pilot-audit.py",
    "downloads/ai-citation-panel-blank.csv",
    "downloads/ai-citation-panel-synthetic.csv",
    "downloads/ai-citation-panel-audit.py",
    "downloads/ai-search-visibility-monthly-worksheet.md",
    "downloads/incremental-game-first-minute-playtest.md",
    "downloads/incremental-upgrade-payback-worksheet.md",
    "downloads/living-well-wine-tasting-notes.md",
)
GUIDES = (
    "technology/ai-workflow-pilot/index.html",
    "technology/ai-website-visibility/index.html",
    "creative/incremental-game-loop/index.html",
    "creative/incremental-upgrade-payback/index.html",
    "living-well/wine-tasting-notes/index.html",
)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def kit_section(page: str) -> str:
    begin = page.find(BEGIN)
    end = page.find(END, begin)
    if begin < 0 or end < 0:
        raise AssertionError("Resource kits must appear before the original AI task guide")
    return page[begin:end]

class TagIndex(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = {}
        self.links = []
        self.tags = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if "id" in attrs:
            self.ids[attrs["id"]] = self.ids.get(attrs["id"], 0) + 1
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])

class ResourceKitsTests(unittest.TestCase):
    def test_source_and_generated_section_are_identical(self):
        src = read(SOURCE)
        rendered = read(PAGE)
        self.assertEqual(kit_section(src), kit_section(rendered))
        self.assertEqual(src.count(BEGIN), 1)
        self.assertEqual(rendered.count(BEGIN), 1)

    def test_four_kits_are_reachable_and_semantic(self):
        body = kit_section(read(PAGE))
        index = TagIndex()
        index.feed(body)
        self.assertEqual(body.count('class="identity-reading"'), 4)
        self.assertEqual(index.ids.get("resource-new-kits"), 1)
        self.assertEqual(index.tags.count("article"), 4)
        self.assertEqual(index.tags.count("h4"), 4)
        self.assertTrue(all(link.startswith("/") for link in index.links))

    def test_all_downloads_and_guide_pages_exist(self):
        body = kit_section(read(PAGE))
        for file in DOWNLOADS:
            with self.subTest(file=file):
                self.assertIn('href="/' + file + '" download', body)
                self.assertTrue((ROOT / file).is_file())
        for file in GUIDES:
            with self.subTest(file=file):
                self.assertIn('href="/' + file.replace("index.html", ""), body)
                self.assertTrue((ROOT / file).is_file())

    def test_discovery_jump_and_older_paths_remain(self):
        src = read(SOURCE)
        rendered = read(PAGE)
        for page in (src, rendered):
            with self.subTest(page="source" if page is src else "published"):
                self.assertEqual(page.count('href="#resource-new-kits"'), 1)
                self.assertEqual(page.count('id="resource-new-kits"'), 1)
                for anchor in ("resources-entry-title", "resource-collections-title",
                               "ai-task-choice-resource", "answer-review-resource",
                               "summary-review-resource", "project-evidence-resources",
                               "workflow-resource-title", "thinking-worksheets"):
                    self.assertIn('id="' + anchor + '"', page)

    def test_claims_and_privacy_are_bounded(self):
        body = kit_section(read(SOURCE)).lower()
        for phrase in ("synthetic", "fictional", "manually", "not observed",
                       "private exports", "no account", "not a claim",
                       "not a measured client result"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        for forbidden in ("\u2014", "customer savings increased", "confirmed google ranking",
                          "production client", "private game prototypes"):
            self.assertNotIn(forbidden, body)

    def test_sitemap_and_schema_reflect_real_revision(self):
        pages = json.loads(read(ROOT / "_source/pages.json"))
        resource = [p for p in pages if p["id"] == "resources"]
        self.assertEqual(len(resource), 1)
        self.assertEqual(resource[0]["path"], "/resources/")
        self.assertEqual(resource[0]["updated"], "2026-11-14")
        self.assertFalse(resource[0].get("noindex"))
        self.assertNotIn("date", resource[0])
        html = read(PAGE)
        self.assertEqual(html.count('<link rel="canonical" href="https://nolankido.com/resources/">'), 1)
        self.assertIn('"dateModified": "2026-11-14"', html)
        self.assertNotIn('article:published_time', html)
        sitemap = ET.fromstring(read(ROOT / "sitemap.xml"))
        namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        matching = [x for x in sitemap.findall(namespace + "url")
                    if x.findtext(namespace + "loc") == "https://nolankido.com/resources/"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].findtext(namespace + "lastmod"), "2026-11-14")

if __name__ == "__main__":
    unittest.main()
