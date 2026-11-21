"""Turn 49: a clear path from public book subject to original free practice.

Offline evidence and document link checks only. No checkout of KDP, paid
retailer API, private book chapters, or measurement of reader clicks.
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
CATALOG = ROOT / "_source/books/index.html"
CATALOG_OUT = ROOT / "books/index.html"
BOOKS = (
    {
        "slug": "one-workflow-at-a-time",
        "sample": "ai-book-first-exercise",
        "second": "ai-book-sample-answer",
        "worksheet": "one-workflow-ai-pilot-worksheet.md",
    },
    {
        "slug": "how-to-play-no-limit-texas-holdem",
        "sample": "poker-book-first-exercise",
        "second": "poker-book-sample-answer",
        "worksheet": "holdem-river-call-check-worksheet.md",
    },
)
REFERRALS = (
    ("_source/technology/ai-workflow-pilot.html",
     "technology/ai-workflow-pilot/index.html",
     "Related author book:", BOOKS[0], "ten runs after setup"),
    ("_source/poker/poker-books-and-courses.html",
     "poker/poker-books-and-courses/index.html",
     "My own book:", BOOKS[1], "original website-only example"),
    ("_source/poker/no-limit-holdem-guide.html",
     "poker/no-limit-holdem-guide/index.html",
     "Related author book:", BOOKS[1], "original no-wager"),
)
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def section(document: str, name: str) -> str:
    marker = '<section class="section folio-row" aria-labelledby="' + name + '">'
    if document.count(marker) != 1:
        raise ValueError("Expected one catalog section: " + name)
    start = document.index(marker)
    end = document.find("</section>", start)
    if end == -1:
        raise ValueError("Unclosed catalog section")
    return document[start:end + len("</section>")]


def referred_paragraph(document: str, label: str) -> str:
    found = re.findall(
        r'<p(?: class="small-copy")?><strong>' +
        re.escape(label) + r'</strong>.*?</p>', document, re.S)
    if len(found) != 1:
        raise ValueError("Expected one exact topical book referral for " + label)
    return found[0]


def errors(catalog: str) -> list[str]:
    issues = []
    try:
        compare = section(catalog, "books-catalog-comparison")
        practice = section(catalog, "books-catalog-free-learning")
    except ValueError as e:
        return [str(e)]
    if compare.count('href="#books-catalog-free-learning"') != 2:
        issues.append("Comparison cards are not pointing to one practice section")
    for book in BOOKS:
        slug = book["slug"]
        root = "/books/" + slug + "/"
        sample = root + "#" + book["sample"]
        worksheet = "/downloads/" + book["worksheet"]
        if catalog.count('href="' + root + '"') != 1:
            issues.append("Missing or duplicated canonical book link " + slug)
        if compare.count('href="' + worksheet + '"') != 0:
            issues.append("Worksheet is promoted in comparison card " + slug)
        if practice.count('href="' + sample + '"') != 1:
            issues.append("Missing or duplicated sample link " + slug)
        if practice.count('href="' + worksheet + '" download') != 1:
            issues.append("Missing or duplicated practice download " + slug)
        if catalog.count('href="' + worksheet + '"') != 1:
            issues.append("Worksheet is repeated outside practice " + slug)
    for text in ("not copies of book chapters", "neither example is a verified retail excerpt",
                 "not a recorded hand or verified book excerpt"):
        if text.lower() not in catalog.lower():
            issues.append("Missing independent teaching-source boundary: " + text)
    if chr(0x2014) in catalog:
        issues.append("Em dash in revised book catalog")
    return issues


class BookTopicReaderPathsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = CATALOG.read_text(encoding="utf-8")
        cls.published = CATALOG_OUT.read_text(encoding="utf-8")

    def test_one_canonical_catalog_and_clear_compare_to_practice_handoff(self):
        self.assertEqual(self.catalog, self.published)
        self.assertEqual(errors(self.catalog), [])
        self.assertEqual(self.catalog.count('id="books-catalog-free-learning"'), 1)
        self.assertEqual(self.catalog.count('id="books-catalog-comparison"'), 1)
        self.assertIsNotNone(book_pages.hub_record(ROOT))

    def test_negative_mutations_detect_duplicate_or_misdirected_paths(self):
        base = self.catalog
        first = BOOKS[0]
        mutations = [
            base.replace('href="#books-catalog-free-learning"',
                         'href="#missing-book-section"', 1),
            base.replace('href="/books/' + first["slug"] + '/"',
                         'href="/books/missing/"', 1),
            base.replace('href="/downloads/' + first["worksheet"] + '" download',
                         'href="/downloads/' + first["worksheet"] + '"', 1),
            base.replace('not a recorded hand or verified book excerpt',
                         'a verified retail chapter and real tournament hand', 1),
        ]
        for bad in mutations:
            with self.subTest(change=bad != base):
                self.assertNotEqual(bad, base)
                self.assertTrue(errors(bad))

    def test_all_book_samples_and_original_worksheets_exist(self):
        for book in BOOKS:
            with self.subTest(slug=book["slug"]):
                page = read("books/" + book["slug"] + "/index.html")
                self.assertIn('id="' + book["sample"] + '"', page)
                self.assertIn('id="' + book["second"] + '"', page)
                self.assertIn('<details class="book-sample-answer"', page)
                worksheet = ROOT / "downloads" / book["worksheet"]
                self.assertTrue(worksheet.is_file())
                self.assertIn("Free companion resource", worksheet.read_text(encoding="utf-8"))
                self.assertIn("not a verified chapter excerpt", page)

    def test_three_topical_referrals_keep_exact_book_and_worksheet_paths(self):
        for source, rendered, label, book, evidence in REFERRALS:
            with self.subTest(source=source):
                s, p = read(source), read(rendered)
                paragraph = referred_paragraph(s, label)
                self.assertEqual(paragraph, referred_paragraph(p, label))
                route = "/books/" + book["slug"] + "/"
                worksheet = "/downloads/" + book["worksheet"]
                self.assertEqual(s.count('href="' + route + '"'), 1)
                self.assertEqual(s.count('href="' + worksheet + '"'), 1)
                self.assertIn(evidence.lower(), paragraph.lower())
                self.assertIn("free", paragraph.lower())
                self.assertIn("neither is a verified", paragraph.lower())
                self.assertNotIn(chr(0x2014), paragraph)

    def test_home_has_only_one_books_overview_destination(self):
        for page in ("_source/home.html", "index.html"):
            with self.subTest(page=page):
                text = read(page)
                for href in ("/books/", "/books/one-workflow-at-a-time/",
                             "/books/how-to-play-no-limit-texas-holdem/"):
                    self.assertEqual(text.count('href="' + href + '"'), 1)
                self.assertNotIn('href="/creative/#books-by-nolan-kido"', text)
                self.assertIn("not verified retail chapter excerpts", text)
                self.assertIn("exact retailer edition", text)

    def test_about_bio_and_creative_keep_distinct_original_author_routes(self):
        for source, generated, links in (
            ("_source/about.html", "about/index.html", 1),
            ("_source/creative/home.html", "creative/index.html", 1),
            ("_source/bio.html", "bio/index.html", 2),
        ):
            with self.subTest(source=source):
                s, p = read(source), read(generated)
                self.assertIn('href="/books/"', s)
                self.assertIn('href="/books/"', p)
                for item in BOOKS:
                    route = "/books/" + item["slug"] + "/"
                    self.assertEqual(s.count('href="' + route + '"'), links)
                    self.assertEqual(p.count('href="' + route + '"'), links)
        self.assertIn('id="profile-books"', read("bio/index.html"))
        self.assertIn('id="books-by-nolan-kido"', read("creative/index.html"))

    def test_book_jsonld_and_editions_remain_nonretail_without_invented_offers(self):
        for book in BOOKS:
            page = read("books/" + book["slug"] + "/index.html")
            raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
            self.assertIsNotNone(raw)
            entity = json.loads(raw.group(1))["mainEntity"]
            self.assertEqual(entity["@id"], "https://nolankido.com/books/" + book["slug"] + "/#book")
            self.assertEqual(entity["author"]["@id"], book_pages.PERSON)
            for unsupported in ("isbn", "offers", "bookFormat", "datePublished",
                                "aggregateRating"):
                self.assertNotIn(unsupported, entity)
            self.assertIn("not independently verified", page)
        ledger = json.loads(read("downloads/nolan-kido-book-edition-evidence.json"))
        self.assertTrue(all(f["status"] == "not_verified"
                            for w in ledger["works"] for f in w["formats"]))

    def test_existing_canonical_sitemap_records_not_republished(self):
        root = ElementTree.fromstring(read("sitemap.xml"))
        urls = [(p.findtext("{*}loc"), p.findtext("{*}lastmod")) for p in root]
        for path in ("/books/", *(f"/books/{item['slug']}/" for item in BOOKS)):
            matches = [lastmod for url, lastmod in urls
                       if url == "https://nolankido.com" + path]
            self.assertEqual(matches, ["2026-11-20"])
        for book in BOOKS:
            route = "/books/" + book["slug"] + "/"
            self.assertIn('rel="canonical" href="https://nolankido.com' + route + '"',
                          read("books/" + book["slug"] + "/index.html"))

    def test_local_release_check_is_registered_without_background_jobs(self):
        checks = read("_scripts/local_release_checks.py")
        self.assertIn("test_turn49_book_topic_reader_paths.py", checks)
        self.assertIn("test_book_pages.py", checks)
        self.assertIn("test_turn48_book_reader_journeys.py", checks)
        workflow = ROOT / ".github/workflows"
        self.assertFalse(workflow.exists() and any(
            p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            for p in workflow.iterdir()))


if __name__ == "__main__":
    unittest.main()
