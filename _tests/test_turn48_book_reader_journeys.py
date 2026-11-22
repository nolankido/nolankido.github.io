"""Turn 48: reader-first, keyboard-friendly book paths and original practice.

Runs offline. Any future edition offer needs a separately verified listing;
the site-only exercises must never be represented as book excerpts.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "assets/book-reader-journey.css"
CSS_URL = "/assets/book-reader-journey.css?v=20261120"
PAGES = (
    {"slug": "one-workflow-at-a-time", "class": "page-book-one-workflow-at-a-time",
     "reader": "ai-book-reader", "example": "ai-book-first-exercise",
     "worksheet_section": "ai-book-free", "edition": "ai-book-listing",
     "answer": "ai-book-sample-answer",
     "worksheet": "/downloads/one-workflow-ai-pilot-worksheet.md",
     "math": ("10 × 12", "30 + (10 × 8)", "120 minutes", "110 minutes", "hypothetical 10-minute advantage")},
    {"slug": "how-to-play-no-limit-texas-holdem", "class": "page-book-how-to-play-no-limit-texas-holdem",
     "reader": "poker-book-reader", "example": "poker-book-first-exercise",
     "worksheet_section": "poker-book-free", "edition": "poker-book-listing",
     "answer": "poker-book-sample-answer",
     "worksheet": "/downloads/holdem-river-call-check-worksheet.md",
     "math": ("20%", "25%", "hypothetical", "not an observed range")},
)
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.anchors = []
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        self.tags.append((tag, attr))
        if attr.get("id"):
            self.ids.append(attr["id"])
        if tag == "a":
            self.anchors.append((attr.get("href"), "download" in attr))


def journey(document):
    matches = re.findall(
        r'<nav class="shell book-reader-jumps" aria-label="[^"]+">(.*?)</nav>',
        document, re.S)
    if len(matches) != 1:
        raise ValueError("Expected one named first-screen reader journey")
    return matches[0]


def practice(document, item):
    matches = re.findall(
        r'<details class="book-sample-answer" id="' + item["answer"] +
        r'">(.*?)</details>', document, re.S)
    if len(matches) != 1:
        raise ValueError("Expected one native answer-reveal control")
    return matches[0]


class BookReaderJourneyTests(unittest.TestCase):
    def test_source_and_published_book_pages_exactly_match(self):
        for item in PAGES:
            with self.subTest(slug=item["slug"]):
                source = (ROOT / "_source/books" / (item["slug"] + ".html")).read_text(encoding="utf-8")
                public = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
                self.assertEqual(source, public)
                self.assertEqual(source.count('href="' + CSS_URL + '"'), 1)
                self.assertNotIn(chr(0x2014), public)
        self.assertEqual({p["slug"] for p in book_pages.published(ROOT)},
                         {p["slug"] for p in PAGES})

    def test_reader_navigation_links_to_four_true_destinations(self):
        for item in PAGES:
            with self.subTest(slug=item["slug"]):
                html = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
                nav = journey(html)
                parser = Elements(html)
                expected = [item["reader"], item["example"], item["worksheet_section"], item["edition"]]
                self.assertEqual([ref for ref, _ in Elements(nav).anchors],
                                 ["#" + x for x in expected])
                self.assertTrue(all(parser.ids.count(x) == 1 for x in expected))
                self.assertLess(html.index('class="page-hero shell"'),
                                html.index('class="shell book-reader-jumps"'))
                self.assertLess(html.index('class="shell book-reader-jumps"'),
                                html.index('id="' + item["reader"] + '"'))
                self.assertEqual(len(re.findall(r'<h1\b', html)), 1)
                self.assertIn('aria-label="Explore ', html)

    def test_practice_uses_native_details_with_no_scripts_or_excerpt_claims(self):
        for item in PAGES:
            with self.subTest(slug=item["slug"]):
                html = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
                answer = practice(html, item)
                self.assertEqual(answer.count("<summary>"), 1)
                self.assertEqual(answer.count("</summary>"), 1)
                self.assertLess(html.index('id="' + item["example"] + '"'),
                                html.index('id="' + item["answer"] + '"'))
                self.assertIn("original site-only", html)
                self.assertIn("not a verified chapter excerpt", answer.lower())
                self.assertNotIn("onclick=", answer)
                self.assertNotIn("<script", answer)
                for expected in item["math"]:
                    self.assertIn(expected, answer)
                self.assertIn('href="' + item["worksheet"] + '" download', html)
                self.assertTrue((ROOT / item["worksheet"].lstrip("/")).is_file())

    def test_author_supplied_kindle_link_does_not_imply_verified_print_or_offer(self):
        for item in PAGES:
            page = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
            record = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
            self.assertIsNotNone(record)
            schema = json.loads(record.group(1))
            self.assertEqual(schema["mainEntity"]["author"]["@id"],
                             "https://nolankido.com/about/#nolan-kido")
            self.assertIn("not independently verified", page)
            for bad in ("isbn", "offers", "datePublished", "bookFormat", "aggregateRating"):
                self.assertNotIn(bad, schema["mainEntity"])
            self.assertNotIn('href="https://www.amazon.com/dp/', page)
            if item["slug"] == "how-to-play-no-limit-texas-holdem":
                self.assertIn("https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324", page)
                self.assertIn('data-umami-event="poker-book-kindle-amazon-click"', page)
            else:
                self.assertNotIn("B0HSB98324", page)
            self.assertIn("not an official cover of this book", page)

    def test_css_has_responsive_320px_routes_and_keyboard_focus(self):
        css = CSS.read_text(encoding="utf-8")
        for token in ("book-reader-jumps", "book-sample-answer", "flex-wrap: wrap",
                      "@media (max-width: 480px)", "flex: 1 1 100%",
                      "min-height: 44px", "overflow-wrap: anywhere",
                      ":focus-visible", "outline: 3px",
                      "@media (forced-colors: active)", "@media print"):
            with self.subTest(token=token):
                self.assertIn(token, css)
        self.assertIn(".book-sample-answer:not([open]) > :not(summary)", css)
        self.assertNotIn(chr(0x2014), css)

    def test_catalog_paths_and_existing_companions_stay_distinct(self):
        html = (ROOT / "books/index.html").read_text(encoding="utf-8")
        self.assertEqual(html, (ROOT / "_source/books/index.html").read_text(encoding="utf-8"))
        for item in PAGES:
            with self.subTest(slug=item["slug"]):
                book = "/books/" + item["slug"] + "/"
                book_page = (ROOT / book.lstrip("/") / "index.html").read_text(encoding="utf-8")
                self.assertEqual(html.count('href="' + book + '"'), 1)
                self.assertEqual(book_page.count('href="/books/"'), 1)
                self.assertIn("not independently verified", book_page)
        self.assertIsNotNone(book_pages.hub_record(ROOT))

    def test_existing_book_dates_and_sitemap_have_no_fake_retail_release(self):
        root = ElementTree.parse(ROOT / "sitemap.xml").getroot()
        dates = {node.findtext("{*}loc"): node.findtext("{*}lastmod") for node in root}
        for route in ("/books/", *(f"/books/{item['slug']}/" for item in PAGES)):
            with self.subTest(route=route):
                expected = "2026-11-22" if route in ("/books/", "/books/how-to-play-no-limit-texas-holdem/") else "2026-11-20"
                self.assertEqual(dates["https://nolankido.com" + route], expected)
        for item in PAGES:
            html = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
            expected = "2026-11-22" if item["slug"] == "how-to-play-no-limit-texas-holdem" else "2026-11-20"
            self.assertIn('"dateModified": "' + expected + '"', html)

    def test_public_css_and_two_worksheets_in_live_inventory(self):
        import check_live
        targets = check_live.targets(ROOT)
        css_route = "/assets/book-reader-journey.css"
        self.assertEqual(targets[css_route], (200, CSS.read_bytes()))
        for item in PAGES:
            self.assertIn(item["worksheet"], targets)

    def test_release_checklist_includes_reader_regression_and_books_build(self):
        file = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn48_book_reader_journeys.py", file)
        self.assertIn("['_scripts/build_books.py', '--check']", file)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            x.is_file() and x.suffix.lower() in (".yaml", ".yml") for x in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
