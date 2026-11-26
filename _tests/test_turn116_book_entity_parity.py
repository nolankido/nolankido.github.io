"""Canonical work identity parity; synthetic negative controls and real-site checks."""
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import book_pages as books


def schema(html):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))


def replace_schema(html, data):
    match = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', html, re.S)
    return html[:match.start(2)] + json.dumps(data, ensure_ascii=False) + html[match.end(2):]


def render(title, heading, desc, url, data, body):
    # Use the actual canonical page and shared website/publisher contract.
    data = deepcopy(data)
    data['@id'] = url + '#webpage'
    data['isPartOf'] = {'@type': 'WebSite', '@id': books.ORIGIN + '/#website',
                        'url': books.ORIGIN + '/',
                        'publisher': {'@type': 'Person', '@id': books.PERSON,
                                      'url': books.ORIGIN + '/about/'}}
    fields = [('name', 'description', desc), ('property', 'og:title', title),
              ('property', 'og:description', desc), ('property', 'og:url', url),
              ('name', 'twitter:title', title), ('name', 'twitter:description', desc)]
    meta = ''.join(f'<meta {kind}="{name}" content="{escape(value, quote=True)}">'
                   for kind, name, value in fields)
    return ('<!doctype html><html><head><title>' + escape(title) + '</title>'
            + '<link rel="canonical" href="' + url + '">' + meta
            + '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False)
            + '</script></head><body><main><h1>' + escape(heading) + '</h1>'
            + body + '</main></body></html>')


class EntityFixtureTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        links = '<a href="/books/">Catalog</a>' + ''.join(
            '<a href="' + books.route(item) + '">Book</a>' for item in books.BOOKS)
        for path in ('index.html', 'about/index.html', 'bio/index.html', 'creative/index.html'):
            self.write(path, links)
        for item in books.BOOKS:
            url = books.ORIGIN + books.route(item)
            data = {'@type': 'WebPage', 'url': url, 'name': item['seo'],
                    'description': item['description'], 'dateModified': item['modified'],
                    'about': {'@id': url + '#book'}, 'mainEntity': books.book_entity(item)}
            html = render(item['seo'], item['title'], item['description'], url, data,
                          '<a href="/books/">Catalog</a>')
            self.book_pair(item, html)
        data = {'@type': 'CollectionPage', 'url': books.HUB_URL, '@id': books.HUB_URL + '#webpage',
                'name': books.HUB_TITLE, 'description': books.HUB_DESCRIPTION, 'dateModified': books.UPDATED,
                'about': {'@id': books.PERSON}, 'mainEntity': {'@type': 'ItemList',
                    '@id': books.HUB_URL + '#book-list', 'name': 'Books by Nolan Kido',
                    'itemListElement': books.entity_list()}}
        body = '<section id="book-ai-works-human-decides">' + books.THIRD_BOOK['description'] + '</section>'
        body += ''.join('<a href="' + books.route(item) + '">Book</a>' for item in books.BOOKS)
        self.hub = render(books.HUB_TITLE, 'Books by Nolan Kido', books.HUB_DESCRIPTION,
                          books.HUB_URL, data, body)
        self.hub_pair(self.hub)

    def write(self, path, html):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')

    def book_pair(self, item, html):
        self.write('_source/books/' + item['slug'] + '.html', html)
        self.write(books.route(item).strip('/') + '/index.html', html)

    def hub_pair(self, html):
        self.write(books.HUB_SOURCE, html)
        self.write(books.HUB_OUTPUT, html)

    def test_all_three_entities_register_and_keep_sitemap_and_find_routes(self):
        self.assertEqual(books.published(self.root), books.BOOKS)
        self.assertEqual(books.hub_record(self.root)['url'], books.HUB_URL)
        index = ET.Element('urlset')
        books.add_to_sitemap(index, self.root)
        self.assertEqual([node.findtext('loc') for node in index],
                         [books.HUB_URL] + [books.ORIGIN + books.route(item) for item in books.BOOKS])
        self.assertEqual({row['path'] for row in books.find_entries(self.root)},
                         {books.HUB_ROUTE, *(books.route(item) for item in books.BOOKS)})

    def test_each_book_page_rejects_matching_source_and_output_with_wrong_description(self):
        for item in books.BOOKS:
            with self.subTest(slug=item['slug']):
                path = self.root / books.route(item).strip('/') / 'index.html'
                original = path.read_text(encoding='utf-8')
                data = schema(original)
                data['mainEntity']['description'] = 'Unreviewed claim'
                self.book_pair(item, replace_schema(original, data))
                with self.assertRaisesRegex(ValueError, 'differs from reviewed identity'):
                    books.published(self.root)
                self.book_pair(item, original)

    def test_book_and_catalog_registries_reject_disconnected_page_graphs(self):
        for item in books.BOOKS:
            path = self.root / books.route(item).strip('/') / 'index.html'
            original = path.read_text(encoding='utf-8')
            for field in ('@id', 'isPartOf'):
                with self.subTest(slug=item['slug'], field=field):
                    data = schema(original)
                    del data[field]
                    self.book_pair(item, replace_schema(original, data))
                    with self.assertRaisesRegex(ValueError, 'canonical Web(Page|Site)'):
                        books.published(self.root)
                    self.book_pair(item, original)
        data = schema(self.hub)
        data['isPartOf']['publisher']['@id'] = 'https://example.invalid/#person'
        self.hub_pair(replace_schema(self.hub, data))
        with self.assertRaisesRegex(ValueError, 'Person publisher'):
            books.hub_record(self.root)
        self.hub_pair(self.hub)
        self.assertEqual(books.hub_record(self.root)['url'], books.HUB_URL)

    def test_catalog_rejects_omitted_fields_and_wrong_descriptions_for_every_work(self):
        for position in range(len(books.BOOKS)):
            for key in ('description', 'mainEntityOfPage'):
                with self.subTest(position=position, key=key):
                    data = schema(self.hub)
                    del data['mainEntity']['itemListElement'][position]['item'][key]
                    self.hub_pair(replace_schema(self.hub, data))
                    with self.assertRaises(ValueError):
                        books.hub_record(self.root)
                    self.hub_pair(self.hub)

    def test_extra_retail_fields_fail_even_when_value_is_null(self):
        item = books.BOOKS[0]
        original = (self.root / books.route(item).strip('/') / 'index.html').read_text(encoding='utf-8')
        for field in ('isbn', 'offers', 'datePublished', 'bookFormat', 'aggregateRating', 'sameAs'):
            with self.subTest(field=field):
                data = schema(original)
                data['mainEntity'][field] = None
                self.book_pair(item, replace_schema(original, data))
                with self.assertRaises(ValueError):
                    books.published(self.root)
        self.book_pair(item, original)

    def test_graph_checks_every_work_while_ignoring_other_entity_types(self):
        works = [books.book_entity(item) for item in books.BOOKS]
        person = {'@type': 'Person', '@id': books.PERSON}
        books.validate_identity_graph({'@graph': [person, *reversed(works)]})
        for bad in ([], works[:-1], [*works, works[0]], [works[0], works[0], works[2]]):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'all reviewed book entities'):
                books.validate_identity_graph({'@graph': bad})
        for i in range(len(works)):
            bad = deepcopy(works)
            bad[i]['description'] = 'Unreviewed claim'
            with self.subTest(position=i), self.assertRaises(ValueError):
                books.validate_identity_graph({'@graph': bad})
        with self.assertRaisesRegex(ValueError, 'graph list'):
            books.validate_identity_graph({'@graph': 'wrong'})

    def test_entities_are_fresh_records_with_shared_identity_and_known_subtitle(self):
        records = books.entity_list()
        self.assertEqual(len(records), 3)
        for entry, item in zip(records, books.BOOKS):
            record = entry['item']
            self.assertEqual(record['author']['@id'], books.PERSON)
            self.assertEqual(record['@id'], books.ORIGIN + books.route(item) + '#book')
        self.assertIn('How Small Business Owners Can Test AI', records[0]['item']['alternateName'])
        records[0]['item']['author']['@id'] = 'wrong'
        self.assertEqual(books.entity_list()[0]['item']['author']['@id'], books.PERSON)
        self.assertEqual(books.book_entity(books.BOOKS[-1]), books.THIRD_BOOK)


class PublishedEntityTests(unittest.TestCase):
    def test_every_book_identity_matches_all_four_public_surfaces(self):
        expected = books.entity_list()
        for filename in ('books/index.html', 'creative/index.html'):
            data = schema((ROOT / filename).read_text(encoding='utf-8'))
            self.assertEqual(data['mainEntity']['itemListElement'], expected, filename)
        for item in books.BOOKS:
            page = ROOT / books.route(item).strip('/') / 'index.html'
            self.assertEqual(schema(page.read_text(encoding='utf-8'))['mainEntity'], books.book_entity(item))
        source = json.loads((ROOT / '_source/person-schema.jsonld').read_text(encoding='utf-8'))
        public = json.loads((ROOT / 'assets/nolan-kido-identity.jsonld').read_text(encoding='utf-8'))
        self.assertEqual(source, public)
        books.validate_identity_graph(source)
        books.validate_identity_graph(public)
        self.assertIsNotNone(books.hub_record(ROOT))

    def test_public_identity_graph_is_registered_for_exact_live_verification(self):
        import check_live
        path = 'assets/nolan-kido-identity.jsonld'
        self.assertEqual(check_live.targets(ROOT)['/' + path],
                         (200, (ROOT / path).read_bytes()))


if __name__ == '__main__':
    unittest.main()
