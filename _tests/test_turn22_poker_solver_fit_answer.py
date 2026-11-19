"""Turn 22: source-bounded solver-chart answer, exact bubble math and discovery."""

from fractions import Fraction as F
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import runpy
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/poker/evaluating-poker-advice/'
URL = 'https://nolankido.com' + ROUTE
ANCHOR = 'solver-fit-test'
METHOD = '/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble'
CODE = '/downloads/ten-bb-bubble-icm.py'
PROVIDER = 'https://help.gtowizard.com/how-to-build-custom-solutions/'
HAND = '/poker/episodes/portland-meadows-ep1/#hand-64o-record'


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


def bounded_answer(html):
    m = re.search(r'<section class="viewer-example" id="' + ANCHOR +
                  r'"[^>]*>(.*?)</section>', html, re.S)
    return m[1] if m else ''


def answer_errors(html):
    body = bounded_answer(html)
    if not body:
        return ['missing bounded solver-fit answer']
    problems = []
    links = Nodes(body).links
    for target in (METHOD, CODE, PROVIDER, HAND):
        if links.count(target) != 1:
            problems.append('missing or duplicate source link: ' + target)
    for required in (
        'Can a 10 BB solver chart tell you whether to call on the tournament bubble?',
        '<strong>Short answer: not from the stack label alone.</strong>',
        'four players remain and three are paid $50, $30 and $20',
        'small blind has 40 BB, cutoff 30 BB, button 20 BB',
        'you in the big blind 10 BB',
        '<strong>no ante, bounty or deal</strong>',
        'small blind shoves, covering you',
        '30 BB excess is not part of the pot',
        '<strong>9 / 20 = 45%</strong>',
        '<strong>$12.286143</strong>',
        '<strong>$21.785714</strong>',
        '<strong>$12.286143 / $21.785714 ≈ 56.40%</strong>',
        'A deliberately invented 50% chance',
        'No opponent range or actual hand has been assigned that 50%',
        'mark the chart comparison <strong>unresolved</strong>',
        'not a new solver run, a measured win rate',
        'different blinds and antes',
        'Use these materials only for after-play study.',
    ):
        if required not in body:
            problems.append('missing or altered scenario boundary: ' + required)
    if '\u2014' in body:
        problems.append('new copy contains em dash')
    return problems


class PokerSolverFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/poker/evaluating-poker-advice.html').read_text()
        cls.public = (ROOT / 'poker/evaluating-poker-advice/index.html').read_text()

    def test_one_direct_answer_and_old_guide_anchors(self):
        for html in (self.source, self.public):
            with self.subTest(public=html is self.public):
                self.assertEqual(answer_errors(html), [])
                nodes = Nodes(html)
                self.assertEqual(nodes.ids.count(ANCHOR), 1)
                self.assertEqual(nodes.links.count('#' + ANCHOR), 1)
                self.assertLess(html.index('id="match-the-spot"'), html.index('id="' + ANCHOR + '"'))
                self.assertLess(html.index('id="' + ANCHOR + '"'), html.index('id="watch-the-edit"'))
                for old in ('name-the-claim', 'match-the-spot', 'watch-the-edit',
                            'compare-explanations', 'one-study-output', 'guide-sources'):
                    self.assertEqual(nodes.ids.count(old), 1, old)

    def test_reproduced_exact_fraction_example_is_not_a_solver_strategy(self):
        script = runpy.run_path(str(ROOT / 'downloads/ten-bb-bubble-icm.py'))
        case = script['example']()
        self.assertEqual(case['before_posting_bb'], (40, 30, 20, 10))
        self.assertEqual(case['prizes_dollars'], (50, 30, 20, 0))
        self.assertEqual(case['ante_bb'], 0)
        self.assertEqual(case['hero_additional_call_bb'], 9)
        self.assertEqual(case['contested_final_pot_bb'], 20)
        self.assertEqual(F(9, 20) * 100, 45)
        self.assertEqual(case['classic_icm_threshold_exact'], '76518591/135682300')
        self.assertAlmostEqual(case['classic_icm_call_threshold_percent'], 56.395411192, places=7)
        self.assertLess(F(9, 20), F(1, 2))
        self.assertLess(F(1, 2), F(76518591, 135682300))
        self.assertIn('real_portland_meadows_range_or_icm_result', case)
        self.assertTrue(case['real_portland_meadows_range_or_icm_result'].startswith('unknown'))

    def test_canonical_article_revision_and_three_native_entry_links(self):
        target = ROUTE + '#' + ANCHOR
        for path in ('_source/poker/home.html', 'poker/index.html',
                     '_source/poker/resources.html', 'poker/resources/index.html',
                     '_source/poker/reading-preflop-charts.html',
                     'poker/reading-preflop-charts/index.html'):
            with self.subTest(path=path):
                self.assertEqual(Nodes((ROOT / path).read_text()).links.count(target), 1)
        manifest = json.loads((ROOT / '_source/pages.json').read_text())
        record = next(p for p in manifest if p['path'] == ROUTE)
        self.assertEqual((record['date'], record['updated']), ('2026-10-08', '2026-11-19'))
        self.assertIn('How to Evaluate Poker Solver Advice', record['seo_title'])
        self.assertIn('10 BB bubble example', record['description'])
        self.assertIn('<link rel="canonical" href="' + URL + '">', self.public)
        schemas = [json.loads(s) for s in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        self.assertNotIn('FAQPage', [x.get('@type') for x in schemas])
        article = next(x for x in schemas if x.get('@type') == 'Article')
        self.assertEqual(article['datePublished'], '2026-10-08')
        self.assertEqual(article['dateModified'], '2026-11-19')
        self.assertEqual(article['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        sitemap = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        matches = [x for x in sitemap if x.findtext('{*}loc') == URL]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext('{*}lastmod'), '2026-11-19')

    def test_negative_mutations_catch_unjustified_solver_verdicts(self):
        source = self.source
        mutations = (
            source.replace('A deliberately invented 50% chance', 'An observed 50% win rate', 1),
            source.replace('No opponent range or actual hand has been assigned that 50%',
                           'The player always has that 50%', 1),
            source.replace('not a new solver run, a measured win rate',
                           'a verified solver conclusion and win rate', 1),
            source.replace('<strong>9 / 20 = 45%</strong>', '<strong>9 / 20 = 56.40%</strong>', 1),
            source.replace('different blinds and antes', 'identical conditions', 1),
            source.replace('href="' + METHOD + '"', 'href="/poker/"', 1),
            source.replace('href="' + PROVIDER + '"', 'href="https://fake.example"', 1),
        )
        for edited in mutations:
            with self.subTest(mutated=edited != source):
                self.assertNotEqual(edited, source)
                self.assertTrue(answer_errors(edited))


if __name__ == '__main__':
    unittest.main()
