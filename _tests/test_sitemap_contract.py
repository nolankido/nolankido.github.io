"""Structural sitemap controls, independent of the full site checkout."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from sitemap_contract import inspect_sitemap, NS

ORIGIN = 'https://nolankido.com'
NAMESPACE = NS[1:-1]


class SitemapContractTests(unittest.TestCase):
    def inspect(self, xml):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sitemap.xml'
            path.write_text(xml, encoding='utf-8')
            return inspect_sitemap(path)

    def wrap(self, body):
        return '<urlset xmlns="' + NAMESPACE + '">' + body + '</urlset>'

    def row(self, url=ORIGIN + '/', extra=''):
        return '<url><loc>' + url + '</loc>' + extra + '</url>'

    def test_valid_canonical_rows_and_optional_dates(self):
        _, urls, errors = self.inspect(self.wrap(self.row(extra='<lastmod>2026-11-24</lastmod>') + self.row(ORIGIN + '/books/')))
        self.assertEqual(urls, [ORIGIN + '/', ORIGIN + '/books/'])
        self.assertEqual(errors, [])

    def test_wrong_root_and_namespace_cannot_pass(self):
        for document in (self.wrap(self.row()).replace('urlset', 'wrong'),
                         self.wrap(self.row()).replace(NAMESPACE, 'https://example.invalid/')):
            with self.subTest(document=document):
                self.assertIn('Sitemap must use the standard urlset namespace', self.inspect(document)[2])

    def test_nested_location_cannot_masquerade_as_a_url_record(self):
        xml = self.wrap('<wrapper><loc>' + ORIGIN + '/</loc></wrapper>')
        # The old audit's unrestricted descendant count would match inventory.
        old_locations = [e.text for e in ET.fromstring(xml).iter() if e.tag.endswith('}loc')]
        self.assertEqual(old_locations, [ORIGIN + '/'])
        _, urls, errors = self.inspect(xml)
        self.assertEqual(urls, [])
        self.assertTrue(any('direct url element' in error for error in errors))

    def test_two_locations_in_one_record_cannot_pass(self):
        xml = self.wrap(self.row(extra='<loc>' + ORIGIN + '/books/</loc>'))
        self.assertEqual(len([e for e in ET.fromstring(xml).iter() if e.tag.endswith('}loc')]), 2)
        _, urls, errors = self.inspect(xml)
        self.assertEqual(urls, [])
        self.assertTrue(any('exactly one nonempty direct loc' in error for error in errors))

    def test_empty_nested_or_whitespace_location_is_rejected(self):
        for loc in ('<loc/>', '<loc> </loc>', '<loc> ' + ORIGIN + '/</loc>', '<loc><nested/>' + ORIGIN + '/</loc>', ''):
            with self.subTest(loc=loc):
                _, urls, errors = self.inspect(self.wrap('<url>' + loc + '</url>'))
                self.assertEqual(urls, [])
                self.assertTrue(errors)

    def test_foreign_namespace_location_is_not_canonical(self):
        _, urls, errors = self.inspect(self.wrap('<url><loc xmlns="https://example.invalid/">' + ORIGIN + '/</loc></url>'))
        self.assertEqual(urls, [])
        self.assertTrue(errors)

    def test_invalid_or_duplicate_dates_are_rejected(self):
        for extra in ('<lastmod>2026-02-30</lastmod>', '<lastmod>20261124</lastmod>', '<lastmod/>',
                      '<lastmod>2026-11-24</lastmod><lastmod>2026-11-24</lastmod>'):
            with self.subTest(extra=extra):
                self.assertTrue(any('lastmod' in error for error in self.inspect(self.wrap(self.row(extra=extra)))[2]))

    def test_malformed_xml_returns_diagnostic(self):
        _, urls, errors = self.inspect('<urlset>')
        self.assertEqual(urls, [])
        self.assertTrue(errors[0].startswith('Cannot read sitemap XML:'))

    def test_missing_file_returns_diagnostic(self):
        with TemporaryDirectory() as tmp:
            _, urls, errors = inspect_sitemap(Path(tmp) / 'missing.xml')
            self.assertEqual(urls, [])
            self.assertTrue(errors[0].startswith('Cannot read sitemap XML:'))

    def test_duplicate_urls_remain_visible_for_inventory_comparison(self):
        _, urls, errors = self.inspect(self.wrap(self.row() + self.row()))
        self.assertEqual(errors, [])
        self.assertEqual(urls, [ORIGIN + '/', ORIGIN + '/'])
        self.assertNotEqual(len(urls), len(set(urls)))


if __name__ == '__main__':
    unittest.main()
