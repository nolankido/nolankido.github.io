"""Canonical WebPage and publisher graph contracts for standalone book discovery."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from book_metadata import validate_page_identity

ORIGIN = 'https://nolankido.com'
PERSON = ORIGIN + '/about/#nolan-kido'
ROUTES = ('/books/', '/books/one-workflow-at-a-time/',
          '/books/how-to-play-no-limit-texas-holdem/', '/books/ai-works-human-decides/')


def fixture(route):
    return {'@id': ORIGIN + route + '#webpage',
            'isPartOf': {'@type': 'WebSite', '@id': ORIGIN + '/#website',
                         'url': ORIGIN + '/',
                         'publisher': {'@type': 'Person', '@id': PERSON,
                                       'url': ORIGIN + '/about/'}}}


def verify(record, route):
    return validate_page_identity(record, url=ORIGIN + route, origin=ORIGIN, author_id=PERSON)


class BookWebpageIdentityTests(unittest.TestCase):
    def test_all_registered_routes_pass_without_mutation(self):
        for route in ROUTES:
            with self.subTest(route=route):
                record = fixture(route)
                before = deepcopy(record)
                verify(record, route)
                self.assertEqual(record, before)

    def test_missing_page_identity_is_rejected(self):
        for route in ROUTES:
            record = fixture(route)
            del record['@id']
            with self.subTest(route=route), self.assertRaisesRegex(ValueError, 'canonical WebPage identity'):
                verify(record, route)

    def test_book_or_other_page_id_cannot_replace_webpage_identity(self):
        for route in ROUTES:
            for wrong in (ORIGIN + route + '#book', ORIGIN + route,
                          'https://example.invalid/#webpage', ORIGIN + '/about/#webpage', None):
                record = fixture(route)
                record['@id'] = wrong
                with self.subTest(route=route, wrong=wrong), self.assertRaisesRegex(ValueError, 'canonical WebPage identity'):
                    verify(record, route)

    def test_missing_or_malformed_website_is_rejected(self):
        for value in (None, [], 'wrong', {}):
            record = fixture(ROUTES[0])
            record['isPartOf'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'canonical WebSite'):
                verify(record, ROUTES[0])

    def test_website_type_id_and_url_are_all_required(self):
        for field in ('@type', '@id', 'url'):
            for value in (None, 'https://example.invalid/'):
                record = fixture(ROUTES[1])
                record['isPartOf'][field] = value
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, 'canonical WebSite'):
                    verify(record, ROUTES[1])

    def test_missing_or_malformed_publisher_is_rejected(self):
        for value in (None, [], 'wrong', {}):
            record = fixture(ROUTES[2])
            record['isPartOf']['publisher'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Person publisher'):
                verify(record, ROUTES[2])

    def test_publisher_type_id_and_url_are_all_required(self):
        for field in ('@type', '@id', 'url'):
            for value in (None, 'https://example.invalid/'):
                record = fixture(ROUTES[3])
                record['isPartOf']['publisher'][field] = value
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, 'Person publisher'):
                    verify(record, ROUTES[3])

    def test_independently_reviewed_optional_name_is_not_rewritten(self):
        record = fixture(ROUTES[0])
        record['isPartOf']['name'] = 'Nolan Kido'
        record['isPartOf']['publisher']['name'] = 'Nolan Kido'
        before = json.dumps(record)
        verify(record, ROUTES[0])
        self.assertEqual(json.dumps(record), before)


if __name__ == '__main__':
    unittest.main()
