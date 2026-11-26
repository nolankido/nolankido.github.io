"""Exact-title book discovery and catalog-backed identity, not edition verification."""
from html import unescape
import json
from pathlib import Path
import re
import sys
import tempfile
import shutil
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def schema(page):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S).group(1))

class CatalogIdentityTests(unittest.TestCase):
    def test_search_copy_and_share_summary(self):
        page = read("books/index.html")
        self.assertEqual(page, read("_source/books/index.html"))
        desc = book_pages.HUB_DESCRIPTION
        for title in [book_pages.THIRD_BOOK["name"]] + [b["title"] for b in book_pages.BOOKS]:
            self.assertIn(title, desc)
        for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            self.assertEqual(unescape(re.search(r'<meta ' + attr + r' content="([^"]+)">', page).group(1)), desc)
        self.assertEqual(schema(page)["description"], desc)
        self.assertIn('<h3><a href="/books/">Books by Nolan Kido</a></h3><p class="find-description">' + desc + '</p>', read("find/index.html"))

    def test_catalog_and_identity_graph_agree(self):
        page = read("books/index.html")
        expected = book_pages.THIRD_BOOK
        authored = json.loads(read("_source/person-schema.jsonld"))
        public = json.loads(read("assets/nolan-kido-identity.jsonld"))
        self.assertEqual(authored, public)
        self.assertEqual(schema(page)["mainEntity"]["itemListElement"][2]["item"], expected)
        self.assertNotIn("mentions", schema(page))
        self.assertEqual([n for n in public["@graph"] if n["@id"] == expected["@id"]], [expected])
        self.assertEqual(len([n for n in public["@graph"] if n["@type"] == "Book"]), 3)
        self.assertEqual(len(book_pages.BOOKS), 3)
        self.assertEqual(page.count('id="book-ai-works-human-decides"'), 1)
        self.assertIn(expected["description"], page)
        for field in ("isbn", "offers", "datePublished", "bookFormat", "aggregateRating", "sameAs"):
            self.assertNotIn(field, expected)

    def test_canonical_and_separate_essay(self):
        page = read("books/index.html")
        self.assertIn('href="/notes/keep-the-judgment/"', page)
        self.assertIn("The essay is not a book excerpt.", page)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/notes/keep-the-judgment/">', read("notes/keep-the-judgment/index.html"))
        self.assertEqual(len(schema(page)["mainEntity"]["itemListElement"]), 3)
        rows = ET.fromstring(read("sitemap.xml"))
        urls = [(r.findtext("{*}loc"), r.findtext("{*}lastmod")) for r in rows]
        self.assertEqual([d for u,d in urls if u == book_pages.HUB_URL], [book_pages.UPDATED])
        self.assertEqual(len(urls), len(set(u for u,d in urls)))
        self.assertEqual([d for u,d in urls if u == "https://nolankido.com/books/ai-works-human-decides/"], [book_pages.UPDATED])

    def test_registry_rejects_unverified_third_work_claims(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = [book_pages.HUB_SOURCE, book_pages.HUB_OUTPUT,
                     Path("index.html"), Path("creative/index.html"),
                     Path("about/index.html"), Path("bio/index.html")]
            for book in book_pages.BOOKS:
                paths.extend([Path("_source/books") / (book["slug"] + ".html"),
                              Path("books") / book["slug"] / "index.html"])
            for path in paths:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertIsNotNone(book_pages.hub_record(root))
            original = read("books/index.html")
            changed = original.replace('"position": 3, "item": {"@type": "Book",', '"position": 3, "item": {"@type": "Book", "offers": {"price": "1.00"},', 1)
            self.assertNotEqual(changed, original)
            for path in (book_pages.HUB_SOURCE, book_pages.HUB_OUTPUT):
                (root / path).write_text(changed, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "third-title provenance"):
                book_pages.hub_record(root)

if __name__ == "__main__":
    unittest.main()
