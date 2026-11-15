"""Turn 13: independently audit fixed KO / PKO cash and side-pot accounting."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


def bounty_split(target, prior_own, immediate_fraction):
    """Model a single eligible knockout under an explicitly supplied split."""
    cash_now = target * immediate_fraction
    progress = target - cash_now
    return cash_now, progress, prior_own + progress


def side_pots(contributions):
    """Return each distinct contribution tier with its eligible players."""
    pots = []
    previous = Fraction(0)
    for cap in sorted(set(contributions)):
        eligible = tuple(i for i, amount in enumerate(contributions) if amount >= cap)
        amount = (cap - previous) * len(eligible)
        if len(eligible) > 1:
            pots.append((amount, eligible))
        previous = cap
    return tuple(pots)


class BountyKnockoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'bounty-knockout-equity'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_canonical_metadata_and_discovery(self):
        matches = [p for p in self.pages if p['path'] == self.route]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]['poker_guide'])
        self.assertEqual(matches[0]['date'], '2026-11-15')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for output in ('poker/library/index.html', 'poker/find/index.html',
                       'poker/topics/tournaments/index.html',
                       'poker/topics/strategy/index.html', 'poker/feed.xml',
                       'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(output)], output)

    def test_research_limits_and_original_assumptions_are_clear(self):
        for phrase in ('After-play study only', 'fictional', 'no rake',
                       'no ties', 'ordinary finishing-position',
                       'separate model', 'bounty stage', 'not itself a completed',
                       'no real-hand recommendation', 'Prepared with AI assistance',
                       'promise of gambling profit'):
            self.assertIn(phrase.lower(), self.article.lower())
        for official_source in (
            'pokerstars.com/help/articles/trn-knockout/213401/',
            'pokerstars.com/help/articles/trn-elimination-bounty/182700/',
            'holdemresources.net/blog/hrc-1v4-update-knockout-bounty/',
            'blog.gtowizard.com/bounty-models-explained-solving-knockout-tournaments/',
        ):
            self.assertIn(official_source, self.article)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_accessible_study_interfaces(self):
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count(
            'class="short-stack-table" role="region" tabindex="0"'), 4)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 4)
        self.assertIn('poker-short-stack.css?v=', self.article)
        for fragment in ('#bounty-rules', '#bounty-single', '#bounty-chain',
                         '#bounty-side', '#bounty-prob', '#bounty-model',
                         '#bounty-practice', '#bounty-record'):
            self.assertIn(fragment, self.article)

    def test_fixed_ko_pays_entire_target_bounty(self):
        cash, added, own = bounty_split(Fraction(80), Fraction(80), Fraction(1))
        self.assertEqual((cash, added, own), (80, 0, 80))
        self.assertIn('<strong>$80</strong></td><td><strong>$0</strong></td>',
                      self.article)

    def test_pko_pays_half_and_adds_half_to_own_marker(self):
        cash, added, own = bounty_split(Fraction(80), Fraction(40), Fraction(1, 2))
        self.assertEqual((cash, added, own), (40, 40, 80))
        self.assertIn('<strong>$40</strong></td><td><strong>$40</strong></td>',
                      self.article)
        self.assertIn('not another cash receipt', self.article)

    def test_two_consecutive_knockouts_do_not_duplicate_cash(self):
        cash1, increment1, head1 = bounty_split(80, 40, Fraction(1, 2))
        cash2, increment2, head2 = bounty_split(60, head1, Fraction(1, 2))
        self.assertEqual((cash1, increment1, head1), (40, 40, 80))
        self.assertEqual((cash2, increment2, head2), (30, 30, 110))
        self.assertEqual(cash1 + cash2, 70)
        self.assertEqual(increment1 + increment2, 70)
        self.assertEqual(head2, 40 + increment1 + increment2)
        self.assertIn('$40 + $30 = <strong>$70</strong>', self.article)
        self.assertIn('$80 + $30 = <strong>$110</strong>', self.article)

    def test_three_player_preflop_betting_is_legal_and_conserves_chips(self):
        starting = (Fraction(4), Fraction(14), Fraction(9))  # X, hero, Y
        posted = (Fraction(0), Fraction(1, 2), Fraction(1))
        initial_total = sum(starting)
        self.assertEqual(initial_total, 27)
        self.assertEqual(sum(posted), Fraction(3, 2))
        # Button X shoves to four. Hero SB calls to four.
        self.assertEqual(Fraction(4) - posted[1], Fraction(7, 2))
        # Y BB raises from four to nine: +5, larger than X's +3.
        self.assertGreaterEqual(Fraction(9) - 4, Fraction(4) - 1)
        self.assertEqual(Fraction(9) - posted[2], 8)
        self.assertEqual(Fraction(9) - 4, 5)  # Hero final call increment
        self.assertEqual(tuple(Fraction(x) for x in (4, 9, 9)), (4, 9, 9))
        self.assertEqual(starting[1] - 9, 5)  # Unwagered hero stack
        pots = side_pots((Fraction(4), Fraction(9), Fraction(9)))
        self.assertEqual(pots, ((12, (0, 1, 2)), (10, (1, 2))))
        self.assertEqual(sum(amount for amount, _ in pots) + 5, initial_total)
        self.assertIn('12 + 10 + 5 = 27 BB', self.article)

    def test_shortest_player_wins_main_and_hero_wins_side(self):
        # X strongest, hero second, Y weakest. Main = X; side = hero.
        final = (12, 10 + 5, 0)
        self.assertEqual(final, (12, 15, 0))
        self.assertEqual(sum(final), 27)
        cash, added, _ = bounty_split(60, 40, Fraction(1, 2))
        self.assertEqual((cash, added), (30, 30))
        self.assertIn('12 / 15 / 0 BB', self.article)
        self.assertIn("Y's $60 pays you <strong>$30 cash</strong>", self.article)
        self.assertIn("X keeps their $80 marker", self.article)

    def test_covering_opponent_wins_both_pots(self):
        # Y strongest, hero second, X weakest. Y eliminates X.
        final = (0, 5, 12 + 10)
        self.assertEqual(final, (0, 5, 22))
        self.assertEqual(sum(final), 27)
        self.assertIn('0 / 5 / 22 BB', self.article)
        self.assertIn('Y eliminates X', self.article)

    def test_hero_wins_both_pots_and_two_bounties(self):
        final = (0, 12 + 10 + 5, 0)
        self.assertEqual(final, (0, 27, 0))
        self.assertEqual(sum(final), 27)
        cash = 0
        head = 40
        for target in (80, 60):
            award, _, head = bounty_split(target, head, Fraction(1, 2))
            cash += award
        self.assertEqual((cash, head), (70, 110))
        self.assertIn('0 / 27 / 0 BB', self.article)
        self.assertIn('Their combined $140 pays <strong>$70 cash</strong>',
                      self.article)

    def test_conditional_expected_immediate_cash_is_not_total_ev(self):
        p = Fraction(2, 5)
        fixed, _, _ = bounty_split(80, 80, Fraction(1))
        pko, on_head, _ = bounty_split(80, 40, Fraction(1, 2))
        self.assertEqual(p * fixed, 32)
        self.assertEqual(p * pko, 16)
        self.assertEqual(p * on_head, 16)
        self.assertIn('0.40 × $80', self.article)
        self.assertIn('0.40 × $40', self.article)
        self.assertIn('not</em> another $16 expected cash', self.article)
        self.assertIn('not a total action EV', self.article)

    def test_inbound_study_paths_and_prose_link_graph(self):
        graph = poker_link_graph.scan(ROOT)
        new = next(r for r in graph['records'] if r['slug'] == self.slug)
        for source in ('tournament-formats', 'tournament-equity',
                       'short-stack-decisions', 'satellite-bubble-seat-equity',
                       'choosing-a-tournament', 'reading-preflop-charts',
                       'limped-multiway-pots', 'pot-odds-workshop',
                       'practice-room'):
            self.assertIn('/poker/' + source + '/', new['prose_inbound_guides'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())
        self.assertTrue(new['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(new['inbound_count'], 9)
        self.assertGreaterEqual(new['outbound_count'], 8)
        self.assertEqual(sum(not r['reachable_from_poker_entrypoints']
                             for r in graph['records']), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
