"""Keep 2012 scholarly evidence distinct from 2026 explanatory writing."""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/about/accounting-research/'
DOI = 'https://doi.org/10.1111/j.1475-679X.2012.00447.x'
MIT = 'https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class PublishedAccountingResearchTests(unittest.TestCase):
    def test_single_dated_searchable_article(self):
        pages = json.loads(read('_source/pages.json'))
        matching = [p for p in pages if p['path'] == ROUTE or p['id'] == 'accounting-research']
        self.assertEqual(len(matching), 1)
        item = matching[0]
        self.assertEqual(item['section'], 'about')
        self.assertEqual(item['date'], '2026-11-13')
        self.assertTrue(item['evidence_article'])
        self.assertFalse(item.get('noindex'))
        html = read('about/accounting-research/index.html')
        self.assertIn('rel="canonical" href="https://nolankido.com' + ROUTE + '"', html)
        self.assertIn('article:published_time" content="2026-11-13"', html)
        self.assertNotIn('noindex', html)
        sitemap = ET.fromstring(read('sitemap.xml'))
        matches = [el for el in sitemap.findall('{*}url') if el.findtext('{*}loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext('{*}lastmod'), '2026-11-13')

    def test_scholarship_and_commentary_have_distinct_structured_dates_and_authors(self):
        html = read('about/accounting-research/index.html')
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(schema['datePublished'], '2026-11-13')
        paper = schema['about']
        self.assertEqual(paper['@type'], 'ScholarlyArticle')
        self.assertEqual(paper['@id'], DOI)
        self.assertEqual(paper['datePublished'], '2012-02-06')
        self.assertEqual(paper['isPartOf']['name'], 'Journal of Accounting Research')
        self.assertEqual([a['name'] for a in paper['author']], ['Nolan Kido', 'Reining Petacchi', 'Joseph Weber'])
        self.assertEqual(paper['author'][0]['@id'], schema['author']['@id'])
        self.assertEqual(set(schema['citation']), {DOI, MIT})

    def test_bounded_public_source_and_result_language(self):
        text = read('_source/about/accounting-research.html')
        for expected in ('compensated absences', 'unfunded pension',
                         'systematically lower', 'associated with proxy',
                         'does not by itself identify', 'not</strong> evidence',
                         'not an AI study', 'not a claim about my employment',
                         '2012 article', 'November 2026', DOI, MIT):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)
        self.assertNotIn('\u2014', text)
        self.assertNotIn('the AI paper', text.lower())
        self.assertIn('id="research-table-hint"', text)
        self.assertIn('aria-describedby="research-table-hint"', text)

    def test_reachable_from_home_about_and_project_portfolio(self):
        for path in ('index.html', 'about/index.html', 'projects/index.html'):
            with self.subTest(path=path):
                self.assertIn('href="' + ROUTE + '"', read(path))
        home = read('index.html')
        self.assertIn('href="https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x"', home)
        self.assertIn('href="' + MIT + '"', home)
        self.assertIn('Published research explanation', read('notes/index.html'))

    def test_modified_dates_follow_content_changes_only(self):
        pages = {p['path']: p for p in json.loads(read('_source/pages.json'))}
        sitemap = ET.fromstring(read('sitemap.xml'))
        dated = {url.findtext('{*}loc'): url.findtext('{*}lastmod') for url in sitemap}
        for route in ('/', '/about/', '/projects/'):
            self.assertEqual(pages[route]['updated'], '2026-11-13')
            self.assertEqual(dated['https://nolankido.com' + route], '2026-11-13')
        self.assertNotIn('date', pages['/about/'])


if __name__ == '__main__':
    unittest.main()
