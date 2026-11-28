"""Turn 111: canonical third author page and cross-surface source parity."""
import json
import re
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import book_pages

ROUTE = "/books/ai-works-human-decides/"
URL = book_pages.ORIGIN + ROUTE

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def schema(page):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S).group(1))

class BookMigrationTests(unittest.TestCase):
    def test_registered_source_and_catalog(self):
        page = read("books/ai-works-human-decides/index.html")
        self.assertEqual(page, read("_source/books/ai-works-human-decides.html"))
        self.assertEqual(schema(page)["mainEntity"], book_pages.THIRD_BOOK)
        self.assertEqual([book_pages.route(b) for b in book_pages.published(ROOT)].count(ROUTE), 1)
        catalog = read("books/index.html")
        self.assertEqual(catalog, read("_source/books/index.html"))
        self.assertEqual(schema(catalog)["mainEntity"]["itemListElement"][2]["item"], book_pages.THIRD_BOOK)
        self.assertNotIn("mentions", schema(catalog))
        self.assertEqual(catalog.count('id="book-ai-works-human-decides"'), 1)
        self.assertIsNotNone(book_pages.hub_record(ROOT))

    def test_identity_and_edition_boundary(self):
        graph = json.loads(read("assets/nolan-kido-identity.jsonld"))
        self.assertEqual(graph, json.loads(read("_source/person-schema.jsonld")))
        works = [n for n in graph["@graph"] if n["@type"] == "Book"]
        self.assertEqual(len(works), 3)
        self.assertEqual([n for n in works if n["@id"] == URL + "#book"], [book_pages.THIRD_BOOK])
        self.assertNotIn("https://nolankido.com/books/#book-ai-works-human-decides", [n["@id"] for n in works])
        self.assertEqual(schema(read("creative/index.html"))["mainEntity"]["itemListElement"][2]["item"], book_pages.THIRD_BOOK)
        for key in ("isbn", "offers", "datePublished", "bookFormat", "aggregateRating"):
            self.assertNotIn(key, book_pages.THIRD_BOOK)
        ledger = json.loads(read("downloads/nolan-kido-book-edition-evidence.json"))
        self.assertEqual(len(ledger["works"]), 2)
        supplemental = ledger["supplementary_author_supplied_titles"][0]
        self.assertEqual(supplemental["canonical_author_page"], URL)
        self.assertEqual(supplemental["retailer_verification_status"], "not_verified")
        self.assertFalse(supplemental["retail_page_inspected"])

    def test_navigation_and_index(self):
        for path in ("index.html", "about/index.html", "bio/index.html", "creative/index.html", "books/index.html"):
            self.assertIn('href="' + ROUTE + '"', read(path))
        self.assertIn('href="/books/#book-ai-works-human-decides"', read("books/ai-works-human-decides/index.html"))
        sitemap = ET.fromstring(read("sitemap.xml"))
        rows = [el.findtext("{*}loc") for el in sitemap]
        self.assertEqual(rows.count(URL), 1)
        self.assertEqual(len(rows), len(set(rows)))
        finder = read("find/index.html")
        self.assertEqual(finder.count('href="' + ROUTE + '"'), 1)
        payload = json.loads(re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>', finder, re.S).group(1))
        sections = payload["pages"]["books"]["ai-works-human-decides/"]
        self.assertEqual(len(sections), 12)
        self.assertIn("human-decides-exercise", sections)
        self.assertIn("human-decides-evidence", sections)

    def test_existing_ai_guides_and_essay_link_to_exact_book_exercises(self):
        workflow = '/books/one-workflow-at-a-time/#ai-book-free'
        exercise = ROUTE + '#human-decides-exercise'
        for paths, links in (
            (('_source/technology/home.html', 'technology/index.html'), (workflow, exercise)),
            (('_source/notes/keep-the-judgment.html', 'notes/keep-the-judgment/index.html'), (exercise,)),
            (('_source/technology/check-ai-answers.html', 'technology/check-ai-answers/index.html'), (exercise,)),
        ):
            for path in paths:
                with self.subTest(path=path):
                    for link in links:
                        self.assertEqual(read(path).count(f'href="{link}"'), 1)
        self.assertEqual(read('books/one-workflow-at-a-time/index.html').count('id="ai-book-free"'), 1)
        self.assertEqual(read('books/ai-works-human-decides/index.html').count('id="human-decides-exercise"'), 1)
        self.assertIn('This essay is not a book excerpt.', read('notes/keep-the-judgment/index.html'))
        self.assertIn('The exercise is an original site resource, not a verified book excerpt.',
                      read('technology/index.html'))

    def test_release_inventory(self):
        import check_live
        import check_html5
        import build
        self.assertEqual(check_live.targets(ROOT)[ROUTE], (200, (ROOT / "books/ai-works-human-decides/index.html").read_bytes()))
        self.assertEqual(check_html5.publication_paths(ROOT, build.public_pages())[ROUTE], Path("books/ai-works-human-decides/index.html"))


    def test_practical_ai_hub_and_essay_have_reciprocal_author_book_paths(self):
        for source, public, boundary in (
            ("_source/technology/home.html", "technology/index.html",
             "The exercise is an original site resource, not a verified book excerpt."),
            ("_source/notes/keep-the-judgment.html", "notes/keep-the-judgment/index.html",
             "This essay is not a book excerpt."),
        ):
            for path in (source, public):
                with self.subTest(path=path):
                    text = read(path)
                    self.assertEqual(text.count('href="' + ROUTE + '"'), 1)
                    self.assertIn('<a href="' + ROUTE + '"><cite>AI Works, Human Decides</cite></a>', text)
                    self.assertIn(boundary, text)
        technology = read("technology/index.html")
        self.assertIn('id="ai-works-human-decides"', technology)
        self.assertIn('href="/books/#ai-works-decision-lab"', technology)
        book = read("books/ai-works-human-decides/index.html")
        self.assertEqual(book.count('href="/technology/#ai-works-human-decides"'), 1)
        self.assertEqual(book.count('href="/notes/keep-the-judgment/"'), 1)
        self.assertEqual(book, read("_source/books/ai-works-human-decides.html"))

if __name__ == "__main__":
    unittest.main()
