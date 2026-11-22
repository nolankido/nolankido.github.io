"""Turn 47: protect two author works from invented retailer edition identities.

This is an offline source verification gate, not an Amazon product lookup.
Negative controls are constructed, not evidence of available products.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "downloads/nolan-kido-book-edition-evidence.json"
GUIDE = ROOT / "downloads/nolan-kido-book-edition-verification.md"
CATALOG_SOURCE = ROOT / "_source/books/index.html"
CATALOG_RENDERED = ROOT / "books/index.html"
FORMATS = ("kindle_ebook", "paperback", "hardcover")
UNKNOWN_FIELDS = (
    "verified_retailer_title", "verified_retailer_author",
    "retailer_product_url", "retailer_asin", "print_isbn13",
    "retailer_publication_date", "official_retailer_cover_url",
    "public_evidence_url", "observed_on"
)
PRIMARY_HELP = (
    "https://kdp.amazon.com/en_US/help/topic/GPYDJ3SECAVVPNVG",
    "https://kdp.amazon.com/en_US/help/topic/G200627450",
    "https://kdp.amazon.com/en_US/help/topic/G200652190",
    "https://kdp.amazon.com/en_US/help/topic/G7DMSKCM9DVS65TC",
    "https://kdp.amazon.com/en_US/help/topic/GTQGN866DSS6XBD2",
    "https://kdp.amazon.com/en_US/help/topic/G202173620"
)
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages


def evidence_problems(data: dict) -> list[str]:
    """Fail closed on claims of editions not backed by documented evidence.

    This does not authenticate a retailer. Before a future 'verified' entry
    may be released, independent public detail-page verification and an
    explicit reviewed policy/test update are required.
    """
    errors = []
    if data.get("schema_version") != 1 or data.get("reviewed_on") != "2026-11-22":
        errors.append("Unexpected evidence version or review date")
    if data.get("author_name") != "Nolan Kido":
        errors.append("Author mismatch")
    if not isinstance(data.get("works"), list) or len(data["works"]) != 2:
        return errors + ["Expected precisely two author book works"]
    work_by_slug = {w.get("slug"): w for w in data["works"] if isinstance(w, dict)}
    expected_slugs = {w["slug"] for w in book_pages.BOOKS}
    if len(work_by_slug) != 2 or set(work_by_slug) != expected_slugs:
        return errors + ["Duplicate or unexpected work"]
    for work in book_pages.BOOKS:
        row = work_by_slug[work["slug"]]
        expected = book_pages.ORIGIN + book_pages.route(work)
        if row.get("author_title") != work["title"] or row.get("canonical") != expected:
            errors.append("Work identity or canonical mismatch: " + work["slug"])
        if row.get("retail_verification_status") != "not_verified":
            errors.append("Publication claims require an independently audited release update")
        editions = row.get("formats")
        if not isinstance(editions, list) or len(editions) != 3:
            errors.append("Incomplete format matrix")
            continue
        if {item.get("format") for item in editions if isinstance(item, dict)} != set(FORMATS):
            errors.append("Missing or duplicate format")
        for edition in editions:
            if not isinstance(edition, dict) or edition.get("status") != "not_verified":
                errors.append("Unsupported edition publication assertion")
                continue
            if any(edition.get(key, "__MISSING__") is not None for key in UNKNOWN_FIELDS):
                errors.append("Unverified edition contains fabricated or missing retailer data")
    # The author-provided URL is not proof of independently verified product metadata.
    poker_work = work_by_slug["how-to-play-no-limit-texas-holdem"]
    kindle = next((e for e in poker_work["formats"] if e.get("format") == "kindle_ebook"), {})
    if (kindle.get("author_supplied_product_url") != "https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324"
            or kindle.get("author_supplied_asin") != "B0HSB98324"
            or kindle.get("source_type") != "author_direct"
            or kindle.get("supplied_on") != "2026-11-22"):
        errors.append("Author-provided Kindle destination mismatch")
    for row in data["works"]:
        for edition in row["formats"]:
            if row is poker_work and edition is kindle:
                continue
            if any(key in edition for key in ("author_supplied_product_url",
                                            "author_supplied_asin", "source_type")):
                errors.append("Unexpected author-provided destination on another format")
    if set(data.get("publisher_primary_guidance", {}).values()) != set(PRIMARY_HELP):
        errors.append("Publisher guidance source set changed without review")
    return errors


class BookEditionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.guide = GUIDE.read_text(encoding="utf-8")

    def test_six_editions_have_unknown_not_false_publication_data(self):
        self.assertEqual(evidence_problems(self.data), [])
        self.assertEqual(len(self.data["works"]), 2)
        self.assertEqual(sum(len(w["formats"]) for w in self.data["works"]), 6)
        self.assertIn("not evidence of nonpublication", self.data[
            "verification_state_definition"]["not_verified"].lower())

    def test_bad_edition_name_status_and_identifiers_are_rejected(self):
        data = json.loads(json.dumps(self.data))
        data["works"][0]["formats"][0]["retailer_asin"] = "B0INVENTED"
        self.assertTrue(evidence_problems(data))
        data = json.loads(json.dumps(self.data))
        data["works"][0]["formats"][0]["status"] = "verified"
        self.assertTrue(evidence_problems(data))
        data = json.loads(json.dumps(self.data))
        data["works"][1]["formats"][0]["author_supplied_asin"] = "B0INVENTED"
        self.assertTrue(evidence_problems(data))
        data = json.loads(json.dumps(self.data))
        data["works"][1]["canonical"] = "https://www.amazon.com/dp/B0INVENTED"
        self.assertTrue(evidence_problems(data))

    def test_duplicate_work_or_format_would_not_be_silently_accepted(self):
        data = json.loads(json.dumps(self.data))
        data["works"][1]["slug"] = data["works"][0]["slug"]
        self.assertTrue(evidence_problems(data))
        data = json.loads(json.dumps(self.data))
        data["works"][0]["formats"][1]["format"] = "kindle_ebook"
        self.assertTrue(evidence_problems(data))

    def test_primary_publisher_sources_identified_by_exact_urls(self):
        for url in PRIMARY_HELP:
            with self.subTest(url=url):
                self.assertIn(url, self.guide)
                self.assertIn(url, self.data["publisher_primary_guidance"].values())
        self.assertIn("View on Amazon", self.guide)
        self.assertIn("ISBN-13", self.guide)
        self.assertIn("Kindle eBook does not need one", self.guide)
        self.assertIn("print editions", self.guide)

    def test_author_catalog_has_visible_six_format_status_and_links(self):
        source = CATALOG_SOURCE.read_text(encoding="utf-8")
        rendered = CATALOG_RENDERED.read_text(encoding="utf-8")
        self.assertEqual(source, rendered)
        self.assertEqual(source.count('id="books-retailer-evidence"'), 1)
        for book in book_pages.BOOKS:
            self.assertIn(book["title"], source)
            self.assertEqual(source.count('href="' + book_pages.route(book) + '"'), 1)
        self.assertIn("not independently verified", source)
        self.assertIn("not unpublished or unavailable", source)
        self.assertIn("https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324", source)
        self.assertEqual(source.count('data-umami-event="poker-book-kindle-amazon-click"'), 1)
        self.assertIn('href="/downloads/nolan-kido-book-edition-verification.md" download',
                      source)
        self.assertIn('href="/downloads/nolan-kido-book-edition-evidence.json" download',
                      source)

    def test_each_book_page_links_to_evidence_without_made_up_offer(self):
        anchor = {
            "one-workflow-at-a-time": "ai-book-edition-evidence",
            "how-to-play-no-limit-texas-holdem": "poker-book-edition-evidence",
        }
        for item in book_pages.BOOKS:
            with self.subTest(slug=item["slug"]):
                source = ROOT / "_source/books" / (item["slug"] + ".html")
                page = ROOT / "books" / item["slug"] / "index.html"
                s, p = source.read_text(encoding="utf-8"), page.read_text(encoding="utf-8")
                self.assertEqual(s, p)
                self.assertEqual(s.count('id="' + anchor[item["slug"]] + '"'), 1)
                for doc in ("nolan-kido-book-edition-verification.md",
                            "nolan-kido-book-edition-evidence.json"):
                    self.assertIn('href="/downloads/' + doc + '" download', s)
                self.assertIn("not independently verified", s)
                self.assertIn("not an official cover of this book", s)
                if item["slug"] == "how-to-play-no-limit-texas-holdem":
                    self.assertEqual(s.count("https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324"), 1)
                    self.assertIn('id="poker-book-amazon-cta"', s)
                else:
                    self.assertNotIn("B0HSB98324", s)
                raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
                schema = json.loads(raw.group(1))
                for field in ("isbn", "offers", "bookFormat", "datePublished",
                              "aggregateRating"):
                    self.assertNotIn(field, schema["mainEntity"])
                self.assertNotIn('href="https://www.amazon.com/dp/', s)

    def test_existing_books_build_and_sitemap_contract_preserved(self):
        self.assertIsNotNone(book_pages.hub_record(ROOT))
        self.assertEqual(len(book_pages.published(ROOT)), 2)
        xml = ElementTree.parse(ROOT / "sitemap.xml")
        urls = [x.text for x in xml.findall("{*}url/{*}loc")]
        for route in ("/books/", *(book_pages.route(p) for p in book_pages.BOOKS)):
            self.assertEqual(urls.count("https://nolankido.com" + route), 1)

    def test_public_ledger_does_not_publish_private_account_evidence(self):
        self.assertIn("No private KDP Bookshelf", self.data["scope"])
        for item in self.data["works"]:
            for edition in item["formats"]:
                self.assertIsNone(edition["public_evidence_url"])
                self.assertIsNone(edition["retailer_product_url"])
        self.assertNotIn(chr(0x2014), self.guide)
        self.assertNotIn(chr(0x2014), LEDGER.read_text(encoding="utf-8"))

    def test_downloads_registered_for_exact_byte_verification(self):
        import check_live
        targets = check_live.targets(ROOT)
        for file in (GUIDE, LEDGER):
            with self.subTest(file=file.name):
                route = "/downloads/" + file.name
                self.assertEqual(targets[route], (200, file.read_bytes()))

    def test_local_release_coverage_and_no_github_actions(self):
        release = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn47_book_edition_evidence.py", release)
        self.assertIn("test_book_pages.py", release)
        self.assertIn("build_books.py", release)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            for p in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
