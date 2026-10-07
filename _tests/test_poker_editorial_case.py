"""Evidence and reader-path contracts for the concrete public-page editing case."""
from fractions import Fraction
from pathlib import Path
import re
import unittest
from test_site import Page, ROOT, build

# Visible in the prior public hand-review page at production f2f5cebc.
# This is a quotation of the site's fictional ledger, not a private hand note.
PREVIOUS_LEDGER = ('The pot is now 14.5 BB: 5.5 + 2 + 7. '
                   'The button faces 5 BB more to call, not 7 BB.')


class PokerEditorialCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.hand = cls.outputs[Path('poker/reviewing-a-hand/index.html')]
        cls.case = cls.outputs[Path('poker/hand-to-vlog/index.html')]

    def test_snapshot_matches_the_unchanged_ledger(self):
        pot = Fraction('2.5') * 2 + Fraction('0.5') + 2 + 7
        call = 7 - 2
        self.assertEqual(pot, Fraction('14.5'))
        self.assertEqual(call, 5)
        snapshot = re.search(r'<dl class="reader-pot-strip">(.*?)</dl>', self.hand, re.S).group(1)
        facts = re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', snapshot)
        self.assertEqual(facts, [('Acting player', 'Button'),
                                ('Pot before the response', '14.5 BB'),
                                ('Additional amount to call', '5 BB')])
        self.assertIn(PREVIOUS_LEDGER, self.hand)
        self.assertIn('30 big blinds effective at the start', self.hand)
        for card in ['K♠', 'Q♠', 'Q♦', '8♣', '3♥']:
            self.assertIn(card, self.hand)

    def test_snapshot_is_inside_the_fictional_example_before_cards_and_ledger(self):
        self.assertLess(self.hand.index('class="fictional-hand"'), self.hand.index('id="decision-summary"'))
        self.assertLess(self.hand.index('id="decision-summary"'), self.hand.index('<figure class="hand-illustration">'))
        self.assertLess(self.hand.index('id="decision-summary"'), self.hand.index('id="pot-ledger"'))
        self.assertIn('role="group" aria-label="Fictional decision snapshot"', self.hand)
        self.assertIn('href="#decision-summary">See the worked hand', self.hand)

    def test_before_quote_and_after_fields_are_grounded_in_the_actual_page(self):
        self.assertIn('<blockquote><p>' + PREVIOUS_LEDGER + '</p></blockquote>', self.case)
        for label, value in [('Acting player', 'Button'), ('Pot before the response', '14.5 BB'),
                             ('Additional amount to call', '5 BB')]:
            self.assertIn(f'<dt>{label}</dt><dd>{value}</dd>', self.case)
        self.assertIn('Its arithmetic was already consistent.', self.case)
        self.assertIn('presentation change, not the discovery of a miscounted pot', self.case)

    def test_case_has_specific_scope_and_no_invented_research_result(self):
        self.assertIn('The page edit is real; the hand is fictional.', self.case)
        self.assertIn('no audience test or improvement in comprehension is claimed', self.case)
        self.assertIn('not a recovered tournament note, a vlog screenshot', self.case)
        source = (ROOT / '_source/poker/hand-to-vlog.html').read_text()
        for forbidden in ['<script', '<iframe', '<form', 'data-umami-event', chr(0x2014)]:
            self.assertNotIn(forbidden, source)
        self.assertIn('Prepared with AI assistance.', self.case)

    def test_overview_case_and_decision_are_connected(self):
        home = self.outputs[Path('poker/index.html')]
        self.assertIn('href="/poker/hand-to-vlog/#behind-the-edit">See one explanation before and after', home)
        self.assertIn('id="behind-the-edit"', self.case)
        self.assertIn('role="group" aria-label="Before and after the page edit"', self.case)
        self.assertIn('href="/poker/reviewing-a-hand/#decision-summary"', self.case)
        self.assertIn('href="/poker/reviewing-a-hand/#pot-ledger"', self.case)
        self.assertIn('href="#behind-the-edit">See an actual page edit', self.case)

    def test_previous_guide_fragments_and_reference_links_are_retained(self):
        ids = {attrs.get('id') for _, attrs in Page(self.case).elements}
        self.assertTrue({'hand-story', 'select', 'reconstruct', 'narration', 'graphics',
                         'episode', 'publish', 'behind-the-edit', 'edit-case-title'} <= ids)
        ids = {attrs.get('id') for _, attrs in Page(self.hand).elements}
        self.assertTrue({'record', 'decision', 'example-title', 'pot-ledger', 'assumptions',
                         'alternatives', 'after-the-session', 'review-sheet', 'decision-summary'} <= ids)
        self.assertIn('href="/downloads/poker-episode-plan.md" download', self.case)
        self.assertIn('href="/poker/viewer-questions/#graphics"', self.case)


if __name__ == '__main__':
    unittest.main()
