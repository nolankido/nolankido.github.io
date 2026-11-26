"""Offline controls for duplicate metadata and accidental indexing exclusions."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from search_metadata_contract import inspect_metadata


class MetaParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.meta = []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            self.meta.append(dict(attrs))


def inspect(html, expected=False):
    return inspect_metadata(MetaParser(html).meta, expected_noindex=expected)


class SearchMetadataControls(unittest.TestCase):
    def test_ordinary_indexable_metadata_is_unchanged(self):
        values, noindex, errors = inspect('<meta name="description" content="Nolan Kido &amp; AI"><meta property="og:title" content="Practical AI">')
        self.assertEqual(values, {'description': 'Nolan Kido & AI', 'og:title': 'Practical AI'})
        self.assertFalse(noindex)
        self.assertEqual(errors, [])

    def test_explicit_utility_noindex_is_preserved(self):
        for value in ('noindex, follow', 'NOINDEX , follow', 'follow, noindex', 'noindex follow'):
            with self.subTest(value=value):
                _, noindex, errors = inspect('<meta name="robots" content="' + value + '">', True)
                self.assertTrue(noindex)
                self.assertEqual(errors, [])

    def test_duplicate_robots_cannot_hide_noindex(self):
        for html in ('<meta name="robots" content="noindex"><meta name="robots" content="index,follow">',
                     '<meta name="robots" content="index,follow"><meta name="ROBOTS" content="noindex">'):
            with self.subTest(html=html):
                _, noindex, errors = inspect(html)
                self.assertTrue(noindex)
                self.assertIn('Duplicate search metadata (robots)', errors)
                self.assertTrue(any('crawl policy' in error for error in errors))

    def test_crawler_specific_exclusions_cannot_pass(self):
        for name in ('googlebot', 'bingbot', 'Googlebot-News', 'OAI-SearchBot'):
            for value in ('nofollow, NOINDEX', 'follow noindex', 'none'):
                with self.subTest(name=name, value=value):
                    _, noindex, errors = inspect(f'<meta content="{value}" name="{name}">')
                    self.assertFalse(noindex)
                    self.assertEqual(errors, ['Robots directive disagrees with explicit crawl policy (' + name.lower() + ')'])

    def test_global_none_blocks_public_indexability(self):
        _, _, errors = inspect('<meta name="robots" content="none">')
        self.assertTrue(errors)
        self.assertIn('crawl policy', errors[0])

    def test_utility_requires_global_noindex(self):
        for html in ('', '<meta name="robots" content="index,follow">',
                     '<meta name="googlebot" content="noindex">'):
            with self.subTest(html=html):
                _, noindex, errors = inspect(html, True)
                self.assertFalse(noindex)
                self.assertEqual(errors, ['Robots directive disagrees with explicit crawl policy'])

    def test_preview_none_is_not_a_page_indexing_exclusion(self):
        for value in ('max-image-preview:none', 'max-image-preview: none, index, follow', 'max-snippet:0, noarchive'):
            with self.subTest(value=value):
                self.assertEqual(inspect(f'<meta name="robots" content="{value}">')[2], [])

    def test_every_reviewed_singleton_rejects_duplicate_even_when_equal(self):
        for name in ('description', 'og:url', 'og:title', 'og:description', 'og:image',
                     'twitter:image', 'twitter:title', 'twitter:description'):
            kind = 'property' if name.startswith('og:') else 'name'
            html = f'<meta {kind}="{name}" content="same"><meta {kind}="{name.upper()}" content="same">'
            with self.subTest(name=name):
                self.assertEqual(inspect(html)[2], ['Duplicate search metadata (' + name + ')'])

    def test_multiple_distinct_image_attributes_are_not_duplicates(self):
        html = ('<meta property="og:image" content="picture.png">'
                '<meta property="og:image:alt" content="Topic graphic">'
                '<meta property="og:image:width" content="1200">'
                '<meta name="twitter:image" content="picture.png">')
        self.assertEqual(inspect(html)[2], [])

    def test_input_is_not_mutated(self):
        meta = [{'name': 'ROBOTS', 'content': 'noindex, follow'}]
        inspect_metadata(meta, expected_noindex=True)
        self.assertEqual(meta, [{'name': 'ROBOTS', 'content': 'noindex, follow'}])


if __name__ == '__main__':
    unittest.main()
