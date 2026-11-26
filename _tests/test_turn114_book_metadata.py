"""Standalone discovery metadata and mutation controls; no network requests."""
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import book_metadata

TITLE = 'AI Works, Human Decides: Book by Nolan Kido'
HEADING = 'AI Works, Human Decides'
DESCRIPTION = "Explore Nolan Kido's book AI Works, Human Decides, on delegating work, checking evidence and keeping responsibility. Try a free decision-review exercise."
URL = 'https://nolankido.com/books/ai-works-human-decides/'


def schema():
    return {'name': TITLE, 'description': DESCRIPTION, 'url': URL,
            'mainEntity': {'name': HEADING}}


def fixture():
    fields = [('name', 'description', DESCRIPTION), ('property', 'og:title', TITLE),
              ('property', 'og:description', DESCRIPTION), ('property', 'og:url', URL),
              ('name', 'twitter:title', TITLE), ('name', 'twitter:description', DESCRIPTION)]
    meta = ''.join(f'<meta content="{escape(value, quote=True)}" {kind}="{name}">' for kind, name, value in fields)
    return (f'<html><head><title>{TITLE}</title><link href="{URL}" rel="canonical">'
            + meta + '</head><body><h1>AI Works, <cite>Human Decides</cite></h1></body></html>')


def verify(document, record):
    return book_metadata.validate(document, title=TITLE, heading=HEADING,
                                  description=DESCRIPTION, url=URL, schema=record)


class BookMetadataTests(unittest.TestCase):
    def test_correct_escaped_and_reordered_attributes(self):
        verify(fixture(), schema())

    def test_title_and_heading_mutations(self):
        for old, new in (('<title>', '<title>Wrong '), ('<cite>Human Decides', '<cite>Other book')):
            with self.subTest(new=new), self.assertRaisesRegex(ValueError, 'title or visible heading'):
                verify(fixture().replace(old, new, 1), schema())

    def test_each_search_and_share_field_required(self):
        for field in ('description', 'og:title', 'og:description', 'og:url', 'twitter:title', 'twitter:description'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'search/share metadata mismatch'):
                verify(fixture().replace(f'="{field}"', '="unrelated"', 1), schema())

    def test_wrong_share_description_cannot_pass(self):
        old = f'content="{escape(DESCRIPTION, quote=True)}" property="og:description"'
        with self.assertRaisesRegex(ValueError, 'og:description'):
            verify(fixture().replace(old, 'content="Unrelated summary" property="og:description"'), schema())

    def test_duplicate_metadata_and_canonical_fail_even_if_equal(self):
        for duplicate in (f'<meta name="description" content="{escape(DESCRIPTION, quote=True)}">',
                          f'<link rel="canonical" href="{URL}">',
                          f'<title>{TITLE}</title>'):
            with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                verify(fixture().replace('</head>', duplicate + '</head>'), schema())

    def test_noindex_variations_fail(self):
        for name, value in (('robots', 'follow, NOINDEX'), ('googlebot', 'none'),
                            ('bingbot', 'nofollow noindex'), ('robots', 'noindex,follow')):
            with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, 'remain indexable'):
                verify(fixture().replace('</head>', f'<meta content="{value}" name="{name}"></head>'), schema())
        verify(fixture().replace('</head>', '<meta name="robots" content="index,follow"></head>'), schema())

    def test_duplicate_normalized_robots_fields_fail(self):
        for name in ('robots', 'googlebot', 'Googlebot-News', 'OAI-SearchBot'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Duplicate search metadata'):
                meta = (f'<meta name="{name}" content="index,follow">'
                        f'<meta name=" {name.upper()} " content="index,follow">')
                verify(fixture().replace('</head>', meta + '</head>'), schema())

    def test_duplicate_sharing_images_fail(self):
        for kind, name in (('property', 'og:image'), ('name', 'twitter:image')):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Duplicate search metadata'):
                meta = (f'<meta {kind}="{name}" content="first.png">'
                        f'<meta {kind}="{name.upper()}" content="second.png">')
                verify(fixture().replace('</head>', meta + '</head>'), schema())

    def test_normalized_search_field_duplicates_fail(self):
        for field in ('description', 'twitter:title', 'og:description'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Duplicate search metadata'):
                meta = f'<meta name=" {field.upper()} " content="Different text">'
                verify(fixture().replace('</head>', meta + '</head>'), schema())

    def test_preview_none_does_not_block_indexability(self):
        for name in ('robots', 'googlebot', 'OAI-SearchBot'):
            for value in ('max-image-preview: none, index, follow', 'max-image-preview:none', 'max-snippet: 0'):
                with self.subTest(name=name, value=value):
                    meta = f'<meta name="{name}" content="{value}">'
                    verify(fixture().replace('</head>', meta + '</head>'), schema())

    def test_normalized_crawler_exclusions_still_fail(self):
        for name in (' ROBOTS ', ' Googlebot-News ', ' BingBot ', ' OAI-SearchBot '):
            for value in ('none', 'follow, NOINDEX', 'max-image-preview: none, noindex'):
                with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, 'remain indexable'):
                    meta = f'<meta name="{name}" content="{value}">'
                    verify(fixture().replace('</head>', meta + '</head>'), schema())

    def test_schema_identity_mismatch_fails(self):
        for key in ('name', 'description', 'url', 'mainEntity'):
            record = deepcopy(schema())
            record[key] = 'wrong'
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'structured identity'):
                verify(fixture(), record)
        record = schema()
        record['mainEntity']['name'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'structured identity'):
            verify(fixture(), record)

    def test_current_third_book_page(self):
        page = (ROOT / 'books/ai-works-human-decides/index.html').read_text(encoding='utf-8')
        raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
        self.assertIsNotNone(raw)
        verify(page, json.loads(raw.group(1)))


if __name__ == '__main__':
    unittest.main()
