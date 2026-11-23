"""Turn 103: exact branch-by-branch satellite equity when a call can tie.

The mathematical tests require only the standard library. Site checks use the
matching complete repository and retain the original no-tie exercise.
"""
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
from html.parser import HTMLParser
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source/poker/satellite-bubble-seat-equity.html'
PUBLIC = ROOT / 'poker/satellite-bubble-seat-equity/index.html'
NAV_LINK = '<a href="#sat-tie-branch">Include split pots</a>'
BRANCH = re.compile(r'<details class="poker-details" id="sat-tie-branch" data-reading-optional="true">.*?</details>', re.S)
FOLD = (11, 9, 1)
WIN = (0, 20, 1)
TIE = (10, 10, 1)
LOSS = (20, 0, 1)


def seat_values(stacks):
    """Exact equal-seat ICM over the finishing orders of active players."""
    if len(stacks) != 3 or any(s < 0 for s in stacks) or sum(stacks) != 21:
        raise ValueError('Expected a three-player, 21 BB model state')
    alive = tuple(i for i, s in enumerate(stacks) if s > 0)
    if len(alive) < 2:
        raise ValueError('At least two eligible survivors are required')
    values = [F(0)] * 3
    for order in permutations(alive):
        total = sum(stacks)
        probability = F(1)
        for i in order:
            probability *= F(stacks[i], total)
            total -= stacks[i]
        for i in order[:2]:
            values[i] += probability
    return tuple(values)


def call_values(w, t, l):
    if min(w, t, l) < 0 or w + t + l != 1:
        raise ValueError('Need three nonnegative probabilities summing to one')
    weights = (w, t, l)
    branches = (WIN, TIE, LOSS)
    chips = sum(weight * stacks[1] for weight, stacks in zip(weights, branches))
    seats = sum(weight * seat_values(stacks)[1] for weight, stacks in zip(weights, branches))
    return chips, seats


class SatelliteTieMath(unittest.TestCase):
    def test_all_four_states_conserve_chips_and_both_seats(self):
        for state in (FOLD, WIN, TIE, LOSS):
            with self.subTest(state=state):
                self.assertEqual(sum(state), 21)
                self.assertEqual(sum(seat_values(state)), 2)
                self.assertTrue(all(0 <= value <= 1 for value in seat_values(state)))
        self.assertEqual(seat_values(FOLD), (F(33,35), F(129,140), F(19,140)))
        self.assertEqual(seat_values(WIN), (F(0), F(1), F(1)))
        self.assertEqual(seat_values(LOSS), (F(1), F(0), F(1)))

    def test_equal_split_keeps_three_players_and_is_not_half_a_seat(self):
        self.assertEqual(TIE, (10,10,1))
        self.assertEqual(seat_values(TIE), (F(431,462),F(431,462),F(31,231)))
        third = F(10,21)*F(1,11) + F(1,21)*F(10,20)
        self.assertEqual(third, F(31,462))
        self.assertEqual(seat_values(TIE)[1], 1-third)
        self.assertNotEqual(seat_values(TIE)[1], F(1,2))

    def test_equal_chip_equity_does_not_identify_seat_value(self):
        a = (F(9,10), F(0), F(1,10))
        b = (F(17,20), F(1,10), F(1,20))
        fold = seat_values(FOLD)[1]
        self.assertEqual(a[0]+a[1]/2, b[0]+b[1]/2)
        self.assertEqual(a[0]+a[1]/2, F(9,10))
        self.assertEqual(call_values(*a), (F(18),F(9,10)))
        self.assertEqual(call_values(*b), (F(18),F(2179,2310)))
        self.assertLess(call_values(*a)[1], fold)
        self.assertGreater(call_values(*b)[1], fold)
        self.assertEqual(call_values(*a)[1]-fold, -F(3,140))
        self.assertEqual(call_values(*b)[1]-fold, F(101,4620))
        self.assertEqual(call_values(*a)[0]-FOLD[1], 9)
        self.assertEqual(call_values(*b)[0]-FOLD[1], 9)

    def test_fixed_tie_rate_break_even_is_conditional(self):
        t = F(1,10)
        w = seat_values(FOLD)[1] - t*seat_values(TIE)[1]
        self.assertEqual(w, F(1913,2310))
        self.assertEqual(w+t/2, F(4057,4620))
        self.assertEqual(call_values(w,t,1-w-t)[1], seat_values(FOLD)[1])
        self.assertEqual(call_values(F(129,140),F(0),F(11,140))[1], seat_values(FOLD)[1])
        self.assertAlmostEqual(float(w)*100,82.81,places=2)
        self.assertAlmostEqual(float(w+t/2)*100,87.81,places=2)

    def test_invalid_probability_combinations_are_not_silently_normalized(self):
        for values in ((F(9,10),F(1,10),F(1,10)), (F(1),F(1,10),-F(1,10)), (F(0),F(0),F(0))):
            with self.subTest(values=values), self.assertRaises(ValueError):
                call_values(*values)


class BranchMarkup(HTMLParser):
    """Parse the small disclosure without needing a site-wide build."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))

    def handle_data(self, data):
        self.parts.append(data)


def markup_errors(fragment):
    parser = BranchMarkup()
    parser.feed(fragment)
    tags = [tag for tag, _ in parser.tags]
    words = ' '.join(' '.join(parser.parts).split())
    required = (
        'same chip equity have different seat values', 'All three players survive',
        '31 / 462', '431 / 462', '93.29%', '129 / 140',
        '90% win, 0% tie, 10% loss', '85% win, 10% tie, 5% loss',
        '2179 / 2310', '94.33%', '2.14 percentage points below folding',
        '2.19 percentage points above folding', 'Both calls gain 9 BB',
        '1913 / 2310', '82.81%', '4057 / 4620', '87.81%',
        'Neither distribution is an estimate', 'Study after play only',
    )
    errors = [f'Missing: {phrase}' for phrase in required if phrase not in words]
    if tags.count('details') != 1 or tags.count('summary') != 1 or tags[:2] != ['details','summary']:
        errors.append('Expected a single native, labelled disclosure')
    if any(tag in ('form','script','iframe','table','input') for tag in tags):
        errors.append('No new script, form, data inputs or scrolling table')
    if chr(0x2014) in fragment:
        errors.append('Prohibited punctuation')
    if not parser.tags or parser.tags[0][1].get('id') != 'sat-tie-branch':
        errors.append('Missing stable deep link')
    if 'open' in parser.tags[0][1]:
        errors.append('Keep advanced answer disclosure collapsed on initial view')
    return errors


class SatelliteTieSiteIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.public = PUBLIC.read_text(encoding='utf-8')

    def test_shared_native_disclosure_and_link_are_exactly_once(self):
        authored = BRANCH.findall(self.source)
        generated = BRANCH.findall(self.public)
        self.assertEqual(len(authored), 1)
        self.assertEqual(authored, generated)
        self.assertEqual(markup_errors(authored[0]), [])
        for content in (self.source,self.public):
            self.assertEqual(content.count(NAV_LINK),1)
            self.assertEqual(content.count('class="poker-details viewer-question"'),8)
            self.assertEqual(content.count('class="short-stack-table" role="region" tabindex="0"'),3)
            self.assertIn('q = 129 / 140',content)
            self.assertLess(content.index('id="sat-call"'),content.index('id="sat-tie-branch"'))
            self.assertLess(content.index('id="sat-tie-branch"'),content.index('id="sat-payouts"'))
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/satellite-bubble-seat-equity/">',self.public)

    def test_native_finder_keeps_exercise_answers_out_of_existing_snippets(self):
        sys.path.insert(0,str(ROOT/'_scripts'))
        import poker_finder
        prior = BRANCH.sub('',self.source,count=1).replace(NAV_LINK,'',1)
        self.assertEqual(poker_finder.GuideText(prior).sections,
                         poker_finder.GuideText(self.source).sections)

    def test_generated_article_manual_registration_and_no_actions(self):
        sys.path.insert(0,str(ROOT/'_scripts'))
        import build
        self.assertEqual(build.build_outputs()[Path('poker/satellite-bubble-seat-equity/index.html')],self.public)
        runner = (ROOT/'_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn103_satellite_tie_branch.py',runner)
        workflows = ROOT/'.github/workflows'
        self.assertFalse(workflows.exists() and any(p.suffix.lower() in ('.yaml','.yml') for p in workflows.iterdir() if p.is_file()))


if __name__ == '__main__':
    unittest.main()
