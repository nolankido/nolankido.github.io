"""Turn 104: exact conditional mystery-bounty draws and unchanged reader paths.

The arithmetic tests use standard-library rational numbers and enumerate labelled
physical envelopes, including repeated cash amounts. The site checks require the
matching complete repository. This is a fictional study fixture, not a player model.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
from html.parser import HTMLParser
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source/poker/bounty-knockout-equity.html'
PUBLIC = ROOT / 'poker/bounty-knockout-equity/index.html'
NAV_LINK = '<a href="#bounty-mystery-draw">Mystery draw inventory</a>'
BRANCH = re.compile(r'<details class="poker-details" id="bounty-mystery-draw" data-reading-optional="true">.*?</details>', re.S)
ENVELOPES = (50, 50, 50, 100, 100, 650)


def mean_award(envelopes):
    if not envelopes or any(type(value) is not int or value < 0 for value in envelopes):
        raise ValueError('Need a nonempty inventory of nonnegative integer awards')
    return F(sum(envelopes), len(envelopes))


def expected_receipt(envelopes, chance):
    if not 0 <= chance <= 1:
        raise ValueError('Draw probability must be between zero and one')
    return chance * mean_award(envelopes)


def remove_award(envelopes, award):
    remaining = list(envelopes)
    remaining.remove(award)
    return tuple(remaining)


class MysteryBountyMath(unittest.TestCase):
    def test_inventory_counts_and_weighted_cash_mean(self):
        self.assertEqual(Counter(ENVELOPES), {50: 3, 100: 2, 650: 1})
        self.assertEqual(sum(ENVELOPES), 1000)
        self.assertEqual(mean_award(ENVELOPES), F(500, 3))
        self.assertNotIn(F(500, 3), ENVELOPES)
        self.assertNotEqual(mean_award(ENVELOPES), F(50 + 100 + 650, 3))
        self.assertEqual(F(ENVELOPES.count(650), len(ENVELOPES)), F(1, 6))

    def test_earning_a_draw_and_receiving_jackpot_are_different_events(self):
        self.assertEqual(expected_receipt(ENVELOPES, F(2, 5)), F(200, 3))
        self.assertEqual(F(2, 5) * F(1, 6), F(1, 15))
        self.assertEqual(expected_receipt(ENVELOPES, 0), 0)
        self.assertEqual(expected_receipt(ENVELOPES, 1), F(500, 3))

    def test_remaining_prize_value_changes_after_each_possible_award(self):
        for first, total, expected, jackpot_probability in (
            (650, 350, 70, F(0)), (50, 950, 190, F(1, 5)), (100, 900, 180, F(1, 5))
        ):
            with self.subTest(first=first):
                remaining = remove_award(ENVELOPES, first)
                self.assertEqual(len(remaining), 5)
                self.assertEqual(sum(remaining), total)
                self.assertEqual(sum(remaining) + first, 1000)
                self.assertEqual(mean_award(remaining), expected)
                self.assertEqual(F(remaining.count(650), len(remaining)), jackpot_probability)

    def test_two_guaranteed_draws_are_without_replacement(self):
        # Distinguish physical envelopes even when their awards are identical.
        paths = tuple(permutations(range(len(ENVELOPES)), 2))
        self.assertEqual(len(paths), 30)
        self.assertTrue(all(a != b for a, b in paths))
        payout = sum(ENVELOPES[a] + ENVELOPES[b] for a, b in paths)
        self.assertEqual(F(payout, len(paths)), F(1000, 3))
        jackpot_paths = sum(650 in (ENVELOPES[a], ENVELOPES[b]) for a, b in paths)
        self.assertEqual(F(jackpot_paths, len(paths)), F(1, 3))
        self.assertNotEqual(F(jackpot_paths, len(paths)), 1-F(5, 6)**2)
        self.assertEqual(sum(ENVELOPES[b] for _, b in paths) * F(1, len(paths)), F(500, 3))

    def test_total_expectation_of_second_draw_uses_conditional_inventory(self):
        self.assertEqual(F(3, 6)*190 + F(2, 6)*180 + F(1, 6)*70, F(500, 3))

    def test_invalid_inventory_or_probability_is_rejected(self):
        for inventory in ((), (-1, 50), (True, 50), (1.5, 50)):
            with self.subTest(inventory=inventory), self.assertRaises(ValueError):
                mean_award(inventory)
        for chance in (-F(1, 10), F(11, 10)):
            with self.subTest(chance=chance), self.assertRaises(ValueError):
                expected_receipt(ENVELOPES, chance)
        with self.assertRaises(ValueError):
            remove_award(ENVELOPES, 500)


class FragmentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            self.errors.append('Unbalanced tag: ' + tag)

    def handle_data(self, data):
        self.text.append(data)


def markup_errors(fragment):
    parsed = FragmentParser()
    parsed.feed(fragment)
    errors = list(parsed.errors)
    if parsed.stack:
        errors.append('Unclosed tags')
    tags = [tag for tag, _ in parsed.tags]
    prose = ' '.join(' '.join(parsed.text).split())
    if tags[:2] != ['details', 'summary'] or tags.count('details') != 1 or tags.count('summary') != 1:
        errors.append('Expected exactly one native labelled disclosure')
    if not parsed.tags or parsed.tags[0][1].get('id') != 'bounty-mystery-draw' or 'open' in parsed.tags[0][1]:
        errors.append('Expected stable anchor and initially collapsed exercise')
    if any(tag not in {'details', 'summary', 'div', 'h3', 'p', 'ul', 'li', 'strong'} for tag in tags):
        errors.append('Only static, accessible learning markup is allowed')
    for phrase in (
        'fictional mystery-bounty event', 'equally likely to be drawn', 'without replacement',
        '6 envelopes and $1,000', '$500 / 3 ≈ $166.67', '1 / 6', '$200 / 3 ≈ $66.67',
        '1 / 15 ≈ 6.67%', '$350 / 5 = $70', '$950 / 5 = $190', '$900 / 5 = $180',
        '$1,000 / 3 ≈ $333.33', '1 / 3', 'two draws from this same inventory are already guaranteed',
        'not guaranteed', 'Neither the jackpot nor the expected receipt is a complete call or shove EV', 'if they are unknown, leave the number unresolved',
        'Study after play only',
    ):
        if phrase not in prose:
            errors.append('Missing required evidence boundary or numeric result: ' + phrase)
    if any(key.startswith('on') or key in ('src', 'href', 'style') for _, attrs in parsed.tags for key in attrs):
        errors.append('Unexpected script, external asset or inline behavior')
    if chr(0x2014) in fragment:
        errors.append('Prohibited punctuation')
    return errors


class MysteryBountySiteIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.public = PUBLIC.read_text(encoding='utf-8')

    def test_matching_native_disclosure_and_jump_link(self):
        authored, public = BRANCH.findall(self.source), BRANCH.findall(self.public)
        self.assertEqual(len(authored), 1)
        self.assertEqual(authored, public)
        self.assertEqual(markup_errors(authored[0]), [])
        for content in (self.source, self.public):
            self.assertEqual(content.count(NAV_LINK), 1)
            self.assertEqual(content.count('class="poker-details viewer-question"'), 8)
            self.assertEqual(content.count('class="short-stack-table" role="region" tabindex="0"'), 4)
            self.assertLess(content.index('id="bounty-model"'), content.index('id="bounty-mystery-draw"'))
            self.assertLess(content.index('id="bounty-mystery-draw"'), content.index('id="bounty-practice"'))
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/bounty-knockout-equity/">', self.public)

    def test_finder_indexes_only_the_optional_title_without_answers(self):
        sys.path.insert(0, str(ROOT/'_scripts'))
        import poker_finder
        before = BRANCH.sub('', self.source, count=1).replace(NAV_LINK, '', 1)
        title = 'Advanced example (extra reading time): mystery bounty draw inventory. What is a mystery bounty worth after the jackpot has been drawn?'
        expected = {'anchor':'bounty-mystery-draw', 'title':title, 'text':title}
        sections = poker_finder.GuideText(self.source).sections
        self.assertEqual(sections, poker_finder.GuideText(before).sections + [expected])
        self.assertNotIn('$1,000 / 3', repr(sections))

    def test_build_parity_manual_registration_and_no_actions(self):
        sys.path.insert(0, str(ROOT/'_scripts'))
        import build
        self.assertEqual(build.build_outputs()[Path('poker/bounty-knockout-equity/index.html')], self.public)
        runner = (ROOT/'_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn104_mystery_bounty_inventory.py', runner)
        workflows = ROOT/'.github/workflows'
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yml', '.yaml') for p in workflows.iterdir()))


if __name__ == '__main__':
    unittest.main()
