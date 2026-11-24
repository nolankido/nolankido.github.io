"""Turn 111: canonical third author page and cross-surface source parity."""
import json
import re
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages

ROUTE = "/books/ai-works-human-decides/"
URL = book_pages.ORIGIN + ROUTE

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def schema(page):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S).group(1))

class BookMigrationTests(unittest.TestCase):
    def test_registered_source_and_catalog(self):
        page = read("books/ai-works-human-decides/index.html")
        self.assertEqual(page, read("_source/books/ai-works-human-decides.html"))
        self.assertEqual(schema(page)["mainEntity"], book_pages.THIRD_BOOK)
        self.assertEqual([book_pages.route(b) for b in book_pages.published(ROOT)].count(ROUTE), 1)
        catalog = read("books/index.html")
        self.assertEqual(catalog, read("_source/books/index.html"))
        self.assertEqual(schema(catalog)["mainEntity"]["itemListElement"][2]["item"], book_pages.THIRD_BOOK)
        self.assertNotIn("mentions", schema(catalog))
        self.assertEqual(catalog.count('id="book-ai-works-human-decides"'), 1)
        self.assertIsNotNone(book_pages.hub_record(ROOT))

    def test_identity_and_edition_boundary(self):
        graph = json.loads(read("assets/nolan-kido-identity.jsonld"))
        self.assertEqual(graph, json.loads(read("_source/person-schema.jsonld")))
        works = [n for n in graph["@graph"] if n["@type"] == "Book"]
        self.assertEqual(len(works), 3)
        self.assertEqual([n for n in works if n["@id"] == URL + "#book"], [book_pages.THIRD_BOOK])
        self.assertNotIn("https://nolankido.com/books/#book-ai-works-human-decides", [n["@id"] for n in works])
        self.assertEqual(schema(read("creative/index.html"))["mainEntity"]["itemListElement"][2]["item"], book_pages.THIRD_BOOK)
        for key in ("isbn", "offers", "datePublished", "bookFormat", "aggregateRating"):
            self.assertNotIn(key, book_pages.THIRD_BOOK)
        ledger = json.loads(read("downloads/nolan-kido-book-edition-evidence.json"))
        self.assertEqual(len(ledger["works"]), 2)
        supplemental = ledger["supplementary_author_supplied_titles"][0]
        self.assertEqual(supplemental["canonical_author_page"], URL)
        self.assertEqual(supplemental["retailer_verification_status"], "not_verified")
        self.assertFalse(supplemental["retail_page_inspected"])

    def test_navigation_and_index(self):
        for path in ("index.html", "about/index.html", "bio/index.html", "creative/index.html", "books/index.html"):
            self.assertIn('href="' + ROUTE + '"', read(path))
        self.assertIn('href="/books/#book-ai-works-human-decides"', read("books/ai-works-human-decides/index.html"))
        sitemap = ET.fromstring(read("sitemap.xml"))
        rows = [el.findtext("{*}loc") for el in sitemap]
        self.assertEqual(rows.count(URL), 1)
        self.assertEqual(len(rows), len(set(rows)))
        finder = read("find/index.html")
        self.assertEqual(finder.count('href="' + ROUTE + '"'), 1)
        payload = json.loads(re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>', finder, re.S).group(1))
        sections = payload["pages"]["books"]["ai-works-human-decides/"]
        self.assertEqual(len(sections), 12)
        self.assertIn("human-decides-exercise", sections)
        self.assertIn("human-decides-evidence", sections)

    def test_release_inventory(self):
        import check_live
        import check_html5
        import build
        self.assertEqual(check_live.targets(ROOT)[ROUTE], (200, (ROOT / "books/ai-works-human-decides/index.html").read_bytes()))
        self.assertEqual(check_html5.publication_paths(ROOT, build.public_pages())[ROUTE], Path("books/ai-works-human-decides/index.html"))

if __name__ == "__main__":
    unittest.main()
