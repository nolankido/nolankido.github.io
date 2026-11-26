"""Book breadcrumbs identify the public catalog in both HTML and JSON-LD."""
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET
from html import escape

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nolankido.com'
BOOKS = (
    ('one-workflow-at-a-time', 'One Workflow at a Time'),
    ('how-to-play-no-limit-texas-holdem', 'How to Play No-Limit Texas Hold’em'),
    ('ai-works-human-decides', 'AI Works, Human Decides'),
)
NAV = re.compile(r'<nav\b[^>]*aria-label="Breadcrumb"[^>]*>.*?</nav>', re.S)
SCHEMA = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def expected_breadcrumb(slug, title):
    url = ORIGIN + '/books/' + slug + '/'
    return {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'name': label, 'item': target}
                for i, (label, target) in enumerate(
                    [('Home', ORIGIN + '/'), ('Books', ORIGIN + '/books/'),
                     (title, url)], start=1)]}


def breadcrumb_errors(document, slug, title):
    navs = NAV.findall(document)
    if len(navs) != 1:
        return ['one visible breadcrumb required']
    try:
        nav = ET.fromstring(navs[0])
        items = nav.findall('./ol/li')
        labels = [' '.join(''.join(li.itertext()).split()) for li in items]
        links = [(a.get('href'), ' '.join(''.join(a.itertext()).split()))
                 for a in nav.iter('a')]
        current = [el for el in nav.iter() if el.get('aria-current') == 'page']
    except ET.ParseError:
        return ['invalid breadcrumb fragment']
    errors = []
    if (labels != ['Home', 'Books', title] or links != [('/', 'Home'), ('/books/', 'Books')]
            or len(current) != 1 or current[0].tag != 'span'
            or current[0] not in list(items[-1])):
        errors.append('visible breadcrumb must identify the catalog and current book')
    records = SCHEMA.findall(document)
    try:
        record = json.loads(records[0]) if len(records) == 1 else {}
    except ValueError:
        record = {}
    if (not isinstance(record, dict)
            or record.get('breadcrumb') != expected_breadcrumb(slug, title)):
        errors.append('structured breadcrumb must match the canonical visible path')
    return errors


def fixture(slug, title):
    return ('<nav class="search-breadcrumb shell" aria-label="Breadcrumb"><ol>'
            '<li><a href="/">Home</a></li><li><a href="/books/">Books</a></li>'
            '<li><span aria-current="page">' + escape(title) + '</span></li></ol></nav>'
            '<script type="application/ld+json">'
            + json.dumps({'breadcrumb': expected_breadcrumb(slug, title)}, ensure_ascii=False)
            + '</script>')


class BreadcrumbControls(unittest.TestCase):
    def test_each_reviewed_book_uses_the_catalog_parent(self):
        for slug, title in BOOKS:
            with self.subTest(slug=slug):
                self.assertEqual(breadcrumb_errors(fixture(slug, title), slug, title), [])

    def test_visible_wrong_parent_and_wrong_current_page_fail(self):
        slug, title = BOOKS[0]
        original = fixture(slug, title)
        for changed in (original.replace('<a href="/books/">Books</a>', '<a href="/creative/">Creative Work</a>'),
                        original.replace('aria-current="page"', 'aria-current="false"'),
                        original.replace(escape(title) + '</span>', 'Other book</span>')):
            with self.subTest(changed=changed[:170]):
                self.assertTrue(breadcrumb_errors(changed, slug, title))

    def test_structured_wrong_parent_position_and_canonical_fail(self):
        slug, title = BOOKS[1]
        original = fixture(slug, title)
        for changed in (original.replace('"item": "https://nolankido.com/books/"', '"item": "https://nolankido.com/creative/"'),
                        original.replace('"position": 2', '"position": 4'),
                        original.replace('"item": "https://nolankido.com/books/' + slug + '/"', '"item": "https://example.invalid/"')):
            self.assertTrue(breadcrumb_errors(changed, slug, title))

    def test_missing_and_duplicate_breadcrumb_fail(self):
        slug, title = BOOKS[2]
        original = fixture(slug, title)
        nav = NAV.search(original).group(0)
        self.assertTrue(breadcrumb_errors(original.replace(nav, ''), slug, title))
        self.assertTrue(breadcrumb_errors(original + nav, slug, title))

    def test_exact_third_book_document(self):
        slug, title = BOOKS[2]
        document = (ROOT / 'books' / slug / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(breadcrumb_errors(document, slug, title), [])


class PublishedBookBreadcrumbTests(unittest.TestCase):
    def test_all_book_sources_public_paths_and_catalog_return(self):
        catalog = (ROOT / 'books/index.html').read_text(encoding='utf-8')
        self.assertEqual(catalog.count('id="books-catalog-comparison"'), 1)
        for slug, title in BOOKS:
            with self.subTest(slug=slug):
                source = (ROOT / '_source/books' / (slug + '.html')).read_text(encoding='utf-8')
                document = (ROOT / 'books' / slug / 'index.html').read_text(encoding='utf-8')
                self.assertEqual(source, document)
                self.assertEqual(breadcrumb_errors(document, slug, title), [])
                self.assertEqual(document.count('href="/books/"'), 1)
                if slug != BOOKS[2][0]:
                    self.assertIn('href="/books/#books-catalog-comparison"', document)
                else:
                    self.assertIn('href="/books/#book-ai-works-human-decides"', document)


if __name__ == '__main__':
    unittest.main()
