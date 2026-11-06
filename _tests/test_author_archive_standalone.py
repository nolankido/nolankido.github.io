"""The complete author archive includes exactly the verified standalone Articles."""
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import author_archive
import build
import local_laptop_case
import poker_episode
import poker_standoff_episode
import reply_audit_case

ORIGIN = 'https://nolankido.com'
PERSON = ORIGIN + '/about/#nolan-kido'
MANUAL = (
    (local_laptop_case, 'local-ai-gaming-laptop', '2026-11-02', 'practical-ai', 'Practical guide'),
    (reply_audit_case, 'review-reply-evidence-audit', '2026-11-03', 'practical-ai', 'Recorded case'),
    (poker_episode, 'poker-portland-meadows-ep1', '2026-11-02', 'poker', 'First-person video companion'),
    (poker_standoff_episode, 'poker-portland-meadows-standoff', '2026-11-04', 'poker', 'First-person video companion'),
)


def schema_from(document):
    matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', document, re.S)
    if len(matches) != 1:
        raise AssertionError('Expected one public schema record')
    return json.loads(matches[0])


class PublicArticle(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.headlines = []
        self.descriptions = []
        self.canonicals = []
        self.in_h1 = False
        self.feed(document)
        self.schema = schema_from(document)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.headlines.append('')
            self.in_h1 = True
        if tag == 'meta' and attrs.get('name') == 'description':
            self.descriptions.append(attrs.get('content'))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))

    def handle_data(self, data):
        if self.in_h1:
            self.headlines[-1] += data

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False


class VisibleArchive(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.groups = []
        self.group = None
        self.row = None
        self.capture = None
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'details' and 'archive-group' in classes:
            self.group = attrs['id'].removeprefix('archive-')
            self.groups.append(self.group)
        if tag == 'li' and 'data-archive-id' in attrs:
            self.row = {'id': attrs['data-archive-id'], 'group': self.group,
                        'title': '', 'description': '', 'meta': '', 'note': '', 'dates': []}
        if self.row is not None:
            if tag == 'a':
                self.row['path'] = attrs.get('href')
                self.capture = 'title'
            if tag == 'p':
                self.capture = ('description' if 'archive-description' in classes else
                                'meta' if 'archive-meta' in classes else
                                'note' if 'archive-source-note' in classes else None)
            if tag == 'time':
                self.row['dates'].append(attrs.get('datetime'))

    def handle_data(self, data):
        if self.row is not None and self.capture:
            self.row[self.capture] += data

    def handle_endtag(self, tag):
        if tag in {'a', 'p'}:
            self.capture = None
        if tag == 'li' and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        if tag == 'details':
            self.group = None


def copy_publication(root, registry):
    paths = [registry.SOURCE, registry.OUTPUT]
    if hasattr(registry, 'TOOL'):
        paths.extend([registry.TOOL, Path('technology/index.html')])
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)


def change_schema(document, keys, value):
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', document, re.S)
    schema = json.loads(match[1])
    target = schema
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    return document[:match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + document[match.end(1):]


class StandaloneAuthorArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.manifest_articles = [
            page for page in cls.pages
            if schema_from(cls.outputs[build.output_path(page['path'])]).get('@type') == 'Article'
        ]
        cls.expected_count = len(cls.manifest_articles) + len(MANUAL)
        cls.manifest = author_archive.records(cls.pages)
        cls.complete = author_archive.records(cls.pages, ROOT)
        cls.notes = cls.outputs[Path('notes/index.html')]
        cls.about = cls.outputs[Path('about/index.html')]
        cls.visible = VisibleArchive(cls.notes)

    def test_complete_archive_adds_exactly_four_existing_articles(self):
        actual_manifest = {page['path'] for page in self.manifest_articles}
        manual_paths = {registry.ROUTE for registry, *_ in MANUAL}
        self.assertEqual(len(self.manifest), len(actual_manifest))
        self.assertEqual({entry['path'] for entry in self.manifest}, actual_manifest)
        self.assertEqual({entry['path'] for entry in self.complete}, actual_manifest | manual_paths)
        self.assertEqual({entry['path'] for entry in self.complete} - actual_manifest, manual_paths)
        self.assertEqual(len(self.complete), self.expected_count)
        self.assertEqual(len({entry['id'] for entry in self.complete}), self.expected_count)
        complete_by_path = {entry['path']: entry for entry in self.complete}
        for existing in self.manifest:
            self.assertEqual(complete_by_path[existing['path']], existing)
        self.assertEqual(self.notes, (ROOT / 'notes/index.html').read_text(encoding='utf-8'))
        self.assertEqual(self.about, (ROOT / 'about/index.html').read_text(encoding='utf-8'))

    def test_visible_archive_about_count_and_itemlist_describe_the_same_collection(self):
        rows = self.visible.rows
        self.assertEqual(len(rows), self.expected_count)
        self.assertEqual(len({row['path'] for row in rows}), self.expected_count)
        self.assertEqual({row['path'] for row in rows}, {entry['path'] for entry in self.complete})
        self.assertEqual(self.visible.groups, ['practical-ai', 'living-well', 'poker', 'general-essays'])
        expected_groups = Counter(author_archive.group(page) for page in self.manifest_articles)
        expected_groups.update(group for _, _, _, group, _ in MANUAL)
        self.assertEqual(Counter(row['group'] for row in rows), expected_groups)
        schema = schema_from(self.notes)
        listing = schema['mainEntity']
        self.assertEqual(listing['@type'], 'ItemList')
        self.assertEqual(listing['numberOfItems'], len(rows))
        self.assertEqual([item['position'] for item in listing['itemListElement']],
                         list(range(1, self.expected_count + 1)))
        self.assertEqual([(item['url'], item['name']) for item in listing['itemListElement']],
                         [(ORIGIN + row['path'], row['title']) for row in rows])
        self.assertEqual(schema['creator']['@id'], PERSON)
        about_archive = re.findall(re.escape(author_archive.BEGIN) + '(.*?)' + re.escape(author_archive.END), self.about, re.S)
        self.assertEqual(len(about_archive), 1)
        self.assertRegex(about_archive[0], rf'\b{self.expected_count} published pieces\b')
        self.assertIn('href="/notes/#all-writing"', about_archive[0])

    def test_manual_rows_keep_public_identity_descriptions_dates_and_material_labels(self):
        entries = {entry['path']: entry for entry in self.complete}
        rows = {row['path']: row for row in self.visible.rows}
        for registry, identifier, published, group, label in MANUAL:
            with self.subTest(path=registry.ROUTE):
                document = PublicArticle((ROOT / registry.OUTPUT).read_text(encoding='utf-8'))
                record, row = entries[registry.ROUTE], rows[registry.ROUTE]
                self.assertEqual(record['id'], identifier)
                self.assertEqual(record['title'], document.headlines[0])
                self.assertEqual(document.headlines, [document.schema['headline']])
                self.assertEqual(document.canonicals, [ORIGIN + registry.ROUTE])
                self.assertEqual(document.schema['@type'], 'Article')
                self.assertEqual(document.schema['@id'], ORIGIN + registry.ROUTE + '#article')
                self.assertEqual(document.schema['author']['@id'], PERSON)
                self.assertEqual(document.descriptions, [record['description']])
                self.assertEqual(document.schema['description'], record['description'])
                self.assertEqual(record['date'], published)
                self.assertEqual(document.schema['datePublished'], published)
                self.assertEqual(row['dates'], [published])
                self.assertEqual(row['group'], group)
                self.assertEqual(author_archive.label(record), label)
                self.assertTrue(row['meta'].startswith(label + ' · Published '))
                self.assertEqual(row['title'], record['title'])
                self.assertEqual(row['description'], record['description'])
                if group == 'poker':
                    self.assertTrue(record.get('archive_note'))
                    self.assertEqual(row['note'], record['archive_note'])

    def test_profile_utilities_and_noindex_records_do_not_enter_the_archive(self):
        private = {'id': 'private-article', 'path': '/notes/private-article/', 'note': True,
                   'date': '2026-11-05', 'title': 'Private draft', 'description': 'Not a public article.', 'noindex': True}
        utility = {'id': 'dated-utility', 'path': '/dated-utility/', 'date': '2026-11-05',
                   'title': 'A utility', 'description': 'A date alone does not make an article.'}
        entries = author_archive.records(self.pages + [private, utility], ROOT)
        self.assertEqual(entries, self.complete)
        excluded = {'/poker/nolan-kido/', '/about/', '/bio/', '/find/', '/contact/',
                    '/resources/', '/technology/', private['path'], utility['path']}
        self.assertFalse(excluded & {entry['path'] for entry in entries})
        noindex = {page['path'] for page in self.pages if page.get('noindex')}
        self.assertFalse(noindex & {row['path'] for row in self.visible.rows})

    def test_optional_root_preserves_manifest_only_fixtures_and_never_fabricates_missing_publications(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(author_archive.records(self.pages, root), self.manifest)
            self.assertEqual(author_archive.records(self.pages, None), self.manifest)
        for registry, *_ in MANUAL:
            with self.subTest(only_publication=registry.ROUTE), TemporaryDirectory() as folder:
                root = Path(folder)
                copy_publication(root, registry)
                records = author_archive.records(self.pages, root)
                self.assertEqual(len(records), len(self.manifest) + 1)
                self.assertEqual({entry['path'] for entry in records} - {entry['path'] for entry in self.manifest}, {registry.ROUTE})

    def test_records_body_and_schema_do_not_mutate_inputs(self):
        pages = deepcopy(self.pages)
        original = deepcopy(pages)
        notes_page = next(page for page in pages if page['id'] == 'notes')
        source = (ROOT / '_source/notes.html').read_text(encoding='utf-8')
        base_schema = {'@type': 'CollectionPage', 'name': 'Writing', 'url': ORIGIN + '/notes/'}
        original_schema = deepcopy(base_schema)
        records = author_archive.records(pages, ROOT)
        body = author_archive.body(notes_page, source, pages, ROOT)
        schema = author_archive.schema(notes_page, base_schema, pages, {'url': ORIGIN, 'name': 'Nolan Kido'}, ROOT)
        self.assertEqual(len(VisibleArchive(body).rows), self.expected_count)
        self.assertEqual(schema['mainEntity']['numberOfItems'], self.expected_count)
        records[0]['title'] = 'Changed returned copy'
        schema['name'] = 'Changed returned schema'
        self.assertEqual(pages, original)
        self.assertEqual(base_schema, original_schema)

    def test_duplicate_article_routes_and_ids_are_rejected(self):
        original = self.manifest[0]
        duplicate_route = dict(original, id='different-id-same-route')
        duplicate_id = dict(original, path='/notes/different-route-same-id/')
        for duplicate in [duplicate_route, duplicate_id]:
            with self.subTest(duplicate=duplicate['id']):
                with self.assertRaises(ValueError):
                    author_archive.records(self.pages + [duplicate], ROOT)
        for registry, identifier, *_ in MANUAL:
            for collision in [dict(id='utility-owning-manual-route', path=registry.ROUTE),
                              dict(id=identifier, path='/utility-owning-manual-id/', noindex=True)]:
                with self.subTest(publication=registry.ROUTE, collision=collision):
                    with self.assertRaises(ValueError):
                        author_archive.records(self.pages + [collision], ROOT)

    def test_incomplete_or_inconsistent_publications_fail_before_archive_inclusion(self):
        for registry, *_ in MANUAL:
            with self.subTest(publication=registry.ROUTE), TemporaryDirectory() as folder:
                root = Path(folder)
                copy_publication(root, registry)
                source = (root / registry.SOURCE).read_text(encoding='utf-8')
                html = (root / registry.OUTPUT).read_text(encoding='utf-8')
                originals = {registry.SOURCE: source, registry.OUTPUT: html}
                mutations = [
                    ('missing source', registry.SOURCE, None),
                    ('missing HTML', registry.OUTPUT, None),
                    ('unpublished source edit', registry.SOURCE, source + '\n<p>Unpublished change.</p>\n'),
                    ('missing source body', registry.OUTPUT, html.replace(source, '<p>Removed source body.</p>', 1)),
                    ('wrong canonical', registry.OUTPUT, html.replace('rel="canonical" href="' + registry.URL + '"', 'rel="canonical" href="https://invalid.example/"', 1)),
                    ('foreign author', registry.OUTPUT, change_schema(html, ['author', '@id'], 'https://invalid.example/#author')),
                    ('not an Article', registry.OUTPUT, change_schema(html, ['@type'], 'ProfilePage')),
                    ('changed H1', registry.OUTPUT, re.sub(r'(<h1\b[^>]*>).*?(</h1>)', r'\1Unreviewed headline\2', html, count=1, flags=re.S)),
                    ('changed schema headline', registry.OUTPUT, change_schema(html, ['headline'], 'Unreviewed headline')),
                    ('changed description', registry.OUTPUT, re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="An unreviewed description.">', html, count=1)),
                    ('noindex publication', registry.OUTPUT, html.replace('</head>', '<meta name="robots" content="noindex"></head>', 1)),
                ]
                for name, path, value in mutations:
                    with self.subTest(publication=registry.ROUTE, mutation=name):
                        self.assertNotEqual(value, originals[path])
                        target = root / path
                        if value is None:
                            target.unlink()
                        else:
                            target.write_text(value, encoding='utf-8')
                        try:
                            with self.assertRaises(ValueError):
                                author_archive.records(self.pages, root)
                        finally:
                            target.write_text(originals[path], encoding='utf-8')


if __name__ == '__main__':
    unittest.main()
