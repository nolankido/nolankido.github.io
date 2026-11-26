"""Turn 20: answer-first person identity with separated public source classes."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import public_identity

ROUTE = '/about/'
URL = 'https://nolankido.com/about/'
ID = 'who-is-nolan-kido'
DOI = 'https://doi.org/10.1111/j.1475-679X.2012.00447.x'
RRW = 'https://github.com/nolankido/reviewReplyWriter/tree/1c5e0487c331d5202410c9f342557d9355951c3a'
PREFLIGHT = 'https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/README.md'


class LinksAndIds(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))


def answer_section(value):
    start = '<section aria-labelledby="' + ID + '">'
    pieces = value.split(start, 1)
    return pieces[1].split('</section>', 1)[0] if len(pieces) == 2 else ''


def answer_errors(value):
    body = answer_section(value)
    if not body:
        return ['missing bounded answer section']
    errors = []
    links = LinksAndIds(body).links
    for target in (
        RRW, PREFLIGHT, DOI, '/technology/local-ai-review-replies/',
        '/technology/ai-book-continuity-checker/', '/projects/#projects-checks',
        '/poker/nolan-kido/#player-record-title', '/bio/#profile-fact-check',
        'https://www.youtube.com/@NolanPoker',
    ):
        if links.count(target) != 1:
            errors.append('source route missing or duplicated: ' + target)
    for claim in (
        'Who is Nolan Kido, and what has he built?',
        'Short answer:',
        'Public AI work:',
        'Independent records and other interests:',
        'a writer and builder documenting practical AI projects',
        'archived fictional review-reply tests',
        'Sherlock Holmes continuity audit, misses and false alarms',
        'not</strong> independently measured client results',
        'The paper does not establish a current faculty appointment',
        'a tournament listing does not establish net profit',
        'not an independently verified full résumé',
    ):
        if claim not in body:
            errors.append('source limitation missing: ' + claim)
    if '—' in body:
        errors.append('em dash in identity answer')
    return errors


class SourceBoundedIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/about.html').read_text()
        cls.public = (ROOT / 'about/index.html').read_text()

    def test_one_direct_answer_before_existing_evidence(self):
        for html in (self.source, self.public):
            with self.subTest(generated=html is self.public):
                self.assertEqual(answer_errors(html), [])
                nodes = LinksAndIds(html)
                self.assertEqual(nodes.ids.count(ID), 1)
                self.assertEqual(nodes.links.count('#' + ID), 1)
                self.assertLess(html.index('id="' + ID + '"'), html.index('id="about-evidence-title"'))
                for old_id in ('about-evidence-title', 'what-matters-in-the-work',
                               'public-ai-projects', 'try-the-work', 'public-work-elsewhere'):
                    self.assertEqual(nodes.ids.count(old_id), 1, old_id)

    def test_identity_navigation_and_existing_author_anchors(self):
        for path in ('_source/home.html', 'index.html',
                     '_source/projects.html', 'projects/index.html',
                     '_source/bio.html', 'bio/index.html'):
            html = (ROOT / path).read_text()
            self.assertIn('href="' + ROUTE + '#' + ID + '"', html, path)
        for path, ident in (('about/index.html', 'about-evidence-title'),
                            ('projects/index.html', 'projects-checks'),
                            ('bio/index.html', 'profile-fact-check')):
            self.assertIn('id="' + ident + '"', (ROOT / path).read_text())
        self.assertIn('href="/about/#about-evidence-title"', (ROOT / 'index.html').read_text())

    def test_metadata_and_profile_person_do_not_duplicate_identity(self):
        manifest = json.loads((ROOT / '_source/pages.json').read_text())
        page = next(p for p in manifest if p['path'] == ROUTE)
        # Later reviewed revisions may change the calendar date, not identity or evidence.
        self.assertGreaterEqual(page['updated'], '2026-11-19')
        self.assertIn('Who is Nolan Kido?', page['description'])
        self.assertIn('AI Works, Human Decides', page['description'])
        for path in ('/', '/bio/', '/projects/'):
            record = next(p for p in manifest if p['path'] == path)
            self.assertGreaterEqual(record['updated'], '2026-11-18')
        self.assertEqual(LinksAndIds(self.public).ids.count(ID), 1)
        self.assertIn('<link rel="canonical" href="' + URL + '">', self.public)
        schemas = [json.loads(raw) for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        profile = [s for s in schemas if s.get('@type') == 'ProfilePage']
        self.assertEqual(len(profile), 1)
        schema = profile[0]
        self.assertEqual(schema['url'], URL)
        self.assertEqual(schema['mainEntity']['@id'], URL + '#nolan-kido')
        self.assertEqual(schema['about'], schema['mainEntity'])
        self.assertEqual(schema['mainEntity']['sameAs'], public_identity.same_as())
        sitemap = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        urls = [e for e in sitemap if e.findtext('{*}loc') == URL]
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0].findtext('{*}lastmod'), page['updated'])
        for path in ('/', '/bio/', '/projects/'):
            record = next(p for p in manifest if p['path'] == path)
            matches = [e for e in sitemap if e.findtext('{*}loc') == 'https://nolankido.com' + path]
            self.assertEqual(len(matches), 1, path)
            self.assertEqual(matches[0].findtext('{*}lastmod'), record['updated'], path)

    def test_claim_inflation_and_link_drift_are_rejected(self):
        source = self.source
        mutations = (
            source.replace('archived fictional review-reply tests', 'real paying clients', 1),
            source.replace('not</strong> independently measured client results',
                           'yes</strong> independently measured client results', 1),
            source.replace('a tournament listing does not establish net profit',
                           'a tournament listing establishes net profit', 1),
            source.replace('The paper does not establish a current faculty appointment',
                           'The paper establishes a current faculty appointment', 1),
            source.replace('href="' + DOI + '"', 'href="https://doi.example/false"', 1),
            source.replace('href="' + RRW + '"', 'href="/projects/"', 1),
        )
        for changed in mutations:
            with self.subTest(mutated=changed != source):
                self.assertNotEqual(changed, source)
                self.assertTrue(answer_errors(changed))


if __name__ == '__main__':
    unittest.main()
