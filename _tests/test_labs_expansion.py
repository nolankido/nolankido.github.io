"""Independent case arithmetic plus source-bound discovery and outline contracts."""
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET
import unittest
from test_site import ROOT, Page, build
from test_viewer_guides import best
from poker_reading import section_outline, next_reads, NEXT_READS
import poker_library
import check_live

NEW = ['flush-and-redraw', 'side-pot-lab']


def settle(contributions, scores):
    """Independent pot-layer oracle: unmatched one-person layers are refunds."""
    awards = [Fraction(0) for _ in contributions]
    pots, refunds = [], []
    previous = 0
    for level in sorted(set(contributions)):
        eligible = [i for i, amount in enumerate(contributions) if amount >= level]
        total = (level - previous) * len(eligible)
        if len(eligible) == 1:
            awards[eligible[0]] += total
            refunds.append((eligible[0], total))
        else:
            highest = max(scores[i] for i in eligible)
            winners = [i for i in eligible if scores[i] == highest]
            for winner in winners:
                awards[winner] += Fraction(total, len(winners))
            pots.append((total, eligible))
        previous = level
    return awards, pots, refunds


class LabsExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.entries = poker_library.load(ROOT, cls.pages)

    def content(self, slug):
        return self.outputs[Path('poker') / slug / 'index.html']

    def fixture(self, slug):
        return next(attrs for tag, attrs in Page(self.content(slug)).elements if 'data-case-a' in attrs)

    def test_new_cases_are_in_every_discovery_path(self):
        study = self.content('study')
        hub = self.content('decision-labs')
        feed = ET.fromstring(self.outputs[Path('poker/feed.xml')])
        links = {item.findtext('link') for item in feed.findall('./channel/item')}
        for slug in NEW:
            route = '/poker/' + slug + '/'
            page = next(p for p in self.pages if p['path'] == route)
            self.assertEqual(page['date'], '2026-10-06')
            self.assertTrue(page['poker_guide'])
            for directory in [study, hub, self.content('library'), self.outputs[Path('poker/index.html')]]:
                self.assertIn(route, directory)
            self.assertIn('https://nolankido.com' + route, links)
            self.assertIn(route, check_live.targets())
        self.assertEqual(len(self.entries), 24)
        self.assertIn('/poker/decision-labs/', check_live.targets())
        self.assertIn('/poker/decision-lab/', hub)
        self.assertIn('/poker/decision-labs/', self.content('decision-lab'))

    def test_published_cards_and_all_rivers_match_the_answers(self):
        f = self.fixture('flush-and-redraw')
        a, b, board = (f['data-case-' + key].split() for key in ['a', 'b', 'board'])
        self.assertEqual(len(set(a + b + board)), 9)
        scores = [(best(a + board[:n]), best(b + board[:n])) for n in [3, 4, 5]]
        self.assertEqual([left > right for left, right in scores], [False, True, False])
        self.assertEqual(scores[1][0][0], 5)
        self.assertEqual(scores[2][1], (6, 9, 2))
        deck = {r + s for r in '23456789TJQKA' for s in 'cdhs'}
        remaining = deck - set(a + b + board[:4])
        losing = {river for river in remaining if best(a + board[:4] + [river]) < best(b + board[:4] + [river])}
        tied = {river for river in remaining if best(a + board[:4] + [river]) == best(b + board[:4] + [river])}
        self.assertEqual(len(remaining), 44)
        self.assertEqual(losing, set('9s 7c 7d 7s 2h 2d 2s 4c 4d 4s'.split()))
        self.assertEqual(tied, set())
        for numerator in [len(losing), len(remaining) - len(losing)]:
            self.assertIn(f'{100 * numerator / len(remaining):.1f}%', self.content('flush-and-redraw'))
        self.assertEqual(set(f['data-case-losing'].split()), losing)
        self.assertIn('2h', losing)
        alternate = f['data-case-alt-b'].split()
        remaining = deck - set(a + alternate + board[:4])
        wins = [r for r in remaining if best(alternate + board[:4] + [r]) > best(a + board[:4] + [r])]
        ties = [r for r in remaining if best(alternate + board[:4] + [r]) == best(a + board[:4] + [r])]
        self.assertEqual(set(wins), set('9d 9s 7d 7s'.split()))
        self.assertFalse(ties)
        self.assertIn('4 / 44 = 9.1%', self.content('flush-and-redraw'))
        self.assertIn('34 / 44 = 77.3%', self.content('flush-and-redraw'))
        self.assertIn('aria-label="Player A: ace and jack of hearts"', self.content('flush-and-redraw'))
        self.assertIn('aria-label="Player B: two nines"', self.content('flush-and-redraw'))

    def test_side_pot_eligibility_refund_and_chip_conservation(self):
        f = self.fixture('side-pot-lab')
        board = f['data-case-board'].split()
        hands = [f['data-case-' + k].split() for k in ['a', 'b', 'c']]
        self.assertEqual(len(set(sum(hands, []) + board)), 11)
        scores = [best(hand + board) for hand in hands]
        self.assertGreater(scores[0], scores[1]); self.assertGreater(scores[1], scores[2])
        amounts = list(map(int, f['data-case-contributions'].split()))
        awards, pots, refunds = settle(amounts, scores)
        self.assertEqual(pots, [(18, [0, 1, 2]), (16, [1, 2])])
        self.assertEqual(refunds, [(2, 11)])
        self.assertEqual(awards, [18, 16, 11])
        self.assertEqual(sum(awards), sum(amounts))
        self.assertEqual([awards[i] - amounts[i] for i in range(3)], [12, 2, -14])
        text = self.content('side-pot-lab')
        for phrase in ['18 BB', '16 BB', '11 BB', '+12 BB', '+2 BB', '−14 BB', '18 + 16 + 11 = 45 BB']:
            self.assertIn(phrase, text)
        alternate, alternate_pots, alternate_refunds = settle([4, 10, 16], scores)
        self.assertEqual((alternate, alternate_pots, alternate_refunds), ([12, 12, 6], [(12, [0, 1, 2]), (12, [1, 2])], [(2, 6)]))
        for amounts in [[1, 3, 6], [5, 5, 5], [5, 7, 7]]:
            for strengths in [[3, 2, 1], [1, 2, 3], [1, 1, 1]]:
                out, _, _ = settle(amounts, strengths)
                self.assertEqual(sum(out), sum(amounts))

    def test_answers_start_closed_and_have_no_runtime_instrumentation(self):
        for slug, expected in [('flush-and-redraw', 5), ('side-pot-lab', 4)]:
            content = self.content(slug)
            panels = [a for a in Page(content).tags('details') if 'lab-answer' in a.get('class', '')]
            self.assertEqual(len(panels), expected)
            self.assertTrue(all('open' not in a for a in panels))
            source = (ROOT / '_source/poker' / (slug + '.html')).read_text()
            for phrase in ['fictional', 'After-play', 'Prepared with AI assistance.', 'References and limits']:
                self.assertIn(phrase, source)
            for bad in ['<script', '<form', '<iframe', 'data-umami-event', chr(0x2014)]:
                self.assertNotIn(bad, source)
            for a in Page(content).tags('span'):
                if 'reader-playing-card' in a.get('class', ''):
                    self.assertEqual(a['role'], 'img')
                    self.assertIn(' of ', a['aria-label'])

    def test_outline_uses_visible_existing_anchors_and_not_answers(self):
        source = '<h2 id="intro">Intro</h2><h2 id="first">A &amp; B</h2><details><h2 id="secret">Secret result</h2></details><div hidden><h2 id="hidden">Not shown</h2></div><h2 id="second">Second <em>step</em></h2>'
        result = section_outline(source)
        self.assertIn('A &amp; B', result)
        self.assertIn('Second step', result)
        self.assertIn('href="#first"', result)
        self.assertNotIn('secret', result); self.assertNotIn('hidden', result)
        self.assertNotIn('href="#intro"', result)
        self.assertNotIn(' open', result)
        self.assertEqual(section_outline('<h2 id="one">One</h2>'), '')
        count = 0
        for entry in self.entries:
            page = next(p for p in self.pages if p['path'] == entry['route'])
            source = (ROOT / '_source' / page['source']).read_text()
            outline = section_outline(source)
            rendered = self.outputs[build.output_path(entry['route'])]
            if outline:
                count += 1
                self.assertIn(outline, rendered)
                ids = {a.get('id') for _, a in Page(rendered).elements}
                for link in Page(outline).tags('a'):
                    self.assertIn(link['href'][1:], ids)
        self.assertGreater(count, 15)
        for path, content in self.outputs.items():
            if path.suffix == '.html' and not str(path).startswith('poker/'):
                self.assertNotIn('reader-outline', content)

    def test_related_guides_are_curated_complete_and_never_self_referential(self):
        slugs = {e['slug'] for e in self.entries}
        self.assertEqual(slugs, set(NEXT_READS))
        for entry in self.entries:
            chosen = next_reads(entry, self.entries)
            self.assertEqual(len(chosen), 2)
            self.assertEqual([e['slug'] for e in chosen], list(NEXT_READS[entry['slug']]))
            self.assertTrue(all(e['slug'] != entry['slug'] for e in chosen))
            self.assertTrue(set(NEXT_READS[entry['slug']]) <= slugs)
        creator = next(e for e in self.entries if e['slug'] == 'hand-to-vlog')
        self.assertEqual([e['slug'] for e in next_reads(creator, self.entries)], ['reviewing-a-hand', 'variance-and-results'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
