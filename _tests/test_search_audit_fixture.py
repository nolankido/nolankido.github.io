"""Regression controls for the shared minimal search-audit fixture."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '_scripts'))
import tenbb_companion
from search_audit_fixture import complete_audit_fixture


class SearchAuditFixtureTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.source = Path(temp.name) / 'source'
        self.target = Path(temp.name) / 'target'
        self.origin = tenbb_companion.ORIGIN
        self.playbook_url = self.origin + tenbb_companion.ROUTE
        self.paths = (tenbb_companion.OUTPUT, tenbb_companion.CODE, tenbb_companion.WORKSHEET)
        schema = {'@type': 'Article', 'url': self.playbook_url,
                  'author': {'@id': self.origin + '/about/#nolan-kido'},
                  'datePublished': '2026-11-19', 'dateModified': '2026-11-21'}
        html = (f'<link rel="canonical" href="{self.playbook_url}">'
                '<h1 class="page-title">The 10 Big Blind Tournament Playbook</h1>'
                '<meta property="article:published_time" content="2026-11-19">'
                '<meta property="article:modified_time" content="2026-11-21">'
                '<p id="icm-reproduce"></p>'
                f'<a href="/{tenbb_companion.CODE}">Checker</a>'
                f'<a href="/{tenbb_companion.WORKSHEET}">Worksheet</a>'
                '<script type="application/ld+json">' + json.dumps(schema) + '</script>')
        for relative, content in zip(self.paths, (html, '# fixture checker\n', 'fixture worksheet\n')):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')

    def test_copies_all_three_assets_and_registers_exactly_once(self):
        urls = [self.origin + '/', self.origin + '/about/']
        complete_audit_fixture(self.target, self.source, urls)
        self.assertEqual(urls, [self.origin + '/', self.origin + '/about/'])
        for relative in self.paths:
            self.assertEqual((self.target / relative).read_bytes(), (self.source / relative).read_bytes())
        self.assertEqual(tenbb_companion.record(self.target), tenbb_companion.record(self.source))
        entries = ET.parse(self.target / 'sitemap.xml').getroot()
        self.assertEqual([e.findtext('{*}loc') for e in entries], urls + [self.playbook_url])
        self.assertEqual(entries[-1].findtext('{*}lastmod'), '2026-11-21')

    def test_incomplete_source_cannot_create_a_passing_fixture(self):
        for relative in self.paths:
            with self.subTest(relative=relative):
                path = self.source / relative
                original = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaisesRegex(ValueError, 'missing'):
                        complete_audit_fixture(self.target, self.source, [self.origin + '/'])
                    self.assertFalse(self.target.exists())
                finally:
                    path.write_bytes(original)

    def test_duplicate_routes_are_refused(self):
        for urls in ([self.origin + '/', self.origin + '/'], [self.playbook_url]):
            with self.subTest(urls=urls), self.assertRaisesRegex(ValueError, 'Duplicate canonical'):
                complete_audit_fixture(self.target, self.source, urls)
        self.assertFalse(self.target.exists())

    def test_wrong_playbook_identity_is_refused(self):
        page = self.source / tenbb_companion.OUTPUT
        page.write_text(page.read_text(encoding='utf-8').replace('id="icm-reproduce"', 'id="wrong"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'reproducibility heading'):
            complete_audit_fixture(self.target, self.source, [])
        self.assertFalse(self.target.exists())

    def test_source_overwrite_is_refused(self):
        before = [(self.source / relative).read_bytes() for relative in self.paths]
        with self.assertRaisesRegex(ValueError, 'must not overwrite'):
            complete_audit_fixture(self.source, self.source, [])
        self.assertEqual([(self.source / relative).read_bytes() for relative in self.paths], before)
        self.assertFalse((self.source / 'sitemap.xml').exists())


if __name__ == '__main__':
    unittest.main()
