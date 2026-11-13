"""Keep the public projects index grounded, discoverable, and separate from claims."""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PERSON_ID = 'https://nolankido.com/about/#nolan-kido'
ROUTE = '/projects/'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class PublicProjectPortfolioTests(unittest.TestCase):
    def test_one_indexable_collection_page_with_honest_date(self):
        pages = json.loads(read('_source/pages.json'))
        records = [p for p in pages if p['id'] == 'projects' or p['path'] == ROUTE]
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record['id'], 'projects')
        self.assertEqual(record['source'], 'projects.html')
        self.assertEqual(record['section'], 'technology')
        self.assertEqual(record['updated'], '2026-11-13')
        self.assertNotIn('date', record)
        self.assertFalse(record.get('noindex'))

        html = read('projects/index.html')
        self.assertFalse(any(line.strip() == '' and line != '' for line in html.splitlines()))
        self.assertEqual(html.count('<h1 class="page-title">Projects by Nolan Kido</h1>'), 1)
        self.assertEqual(html.count('<link rel="canonical" href="https://nolankido.com/projects/">'), 1)
        self.assertNotIn('noindex', html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema['@type'], 'CollectionPage')
        self.assertEqual(schema['url'], 'https://nolankido.com/projects/')
        self.assertEqual(schema['about']['@id'], PERSON_ID)
        self.assertNotIn('datePublished', schema)

        entries = ET.fromstring(read('sitemap.xml')).findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        matches = [x for x in entries if x.findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}loc') == 'https://nolankido.com/projects/']
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod'), '2026-11-13')

    def test_methods_and_caveats_are_visible_to_readers(self):
        content = read('_source/projects.html')
        html = read('projects/index.html')
        for heading in ('projects-intro-title', 'projects-try-title', 'projects-apps-title',
                        'projects-checks-title', 'projects-creative-title'):
            with self.subTest(heading=heading):
                self.assertEqual(content.count('id="' + heading + '"'), 1)
                self.assertIn('id="' + heading + '"', html)
        for route in ('/technology/task-brief/', '/technology/ai-time-savings/',
                      '/poker/study-calculators/', '/technology/local-ai-review-replies/',
                      '/technology/ai-book-continuity-checker/', '/technology/dinner-on-time/',
                      '/technology/local-ai-test-record/', '/technology/checking-ai-website-changes/',
                      '/technology/ai-poker-video-evidence/', '/poker/nolan-kido/',
                      '/poker/comics/'):
            with self.subTest(route=route):
                self.assertIn('href="' + route, content)
        for caveat in ('fictional', 'archived', 'not evidence', 'not a guarantee',
                       'gross cash', 'unfinished game', 'private projects'):
            with self.subTest(caveat=caveat):
                self.assertIn(caveat, content.lower())
        self.assertNotIn('\u2014', content)
        self.assertNotIn('\u2014', html)

    def test_portfolio_reachable_from_five_public_entrypoints(self):
        for route in ('index.html', 'about/index.html', 'technology/index.html',
                      'creative/index.html', 'bio/index.html'):
            with self.subTest(route=route):
                html = read(route)
                self.assertEqual(html.count('href="/projects/"'), 1)
        find = read('find/index.html')
        self.assertEqual(find.count('<a href="/projects/">Projects by Nolan Kido</a>'), 1)
        self.assertIn('data-interests="technology poker creative"', find)

    def test_public_index_remains_hub_not_historical_article(self):
        html = read('projects/index.html')
        self.assertNotIn('article:published_time', html)
        self.assertNotIn('client testimonials', html.lower())
        self.assertNotIn('results guarantee', html.lower())
        self.assertIn('What has Nolan Kido built and published?', html)
        self.assertIn('AI Works, Human Decides', html)


if __name__ == '__main__':
    unittest.main()
