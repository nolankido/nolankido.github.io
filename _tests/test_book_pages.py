"""Regression checks for two canonical, source-backed Nolan Kido book pages."""
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages


class BookPublicationTests(unittest.TestCase):
    def test_both_book_pages_have_matching_sources_and_registered_routes(self):
        items = book_pages.published(ROOT)
        self.assertEqual({x["slug"] for x in items}, {x["slug"] for x in book_pages.BOOKS})

    def test_book_pages_are_indexable_and_identified_to_author(self):
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                page = (ROOT / "books" / book["slug"] / "index.html").read_text(encoding="utf-8")
                canonical = book_pages.ORIGIN + book_pages.route(book)
                self.assertEqual(page.count('<link rel="canonical" href="' + canonical + '">'), 1)
                self.assertEqual(page.count('<meta property="og:url" content="' + canonical + '">'), 1)
                self.assertNotIn('content="noindex', page)
                self.assertEqual(len(re.findall(r"<h1\b", page)), 1)
                match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                self.assertIsNotNone(match)
                record = json.loads(match.group(1))
                self.assertEqual(record["mainEntity"]["@id"], canonical + "#book")
                self.assertEqual(record["mainEntity"]["author"]["@id"], book_pages.PERSON)
                for forbidden in ("isbn", "offers", "bookFormat", "datePublished", "aggregateRating"):
                    self.assertNotIn(forbidden, record["mainEntity"])

    def test_companion_files_links_arithmetic_and_image_alt(self):
        companions = {
            "one-workflow-at-a-time": ("downloads/one-workflow-ai-pilot-worksheet.md",
                                       "4 + 3 + 7 + 1 = 15 minutes"),
            "how-to-play-no-limit-texas-holdem": ("downloads/holdem-river-call-check-worksheet.md",
                                                   "10 / 40 = 25%"),
        }
        creative = (ROOT / "_source/creative/home.html").read_text(encoding="utf-8")
        for item in book_pages.BOOKS:
            with self.subTest(slug=item["slug"]):
                path, example = companions[item["slug"]]
                worksheet = (ROOT / path).read_text(encoding="utf-8")
                page = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
                self.assertGreater(len(worksheet), 1500)
                self.assertIn("Free companion resource", worksheet)
                self.assertIn('href="/' + path + '"', page)
                self.assertIn('href="/' + path + '"', creative)
                self.assertIn(example, worksheet.replace("**", ""))
                self.assertIn("not an official cover of this book", page)
                self.assertNotIn(chr(0x2014), worksheet)

    def test_sitemap_and_find_link_each_book_once(self):
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap = ElementTree.parse(ROOT / "sitemap.xml")
        site_urls = [element.text for element in sitemap.findall(".//s:loc", namespace)]
        finder = (ROOT / "find/index.html").read_text(encoding="utf-8")
        self.assertIn('<option value="book">Books</option>', finder)
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                path = book_pages.route(book)
                self.assertEqual(site_urls.count(book_pages.ORIGIN + path), 1)
                self.assertEqual(finder.count('href="' + path + '"'), 1)
                self.assertIn('data-kind="book"', finder)

    def test_internal_source_links_and_generated_book_schema_agree(self):
        home = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        creative = (ROOT / "_source/creative/home.html").read_text(encoding="utf-8")
        public = (ROOT / "creative/index.html").read_text(encoding="utf-8")
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', public, re.S)
        self.assertIsNotNone(m)
        items = json.loads(m.group(1))["mainEntity"]["itemListElement"]
        refs = {x["item"]["@id"] for x in items}
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                path = book_pages.route(book)
                self.assertIn('href="' + path + '"', home)
                self.assertIn('href="' + path + '"', creative)
                self.assertIn(book_pages.ORIGIN + path + "#book", refs)


if __name__ == "__main__":
    unittest.main()
