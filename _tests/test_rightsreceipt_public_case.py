"""Verify RightsReceipt's public source provenance and noninflated claims."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/technology/rightsreceipt-ai-licensing/'
REPO = 'https://github.com/nolankido/rightsreceipt-hackathon'
SNAPSHOT = '646182a95faf6ab5448f10927ded1650ff38bdf5'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class RightsReceiptPublicCaseTests(unittest.TestCase):
    def test_article_is_canonical_dated_and_searchable(self):
        pages = json.loads(read('_source/pages.json'))
        items = [p for p in pages if p.get('id') == 'rightsreceipt-case' or p.get('path') == ROUTE]
        self.assertEqual(len(items), 1)
        page = items[0]
        self.assertEqual(page['path'], ROUTE)
        self.assertEqual(page['date'], '2026-11-13')
        self.assertEqual(page['section'], 'technology')
        self.assertTrue(page['evidence_article'])
        self.assertFalse(page.get('noindex'))
        html = read('technology/rightsreceipt-ai-licensing/index.html')
        self.assertIn('<link rel="canonical" href="https://nolankido.com' + ROUTE + '"', html)
        self.assertIn('article:published_time', html)
        self.assertNotIn('noindex', html)
        sitemap = ET.fromstring(read('sitemap.xml'))
        urls = sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        matches = [el for el in urls if el.findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(matches), 1)

    def test_json_ld_links_code_ownership_and_external_corroboration(self):
        html = read('technology/rightsreceipt-ai-licensing/index.html')
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(schema['about']['@type'], 'SoftwareSourceCode')
        self.assertEqual(schema['about']['codeRepository'], REPO)
        self.assertEqual(schema['about']['author']['@id'], schema['author']['@id'])
        self.assertIn('https://devpost.com/software/rightsreceipt', schema['citation'])
        self.assertIn(REPO + '/tree/' + SNAPSHOT, schema['citation'])
        image = schema['image']
        self.assertEqual(image['url'], 'https://nolankido.com/assets/projects/rightsreceipt-harbor.svg')
        self.assertEqual((image['width'], image['height']), (1200, 720))

    def test_public_claims_separate_real_model_from_simulated_payment(self):
        content = read('_source/technology/rightsreceipt-ai-licensing.html')
        for fragment in ('Devpost', '24 field comparisons', 'Germany only',
                         'United States and Canada', 'simulated_only',
                         'paymentEvidence: "none"', 'not</strong> been independently demonstrated',
                         'fictional', 'copyright', 'Node 22.13', SNAPSHOT,
                         'three database resets', 'zero external requests',
                         'not</em> an independent rerun'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, content)
        self.assertIn('href="https://developer.paypal.com/api/rest/webhooks/rest/"', content)
        self.assertIn('href="' + REPO + '"', content)
        self.assertNotIn('\u2014', content)

    def test_asset_matches_public_demonstration_snapshot(self):
        asset = ROOT / 'assets/projects/rightsreceipt-harbor.svg'
        self.assertTrue(asset.is_file())
        self.assertEqual(sha256(asset.read_bytes()).hexdigest(),
                         'f4f6bb7f356d35489499e8a9d9763de3de56161d4251e52b8de1bd267713debd')
        self.assertIn('src="/assets/projects/rightsreceipt-harbor.svg"', read('technology/rightsreceipt-ai-licensing/index.html'))

    def test_technology_projects_and_creative_offer_direct_paths(self):
        for path in ('technology/index.html', 'projects/index.html', 'creative/index.html', 'about/index.html'):
            with self.subTest(path=path):
                html = read(path)
                self.assertIn('href="' + ROUTE + '"', html)
        for external in ('https://devpost.com/software/rightsreceipt', REPO):
            self.assertIn(external, read('_source/projects.html'))
        self.assertIn('id="projects-public-title"', read('projects/index.html'))
        self.assertIn('id="creative-rightsreceipt-title"', read('creative/index.html'))


if __name__ == '__main__':
    unittest.main()
