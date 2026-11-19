"""Turn 24: one source-bounded AI/poker claim answer with native discovery links."""

from fractions import Fraction
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import runpy
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/technology/check-ai-answers/'
FRAGMENT = 'review-poker-solver-claim'
TARGET = ROUTE + '#' + FRAGMENT
CASE = '/poker/evaluating-poker-advice/#solver-fit-test'
BRANCHES = '/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble'
CHECKER = '/downloads/ten-bb-bubble-icm.py'
REAL_HAND = '/poker/episodes/portland-meadows-ep1/#hand-64o-record'
AUTHOR = '/about/#nolanpoker-ai-link'


class Nodes(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.append(data['id'])
        if tag == 'a':
            self.links.append(data.get('href', ''))


def audit(html):
    match = re.search(
        r'<section class="review-boundary" id="' + FRAGMENT + r'"[^>]*>(.*?)</section>',
        html, re.S)
    return match[1] if match else ''


def audit_errors(html):
    answer = audit(html)
    if not answer:
        return ['missing bounded AI poker claim review']
    failures = []
    hrefs = Nodes(answer).links
    for href in (CASE, BRANCHES, CHECKER, REAL_HAND, AUTHOR):
        if hrefs.count(href) != 1:
            failures.append('missing or duplicate source link: ' + href)
    for required in (
        'How do you check an AI answer that recommends a 10 BB bubble call?',
        '<strong>Short answer:</strong> separate the call price in chips',
        'Claim to audit, invented for this example:',
        '<strong>not</strong> an observed chatbot response',
        'not a new simulation or measured opponent range',
        '40, 30, 20 and 10 BB before posting',
        'Three are paid $50, $30 and $20; fourth receives $0',
        'with no ante, bounty or deal',
        '9 / 20 = 45%',
        'Supported only for chip EV:',
        'Not supported as the tournament prize-equity threshold:',
        '$12.286143',
        '$21.785714',
        'approximately 56.40%, not 45%',
        'Unresolved: “So call.”',
        'No actual hand, opponent range or showdown win probability',
        'invented 50% probability',
        'not a call-or-fold verdict for a real tournament',
        'Do not reuse the unconditional instruction to call',
        'different conditions and no verified solver or ICM decision',
        'without turning either example into a documented playing result',
        'datetime="2026-11-19"',
    ):
        if required not in answer:
            failures.append('missing or altered truth boundary: ' + required)
    if '\u2014' in answer:
        failures.append('em dash in answer')
    return failures


class AiPokerClaimBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/technology/check-ai-answers.html').read_text()
        cls.public = (ROOT / 'technology/check-ai-answers/index.html').read_text()

    def test_bounded_answer_and_original_six_methods(self):
        for html in (self.source, self.public):
            with self.subTest(output=html is self.public):
                self.assertEqual(audit_errors(html), [])
                nodes = Nodes(html)
                self.assertEqual(nodes.ids.count(FRAGMENT), 1)
                self.assertEqual(nodes.links.count('#' + FRAGMENT), 1)
                self.assertLess(html.index('id="review-search-advice"'),
                                html.index('id="' + FRAGMENT + '"'))
                self.assertLess(html.index('id="' + FRAGMENT + '"'),
                                html.index('class="review-stop"'))
                for old in ('review-search-advice', 'review-research', 'review-numbers',
                            'review-summary', 'review-writing', 'review-code',
                            'review-advice', 'review-completed-record'):
                    self.assertEqual(nodes.ids.count(old), 1, old)
                self.assertEqual(len(re.findall(r'<details class="review-example" id="', html)), 6)

    def test_chip_and_prize_equity_calculation_reproduces_original_case(self):
        example = runpy.run_path(str(ROOT / 'downloads/ten-bb-bubble-icm.py'))['example']()
        self.assertEqual(example['before_posting_bb'], (40, 30, 20, 10))
        self.assertEqual(example['prizes_dollars'], (50, 30, 20, 0))
        self.assertEqual(example['ante_bb'], 0)
        self.assertEqual(example['hero_additional_call_bb'], 9)
        self.assertEqual(example['contested_final_pot_bb'], 20)
        self.assertEqual(Fraction(9, 20) * 100, 45)
        self.assertEqual(example['classic_icm_threshold_exact'], '76518591/135682300')
        self.assertAlmostEqual(example['classic_icm_call_threshold_percent'], 56.395411192, places=7)
        self.assertLess(Fraction(9, 20), Fraction(1, 2))
        self.assertLess(Fraction(1, 2), Fraction(76518591, 135682300))
        self.assertTrue(example['real_portland_meadows_range_or_icm_result'].startswith('unknown'))

    def test_cross_topic_entry_links_are_native_and_unambiguous(self):
        for source, output in (
            ('_source/technology/home.html', 'technology/index.html'),
            ('_source/poker/evaluating-poker-advice.html', 'poker/evaluating-poker-advice/index.html'),
            ('_source/poker/poker-research-guide.html', 'poker/poker-research-guide/index.html'),
        ):
            for path in (source, output):
                with self.subTest(path=path):
                    html = (ROOT / path).read_text()
                    self.assertEqual(Nodes(html).links.count(TARGET), 1)
                    self.assertNotIn('\u2014', html)
        self.assertIn('id="nolanpoker-ai-link"', (ROOT / 'about/index.html').read_text())
        self.assertIn('id="solver-fit-test"',
                      (ROOT / 'poker/evaluating-poker-advice/index.html').read_text())

    def test_all_four_revision_dates_and_article_identity(self):
        manifest = json.loads((ROOT / '_source/pages.json').read_text())
        records = {page['path']: page for page in manifest}
        sitemap = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        for path, original in (
            (ROUTE, '2026-10-12'),
            ('/poker/evaluating-poker-advice/', '2026-10-08'),
            ('/poker/poker-research-guide/', '2026-10-08'),
            ('/technology/', None),
        ):
            with self.subTest(path=path):
                record = records[path]
                self.assertEqual(record['updated'], '2026-11-19')
                url = 'https://nolankido.com' + path
                found = [node for node in sitemap if node.findtext('{*}loc') == url]
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0].findtext('{*}lastmod'), '2026-11-19')
                public = (ROOT / path.strip('/') / 'index.html').read_text()
                self.assertIn('<link rel="canonical" href="' + url + '">', public)
                if original:
                    self.assertEqual(record['date'], original)
                    schemas = [json.loads(raw) for raw in re.findall(
                        r'<script type="application/ld\+json">(.*?)</script>', public, re.S)]
                    self.assertNotIn('FAQPage', [schema.get('@type') for schema in schemas])
                    article = next(schema for schema in schemas if schema.get('@type') == 'Article')
                    self.assertEqual(article['datePublished'], original)
                    self.assertEqual(article['dateModified'], '2026-11-19')
                    self.assertEqual(article['author']['@id'],
                                     'https://nolankido.com/about/#nolan-kido')

    def test_negative_mutations_reject_false_real_world_conclusions(self):
        changes = (
            ('Claim to audit, invented for this example:</strong> <q>You need',
             'Observed AI advice:</strong> <q>You need'),
            ('<strong>not</strong> an observed chatbot response', 'an actual chatbot transcript'),
            ('approximately 56.40%, not 45%', 'approximately 45%, not 56.40%'),
            ('Unresolved: “So call.”', 'Supported: “So call.”'),
            ('No actual hand, opponent range or showdown win probability',
             'The actual hand and opponent range establish a showdown probability'),
            ('not a call-or-fold verdict for a real tournament',
             'a proven call-or-fold verdict for any tournament'),
            ('href="' + CHECKER + '"', 'href="/poker/"'),
            ('href="' + AUTHOR + '"', 'href="/about/"'),
        )
        for old, new in changes:
            with self.subTest(edited=old):
                self.assertIn(old, self.source)
                self.assertTrue(audit_errors(self.source.replace(old, new, 1)))


if __name__ == '__main__':
    unittest.main()
