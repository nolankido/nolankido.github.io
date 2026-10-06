"""Independent arithmetic, editorial and discovery contracts for after-play workshops."""
from fractions import Fraction
from html.parser import HTMLParser
from itertools import combinations
from math import comb
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import unittest
from test_site import Page, ROOT, build
import check_live

SLUGS = ['pot-odds-workshop', 'short-stack-decisions', 'tournament-equity', 'range-combinations', 'variance-and-results', 'hand-to-vlog', 'practice-room']
DOWNLOADS = ['poker-short-stack-record.md', 'poker-results-review.md', 'poker-episode-plan.md', 'poker-study-cycle.md']

class Words(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.parts = []; self.feed(text)
    def handle_data(self, data): self.parts.append(data)
    def text(self): return ' '.join(self.parts)

class WorkshopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.texts = {slug: cls.outputs[Path('poker') / slug / 'index.html'] for slug in SLUGS}

    def test_substantial_original_content_and_explicit_scope(self):
        total = 0
        for slug in SLUGS:
            source = (ROOT / '_source/poker' / (slug + '.html')).read_text(encoding='utf-8')
            count = len(Words(source).text().split()); total += count
            with self.subTest(slug=slug):
                self.assertGreater(count, 650)
                for phrase in ['fictional', 'Prepared with AI assistance.', 'References and limits', 'After-play']:
                    self.assertIn(phrase.lower(), source.lower())
                for forbidden in ['<form', '<iframe', '<script', 'data-umami-event', chr(0x2014)]:
                    self.assertNotIn(forbidden, source)
        self.assertGreater(total, 6500)

    def test_manifest_feed_sitemap_and_reading_paths_agree(self):
        study = self.outputs[Path('poker/study/index.html')]
        feed = ET.fromstring(self.outputs[Path('poker/feed.xml')])
        links = {i.findtext('link') for i in feed.findall('./channel/item')}
        targets = check_live.targets()
        for slug in SLUGS:
            route = '/poker/' + slug + '/'
            page = next(p for p in build.public_pages() if p['path'] == route)
            with self.subTest(slug=slug):
                self.assertEqual(page['date'], '2026-10-06')
                self.assertTrue(page['poker_guide'])
                self.assertIn(route, study)
                self.assertIn(route, targets)
                self.assertIn('https://nolankido.com' + route, links)
                self.assertIn(route, self.outputs[Path('sitemap.xml')])
                self.assertIn('/poker/study/', self.texts[slug])
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.texts[slug], re.S).group(1))
                self.assertEqual(schema['@type'], 'Article')
                self.assertEqual(schema['datePublished'], '2026-10-06')
        home = self.outputs[Path('poker/index.html')]
        for route in ['/poker/short-stack-decisions/', '/poker/practice-room/', '/poker/hand-to-vlog/']:
            self.assertIn(route, home)
        self.assertNotIn('All seven guides', home)
        self.assertNotIn('Seven deeper guides', home)

    def test_twelve_closed_practice_answers_and_stable_anchors(self):
        content = self.texts['practice-room']
        tags = Page(content)
        panels = [a for a in tags.tags('details') if 'workshop-question' in a.get('class', '')]
        self.assertEqual(len(panels), 12)
        self.assertTrue(all('open' not in a for a in panels))
        for index in range(1, 13): self.assertIn(f'Reveal answer {index:02d}:', content)
        ids = {a.get('id') for _, a in tags.elements}
        for key in ['price-check', 'combo-check', 'spot-check', 'icm-check', 'results-check', 'story-check']:
            self.assertIn(key, ids)

    def test_downloads_are_blank_private_use_and_live_checked(self):
        study = self.outputs[Path('poker/study/index.html')]
        for name in DOWNLOADS:
            source = (ROOT / 'downloads' / name).read_text(encoding='utf-8')
            self.assertIn('/downloads/' + name, study)
            self.assertIn('/downloads/' + name, check_live.targets())
            self.assertIn('private', source.lower())
            self.assertNotIn(chr(0x2014), source)
        self.assertIn('before revealing the answers', (ROOT / 'downloads/poker-study-cycle.md').read_text())

    def test_call_and_raise_prices_match_published_work(self):
        content = self.texts['pot-odds-workshop']
        self.assertEqual(Fraction(10, 20 + 10 + 10), Fraction(1, 4))
        self.assertEqual(Fraction(3, 10) * 40 - 10, 2)
        extra = 14 - 4; current = 10 + 4 + 14; final = current + extra
        self.assertEqual((extra, current, final), (10, 28, 38))
        self.assertIn(f'{100 * extra / final:.1f}%', content)
        for bet in [3, 4, 6, 9, 12, 24]:
            self.assertIn(str(12 + 2 * bet) + ' BB', content)
        self.assertEqual(Fraction(6, 10 + 6), Fraction(3, 8))
        self.assertEqual(Fraction(2, 5) * 10 - Fraction(3, 5) * 6, Fraction(2, 5))
        for phrase in ['37.5%', '+0.4 BB', '27.3%']: self.assertIn(phrase, content)
        practice = self.texts['practice-room']
        for value in [Fraction(8, 34), Fraction(5, 13), Fraction(5, 18)]:
            self.assertIn(f'{float(value) * 100:.1f}%', practice)

    def test_draw_model_by_independent_enumeration(self):
        # Ordered draws of two distinct physical unseen cards; first nine are targets.
        hits = sum(a < 9 or b < 9 for a in range(47) for b in range(47) if a != b)
        probability = Fraction(hits, 47 * 46)
        self.assertEqual(probability, 1 - Fraction(38, 47) * Fraction(37, 46))
        for value in [Fraction(9, 47), probability]:
            self.assertIn(f'{float(value) * 100:.1f}%', self.texts['pot-odds-workshop'])

    def test_range_counts_from_the_physical_deck(self):
        cards = [r + s for r in '23456789TJQKA' for s in 'cdhs']
        known = set('As Qc Ah 7d 2c 9s 3h'.split())
        pairs = list(combinations([c for c in cards if c not in known], 2))
        self.assertEqual(len(known), 7); self.assertEqual(len(pairs), 990)
        aa = [p for p in pairs if p[0][0] == p[1][0] == 'A']
        ak = [p for p in pairs if {c[0] for c in p} == {'A', 'K'}]
        kqs = [p for p in pairs if {c[0] for c in p} == {'K', 'Q'} and p[0][1] == p[1][1]]
        self.assertEqual((len(aa), len(ak), len(kqs)), (1, 8, 3))
        self.assertEqual(sum(a[1] == b[1] for a, b in ak), 2)
        self.assertEqual(comb(52, 2), 1326)
        self.assertEqual(13 * comb(4, 2) + 78 * 4 + 78 * 12, 1326)
        from test_viewer_guides import best
        hero = 'As Qc'.split(); board = 'Ah 7d 2c 9s 3h'.split()
        self.assertTrue(all(best(hero + board) < best(list(p) + board) for p in aa + ak))
        self.assertTrue(all(best(hero + board) > best(list(p) + board) for p in kqs))
        content = self.texts['range-combinations']
        for phrase in ['1,326', '990', '78 pair combinations', '312 suited combinations', '936 offsuit combinations', '14.3%']:
            self.assertIn(phrase, content)
        self.assertEqual(Fraction(3, 2) / (9 + Fraction(3, 2)), Fraction(1, 7))

    def test_icm_by_finish_order_enumeration(self):
        from itertools import permutations
        def equities(stacks, prizes):
            values = [Fraction(0) for _ in stacks]
            for order in permutations(range(len(stacks))):
                chance = Fraction(1); remaining = sum(stacks)
                for player in order:
                    chance *= Fraction(stacks[player], remaining)
                    remaining -= stacks[player]
                for rank, player in enumerate(order): values[player] += chance * prizes[rank]
            return values
        before = equities([10, 10, 10], [50, 30, 20])
        surviving = equities([20, 10], [50, 30])
        self.assertEqual(before, [Fraction(100, 3)] * 3)
        self.assertEqual(surviving, [Fraction(130, 3), Fraction(110, 3)])
        q = (before[0] - 20) / (surviving[0] - 20)
        self.assertEqual(q, Fraction(4, 7))
        expected = Fraction(55, 100) * surviving[0] + Fraction(45, 100) * 20
        self.assertEqual(expected - before[0], Fraction(-1, 2))
        for value in [before[0], surviving[0], surviving[1], expected]:
            self.assertIn(f'${float(value):.2f}', self.texts['tournament-equity'])
        self.assertIn('57.14%', self.texts['tournament-equity'])
        self.assertIn('7.14 percentage points', self.texts['tournament-equity'])

    def test_results_and_probability_arithmetic(self):
        cost = 12 * 200; returned = 3100; profit = returned - cost
        self.assertEqual((cost, profit, profit - 500), (2400, 700, 200))
        content = self.texts['variance-and-results']
        for value in [Fraction(profit, cost), Fraction(2000, 3100), Fraction(9, 10) ** 10, Fraction(9, 10) ** 20]:
            self.assertIn(f'{float(value) * 100:.1f}%', content)
        self.assertEqual(1100 - cost, -1300)
        self.assertEqual(2100 - 6 * 300 - 450, -150)
        self.assertIn('16.7%', self.texts['practice-room'])

if __name__ == '__main__': unittest.main(verbosity=2)
