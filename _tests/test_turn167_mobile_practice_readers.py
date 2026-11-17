"""Turn 167: readable, mobile-first HTML mirrors of the two Markdown study files.

No generated page may leak the practice answer, silently change its Markdown
source, add JavaScript or collect hand-review responses. These are helper
views, not indexed article routes.
"""
from __future__ import annotations

from html.parser import HTMLParser
from hashlib import sha1
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
QUESTION_SOURCE = ROOT / "downloads/poker-hand-review-practice-01.md"
KEY_SOURCE = ROOT / "downloads/poker-hand-review-practice-01-key.md"
QUESTION_HTML = ROOT / "downloads/poker-hand-review-practice-01.html"
KEY_HTML = ROOT / "downloads/poker-hand-review-practice-01-key.html"
QUESTION_ROUTE = "/downloads/poker-hand-review-practice-01.html"
KEY_ROUTE = "/downloads/poker-hand-review-practice-01-key.html"
GUIDE_ROUTE = "/poker/reviewing-a-hand/"
WORKSHEET_ROUTE = "/downloads/poker-hand-review.md"


def git_blob(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class PageReader(HTMLParser):
    def __init__(self, markup: str):
        super().__init__(convert_charrefs=True)
        self.headings = []
        self.links = []
        self.cards = 0
        self.checks = 0
        self._heading = None
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("h1", "h2"):
            self._heading = [tag, ""]
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if attrs.get("class") == "audit-card":
            self.cards += 1
        if tag == "input" and attrs.get("type") == "checkbox":
            self.checks += 1

    def handle_data(self, value):
        if self._heading is not None:
            self._heading[1] += value

    def handle_endtag(self, tag):
        if self._heading is not None and tag == self._heading[0]:
            self.headings.append(tuple(self._heading))
            self._heading = None


def reader_errors(question_html: str, key_html: str,
                  question_source: bytes, key_source: bytes) -> list[str]:
    errors = []
    pages = ((question_html, question_source, QUESTION_ROUTE),
             (key_html, key_source, KEY_ROUTE))
    for html, source, route in pages:
        sha = git_blob(source)
        if html.count('data-source-blob="' + sha + '"') != 1:
            errors.append("Stale or absent Markdown source fingerprint: " + route)
        if html.count('data-source-path="' + route.removesuffix(".html") + '.md"') != 1:
            errors.append("Source path must identify the exact .md file: " + route)
        for guard in (
            '<!doctype html>', '<html lang="en">',
            'name="viewport" content="width=device-width, initial-scale=1"',
            'name="robots" content="noindex,follow"',
            'http-equiv="Content-Security-Policy"',
            'overflow-wrap:anywhere', '@media(max-width:480px)',
            ':focus-visible', 'class="practice-doc"',
            'class="skip-link"',
        ):
            if guard not in html:
                errors.append("Missing responsive/accessibility guard: " + guard)
        for prohibited in ('<script', '<iframe', '<form', 'onload=', 'onclick=',
                           'https://fonts.', 'https://www.google-analytics.',
                           '<link rel="stylesheet"', '\u2014'):
            if prohibited in html:
                errors.append("Unexpected script, remote resource or punctuation: " + prohibited)
        if 'href="' + WORKSHEET_ROUTE + '" download' not in html and html == question_html:
            errors.append("Question view must retain direct editable worksheet download")
        if '<table' in html:
            errors.append("Key tables must be vertically readable cards, not wide tables")
        reader = PageReader(html)
        headings = [x for tag, x in reader.headings if tag == "h2"]
        if len(headings) != (8 if html == question_html else 7):
            errors.append("Original stage headings were dropped")
        if len([x for tag, x in reader.headings if tag == "h1"]) != 1:
            errors.append("Exactly one main page heading is required")
        if not all(any(h.startswith(str(i) + ". ") for h in headings)
                   for i in range(1, 8)):
            errors.append("One or more numbered study stages missing")
    q = PageReader(question_html)
    k = PageReader(key_html)
    if q.cards != 0 or k.cards != 14:
        errors.append("Key's 5 evidence and 9 ledger entries must be vertical cards")
    if k.checks != 5:
        errors.append("Key self-check must have five locally functional checkboxes")
    if KEY_ROUTE in question_html[:question_html.find("Stop here.")]:
        errors.append("Answer-key link leaked before end-of-questions barrier")
    if question_html.count('href="' + KEY_ROUTE + '"') != 1:
        errors.append("Question must have exactly one answer-key navigation at the end")
    if key_html.count('href="' + QUESTION_ROUTE + '"') < 2:
        errors.append("Key must offer an obvious return path top and bottom")
    if 'href="' + QUESTION_ROUTE + '" download' in key_html:
        errors.append("Return to practice must open HTML, not download it")
    if 'href="' + '/downloads/poker-hand-review-practice-01.md' + '" download' not in question_html:
        errors.append("Question source must remain available for private editing")
    if 'href="' + '/downloads/poker-hand-review-practice-01-key.md' + '" download' not in key_html:
        errors.append("Key Markdown original must remain available")
    if "raw Markdown" in question_html:
        errors.append("Question mirror should be readable, not raw Markdown")
    for answer in ("72,000", "20,000", "26,000", "14,000", "92,000", "23.1%"):
        # The HTML question does include source chip numbers such as 24,000,
        # so check only the values that the exercise asks the reader to compute.
        if answer in question_html.split('class="practice-doc"')[1]:
            errors.append("Practice HTML leaked the calculated answer: " + answer)
    if '14,000' not in key_html or '92,000' not in key_html:
        errors.append("Key omitted uncalled refund or final stack")
    if any(href.startswith("https://") for href in q.links + k.links):
        errors.append("Browser-reader links must remain same-origin")
    return errors


class MobilePracticeReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q_md = QUESTION_SOURCE.read_bytes()
        cls.k_md = KEY_SOURCE.read_bytes()
        cls.q = QUESTION_HTML.read_text(encoding="utf-8")
        cls.k = KEY_HTML.read_text(encoding="utf-8")

    def test_html_mirrors_are_formatted_current_and_answer_blind(self):
        self.assertEqual(reader_errors(self.q, self.k, self.q_md, self.k_md), [])
        self.assertIn("Q♠ J♠", self.q)
        self.assertIn("6,000 / 26,000", self.k)
        self.assertNotIn("<h2>Checking key", self.q)

    def test_navigational_contracts_preserve_the_original_downloads(self):
        source = (ROOT / "_source/poker/reviewing-a-hand.html").read_text(encoding="utf-8")
        public = (ROOT / "poker/reviewing-a-hand/index.html").read_text(encoding="utf-8")
        self.assertIn(source, public)
        self.assertIn('href="' + QUESTION_ROUTE + '">Try a new case</a>', source)
        self.assertNotIn('href="' + KEY_ROUTE + '"', source)
        blank = (ROOT / WORKSHEET_ROUTE.lstrip("/")).read_text(encoding="utf-8")
        self.assertIn("https://nolankido.com" + QUESTION_ROUTE, blank)
        self.assertIn("https://nolankido.com/downloads/poker-hand-review-practice-01.md", blank)
        self.assertNotIn(KEY_ROUTE, blank)

    def test_legacy_documented_hand_reviews_are_preserved(self):
        for file in (
            "downloads/poker-hand-review-example-ak.md",
            "downloads/poker-hand-review-example-64o.md",
            "downloads/poker-hand-review-example-77.md",
        ):
            self.assertTrue((ROOT / file).is_file(), file)
        for route in (QUESTION_ROUTE, KEY_ROUTE):
            page = (ROOT / route.lstrip("/")).read_text(encoding="utf-8")
            self.assertIn('content="noindex,follow"', page)

    def test_invalid_source_or_answer_disclosures_are_caught(self):
        bad = (
            (self.q.replace('data-source-blob="' + git_blob(self.q_md) + '"',
                            'data-source-blob="stale"', 1), self.k),
            (self.q.replace('overflow-wrap:anywhere', 'overflow-wrap:normal'), self.k),
            (self.q.replace("Stop here.", "Read answers above.", 1), self.k),
            (self.q.replace("##", "##", 1).replace("<p>Write the arithmetic", "<p>14,000. Write the arithmetic", 1), self.k),
            (self.q.replace('href="' + KEY_ROUTE + '"', 'href="/downloads/invalid-key.html"', 1), self.k),
            (self.q, self.k.replace('class="audit-card"', 'class="old-wide-row"', 1)),
            (self.q, self.k.replace('href="' + QUESTION_ROUTE + '"',
                                    'href="/downloads/invalid.html"')),
        )
        for idx, (q, k) in enumerate(bad):
            with self.subTest(idx=idx):
                self.assertTrue(reader_errors(q, k, self.q_md, self.k_md))


if __name__ == "__main__":
    unittest.main()
