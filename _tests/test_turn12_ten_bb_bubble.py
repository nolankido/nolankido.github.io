"""Turn 12: reproducible ten-blind bubble study, with no live-play advice."""

from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import json
import runpy
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / '_source/poker/six-to-ten-bb-tournament-decisions.html'
PUBLIC = ROOT / 'poker/six-to-ten-bb-tournament-decisions/index.html'
SCRIPT = ROOT / 'downloads/ten-bb-bubble-icm.py'
SHEET = ROOT / 'downloads/ten-bb-bubble-study-sheet.md'
HUB = ROOT / '_source/poker/home.html'
ROUTE = '/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble'


def independent_finish_probabilities(stacks):
    """Full finish-order permutation enumeration, distinct from script recursion."""
    outcomes = [[F(0)] * len(stacks) for _ in stacks]
    for order in permutations(range(len(stacks))):
        chance = F(1)
        remaining = sum(stacks)
        for player in order:
            chance *= F(stacks[player], remaining)
            remaining -= stacks[player]
        for finish_place, player in enumerate(order):
            outcomes[player][finish_place] += chance
    return outcomes


class TenBigBlindBubbleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = runpy.run_path(str(SCRIPT))
        cls.output = cls.model['example']()
        cls.source = GUIDE.read_text(encoding='utf-8')
        cls.public = PUBLIC.read_text(encoding='utf-8')
        cls.sheet = SHEET.read_text(encoding='utf-8')
        cls.hub = HUB.read_text(encoding='utf-8')

    def test_independent_enumeration_reproduces_both_icm_branches(self):
        m = self.model
        self.assertEqual((m['START'], m['FOLD'], m['WIN'], m['LOSE']), (
            (40, 30, 20, 10), (41, 30, 20, 9),
            (30, 30, 20, 20), (50, 30, 20, 0),
        ))
        expected = {'fold': F(76518591, 6228040), 'call_win': F(305, 14)}
        for name, stacks in (('fold', m['FOLD']), ('call_win', m['WIN'])):
            finish = independent_finish_probabilities(stacks)
            self.assertEqual(sum(stacks), 100)
            self.assertEqual(sum(sum(row) for row in finish), 4)
            for player in range(4):
                self.assertEqual(tuple(finish[player]), m['finish_probabilities'](stacks, player))
            values = [sum(p * prize for p, prize in zip(finish[player], m['PRIZES']))
                      for player in range(4)]
            self.assertEqual(sum(values), sum(m['PRIZES']))
            self.assertEqual(values[m['HERO']], expected[name])
            self.assertEqual(m['prize_equity'](stacks, m['HERO']), expected[name])
        self.assertEqual(sum(m['LOSE']), 100)
        self.assertEqual(m['LOSE'][m['HERO']], 0)

    def test_chips_and_prize_value_are_different_objectives(self):
        m = self.model
        self.assertEqual(m['START'][m['HERO']], 10)
        self.assertEqual(m['FOLD'][m['HERO']], 9)
        self.assertEqual(m['WIN'][m['HERO']], 20)
        self.assertEqual(F(10 - 1, 20), F(9, 20))
        self.assertEqual(m['example']()['chip_ev_call_threshold_percent'], 45.0)
        prize_threshold = F(76518591, 135682300)
        self.assertEqual(m['prize_equity'](m['FOLD'], m['HERO']) /
                         m['prize_equity'](m['WIN'], m['HERO']), prize_threshold)
        self.assertAlmostEqual(float(prize_threshold * 100), 56.395411192, places=8)
        # A made-up 50% chance is above the chip price but below ICM break-even.
        self.assertGreater(F(1, 2) * 20, m['FOLD'][m['HERO']])
        self.assertLess(F(1, 2) * m['prize_equity'](m['WIN'], m['HERO']),
                        m['prize_equity'](m['FOLD'], m['HERO']))

    def test_public_script_prints_exactly_the_expected_fixed_case(self):
        run = subprocess.run([sys.executable, str(SCRIPT)], check=True,
                             text=True, capture_output=True)
        output = json.loads(run.stdout)
        self.assertEqual(output, json.loads(json.dumps(self.output)))
        self.assertEqual(output['hero_additional_call_bb'], 9)
        self.assertEqual(output['uncalled_small_blind_refund_bb'], 30)
        self.assertEqual(output['contested_final_pot_bb'], 20)
        self.assertEqual(output['classic_icm_threshold_exact'], '76518591/135682300')
        self.assertEqual(output['real_portland_meadows_range_or_icm_result'].split(';')[0], 'unknown')
        script_source = SCRIPT.read_text(encoding='utf-8')
        for forbidden in ('requests', 'urllib', 'socket', 'subprocess', 'open(', 'input('):
            self.assertNotIn(forbidden, script_source)

    def test_one_canonical_page_has_bubble_answer_and_original_source_limits(self):
        self.assertEqual(self.source.count('id="bridge-bubble"'), 1)
        self.assertIn('href="#bridge-bubble"', self.source)
        self.assertIn('id="bridge-bubble"', self.public)
        for required in (
            'Should you shove or call with 10 BB on the bubble?',
            'four players remaining, three paid', 'no ante',
            '9 / 20 = 45%', '$12.286143', '$21.785714', '56.40%',
            '13 remaining and 10 paid', '8,000/15,000',
            '148,000 / 15,000 ≈ 9.87 BB',
            'the record does not establish', 'No numerical ICM or solver verdict',
            '/poker/episodes/portland-meadows-ep1/#hand-64o-record',
            '/poker/practice-room/', '/poker/poker-math-reference/',
            '/poker/free-poker-learning-path/',
            '/downloads/ten-bb-bubble-icm.py',
            '/downloads/ten-bb-bubble-study-sheet.md',
        ):
            self.assertIn(required.lower(), self.source.lower(), required)
        self.assertIn(ROUTE, self.hub)
        self.assertNotIn('\u2014', self.source)

    def test_source_sheet_and_public_metadata_agree(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        entry = next(p for p in pages if p['id'] == 'poker-six-to-ten-bb-tournament-decisions')
        self.assertEqual(entry['date'], '2026-11-15')
        self.assertEqual(entry['updated'], '2026-11-20')
        self.assertIn('bubble ICM', entry['description'])
        self.assertIn('2026-11-18', self.public)  # historical bubble ICM release
        self.assertIn('article:modified_time" content="2026-11-20"', self.public)
        self.assertIn('2026-11-15', self.public)
        library = json.loads((ROOT / '_source/poker/library.json').read_text(encoding='utf-8'))
        cards = library['entries'] if isinstance(library, dict) else library
        card = next(p for p in cards if p['slug'] == 'six-to-ten-bb-tournament-decisions')
        self.assertIn('bubble', card['description'])
        self.assertIn('10bb', card['keywords'])
        for required in ('## 1. Freeze the decision', '## 2. Check a fully fictional',
                         '## 3. Separate the documented live hand',
                         '## 4. Complete your own post-session analysis',
                         'recorded / calculated / assumed / unknown',
                         '13 left, 10 paid', '9.87 BB', 'no ante',
                         '45%', '56.40%', 'before posting'):
            self.assertIn(required.lower(), self.sheet.lower(), required)
        self.assertNotIn('\u2014', self.sheet)
        check_live_source = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertIn('downloads/ten-bb-bubble-icm.py', check_live_source)
        self.assertIn('downloads/ten-bb-bubble-study-sheet.md', check_live_source)


if __name__ == '__main__':
    unittest.main()
