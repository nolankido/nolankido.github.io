"""Turn 88: safeguard the original AI Works, Human Decides review exercise.

Tests use committed public files only. They do not query an AI model, retailer,
customer records or analytics, and do not approve any real publication.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages
import build

BOOKS_SOURCE = ROOT / "_source/books/index.html"
BOOKS_PUBLIC = ROOT / "books/index.html"
TECH_SOURCE = ROOT / "_source/technology/home.html"
TECH_PUBLIC = ROOT / "technology/index.html"
SHEET = ROOT / "downloads/ai-human-decision-review-worksheet.md"

LAB = '<h3 id="ai-works-decision-lab">'
DOWNLOAD = '/downloads/ai-human-decision-review-worksheet.md'
TECH_NOTE = '<p class="small-copy"><strong>Try the human approval check:'


def extract_lab(html: str) -> str:
    if html.count(LAB) != 1:
        raise ValueError("Expected one human decision lab")
    first = html.index(LAB)
    end = html.find('\n  </div>\n</section>', first)
    if end < 0:
        raise ValueError("Decision lab has no section ending")
    return html[first:end]


def lab_problems(html: str) -> list[str]:
    try:
        fragment = extract_lab(html)
    except ValueError as error:
        return [str(error)]
    required = (
        'Friday at <strong>6:00 p.m.</strong>',
        'Thursday at noon',
        '<strong>24 places</strong>',
        '<strong>18 registrations confirmed</strong>',
        'Accessibility arrangements have not been confirmed',
        'designated organizer must approve',
        'Constructed AI draft, not an actual model output',
        '24 minus 18 equals <strong>6 unreserved places',
        'REVISE AND RECHECK',
        'HOLD PUBLICATION',
        'STOP USING AI FOR THIS TASK',
        'not a real model test',
        'href="' + DOWNLOAD + '" download',
    )
    errors = [text for text in required if text not in fragment]
    if fragment.count('id="ai-works-decision-answer"') != 1:
        errors.append('Missing or duplicate answer disclosure')
    if fragment.count('<summary>Reveal the source check and human decision</summary>') != 1:
        errors.append('Answer is not independently revealable')
    if fragment.count('<li>') != 5 or fragment.count('</li>') != 5:
        errors.append('Five supplied issues are not all explained')
    if fragment.index('Try it first:') > fragment.index('Reveal the source check'):
        errors.append('Answer is ahead of the exercise')
    if '<script' in fragment or chr(0x2014) in fragment:
        errors.append('Unsafe markup or forbidden punctuation')
    return errors


class Turn88HumanDecisionLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = BOOKS_PUBLIC.read_text(encoding='utf-8')
        cls.tech = TECH_PUBLIC.read_text(encoding='utf-8')
        cls.sheet = SHEET.read_text(encoding='utf-8')

    def test_books_catalog_source_public_parity_and_identity(self):
        self.assertEqual(BOOKS_SOURCE.read_text(encoding='utf-8'), self.books)
        self.assertIsNotNone(book_pages.hub_record(ROOT))
        self.assertEqual(len(book_pages.BOOKS), 2)
        self.assertEqual(lab_problems(self.books), [])
        self.assertEqual(self.books.count(LAB), 1)

    def test_third_book_card_points_to_original_site_practice(self):
        self.assertEqual(self.books.count('href="#ai-works-decision-lab"'), 1)
        self.assertLess(self.books.index('id="book-ai-works-human-decides"'),
                        self.books.index('href="#ai-works-decision-lab"'))
        self.assertLess(self.books.index('href="#ai-works-decision-lab"'),
                        self.books.index(LAB))
        self.assertIn('A dedicated author-book page is not yet available', self.books)
        self.assertEqual(self.books.count('href="' + DOWNLOAD + '" download'), 1)

    def test_worksheet_is_blank_and_consequentially_useful(self):
        self.assertTrue(SHEET.is_file())
        for marker in (
            'Tuesday at 2:00 p.m.', '24 capacity minus 18 confirmed registrations',
            'Constructed draft to review', 'Final human approval to publish',
            'actual model response', 'no real time measurements',
            'https://nolankido.com/books/#ai-works-decision-lab',
        ):
            self.assertIn(marker, self.sheet)
        self.assertGreaterEqual(self.sheet.count('| |'), 10)
        self.assertNotIn(chr(0x2014), self.sheet)

    def test_snapshot_arithmetic_and_release_decisions_are_explicit(self):
        self.assertEqual(24 - 18, 6)
        self.assertIn('24 minus 18 equals <strong>6 unreserved places', self.books)
        self.assertIn('not a guarantee', self.books)
        for mode in ('REVISE AND RECHECK', 'HOLD PUBLICATION',
                     'STOP USING AI FOR THIS TASK'):
            self.assertIn(mode, self.books)
            self.assertIn(mode, self.sheet)
        self.assertIn('not an observed model test', self.tech)

    def test_technology_page_links_once_to_case_and_actual_download(self):
        source = TECH_SOURCE.read_text(encoding='utf-8')
        start = source.index(TECH_NOTE)
        note = source[start:source.index('</p>', start) + 4]
        self.assertEqual(source.count(TECH_NOTE), 1)
        self.assertEqual(self.tech.count(note), 1)
        self.assertEqual(self.tech.count('href="/books/#ai-works-decision-lab"'), 1)
        self.assertIn('href="' + DOWNLOAD + '" download', note)
        self.assertIn('id="ai-works-human-decides"', self.tech)

    def test_bad_case_rewrites_are_detected(self):
        alterations = (
            ('24 minus 18 equals <strong>6', '24 minus 18 equals <strong>7'),
            ('HOLD PUBLICATION', 'PUBLISH WITHOUT APPROVAL'),
            ('id="ai-works-decision-answer"', 'id="not-an-answer"'),
            ('href="' + DOWNLOAD + '" download', 'href="/downloads/missing.md"'),
            ('not an actual model output', 'a verified real model output'),
        )
        for original, replacement in alterations:
            with self.subTest(original=original):
                self.assertIn(original, self.books)
                self.assertTrue(lab_problems(self.books.replace(original, replacement, 1)))

    def test_retail_edition_assertions_and_search_identity_are_not_inflated(self):
        schema = json.loads(re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            self.books, re.S).group(1))
        self.assertEqual(schema['dateModified'], '2026-11-22')
        self.assertEqual(len(schema['mainEntity']['itemListElement']), 2)
        self.assertEqual(schema['mentions']['name'], 'AI Works, Human Decides')
        self.assertEqual(self.books.count('id="books-retailer-evidence"'), 1)
        self.assertIn('not independently verified', self.books)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertEqual(sitemap.count('<loc>https://nolankido.com/books/</loc>'), 1)

    def test_download_registered_for_live_bytes_and_no_new_runtime(self):
        release = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertIn("'downloads/ai-human-decision-review-worksheet.md'", release)
        self.assertEqual(self.tech.count('href="' + DOWNLOAD + '" download'), 1)
        self.assertNotIn('<script', extract_lab(self.books))

    def test_generated_technology_page_reproduces_committed_output(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path('technology/index.html')], self.tech)
        self.assertEqual(outputs[Path('sitemap.xml')],
                         (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))

    def test_local_runner_and_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn88_ai_human_decision_lab.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yml', '.yaml')
            for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
