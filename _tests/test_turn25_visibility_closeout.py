"""Turn 25: a truthful public sprint readout with frozen measurement inputs."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/technology/ai-website-visibility/'
URL = 'https://nolankido.com' + ROUTE
ANCHOR = 'site-visibility-sprint-outcome'
TARGET = ROUTE + '#' + ANCHOR
REPORT = ROOT / '_reports/visibility-sprint/seo-geo-turn25-closeout-2026-11-19.md'
FROZEN = ROOT / '_reports/visibility-sprint/assistant-answer-panel-v1-2026-11-17.csv'
PANEL = ROOT / 'downloads/ai-answer-sprint-25-prompts.csv'
BLANK = ROOT / 'downloads/ai-answer-sprint-25-blank.csv'


class Nodes(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if fields.get('id'):
            self.ids.append(fields['id'])
        if tag == 'a':
            self.links.append(fields.get('href', ''))


def readout(html):
    found = re.search(
        r'<section class="section folio-row" id="' + ANCHOR +
        r'"[^>]*>(.*?)</section>', html, re.S)
    return found[1] if found else ''


def readout_errors(html):
    body = readout(html)
    if not body:
        return ['missing sprint closeout answer']
    failures = []
    links = Nodes(body).links
    for url in (
        '/about/#who-is-nolan-kido',
        '/about/#nolanpoker-ai-link',
        '/technology/check-ai-answers/',
        '/technology/check-ai-answers/#review-poker-solver-claim',
        '/poker/evaluating-poker-advice/#solver-fit-test',
        'https://github.com/nolankido/nolankido.github.io/pull/396',
        'https://github.com/nolankido/nolankido.github.io/blob/main/'
        '_reports/visibility-sprint/seo-geo-turn25-closeout-2026-11-19.md',
        'https://support.google.com/webmasters/answer/16984139',
    ):
        if links.count(url) != 1:
            failures.append('missing or duplicate source link: ' + url)
    for boundary in (
        'Did 25 SEO, GEO and AEO improvement turns make this site more visible?',
        '<strong>Short answer:</strong>',
        'It did <strong>not</strong> establish higher search rankings',
        '224 listed URLs in the',
        '225 after Turn 24 on November 19',
        'not</strong> one confirmed indexed page',
        '16 of 16 changed public HTML, CSS, XML and feed files',
        'Not measured in this sprint.',
        'No authenticated Search Console performance export',
        'has no verified completed observation set',
        'Neither an improvement nor a measured zero',
        'October 2026 is before this November 17 to 19 sprint',
        'November mixes before-and-after days',
        'December is the first full month afterward',
        'already included',
        'twenty nonbranded and five branded questions',
        'post-sprint baseline',
        'no comparable presprint answer observations were captured',
        'Fix confirmed indexing or canonical problems first',
        'not every turn introduced a new URL',
        'not assign causation to one release based on an unmatched period',
    ):
        if boundary not in body:
            failures.append('missing factual boundary: ' + boundary)
    if body.count('Not measured in this sprint.') != 2:
        failures.append('both private performance categories must remain unmeasured')
    if '\u2014' in body:
        failures.append('em dash in new answer')
    return failures


class VisibilitySprintCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/technology/ai-website-visibility.html').read_text()
        cls.public = (ROOT / 'technology/ai-website-visibility/index.html').read_text()

    def test_one_direct_answer_and_prior_methods_survive(self):
        for html in (self.source, self.public):
            with self.subTest(output=html is self.public):
                self.assertEqual(readout_errors(html), [])
                nodes = Nodes(html)
                self.assertEqual(nodes.ids.count(ANCHOR), 1)
                self.assertEqual(nodes.ids.count(ANCHOR + '-title'), 1)
                self.assertEqual(nodes.ids.count('site-visibility-sprint-next-measurement'), 1)
                self.assertEqual(nodes.links.count('#' + ANCHOR), 1)
                self.assertLess(html.index('id="' + ANCHOR + '"'),
                                html.index('id="site-visibility-recent-release"'))
                self.assertEqual(len(re.findall(r'<h2[^>]*id="' + ANCHOR + '-title"', html)), 1)
                for old in ('site-visibility-recent-release', 'site-visibility-evidence',
                            'site-visibility-checks', 'site-visibility-limits',
                            'free-visibility-check', 'ai-answer-visibility-check',
                            'ai-answer-sprint-panel', 'ai-citation-offline-audit'):
                    self.assertEqual(nodes.ids.count(old), 1, old)
                self.assertIn('project-table-scroll" role="region"', readout(html))
                self.assertIn('aria-describedby="site-visibility-sprint-outcome-hint" tabindex="0"',
                              readout(html))

    def test_contextual_entry_links_and_canonical_dates(self):
        for source, public in (
            ('_source/technology/home.html', 'technology/index.html'),
            ('_source/resources.html', 'resources/index.html'),
        ):
            for path in (source, public):
                with self.subTest(path=path):
                    self.assertEqual(Nodes((ROOT / path).read_text()).links.count(TARGET), 1)
        manifest = json.loads((ROOT / '_source/pages.json').read_text())
        records = {item['path']: item for item in manifest}
        sitemap = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        for route in (ROUTE, '/technology/', '/resources/'):
            with self.subTest(route=route):
                record = records[route]
                self.assertGreaterEqual(record['updated'], '2026-11-19')
                canonical = 'https://nolankido.com' + route
                page = (ROOT / route.lstrip('/') / 'index.html').read_text()
                self.assertIn('<link rel="canonical" href="' + canonical + '">', page)
                urls = [node for node in sitemap if node.findtext('{*}loc') == canonical]
                self.assertEqual(len(urls), 1)
                self.assertEqual(urls[0].findtext('{*}lastmod'), record['updated'])
        self.assertEqual(records[ROUTE]['date'], '2026-11-03')
        schema = [json.loads(raw) for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        self.assertNotIn('FAQPage', [item.get('@type') for item in schema])
        article = next(item for item in schema if item.get('@type') == 'Article')
        self.assertEqual(article['datePublished'], '2026-11-03')
        self.assertEqual(article['dateModified'], records[ROUTE]['updated'])
        self.assertEqual(article['author']['@id'], 'https://nolankido.com/about/#nolan-kido')

    def test_all_twenty_five_records_and_frozen_panel_remain_intact(self):
        self.assertTrue(REPORT.is_file())
        body = REPORT.read_text()
        records = sorted(p for p in (ROOT / '_reports/visibility-sprint').glob('seo-geo-turn*.md')
                         if re.match(r'seo-geo-turn(?:0[1-9]|1[0-9]|2[0-5])-', p.name))
        self.assertEqual(len(records), 25)
        for turn in range(1, 26):
            with self.subTest(turn=turn):
                self.assertIn('| ' + str(turn).zfill(2) + ' |', body)
                matches = [r for r in records if r.name.startswith('seo-geo-turn' + str(turn).zfill(2) + '-')]
                self.assertEqual(len(matches), 1)
                self.assertIn('](' + matches[0].name + ')', body)
        self.assertEqual(PANEL.read_bytes(), FROZEN.read_bytes())
        self.assertEqual(BLANK.read_text().count('\n'), 1)
        self.assertGreaterEqual(len(ET.fromstring((ROOT / 'sitemap.xml').read_text())), 225)
        self.assertIn('Neither an unknown nor a missing export equals zero', body)
        self.assertIn('first completed 25-question run will be a post-sprint baseline', body)
        self.assertNotIn('\u2014', body)

    def test_negative_mutations_reject_false_performance_claims(self):
        changes = (
            ('It did <strong>not</strong> establish higher search rankings',
             'It did establish higher search rankings'),
            ('Not measured in this sprint.', 'Measured at zero in this sprint.'),
            ('not</strong> one confirmed indexed page',
             'proof of one newly indexed page'),
            ('has no verified completed observation set',
             'was observed citing the site in all trials'),
            ('post-sprint baseline', 'measured AI citation increase'),
            ('no comparable presprint answer observations were captured',
             'an independent presprint AI citation rate was recorded'),
            ('href="https://github.com/nolankido/nolankido.github.io/pull/396"',
             'href="https://github.com/nolankido/nolankido.github.io/pull/1"'),
        )
        for old, new in changes:
            with self.subTest(boundary=old):
                body = readout(self.source)
                self.assertIn(old, body)
                changed = self.source.replace(old, new, 1)
                self.assertTrue(readout_errors(changed))


if __name__ == '__main__':
    unittest.main()
