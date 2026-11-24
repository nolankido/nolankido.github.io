"""Turn 108: all identity hubs link to the existing third-title catalog entry."""
import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAIRS = (
    ("_source/home.html", "index.html", "/", 1),
    ("_source/about.html", "about/index.html", "/about/", 1),
    ("_source/bio.html", "bio/index.html", "/bio/", 2),
    ("_source/creative/home.html", "creative/index.html", "/creative/", 1),
)
THIRD = '/books/#book-ai-works-human-decides'

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

class ThreeTitleIdentityTests(unittest.TestCase):
    def test_native_links_and_canonical_catalog(self):
        catalog = read("books/index.html")
        self.assertEqual(catalog, read("_source/books/index.html"))
        self.assertEqual(catalog.count('id="book-ai-works-human-decides"'), 1)
        self.assertIn("B0HSF8K76R", catalog)
        for src, dest, route, count in PAIRS:
            for path in (src, dest):
                with self.subTest(path=path):
                    page = read(path)
                    self.assertEqual(page.count('href="' + THIRD + '"'), count)
                    self.assertEqual(page.count('href="/books/"'), 1)
                    self.assertIn('<cite>AI Works, Human Decides</cite>', page)
                    self.assertNotIn('/books/ai-works-human-decides/', page)
    def test_bio_search_metadata_agrees(self):
        manifest = {p["id"]: p for p in json.loads(read("_source/pages.json"))}
        desc = manifest["bio"]["description"]
        self.assertIn("three nonfiction book titles", desc)
        from html import escape
        self.assertIn(escape(desc), read("bio/index.html"))
        self.assertIn(escape(desc), read("find/index.html"))
        self.assertNotIn("two nonfiction books", read("bio/index.html"))
    def test_modification_dates_agree(self):
        manifest = {p["path"]: p for p in json.loads(read("_source/pages.json"))}
        sitemap = ET.fromstring(read("sitemap.xml"))
        dates = {el.findtext("{*}loc"): el.findtext("{*}lastmod") for el in sitemap}
        for _, dest, route, _ in PAIRS:
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', read(dest), re.S).group(1))
            self.assertEqual(schema["dateModified"], manifest[route]["updated"])
            self.assertEqual(dates["https://nolankido.com"+route], manifest[route]["updated"])
    def test_retailer_evidence_boundary(self):
        for _, dest, _, _ in PAIRS:
            page = read(dest)
            self.assertNotIn("B0HSF8K76R", page)
            self.assertIn("author-supplied Kindle", page)
        self.assertIn("not independently verified", read("books/index.html"))
        self.assertIn("not verified retail chapter excerpts", read("index.html"))
        self.assertIn("exact retailer edition", read("index.html"))
