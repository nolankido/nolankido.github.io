"""Public biography sources support only claims they can actually establish."""
from __future__ import annotations

import json
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = 'https://doi.org/10.1111/j.1475-679X.2012.00447.x'
MIT = 'https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class PublicBioFactGuideTests(unittest.TestCase):
    def test_public_bio_has_one_source_guide_and_native_navigation(self):
        html = read('bio/index.html')
        self.assertEqual(html.count('id="profile-fact-check"'), 1)
        self.assertEqual(html.count('id="profile-citation-guide"'), 1)
        self.assertIn('href="#profile-fact-check"', html)
        self.assertIn('aria-labelledby="profile-fact-check"', html)
        self.assertIn('rel="canonical" href="https://nolankido.com/bio/"', html)
        self.assertNotIn('noindex', html)

    def test_independent_and_first_person_sources_remain_separate(self):
        html = read('bio/index.html')
        for expected in (
            RESEARCH, MIT, 'Reining Petacchi', 'Joseph Weber',
            'https://devpost.com/software/rightsreceipt',
            'https://github.com/nolankido/rightsreceipt-hackathon',
            '/technology/rightsreceipt-ai-licensing/',
            '/about/accounting-research/', '/technology/ai-workflow-pilot/',
            'https://www.youtube.com/@NolanPoker', '/poker/nolan-kido/',
            '/about/#wine-games-and-life',
            'not a current university appointment',
            'not a hackathon award',
            'not independently measured efficiency',
            'not net profit',
            'not evidence of a wine certification',
            'AI assistance and source review',
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, html)
        self.assertNotIn('\u2014', read('_source/bio.html'))

    def test_existing_reusable_biographies_remain_exact(self):
        site = json.loads(read('_source/site.json'))
        html = read('bio/index.html')
        for size in ('short', 'long'):
            text = site['bio_' + size]
            self.assertIn(text, html)
            self.assertEqual(read(f'downloads/nolan-kido-{size}-bio.txt'), text + '\n')

    def test_about_reaches_fact_guide_and_does_not_mutate_research_date(self):
        self.assertIn('href="/bio/#profile-fact-check"', read('about/index.html'))
        self.assertEqual(read('bio/index.html').count('href="/projects/"'), 1)
        self.assertIn('href="/projects/#projects-checks"', read('bio/index.html'))
        self.assertIn('href="/projects/#projects-apps"', read('bio/index.html'))
        pages = {item['path']: item for item in json.loads(read('_source/pages.json'))}
        self.assertEqual(pages['/bio/']['updated'], '2026-11-13')
        self.assertEqual(pages['/about/']['updated'], '2026-11-13')
        self.assertEqual(pages['/about/accounting-research/']['date'], '2026-11-13')
        sitemap = ET.fromstring(read('sitemap.xml'))
        urls = [node for node in sitemap.findall('{*}url')
                if node.findtext('{*}loc') == 'https://nolankido.com/bio/']
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0].findtext('{*}lastmod'), '2026-11-13')


if __name__ == '__main__':
    unittest.main()
