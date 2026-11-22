"""Turn 49 follow-up: keep book choice, original practice and free worksheets distinct.

A bounded, offline audit that preserves the already-merged direct topic-to-
sample links. No retailer, model or analytics calls.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
BOOKS = (
    ("one-workflow-at-a-time", "ai-book-first-exercise",
     "one-workflow-ai-pilot-worksheet.md"),
    ("how-to-play-no-limit-texas-holdem", "poker-book-first-exercise",
     "holdem-river-call-check-worksheet.md"),
)
TOPICS = (
    ("_source/technology/ai-workflow-pilot.html",
     "technology/ai-workflow-pilot/index.html", BOOKS[0]),
    ("_source/poker/poker-books-and-courses.html",
     "poker/poker-books-and-courses/index.html", BOOKS[1]),
    ("_source/poker/no-limit-holdem-guide.html",
     "poker/no-limit-holdem-guide/index.html", BOOKS[1]),
)
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages


def read(p: str) -> str:
    return (ROOT / p).read_text(encoding="utf-8")


def section(page: str, name: str) -> str:
    marker = '<section class="section folio-row" aria-labelledby="' + name + '">'
    if page.count(marker) != 1:
        raise ValueError("Missing or repeated Books catalog section " + name)
    begin = page.index(marker)
    end = page.find("</section>", begin)
    if end == -1:
        raise ValueError("Unclosed Books catalog section " + name)
    return page[begin:end + len("</section>")]


def route_errors(catalog: str) -> list[str]:
    try:
        compare = section(catalog, "books-catalog-comparison")
        free = section(catalog, "books-catalog-free-learning")
    except ValueError as err:
        return [str(err)]
    errors = []
    if compare.count('href="#books-catalog-free-learning"') != 2:
        errors.append("Two book cards must point to one practice section")
    for slug, sample_id, worksheet in BOOKS:
        root = "/books/" + slug + "/"
        resource = "/downloads/" + worksheet
        if catalog.count('href="' + root + '"') != 1:
            errors.append("Duplicate/missing canonical work link: " + slug)
        if resource in compare:
            errors.append("Duplicate worksheet promotion in comparison card")
        if free.count('href="' + root + "#" + sample_id + '"') != 1:
            errors.append("Missing distinct site-original teaching example")
        if free.count('href="' + resource + '" download') != 1:
            errors.append("Free practice section must contain its actual worksheet")
        if catalog.count('href="' + resource + '"') != 1:
            errors.append("A free worksheet is missing or repeated")
    for phrase in ("not copies of book chapters",
                   "neither example is a verified retail excerpt",
                   "not a recorded hand or verified book excerpt"):
        if phrase.lower() not in catalog.lower():
            errors.append("Missing site-only teaching disclaimer")
    return errors


class BookCatalogPracticeHandoffTests(unittest.TestCase):
    def test_book_catalog_standalone_sources_match_public_copy(self):
        source, output = read("_source/books/index.html"), read("books/index.html")
        self.assertEqual(source, output)
        self.assertEqual(route_errors(source), [])
        self.assertIsNotNone(book_pages.hub_record(ROOT))
        self.assertNotIn(chr(0x2014), source)

    def test_each_work_unique_in_comparison_then_practice_and_download(self):
        page = read("books/index.html")
        compare = section(page, "books-catalog-comparison")
        free = section(page, "books-catalog-free-learning")
        self.assertEqual(compare.count('href="#books-catalog-free-learning"'), 2)
        for slug, sample, worksheet in BOOKS:
            with self.subTest(work=slug):
                self.assertEqual(compare.count('href="/books/' + slug + '/"'), 1)
                self.assertNotIn('href="/downloads/' + worksheet + '"', compare)
                self.assertIn('href="/books/' + slug + '/#' + sample + '"', free)
                self.assertIn('href="/downloads/' + worksheet + '" download', free)
                self.assertTrue((ROOT / "downloads" / worksheet).is_file())
                self.assertIn('id="' + sample + '"',
                              read("books/" + slug + "/index.html"))

    def test_bad_links_duplication_and_false_retail_excerpts_fail_closed(self):
        page = read("_source/books/index.html")
        first_slug, first_sample, first_sheet = BOOKS[0]
        mutations = [
            page.replace('href="#books-catalog-free-learning"',
                         'href="#not-a-books-section"', 1),
            page.replace('href="/books/' + first_slug + '/"',
                         'href="/books/missing/"', 1),
            page.replace('href="/downloads/' + first_sheet + '" download',
                         'href="/downloads/' + first_sheet + '"', 1),
            page.replace('neither example is a verified retail excerpt',
                         'these are verified retail excerpts', 1),
        ]
        for mutated in mutations:
            with self.subTest(mutated=mutated != page):
                self.assertNotEqual(mutated, page)
                self.assertTrue(route_errors(mutated))

    def test_home_has_only_one_book_overview_not_duplicate_creative_link(self):
        for file in ("_source/home.html", "index.html"):
            with self.subTest(file=file):
                html = read(file)
                self.assertEqual(html.count('href="/books/"'), 1)
                for slug, _, _ in BOOKS:
                    self.assertEqual(html.count('href="/books/' + slug + '/"'), 1)
                self.assertNotIn('href="/creative/#books-by-nolan-kido"', html)
                self.assertIn("not verified retail chapter excerpts", html)
                self.assertIn("exact retailer edition", html)

    def test_preserve_previously_merged_direct_topic_to_sample_routes(self):
        for source, output, (slug, sample, sheet) in TOPICS:
            with self.subTest(source=source):
                a, b = read(source), read(output)
                for page in (a, b):
                    self.assertEqual(page.count('href="/books/' + slug + '/"'), 1)
                    self.assertEqual(page.count('href="/books/' + slug + '/#' + sample + '"'), 1)
                    self.assertEqual(page.count('href="/downloads/' + sheet + '"'), 1)
                self.assertIn('id="' + sample + '"',
                              read("books/" + slug + "/index.html"))
        self.assertIn('/technology/ai-workflow-pilot/#pilot-protocol',
                      read("books/one-workflow-at-a-time/index.html"))
        self.assertIn('/poker/no-limit-holdem-guide/#choose-your-route',
                      read("books/how-to-play-no-limit-texas-holdem/index.html"))

    def test_about_bio_and_creative_have_purpose_specific_author_links(self):
        for source, output, n in (
            ("_source/about.html", "about/index.html", 1),
            ("_source/bio.html", "bio/index.html", 2),
            ("_source/creative/home.html", "creative/index.html", 1),
        ):
            with self.subTest(source=source):
                for html in (read(source), read(output)):
                    self.assertEqual(html.count('href="/books/"'), 1)
                    for slug, _, _ in BOOKS:
                        self.assertEqual(html.count('href="/books/' + slug + '/"'), n)
        self.assertIn('id="profile-books"', read("bio/index.html"))
        self.assertIn('id="books-by-nolan-kido"', read("creative/index.html"))

    def test_retained_book_entities_and_nonverified_retailer_fields(self):
        for slug, _, _ in BOOKS:
            html = read("books/" + slug + "/index.html")
            match = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                              html, re.S)
            self.assertIsNotNone(match)
            entity = json.loads(match.group(1))["mainEntity"]
            self.assertEqual(entity["@id"],
                             "https://nolankido.com/books/" + slug + "/#book")
            self.assertEqual(entity["author"]["@id"], book_pages.PERSON)
            self.assertIn("not independently verified", html)
            for key in ("isbn", "offers", "datePublished", "bookFormat",
                        "aggregateRating"):
                self.assertNotIn(key, entity)
        data = json.loads(read("downloads/nolan-kido-book-edition-evidence.json"))
        self.assertTrue(all(edition["status"] == "not_verified"
                            for work in data["works"]
                            for edition in work["formats"]))

    def test_no_sitemap_or_retail_status_changes(self):
        root = ElementTree.fromstring(read("sitemap.xml"))
        urls = [(entry.findtext("{*}loc"), entry.findtext("{*}lastmod"))
                for entry in root]
        for route in ("/books/", *(f"/books/{slug}/" for slug, _, _ in BOOKS)):
            hits = [date for url, date in urls
                    if url == "https://nolankido.com" + route]
            expected = "2026-11-22" if route == "/books/how-to-play-no-limit-texas-holdem/" else "2026-11-20"
            self.assertEqual(hits, [expected])

    def test_offline_release_coverage_no_github_actions(self):
        checklist = read("_scripts/local_release_checks.py")
        self.assertIn("test_turn49_book_catalog_handoff.py", checklist)
        self.assertIn("test_turn49_topic_book_paths.py", checklist)
        self.assertIn("test_book_pages.py", checklist)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml")
            for p in actions.iterdir()))


if __name__ == "__main__":
    unittest.main()
