"""A real, discoverable wine-learning guide without invented first-person tasting facts."""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import check_live
import living_well

SLUG = 'wine-tasting-notes'
ROUTE = '/living-well/' + SLUG + '/'
WORKSHEET = '/downloads/living-well-wine-tasting-notes.md'
WSET = 'https://www.wsetglobal.com/news-insights/insight-opinion/how-to-taste-wine/'
AWRI = 'https://www.awri.com.au/industry_support/winemaking_resources/sensory_assessment/recognition-of-wine-faults-and-taints/wine_faults/'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class WineTastingNotesTests(unittest.TestCase):
    def test_date_metadata_and_single_canonical_route(self):
        entries = [e for e in living_well.load(ROOT) if e['slug'] == SLUG]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry['published'], '2026-11-13')
        self.assertNotIn('updated', entry)
        self.assertEqual(entry['kind'], 'guide')
        self.assertEqual(entry['topic'], 'attention')
        page = [p for p in living_well.manifest(ROOT) if p['path'] == ROUTE]
        self.assertEqual(len(page), 1)
        html = read('living-well/' + SLUG + '/index.html')
        self.assertIn('rel="canonical" href="https://nolankido.com' + ROUTE + '"', html)
        self.assertIn('article:published_time" content="2026-11-13"', html)
        structured = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(structured)
        schema = json.loads(structured.group(1))
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(schema['datePublished'], '2026-11-13')
        self.assertNotIn('noindex', html)
        sitemap = ET.fromstring(read('sitemap.xml'))
        matches = [node for node in sitemap.findall('{*}url')
                   if node.findtext('{*}loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext('{*}lastmod'), '2026-11-13')

    def test_original_method_and_credible_source_boundaries(self):
        data = json.loads(read('_source/living-well/wine.json'))
        entry = data['entries'][0]
        self.assertEqual(len(entry['sections']), 7)
        self.assertEqual(len(entry['sources']), 3)
        self.assertEqual({s['checked'] for s in entry['sources']}, {'2026-11-13'})
        self.assertIn(WSET, {s['url'] for s in entry['sources']})
        self.assertIn(AWRI, {s['url'] for s in entry['sources']})
        source = read('_source/living-well/wine.json')
        html = read('living-well/wine-tasting-notes/index.html')
        for phrase in ('Fictional example, not Nolan', 'not a personal tasting log',
                       'not a claim that I have tasted', 'it cannot smell',
                       'not a copy of a certification exam', 'I did not detect a buttery aroma',
                       'what remains unknown', 'Original blank worksheet'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), (html + source + read('downloads/living-well-wine-tasting-notes.md')).lower())
        self.assertNotIn('\u2014', source)
        self.assertNotIn('\u2014', html)
        self.assertNotIn('<iframe', html)
        self.assertNotIn('<form', html)
        self.assertIn('id="sources-and-context"', html)
        self.assertIn('href="' + WSET + '"', html)
        self.assertIn('href="' + AWRI + '"', html)

    def test_human_reading_routes_and_feed_entry(self):
        for path in ('about/index.html', 'living-well/index.html',
                     'living-well/guides/index.html', 'living-well/topics/attention/index.html'):
            with self.subTest(path=path):
                self.assertIn('href="' + ROUTE + '"', read(path))
        self.assertIn(ROUTE, read('find/index.html'))
        self.assertIn(ROUTE, read('notes/index.html'))
        for path in ('living-well/feed.xml', 'writing.xml'):
            feed = ET.fromstring(read(path))
            matches = [e for e in feed.findall('./channel/item')
                       if e.findtext('link') == 'https://nolankido.com' + ROUTE]
            self.assertEqual(len(matches), 1, path)
        self.assertEqual(read('about/index.html').count('id="wine-games-and-life"'), 1)

    def test_download_is_blank_private_and_live_verifiable(self):
        worksheet = read(WORKSHEET.lstrip('/'))
        article = read('living-well/' + SLUG + '/index.html')
        self.assertIn('href="' + WORKSHEET + '" download', article)
        self.assertIn('Before any label reveal', worksheet)
        self.assertIn('Only after checking independent information', worksheet)
        self.assertIn('What remains unknown:', worksheet)
        self.assertIn('What surprised me?', worksheet)
        self.assertIn('No upload or AI subscription is necessary', worksheet)
        self.assertNotIn('\u2014', worksheet)
        self.assertNotIn('My tasting on ', worksheet)
        self.assertIn(WORKSHEET, check_live.targets())
        self.assertEqual(check_live.targets()[WORKSHEET][1], worksheet.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
