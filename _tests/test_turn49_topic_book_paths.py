"""Regression: topical reader -> original site-only exercise -> free method.

Offline structural test, not a claim of browser rendering or deployed status.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
AI = "/books/one-workflow-at-a-time/"
POKER = "/books/how-to-play-no-limit-texas-holdem/"


def file(path):
    return (ROOT / path).read_text(encoding="utf-8")


class Page(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
        self.ids = []
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("id"):
            self.ids.append(d["id"])
        if tag == "a" and d.get("href"):
            self.hrefs.append(d["href"])


class TopicBookLinks(unittest.TestCase):
    def test_article_book_and_exercise_routes(self):
        cases = (
            ("technology/ai-workflow-pilot/index.html", AI, "ai-book-first-exercise",
             "/downloads/one-workflow-ai-pilot-worksheet.md"),
            ("poker/no-limit-holdem-guide/index.html", POKER, "poker-book-first-exercise",
             "/downloads/holdem-river-call-check-worksheet.md"),
            ("poker/poker-books-and-courses/index.html", POKER, "poker-book-first-exercise",
             "/downloads/holdem-river-call-check-worksheet.md"),
        )
        for path, book, anchor, worksheet in cases:
            with self.subTest(path=path):
                html = file(path)
                links = Page(html).hrefs
                self.assertEqual(links.count(book), 1)
                self.assertEqual(links.count(book + "#" + anchor), 1)
                self.assertIn(worksheet, links)
                self.assertNotIn('href="https://www.amazon.com/dp/', html)
                self.assertEqual(Page(file(book.lstrip("/") + "index.html")).ids.count(anchor), 1)

    def test_reciprocal_guides_have_real_fragment_destinations(self):
        for book, guide, fragment in (
            (AI, "/technology/ai-workflow-pilot/", "pilot-protocol"),
            (POKER, "/poker/no-limit-holdem-guide/", "choose-your-route"),
        ):
            with self.subTest(book=book):
                self.assertIn(guide + "#" + fragment, Page(file(book.lstrip("/") + "index.html")).hrefs)
                self.assertEqual(Page(file(guide.lstrip("/") + "index.html")).ids.count(fragment), 1)

    def test_source_and_committed_output_stay_in_sync(self):
        for slug in ("one-workflow-at-a-time", "how-to-play-no-limit-texas-holdem"):
            self.assertEqual(file("_source/books/" + slug + ".html"),
                             file("books/" + slug + "/index.html"))
        for source, output, fragment in (
            ("_source/technology/ai-workflow-pilot.html", "technology/ai-workflow-pilot/index.html", "ai-book-first-exercise"),
            ("_source/poker/no-limit-holdem-guide.html", "poker/no-limit-holdem-guide/index.html", "poker-book-first-exercise"),
            ("_source/poker/poker-books-and-courses.html", "poker/poker-books-and-courses/index.html", "poker-book-first-exercise"),
        ):
            with self.subTest(source=source):
                link = 'href="' + (AI if fragment.startswith("ai-") else POKER) + "#" + fragment + '"'
                self.assertIn(link, file(source))
                self.assertIn(link, file(output))

    def test_site_hubs_remain_relevant_not_replaced(self):
        for path in ("index.html", "about/index.html", "bio/index.html", "creative/index.html", "books/index.html"):
            with self.subTest(path=path):
                links = Page(file(path)).hrefs
                self.assertIn(AI, links)
                self.assertIn(POKER, links)
        self.assertEqual(file("_source/books/index.html"), file("books/index.html"))
        self.assertIn("not an independent review", file("poker/poker-books-and-courses/index.html"))

    def test_book_identity_and_unknown_retail_editions_preserved(self):
        for slug in ("one-workflow-at-a-time", "how-to-play-no-limit-texas-holdem"):
            doc = file("books/" + slug + "/index.html")
            match = re.search(r'<script type="application/ld\\+json">(.*?)</script>', doc, re.S)
            self.assertIsNotNone(match)
            book = json.loads(match.group(1))["mainEntity"]
            self.assertEqual(book["author"]["@id"], "https://nolankido.com/about/#nolan-kido")
            self.assertIn("not independently verified", doc)
            for forbidden in ("isbn", "offers", "datePublished", "aggregateRating", "bookFormat"):
                self.assertNotIn(forbidden, book)

    def test_local_release_wires_regression_and_never_adds_ci(self):
        runner = file("_scripts/local_release_checks.py")
        self.assertIn("test_turn49_topic_book_paths.py", runner)
        self.assertIn("['_scripts/build_books.py', '--check']", runner)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            f.is_file() and f.suffix.lower() in (".yml", ".yaml") for f in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
