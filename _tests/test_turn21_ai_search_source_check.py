"""Turn 21: source-limited answer reuse and nonbranded search-advice navigation."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/technology/check-ai-answers/'
URL = 'https://nolankido.com' + ROUTE
ID = 'review-search-advice'
GOOGLE_FEATURES = 'https://developers.google.com/search/docs/appearance/ai-features'
GOOGLE_GUIDE = 'https://developers.google.com/search/docs/fundamentals/ai-optimization-guide'


class Nodes(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if 'id' in fields:
            self.ids.append(fields['id'])
        if tag == 'a':
            self.links.append(fields.get('href', ''))


def receipt(html):
    match = re.search(r'<section class="review-boundary" id="' + ID +
                      r'"[^>]*>(.*?)</section>', html, re.S)
    return match[1] if match else ''


def receipt_errors(html):
    body = receipt(html)
    if not body:
        return ['missing bounded source-to-claim receipt']
    problems = []
    links = Nodes(body).links
    for href in (GOOGLE_FEATURES, GOOGLE_GUIDE,
                 '/technology/ai-website-visibility/#ai-answer-sprint-panel',
                 '/technology/ai-website-visibility/#site-visibility-recent-release-outcomes'):
        if links.count(href) != 1:
            problems.append('missing or duplicated evidence link: ' + href)
    for boundary in (
        'When can I repeat an AI claim about search visibility?',
        '<strong>Short answer:</strong> repeat only the part the original source supports',
        'invented for this example',
        '<strong>not</strong> an observed chatbot answer',
        'datetime="2026-11-18"',
        'Contradicted: “Special GEO schema is required.”',
        'Supported, with conditions:',
        'the page is indexed and eligible to appear in Google Search with a snippet',
        'Contradicted: “Adding markup guarantees a citation.”',
        'Unresolved: “This site will be cited for a specific question.”',
        'not a completed visibility result',
        'Do not repeat the required-schema claim',
        'not proof of how other search engines or chatbots select citations',
        'or evidence that NolanKido.com has gained rankings',
    ):
        if boundary not in body:
            problems.append('missing scope or factual boundary: ' + boundary)
    if '—' in body:
        problems.append('em dash in new answer')
    return problems


class AiSearchClaimCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/technology/check-ai-answers.html').read_text()
        cls.public = (ROOT / 'technology/check-ai-answers/index.html').read_text()

    def test_source_to_claim_receipt_preserves_six_methods(self):
        for html in (self.source, self.public):
            with self.subTest(output=html is self.public):
                self.assertEqual(receipt_errors(html), [])
                nodes = Nodes(html)
                self.assertEqual(nodes.ids.count(ID), 1)
                self.assertEqual(nodes.links.count('#' + ID), 1)
                self.assertLess(html.index('id="review-research"'), html.index('id="' + ID + '"'))
                self.assertLess(html.index('id="' + ID + '"'), html.index('id="review-numbers"'))
                for old in ('review-fast-method', 'review-claim-map', 'review-research',
                            'review-numbers', 'review-summary', 'review-writing',
                            'review-code', 'review-advice', 'review-completed-record'):
                    self.assertEqual(nodes.ids.count(old), 1, old)
                self.assertEqual(len(re.findall(r'<details class="review-example" id="', html)), 6)

    def test_native_internal_links_reach_same_canonical_answer(self):
        deeplink = ROUTE + '#' + ID
        for path in ('_source/technology/home.html', 'technology/index.html',
                     '_source/resources.html', 'resources/index.html',
                     '_source/technology/ai-website-visibility.html',
                     'technology/ai-website-visibility/index.html'):
            with self.subTest(path=path):
                self.assertEqual(Nodes((ROOT / path).read_text()).links.count(deeplink), 1)
        self.assertIn('id="site-visibility-recent-release-outcomes"',
                      (ROOT / 'technology/ai-website-visibility/index.html').read_text())

    def test_metadata_dates_and_article_identity_stay_consistent(self):
        manifest = json.loads((ROOT / '_source/pages.json').read_text())
        page = next(x for x in manifest if x['path'] == ROUTE)
        self.assertEqual((page['date'], page['updated']), ('2026-10-12', '2026-11-19'))
        self.assertIn('Check AI answers, citations, math and code', page['description'])
        self.assertIn('sourced Google AI Overviews example', page['description'])
        self.assertIn('not a completed visibility result', receipt(self.public))
        self.assertIn('<link rel="canonical" href="' + URL + '">', self.public)
        schemas = [json.loads(raw) for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        self.assertEqual([x.get('@type') for x in schemas].count('Article'), 1)
        self.assertNotIn('FAQPage', [x.get('@type') for x in schemas])
        article = next(x for x in schemas if x.get('@type') == 'Article')
        self.assertEqual(article['datePublished'], '2026-10-12')
        self.assertEqual(article['dateModified'], '2026-11-19')
        self.assertEqual(article['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        sitemap = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        matches = [x for x in sitemap if x.findtext('{*}loc') == URL]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext('{*}lastmod'), '2026-11-19')

    def test_negative_mutations_reject_unsupported_markup_promise(self):
        source = self.source
        modifications = (
            source.replace('Contradicted: “Special GEO schema is required.”',
                           'Supported: “Special GEO schema is required.”', 1),
            source.replace('Contradicted: “Adding markup guarantees a citation.”',
                           'Supported: “Adding markup guarantees a citation.”', 1),
            source.replace('not a completed visibility result', 'a measured visibility win', 1),
            source.replace('not proof of how other search engines or chatbots select citations',
                           'proof for all AI assistants', 1),
            source.replace('href="' + GOOGLE_FEATURES + '"', 'href="https://invalid.example"', 1),
            source.replace('href="' + GOOGLE_GUIDE + '"', 'href="/technology/"', 1),
        )
        for edited in modifications:
            with self.subTest(mutated=edited != source):
                self.assertNotEqual(edited, source)
                self.assertTrue(receipt_errors(edited))


if __name__ == '__main__':
    unittest.main()
