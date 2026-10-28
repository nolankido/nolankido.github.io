"""Verified public-work links do not promote the separate professional profile."""
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_search


class IdentityJsonLdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.data = json.loads(cls.outputs[Path('assets/nolan-kido-identity.jsonld')])
        cls.graph = {item['@type']: item for item in cls.data['@graph']}

    def test_former_coo_does_not_imply_current_employment(self):
        person = self.graph['Person']
        self.assertIn('Former Chief Operating Officer of Hawaii Dental Clinic and Affiliates', person['description'])
        self.assertNotIn('CEO', json.dumps(self.data))
        self.assertNotIn('Chief Executive Officer', json.dumps(self.data))
        self.assertNotIn('worksFor', person)
        self.assertNotIn('Chief Operating Officer', person['jobTitle'])

    def test_stable_identity_matches_existing_article_authorship(self):
        person_id = 'https://nolankido.com/about/#nolan-kido'
        self.assertEqual(self.graph['Person']['@id'], person_id)
        self.assertEqual(self.graph['WebSite']['publisher']['@id'], person_id)
        self.assertEqual(self.graph['ScholarlyArticle']['author'][0]['@id'], person_id)
        ids = [item['@id'] for item in self.data['@graph']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_identity_data_is_directly_addressable_but_not_linked_from_public_pages(self):
        route = '/assets/nolan-kido-identity.jsonld'
        for path in ['index.html', 'about/index.html']:
            html = self.outputs[Path(path)]
            self.assertNotIn(route, html)
            self.assertNotIn('Hawaii Dental Clinic and Affiliates', html)
            self.assertNotIn('nolan-kido-headshot.jpg', html)
        self.assertNotIn(route, self.outputs[Path('poker/index.html')])

    def test_no_new_photo_or_bio_publication_required(self):
        person = self.graph['Person']
        self.assertNotIn('image', person)
        self.assertNotIn('ImageObject', self.graph)

    def test_standalone_rich_identity_is_preserved_without_inline_expansion(self):
        original = json.loads((ROOT / '_source/person-schema.jsonld').read_text())
        self.assertEqual(self.data, original)
        expected = ['https://github.com/nolankido', 'https://dev.to/kidon']
        for path in ['index.html', 'about/index.html']:
            schema = check_search.Document(self.outputs[Path(path)]).schemas[0]
            person = schema['mainEntity']
            self.assertEqual(schema['about'], person)
            self.assertEqual(set(person), {'@type', '@id', 'name', 'url', 'description', 'sameAs'})
            self.assertEqual(person['sameAs'], expected)
            self.assertEqual(person['@id'], self.graph['Person']['@id'])
        for path, content in self.outputs.items():
            if path.suffix == '.html' and str(path) not in {'index.html', 'about/index.html'}:
                self.assertNotIn('"sameAs"', content, str(path))

    def test_about_explains_native_public_work_links(self):
        html = self.outputs[Path('about/index.html')]
        doc = check_search.Document(html)
        paragraphs = [p for p in doc.tags('p') if p.get('id') == 'public-work-profiles']
        self.assertEqual(paragraphs, [{'class': 'small-copy', 'id': 'public-work-profiles'}])
        profile_links = [a for a in doc.tags('a') if 'me' in a.get('rel', '').split()]
        self.assertEqual(profile_links, [
            {'href': 'https://github.com/nolankido', 'rel': 'me'},
            {'href': 'https://dev.to/kidon', 'rel': 'me'},
        ])
        self.assertIn('public code on GitHub</a>', html)
        self.assertIn('project writing on DEV</a>', html)
        self.assertNotIn('<img', html)

    def audit_profile_pair(self, change=None):
        pages = [p for p in self.pages if p['id'] in {'home', 'about'}]
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for page in pages:
                path = build.output_path(page['path'])
                content = self.outputs[path]
                if change:
                    content = change(page['id'], content)
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text(content)
            (root / 'sitemap.xml').write_text(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://nolankido.com/</loc></url>'
                '<url><loc>https://nolankido.com/about/</loc></url></urlset>'
            )
            return check_search.audit(root, pages, 'https://nolankido.com')

    def test_search_audit_accepts_supported_links_and_rejects_unverified_identity(self):
        self.assertEqual(self.audit_profile_pair()['errors'], [])
        def change(page_id, content):
            return content.replace('https://dev.to/kidon', 'https://dev.to/someone-else')
        report = self.audit_profile_pair(change)
        self.assertEqual(report['status'], 'fail')
        self.assertTrue(any('exactly the verified public-work profiles' in e for e in report['errors']))

    def test_search_audit_rejects_identity_links_outside_the_two_person_nodes(self):
        def change(page_id, content):
            match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content)
            schema = json.loads(match.group(1))
            schema['isPartOf']['sameAs'] = ['https://github.com/nolankido']
            return content.replace(match.group(1), json.dumps(schema), 1)
        report = self.audit_profile_pair(change)
        self.assertEqual(report['status'], 'fail')
        self.assertTrue(any('Unsupported identity claim: sameAs' in e for e in report['errors']))

    def test_search_audit_rejects_a_missing_visible_profile_link(self):
        def change(page_id, content):
            if page_id == 'about':
                return content.replace('<a href="https://dev.to/kidon" rel="me">project writing on DEV</a>', 'project writing on DEV')
            return content
        report = self.audit_profile_pair(change)
        self.assertEqual(report['status'], 'fail')
        self.assertTrue(any('visibly link to the same verified public-work profiles' in e for e in report['errors']))


if __name__ == '__main__':
    unittest.main()
