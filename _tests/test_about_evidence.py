"""The personal About page earns trust with source-linked, bounded claims."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build


class AboutEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = next(page for page in build.public_pages() if page['id'] == 'about')
        cls.html = build.build_outputs()[Path('about/index.html')]

    def test_name_and_evidence_are_immediately_discoverable(self):
        self.assertIn('<h1 class="page-title">About Nolan Kido</h1>', self.html)
        self.assertIn("I'm <strong>Nolan Kido</strong>", self.html)
        self.assertLess(self.html.index('id="about-evidence-title"'), self.html.index('id="what-matters-in-the-work"'))
        self.assertEqual(self.html.count('class="identity-reading"'), 3)
        self.assertIn('AI Works, Human Decides', self.html)
        self.assertEqual(self.page['updated'], '2026-11-06')

    def test_evidence_links_to_existing_work_and_primary_publication(self):
        for link in (
            'https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x',
            'https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829',
            '/technology/local-ai-review-replies/',
            '/technology/review-reply-evidence-audit/#reply-audit-controls',
            '/poker/nolan-kido/#player-record-title',
            'https://www.youtube.com/@NolanPoker',
        ):
            self.assertIn('href="' + link + '"', self.html)
        self.assertIn('The research concerns governmental accounting, not AI performance.', self.html)
        self.assertIn('Tournament cashes are gross results, not profit.', self.html)

    def test_metadata_and_structured_profile_stay_consistent(self):
        self.assertIn('<title>About Nolan Kido: Practical AI | AI Works, Human Decides</title>', self.html)
        self.assertIn('Explore documented projects, published accounting research, and poker.', self.html)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.html).group(1))
        self.assertEqual(schema['@type'], 'ProfilePage')
        self.assertEqual(schema['mainEntity']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertNotIn('jobTitle', schema['mainEntity'])
        self.assertNotIn('hasCredential', schema['mainEntity'])
        self.assertNotIn('Hawaii Dental Clinic and Affiliates', self.html)


if __name__ == '__main__':
    unittest.main()
