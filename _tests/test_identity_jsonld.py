"""An intentionally unlinked profile JSON-LD endpoint remains machine-readable."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build


class IdentityJsonLdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
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


if __name__ == '__main__':
    unittest.main()
