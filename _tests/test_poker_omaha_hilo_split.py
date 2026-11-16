"""Turn 17: independently constructed Omaha/8 highs, lows, awards and links."""

from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


def load_script(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hilo = load_script('poker_omaha_hilo_split', ROOT / 'downloads/poker-omaha-hilo-split-enumerator.py')
prior = load_script('poker_plo_wrap_high', ROOT / 'downloads/poker-plo-wrap-enumerator.py')


class OmahaHiLoSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'omaha-hilo-scoop-quarter-counterfeit'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_manifest_search_topics_feeds_and_canonical(self):
        entries = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0]['poker_guide'])
        self.assertEqual(entries[0]['date'], '2026-11-15')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for output in ('poker/library/index.html', 'poker/find/index.html',
                       'poker/topics/variants/index.html', 'poker/topics/strategy/index.html',
                       'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(output)], output)

    def test_accessible_practice_and_offline_assets(self):
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count('class="short-stack-table" role="region" tabindex="0"'), 3)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 3)
        self.assertIn('poker-short-stack.css?v=', self.article)
        for suffix in ('poker-omaha-hilo-split-enumerator.py',
                       'poker-omaha-hilo-split-review.md'):
            self.assertIn('/downloads/' + suffix, self.article)
            self.assertTrue((ROOT / 'downloads' / suffix).is_file())
        for anchor in ('#hilo-rules', '#hilo-quarter', '#hilo-scoop', '#hilo-nolow',
                       '#hilo-counterfeit', '#hilo-protect', '#hilo-review',
                       '#hilo-practice', '#hilo-download'):
            self.assertIn(anchor, self.article)

    def test_rule_sources_and_false_certainty_guardrails(self):
        for phrase in ('pokerstars.com/poker/games/omaha/high-low/',
                       'pokerstars.com/help/articles/po-game-rules-m/217177/',
                       'exactly two', 'three board cards', 'fictional',
                       'not a model of live betting', 'not a statement about',
                       '225 / 75 / 0', '3 / 40 = 7.5%', '37 / 40 = 92.5%',
                       '52 − 12 = 40', 'Prepared with AI assistance'):
            self.assertIn(phrase.lower(), self.article.lower(), phrase)
        self.assertNotIn('\N{EM DASH}', self.article)
        self.assertNotIn('\N{EM DASH}', (ROOT / 'downloads/poker-omaha-hilo-split-review.md').read_text())

    def test_straight_flush_and_low_scoring(self):
        self.assertEqual(hilo.high_five(('As', '2d', '3c', '4h', '5s')), (4, 5))
        self.assertEqual(hilo.high_five(('As', '2s', '3s', '4s', '5s')), (8, 5))
        self.assertEqual(hilo.low_five(('As', '2s', '3s', '4s', '5s')), (5, 4, 3, 2, 1))
        self.assertIsNone(hilo.low_five(('Ac', 'Ah', '3s', '4c', '5d')))
        self.assertIsNone(hilo.low_five(('As', '2d', '3s', '4c', '9h')))
        self.assertLess(hilo.low_five(('As', '2d', '3s', '5c', '7h')),
                        hilo.low_five(('Ah', '3d', '4s', '5h', '7c')))

    def test_quarter_uses_disjoint_hole_pairs_for_high_and_low(self):
        a_high, a_low = hilo.omaha_scores(hilo.QUARTER_PLAYERS['A'], hilo.QUARTER_BOARD)
        self.assertEqual(a_high, (7, 14, 13))
        self.assertEqual(a_low, (5, 4, 3, 2, 1))
        self.assertEqual(hilo.omaha_scores(hilo.QUARTER_PLAYERS['B'], hilo.QUARTER_BOARD),
                         ((4, 5), (5, 4, 3, 2, 1)))
        self.assertIsNone(hilo.omaha_scores(hilo.QUARTER_PLAYERS['C'], hilo.QUARTER_BOARD)[1])
        self.assertEqual(hilo.awards(hilo.QUARTER_PLAYERS, hilo.QUARTER_BOARD, 300),
                         {'A': Fraction(225), 'B': Fraction(75), 'C': Fraction(0)})

    def test_scoop_and_high_is_straight_not_trips(self):
        self.assertEqual(hilo.omaha_scores(hilo.SCOOP_PLAYERS['A'], hilo.SCOOP_BOARD),
                         ((4, 5), (5, 4, 3, 2, 1)))
        self.assertEqual(hilo.omaha_scores(hilo.SCOOP_PLAYERS['B'], hilo.SCOOP_BOARD)[1],
                         (7, 6, 3, 2, 1))
        self.assertEqual(hilo.awards(hilo.SCOOP_PLAYERS, hilo.SCOOP_BOARD),
                         {'A': Fraction(240), 'B': Fraction(0)})

    def test_no_low_means_high_wins_all(self):
        self.assertTrue(all(hilo.omaha_scores(holes, hilo.NO_LOW_BOARD)[1] is None
                            for holes in hilo.NO_LOW_PLAYERS.values()))
        self.assertEqual(hilo.awards(hilo.NO_LOW_PLAYERS, hilo.NO_LOW_BOARD),
                         {'A': Fraction(240), 'B': Fraction(0)})

    def test_turn_low_and_three_counterfeiting_rivers(self):
        self.assertEqual(hilo.omaha_scores(hilo.TURN_A, hilo.TURN_BOARD)[1], (7, 5, 3, 2, 1))
        self.assertEqual(hilo.omaha_scores(hilo.TURN_B, hilo.TURN_BOARD)[1], (7, 5, 4, 3, 1))
        result = hilo.faceup_low_rivers(hilo.TURN_A, hilo.TURN_B)
        self.assertEqual(set(result['rival']), {'2c', '2d', '2h'})
        self.assertEqual((len(result['hero']), len(result['rival']),
                          len(result['tie']), len(result['neither'])), (37, 3, 0, 0))
        self.assertEqual(len(hilo.remaining(hilo.TURN_A, hilo.TURN_B, hilo.TURN_BOARD)), 40)

    def test_counterfeit_is_not_low_disqualification_or_guaranteed_quarter(self):
        board = hilo.TURN_BOARD + (hilo.COUNTERFEIT_RIVER,)
        self.assertEqual(hilo.omaha_scores(hilo.TURN_A, board)[1], (7, 5, 3, 2, 1))
        self.assertEqual(hilo.omaha_scores(hilo.TURN_B, board),
                         ((4, 5), (5, 4, 3, 2, 1)))
        self.assertEqual(hilo.awards({'A': hilo.TURN_A, 'B': hilo.TURN_B}, board),
                         {'A': Fraction(0), 'B': Fraction(240)})
        self.assertEqual(hilo.omaha_scores(hilo.TURN_A_PROTECTED, board),
                         ((4, 5), (5, 4, 3, 2, 1)))
        self.assertEqual(hilo.awards({'A': hilo.TURN_A_PROTECTED, 'B': hilo.TURN_B}, board),
                         {'A': Fraction(120), 'B': Fraction(120)})

    def test_exact_pot_conservation_with_ties_and_no_low(self):
        for board, players, chips in (
            (hilo.QUARTER_BOARD, hilo.QUARTER_PLAYERS, 301),
            (hilo.SCOOP_BOARD, hilo.SCOOP_PLAYERS, 241),
            (hilo.NO_LOW_BOARD, hilo.NO_LOW_PLAYERS, 239),
            (hilo.TURN_BOARD + ('2h',), {'A': hilo.TURN_A_PROTECTED, 'B': hilo.TURN_B}, 241),
        ):
            result = hilo.awards(players, board, chips)
            self.assertEqual(sum(result.values()), Fraction(chips))
            self.assertTrue(all(isinstance(award, Fraction) for award in result.values()))

    def test_reject_duplicate_cards_bad_hand_or_bad_pot(self):
        with self.assertRaises(ValueError):
            hilo.omaha_scores(('As', 'As', '5c', '9d'), ('2h', '3d', '7s'))
        with self.assertRaises(ValueError):
            hilo.awards({'A': hilo.TURN_A, 'B': hilo.TURN_B}, hilo.TURN_BOARD)
        with self.assertRaises(ValueError):
            hilo.awards(hilo.SCOOP_PLAYERS, hilo.SCOOP_BOARD, -1)
        with self.assertRaises(ValueError):
            hilo.awards({'A': hilo.SCOOP_PLAYERS['A'], 'B': hilo.SCOOP_PLAYERS['A']},
                        hilo.SCOOP_BOARD)

    def test_prior_independent_omaha_high_evaluator(self):
        for board, players in ((hilo.QUARTER_BOARD, hilo.QUARTER_PLAYERS),
                               (hilo.SCOOP_BOARD, hilo.SCOOP_PLAYERS),
                               (hilo.NO_LOW_BOARD, hilo.NO_LOW_PLAYERS)):
            for holes in players.values():
                self.assertEqual(hilo.omaha_scores(holes, board)[0],
                                 prior.best_omaha_high(holes, board))
        for river in hilo.remaining(hilo.TURN_A, hilo.TURN_B, hilo.TURN_BOARD):
            board = hilo.TURN_BOARD + (river,)
            for hand in (hilo.TURN_A, hilo.TURN_B):
                self.assertEqual(hilo.omaha_scores(hand, board)[0],
                                 prior.best_omaha_high(hand, board), river)

    def test_inbound_and_outbound_prose_links(self):
        graph = poker_link_graph.scan(ROOT)
        record = next(item for item in graph['records'] if item['slug'] == self.slug)
        for source in ('omaha-hi-lo-workshop', 'omaha-and-mixed-games',
                       'plo-wrap-redraw-blockers', 'plo-nut-flush-paired-board',
                       'stud-and-lowball-workshop', 'poker-math-reference',
                       'range-combinations', 'multiway-pot-workshop'):
            self.assertIn('/poker/' + source + '/', record['prose_inbound_guides'])
        for destination in ('omaha-hi-lo-workshop', 'omaha-and-mixed-games',
                            'stud-and-lowball-workshop', 'poker-math-reference',
                            'pot-odds-workshop', 'multiway-pot-workshop'):
            self.assertIn('/poker/' + destination + '/', record['prose_outbound_guides'])
        self.assertTrue(record['reachable_from_poker_entrypoints'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())


if __name__ == '__main__':
    unittest.main()
