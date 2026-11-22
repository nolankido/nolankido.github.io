"""PBG-03: check poker book conversion, truthful claims, and free study routes.

Offline source test. It does not measure Amazon sales, search results, or
actual browser geometry; it verifies structures and invariants only.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOOK = "books/how-to-play-no-limit-texas-holdem/index.html"
SOURCE = "_source/books/how-to-play-no-limit-texas-holdem.html"
STYLE = "assets/book-reader-journey.css"
AMAZON = "https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324"
EVENT = "poker-book-kindle-amazon-click"


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


class Elements(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.anchors = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a":
            self.anchors.append(a)


def section(source: str, selector: str, tag: str = "section") -> str:
    start = source.find('<' + tag + ' class="' + selector)
    if start < 0:
        raise ValueError("Required section not found")
    end = source.find('</' + tag + '>', start)
    if end < 0:
        raise ValueError("Section not closed")
    return source[start:end + len('</' + tag + '>')]


def audit_problems(source: str) -> list[str]:
    """Testable guardrails. Synthetic mutation probes do not send analytics."""
    errors = []
    hero = section(source, "page-hero shell poker-book-hero")
    anchors = Elements(hero).anchors
    amazon = [a for a in anchors if a.get("href", "").startswith("https://www.amazon.com/")]
    if len(amazon) != 1 or amazon[0].get("href") != AMAZON:
        errors.append("Exact single author-provided Amazon URL required")
    if len(amazon) == 1 and (amazon[0].get("data-umami-event") != EVENT
                            or amazon[0].get("data-umami-event-source") != "book-page-hero"):
        errors.append("Amazon event identity changed")
    free = [a for a in anchors if a.get("href") == "#poker-book-first-exercise"]
    if len(free) != 1:
        errors.append("First-screen free example link required")
    if source.count('id="poker-book-first-exercise"') != 1:
        errors.append("Free example target must exist once")
    if len(re.findall(r"<h1\b", source)) != 1:
        errors.append("One H1 required")
    return errors


class PokerBookLandingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = read(BOOK)
        cls.css = read(STYLE)

    def test_poker_book_source_and_public_bytes_are_identical(self):
        self.assertEqual(read(SOURCE), self.html)
        self.assertNotIn(chr(0x2014), self.html)

    def test_first_screen_true_two_path_choice(self):
        html = self.html
        self.assertEqual(audit_problems(html), [])
        for token in ("poker-book-hero-lead", "poker-book-hero-actions",
                      "poker-book-hero-outcomes", "poker-book-hero-evidence"):
            self.assertEqual(html.count('class="' + token + '"'), 1)
        self.assertLess(html.index('class="page-hero shell poker-book-hero"'),
                        html.index('class="shell book-reader-jumps"'))
        self.assertLess(html.index('id="poker-book-amazon-cta"'),
                        html.index('href="#poker-book-first-exercise"'))
        self.assertLess(html.index('href="#poker-book-first-exercise"'),
                        html.index('class="shell book-reader-jumps"'))
        self.assertIn("No sign-up or wager required", html)

    def test_three_learning_outcomes_are_clear_and_not_false_claims(self):
        match = re.search(r'<ul class="poker-book-hero-outcomes"[^>]*>(.*?)</ul>',
                          self.html, re.S)
        self.assertIsNotNone(match)
        self.assertEqual(len(re.findall(r"<li\b", match.group(1))), 3)
        for item in ("Follow the hand.", "Explain a choice.",
                     "Notice the setting.", "not a retailer-verified table of contents",
                     "not a promise of winning results"):
            self.assertIn(item, self.html)

    def test_study_route_has_three_distinct_valid_public_destinations(self):
        html = self.html
        match = re.search(r'<ol class="poker-book-study-steps">(.*?)</ol>', html, re.S)
        self.assertIsNotNone(match)
        steps = match.group(1)
        self.assertEqual(len(re.findall(r"<li\b", steps)), 3)
        expected = (
            "/poker/free-poker-learning-path/",
            "/poker/poker-math-reference/",
            "/poker/no-limit-holdem-guide/#choose-your-route",
        )
        anchors = Elements(steps).anchors
        self.assertCountEqual([x["href"] for x in anchors], expected)
        for url in expected:
            self.assertTrue((ROOT / url.split("#")[0].lstrip("/") / "index.html").is_file())
        self.assertIn("not a reproduction of the retail book", html)

    def test_original_river_calculation_and_free_worksheet_unchanged(self):
        for fragment in ("10 / 40 = 25%", "20%", "not an observed range",
                         "not a verified chapter excerpt",
                         'href="/downloads/holdem-river-call-check-worksheet.md" download'):
            self.assertIn(fragment, self.html)
        self.assertEqual(self.html.count('id="poker-book-sample-answer"'), 1)
        self.assertTrue((ROOT / "downloads/holdem-river-call-check-worksheet.md").is_file())

    def test_retail_claims_and_person_metadata_remain_bounded(self):
        self.assertEqual(self.html.count('href="' + AMAZON + '"'), 1)
        self.assertIn("not independently verified", self.html)
        self.assertIn("Author-supplied Amazon link", self.html)
        self.assertIn("B0HSB98324", self.html)
        raw = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                        self.html, re.S)
        self.assertIsNotNone(raw)
        data = json.loads(raw.group(1))
        book = data["mainEntity"]
        self.assertEqual(book["author"]["@id"],
                         "https://nolankido.com/about/#nolan-kido")
        for invalid in ("offers", "isbn", "datePublished", "aggregateRating"):
            self.assertNotIn(invalid, book)

    def test_320px_reflow_and_accessible_focus_are_supported_by_css(self):
        self.assertEqual(
            self.html.count('href="/assets/book-reader-journey.css?v=20261122-pbg03"'),
            1)
        for token in (".page-book-how-to-play-no-limit-texas-holdem",
                      ".poker-book-free-start a:focus-visible",
                      "min-height: 44px", "@media (max-width: 760px)",
                      "@media (max-width: 480px)", "grid-template-columns: minmax(0, 1fr)",
                      "@media (forced-colors: active)", "@media print",
                      "overflow-wrap: anywhere"):
            self.assertIn(token, self.css)
        self.assertNotIn(chr(0x2014), self.css)

    def test_other_book_page_keeps_original_cta_and_unchanged_css_version(self):
        other = read("books/one-workflow-at-a-time/index.html")
        self.assertNotIn("poker-book-hero-actions", other)
        self.assertIn("B0HRQNCP7Y", other)
        self.assertIn('href="/assets/book-reader-journey.css?v=20261122"', other)

    def test_negative_controls_detect_bad_amazon_link_and_missing_example(self):
        self.assertTrue(audit_problems(self.html.replace(AMAZON, "https://example.invalid/", 1)))
        self.assertTrue(audit_problems(self.html.replace(
            'href="#poker-book-first-exercise"', 'href="#missing-example"', 1)))
        self.assertTrue(audit_problems(self.html.replace(
            'data-umami-event="' + EVENT + '"', 'data-umami-event="bad-event"', 1)))

    def test_manual_release_checklist_includes_this_test(self):
        checklist = read("_scripts/local_release_checks.py")
        self.assertIn("test_pbg03_poker_book_landing.py", checklist)
        self.assertIn("['_scripts/build_books.py', '--check']", checklist)
        self.assertNotIn("onclick=", self.html)


if __name__ == "__main__":
    unittest.main()
