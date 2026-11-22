"""PBG-04: keep contextual beginner-book links optional, unique and source-backed.

Local/offline checks only. Links and source counts do not prove search traffic,
assistant references, Amazon landing sessions or sales.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOOK = "/books/how-to-play-no-limit-texas-holdem/"
NEW = (
    "free-poker-learning-path",
    "holdem-basics",
    "starting-hand-decisions",
    "betting-and-pots",
    "beginner-practice",
    "poker-math-reference",
)
SAMPLE = (
    "poker",
    "no-limit-holdem-guide",
    "poker-books-and-courses",
    *NEW,
    "library",
    "study",
)
BASELINE = ROOT / "_reports/poker-book-growth/pbg-02-acquisition-route-baseline.json"
AFTER = ROOT / "_reports/poker-book-growth/pbg-04-contextual-link-coverage.json"
PARAGRAPH = re.compile(r'<p class="poker-book-bridge">.*?</p>', re.S)


class LinkParser(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class BookContextualLinkTests(unittest.TestCase):
    def test_all_six_source_public_links_are_exactly_identical(self):
        for slug in NEW:
            with self.subTest(slug=slug):
                source = read("_source/poker/" + slug + ".html")
                public = read("poker/" + slug + "/index.html")
                a, b = PARAGRAPH.findall(source), PARAGRAPH.findall(public)
                self.assertEqual(len(a), 1)
                self.assertEqual(a, b)
                self.assertEqual(source.count('href="' + BOOK + '"'), 1)
                self.assertEqual(public.count('href="' + BOOK + '"'), 1)
                self.assertNotIn(chr(0x2014), a[0])

    def test_each_link_is_optional_author_disclosed_and_not_a_direct_amazon_redirect(self):
        for slug in NEW:
            with self.subTest(slug=slug):
                paragraph = PARAGRAPH.search(read("poker/" + slug + "/index.html")).group(0)
                parsed = LinkParser(paragraph)
                self.assertEqual(len(parsed.links), 1)
                self.assertEqual(parsed.links[0]["href"], BOOK)
                self.assertNotIn("target", parsed.links[0])
                self.assertNotIn("data-umami-event", parsed.links[0])
                self.assertIn("author", paragraph.lower())
                self.assertNotIn("www.amazon.com", paragraph.lower())
                self.assertNotIn("B0HSB98324", paragraph)
                self.assertNotIn("best-selling", paragraph.lower())
                self.assertNotIn("guarantee", paragraph.lower())

    def test_free_poker_foundations_remains_first_not_a_sales_gate(self):
        page = read("poker/free-poker-learning-path/index.html")
        self.assertLess(page.index('href="/poker/first-decisions/"'),
                        page.index('class="poker-book-bridge"'))
        self.assertLess(page.index('class="poker-book-bridge"'),
                        page.index('class="course-later"'))
        self.assertIn("All six lessons remain free", page)
        self.assertIn('href="/poker/first-decisions/"', page)
        self.assertIn('href="/poker/beginner-checkpoint/', page)

    def test_book_link_follows_subject_teaching_before_sources(self):
        for slug in ("holdem-basics", "starting-hand-decisions", "betting-and-pots",
                     "beginner-practice", "poker-math-reference"):
            with self.subTest(slug=slug):
                page = read("poker/" + slug + "/index.html")
                book_at = page.index('class="poker-book-bridge"')
                self.assertGreater(book_at, page.index('class="article-body shell prose viewer-guide"'))
                if slug == "poker-math-reference":
                    self.assertLess(book_at, page.index('<h2 id="selected-sources">'))
                else:
                    self.assertLess(book_at, page.index('class="viewer-sources"'))

    def test_betting_math_and_practice_original_free_paths_remain(self):
        pages = {
            "betting-and-pots": (
                'id="raise-to"', 'id="all-in"', 'id="try"',
            ),
            "beginner-practice": (
                'id="practice-next-title"', 'href="/poker/beginner-checkpoint/"',
                'href="/poker/free-poker-learning-path/"',
            ),
            "starting-hand-decisions": (
                'id="study-template"', 'id="check-record"',
            ),
            "poker-math-reference": (
                'href="/downloads/poker-math-reference.md" download',
                'id="selected-sources"',
            ),
        }
        for slug, tokens in pages.items():
            with self.subTest(slug=slug):
                page = read("poker/" + slug + "/index.html")
                for token in tokens:
                    self.assertIn(token, page)

    def test_no_unapproved_tracking_or_book_guarantees(self):
        for slug in NEW:
            page = read("poker/" + slug + "/index.html")
            with self.subTest(slug=slug):
                self.assertNotIn('data-umami-event="poker-book-kindle-amazon-click"', page)
                self.assertNotIn('href="https://www.amazon.com/', PARAGRAPH.search(page).group())
                self.assertNotIn("guaranteed profits", PARAGRAPH.search(page).group())
        destination = read("books/how-to-play-no-limit-texas-holdem/index.html")
        self.assertEqual(destination.count(
            'href="https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324"'), 1)
        self.assertEqual(destination.count(
            'data-umami-event="poker-book-kindle-amazon-click"'), 1)

    def test_frozen_before_and_after_eleven_page_coverage(self):
        before = json.loads(BASELINE.read_text(encoding="utf-8"))
        after = json.loads(AFTER.read_text(encoding="utf-8"))
        self.assertEqual(before["summary"]["selected_pages"], 11)
        self.assertEqual(before["summary"]["pages_with_exact_direct_book_link"], 3)
        self.assertEqual(after["summary"]["selected_pages"], 11)
        self.assertEqual(after["summary"]["pages_with_exact_direct_book_link"], 9)
        self.assertEqual(after["summary"]["pages_without_exact_direct_book_link"], 2)
        self.assertEqual(set(row["route"] for row in before["routes"]),
                         set(row["route"] for row in after["routes"]))
        previous = {row["route"]: row["canonical_book_links_in_committed_html"]
                    for row in before["routes"]}
        latest = {row["route"]: row["canonical_book_links_in_committed_html"]
                  for row in after["routes"]}
        for slug in NEW:
            self.assertEqual(previous["/poker/" + slug + "/"], 0)
            self.assertEqual(latest["/poker/" + slug + "/"], 1)
        for route in latest:
            html = read(route.lstrip("/") + "index.html")
            self.assertEqual(html.count('href="' + BOOK + '"'), latest[route])
        for skip in ("/poker/library/", "/poker/study/"):
            self.assertEqual(latest[skip], 0)

    def test_no_false_traffic_or_sales_counts_in_public_snapshot(self):
        after = json.loads(AFTER.read_text(encoding="utf-8"))
        self.assertEqual(after["measurement"]["status"], "not_collected")
        for field in ("google_web_clicks", "google_web_impressions",
                      "amazon_outbound_click_events", "kdp_book_orders",
                      "ai_citation_events"):
            self.assertIsNone(after["measurement"][field])

    def test_local_release_runner_includes_new_contract_and_no_actions(self):
        runner = read("_scripts/local_release_checks.py")
        self.assertIn("test_pbg04_poker_book_contextual_links.py", runner)
        self.assertIn("test_pbg03_poker_book_landing.py", runner)
        self.assertIn("['_scripts/build.py', '--check']", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            x.suffix.lower() in (".yaml", ".yml") for x in workflows.iterdir()))

    def test_author_book_destination_is_a_real_canonical_page(self):
        target = read("books/how-to-play-no-limit-texas-holdem/index.html")
        self.assertEqual(target.count(
            '<link rel="canonical" href="https://nolankido.com' + BOOK + '">'), 1)
        self.assertIn('id="poker-book-first-exercise"', target)
        self.assertIn("not independently verified", target)


if __name__ == "__main__":
    unittest.main()
