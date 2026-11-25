"""Exact UTF-8 book source/output parity, including real registry validation."""
from contextlib import redirect_stderr, redirect_stdout
from html import escape
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import book_pages as books
import build_books as builder


def pairs():
    return [(books.HUB_SOURCE, books.HUB_OUTPUT)] + [
        (Path('_source/books') / (b['slug'] + '.html'), Path('books') / b['slug'] / 'index.html')
        for b in books.BOOKS]


def markup(title, heading, desc, url, schema, body):
    schema.update({'@id': url + '#webpage', 'url': url, 'name': title, 'description': desc,
                   'isPartOf': {'@type': 'WebSite', '@id': books.ORIGIN + '/#website',
                                'url': books.ORIGIN + '/', 'publisher': {'@type': 'Person',
                                '@id': books.PERSON, 'url': books.ORIGIN + '/about/'}}})
    fields = [('name', 'description', desc), ('property', 'og:url', url),
              ('property', 'og:title', title), ('property', 'og:description', desc),
              ('name', 'twitter:title', title), ('name', 'twitter:description', desc)]
    meta = '\n'.join(f'<meta {kind}="{field}" content="{escape(value, quote=True)}">'
                     for kind, field, value in fields)
    return ('<!doctype html>\n<html><head><title>' + escape(title) + '</title>\n'
            + '<link rel="canonical" href="' + url + '">\n' + meta
            + '\n<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False)
            + '</script></head>\n<body><main><h1>' + escape(heading) + '</h1>\n'
            + body + '</main></body></html>\n').encode('utf-8')


class ByteParityControls(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        links = ''.join('<a href="' + books.route(b) + '">Book</a>' for b in books.BOOKS)
        for path in ('index.html', 'creative/index.html', 'about/index.html', 'bio/index.html'):
            self.write(path, ('<a href="/books/">Catalog</a>' + links).encode())
        hub = markup(books.HUB_TITLE, 'Books by Nolan Kido', books.HUB_DESCRIPTION, books.HUB_URL,
                     {'@type': 'CollectionPage', 'dateModified': books.UPDATED,
                      'about': {'@id': books.PERSON}, 'mainEntity': {'@type': 'ItemList',
                      '@id': books.HUB_URL + '#book-list', 'name': 'Books by Nolan Kido',
                      'itemListElement': books.entity_list()}},
                     '<section id="book-ai-works-human-decides">' + books.THIRD_BOOK['description']
                     + '</section>' + links)
        self.write(books.HUB_SOURCE, hub)
        for item, (source, _) in zip(books.BOOKS, pairs()[1:]):
            url = books.ORIGIN + books.route(item)
            data = markup(item['seo'], item['title'], item['description'], url,
                          {'@type': 'WebPage', 'dateModified': item['modified'],
                           'about': {'@id': url + '#book'}, 'mainEntity': books.book_entity(item)},
                          '<a href="/books/">Catalog</a>')
            self.write(source, data)
        self.assertEqual(self.run_build(), 0)

    def write(self, path, data):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)

    def run_build(self, check=False):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return builder.build(self.root, check=check)

    def outputs(self):
        return {target: (self.root / target).read_bytes() for _, target in pairs()}

    def test_exact_build_and_registry_are_idempotent(self):
        before = self.outputs()
        self.assertEqual(self.run_build(check=True), 0)
        self.assertEqual(self.run_build(), 0)
        self.assertEqual(before, self.outputs())
        self.assertEqual(books.published(self.root), books.BOOKS)
        self.assertEqual(books.hub_record(self.root)['url'], books.HUB_URL)
        sitemap = ET.Element('urlset')
        books.add_to_sitemap(sitemap, self.root)
        self.assertEqual(len(sitemap), 4)
        self.assertEqual(len(books.find_entries(self.root)), 4)

    def test_line_ending_only_drift_in_book_is_rejected(self):
        source, target = pairs()[1]
        changed = (self.root / source).read_bytes().replace(b'\n', b'\r\n')
        self.write(target, changed)
        self.assertEqual((self.root / source).read_text(), (self.root / target).read_text())
        before = self.outputs()
        self.assertEqual(self.run_build(check=True), 1)
        self.assertEqual(self.outputs(), before)
        with self.assertRaisesRegex(ValueError, 'exact public source'):
            books.published(self.root)

    def test_line_ending_only_drift_in_catalog_is_rejected(self):
        source, target = pairs()[0]
        self.write(target, (self.root / source).read_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual((self.root / source).read_text(), (self.root / target).read_text())
        before = self.outputs()
        self.assertEqual(self.run_build(check=True), 1)
        self.assertEqual(self.outputs(), before)
        with self.assertRaisesRegex(ValueError, 'differs from source'):
            books.hub_record(self.root)

    def test_crlf_sources_are_copied_without_normalization(self):
        for source, _ in pairs():
            self.write(source, (self.root / source).read_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual(self.run_build(), 0)
        for source, target in pairs():
            self.assertIn(b'\r\n', (self.root / target).read_bytes())
            self.assertEqual((self.root / target).read_bytes(), (self.root / source).read_bytes())
        self.assertEqual(self.run_build(check=True), 0)

    def test_missing_final_source_does_not_modify_earlier_outputs(self):
        before = self.outputs()
        self.write(books.HUB_SOURCE, (self.root / books.HUB_SOURCE).read_bytes() + b'\n')
        (self.root / pairs()[-1][0]).unlink()
        self.assertEqual(self.run_build(), 1)
        self.assertEqual(self.outputs(), before)

    def test_invalid_utf8_final_source_does_not_modify_earlier_outputs(self):
        before = self.outputs()
        self.write(books.HUB_SOURCE, (self.root / books.HUB_SOURCE).read_bytes() + b'\n')
        self.write(pairs()[-1][0], b'\xff')
        self.assertEqual(self.run_build(), 1)
        self.assertEqual(self.outputs(), before)

    def test_missing_output_check_does_not_regenerate_it(self):
        _, target = pairs()[-1]
        (self.root / target).unlink()
        self.assertEqual(self.run_build(check=True), 1)
        self.assertFalse((self.root / target).exists())

    def test_matching_invalid_metadata_still_fails_registry(self):
        source, target = pairs()[1]
        raw = (self.root / source).read_bytes().replace(b'rel="canonical"', b'rel="alternate"')
        self.write(source, raw)
        self.write(target, raw)
        with self.assertRaisesRegex(ValueError, 'canonical'):
            self.run_build(check=True)


class PublishedBookByteCoverage(unittest.TestCase):
    def test_all_actual_book_sources_match_public_bytes(self):
        for source, target in pairs():
            with self.subTest(page=target):
                self.assertEqual((ROOT / source).read_bytes(), (ROOT / target).read_bytes())
        self.assertEqual(builder.build(ROOT, check=True), 0)


if __name__ == '__main__':
    unittest.main()
