"""Turn 18: exact seven-card Stud8/razz hand scoring and static-public discovery."""

from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from math import comb
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


def import_script(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stud = import_script('poker_stud8_razz_check', ROOT / 'downloads/poker-stud8-razz-seven-card-check.py')
hilo = import_script('poker_hilo_turn17', ROOT / 'downloads/poker-omaha-hilo-split-enumerator.py')


class Stud8RazzTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'stud-hilo-razz-hand-reading'
        cls.route = f'/poker/{cls.slug}/'
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_manifest_find_topics_feed_sitemap_and_canonical(self):
        entries = [item for item in build.public_pages() if item['path'] == self.route]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['date'], '2026-11-15')
        self.assertTrue(entries[0]['poker_guide'])
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for path in ('poker/library/index.html', 'poker/find/index.html',
                     'poker/topics/variants/index.html', 'poker/topics/strategy/index.html',
                     'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertIn(self.route, self.outputs[Path(path)], path)

    def test_accessibility_and_downloads(self):
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count('class="short-stack-table" role="region" tabindex="0"'), 3)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 3)
        self.assertIn('poker-short-stack.css?v=', self.article)
        for path in ('poker-stud8-razz-seven-card-check.py',
                     'poker-stud8-razz-seven-card-review.md'):
            self.assertIn('/downloads/' + path, self.article)
            self.assertTrue((ROOT / 'downloads' / path).is_file())
        for anchor in ('#stud-low-rules', '#stud-low-quarter', '#stud-low-scoop',
                       '#stud-low-switch', '#stud-low-ties', '#stud-low-streets',
                       '#stud-low-removal', '#stud-low-review', '#stud-low-practice',
                       '#stud-low-download'):
            self.assertIn(anchor, self.article)

    def test_rules_provenance_and_scope(self):
        for phrase in ('pokerstars.com/poker/games/stud/high-low/',
                       'pokerstars.com/poker/games/razz/',
                       'pokerstars.com/help/articles/po-game-rules-m/217177/',
                       'C(7,5) = 21', 'fictional', 'no shared', 'no eight-or-better qualifier',
                       'A 225, B 75, C 0', 'A 200, B 0', 'A 0, B 200',
                       '52 − 6 = 46', 'Prepared with AI assistance',
                       'not Nolan\'s hands'):
            self.assertIn(phrase.lower(), self.article.lower(), phrase)
        self.assertNotIn('\N{EM DASH}', self.article)
        for filename in ('poker-stud8-razz-seven-card-check.py',
                         'poker-stud8-razz-seven-card-review.md'):
            self.assertNotIn('\N{EM DASH}', (ROOT / 'downloads' / filename).read_text())

    def test_21_subsets_high_and_qualifying_low_independent(self):
        self.assertEqual(comb(7, 5), 21)
        a = stud.QUARTER_PLAYERS['A']
        self.assertEqual(stud.seven_scores(a)[:2],
                         ((5, 14, 7, 4, 3, 2), (0, 5, 4, 3, 2, 1)))
        self.assertIn(('As', '2s', '3s', '4s', '7s'), tuple(combinations(a, 5)))
        self.assertEqual(stud.rank_high_five(('As', '2s', '3s', '4s', '7s'))[0], 5)
        self.assertEqual(stud.ace_five_five(('As', '2s', '3s', '4s', '5h')),
                         (0, 5, 4, 3, 2, 1))

    def test_stud8_three_way_quarter(self):
        scored = {name: stud.seven_scores(hand) for name, hand in stud.QUARTER_PLAYERS.items()}
        self.assertEqual(scored['B'][:2], ((4, 5), (0, 5, 4, 3, 2, 1)))
        self.assertIsNone(scored['C'][1])
        self.assertEqual(stud.stud8_awards(stud.QUARTER_PLAYERS, 300),
                         {'A': Fraction(225), 'B': Fraction(75), 'C': Fraction(0)})

    def test_low_straight_flush_scoops(self):
        self.assertEqual(stud.seven_scores(stud.SCOOP_PLAYERS['A'])[:2],
                         ((8, 5), (0, 5, 4, 3, 2, 1)))
        self.assertIsNone(stud.seven_scores(stud.SCOOP_PLAYERS['B'])[1])
        self.assertEqual(stud.stud8_awards(stud.SCOOP_PLAYERS, 200),
                         {'A': Fraction(200), 'B': Fraction(0)})

    def test_same_cards_reverse_winner_when_variant_changes(self):
        a, b = stud.VARIANT_PLAYERS['A'], stud.VARIANT_PLAYERS['B']
        self.assertEqual(stud.seven_scores(a)[0], (6, 13, 12))
        self.assertIsNone(stud.seven_scores(a)[1])
        self.assertIsNone(stud.seven_scores(b)[1])
        self.assertEqual(stud.seven_scores(b)[2], (0, 9, 4, 3, 2, 1))
        self.assertEqual(stud.stud8_awards(stud.VARIANT_PLAYERS, 200),
                         {'A': Fraction(200), 'B': Fraction(0)})
        self.assertEqual(stud.razz_awards(stud.VARIANT_PLAYERS, 200),
                         {'A': Fraction(0), 'B': Fraction(200)})

    def test_razz_no_qualifier_and_pair_categories(self):
        self.assertEqual(stud.ace_five_five(('Ac', 'Ad', '8h', '9s', 'Tc')),
                         (1, 1, 10, 9, 8))
        self.assertLess(stud.ace_five_five(('Ac', 'Ad', '8h', '9s', 'Tc')),
                        stud.ace_five_five(('2c', '2d', '3h', '4s', '5c')))
        self.assertLess(stud.ace_five_five(('Kc', 'Qc', 'Jc', 'Tc', '9c')),
                        stud.ace_five_five(('Ac', 'Ad', '2h', '3s', '4c')))
        self.assertLess(stud.ace_five_five(('Kc', 'Kd', '4h', '3s', '2c')),
                        stud.ace_five_five(('Kc', 'Kd', 'Kh', '3s', '2c')))

    def test_razz_wheel_tie_ignores_suit(self):
        scores = [stud.seven_scores(hand)[2] for hand in stud.RAZZ_TIE_PLAYERS.values()]
        self.assertEqual(scores, [(0, 5, 4, 3, 2, 1)] * 2)
        self.assertEqual(stud.razz_awards(stud.RAZZ_TIE_PLAYERS, 200),
                         {'A': Fraction(100), 'B': Fraction(100)})

    def test_street_order_with_third_street_suit_tie(self):
        self.assertEqual(stud.bring_in(stud.THIRD_UPCARDS, 'stud8'), 'A')
        self.assertEqual(stud.bring_in(stud.THIRD_UPCARDS, 'razz'), 'B')
        self.assertEqual(stud.fourth_street_first(stud.FOURTH_UPCARDS, 'stud8'), 'B')
        self.assertEqual(stud.fourth_street_first(stud.FOURTH_UPCARDS, 'razz'), 'A')
        with self.assertRaises(ValueError):
            stud.bring_in({'A': 'Ac', 'B': '3d'}, 'stud8')

    def test_visibility_card_removal_is_not_outs(self):
        self.assertEqual(stud.exposed_rank_count(stud.KNOWN_HERO, stud.OTHER_UPCARDS), (46, 3))
        self.assertEqual(stud.exposed_rank_count(stud.KNOWN_HERO,
                                                 stud.OTHER_UPCARDS_MORE_THREES), (46, 2))
        with self.assertRaises(ValueError):
            stud.exposed_rank_count(('Ah', '4h', '7c'), ('Ah', '3s', 'Kc'))

    def test_exotic_pots_conserve_rational_chips(self):
        for players, awards in ((stud.QUARTER_PLAYERS, stud.stud8_awards),
                                (stud.VARIANT_PLAYERS, stud.stud8_awards),
                                (stud.VARIANT_PLAYERS, stud.razz_awards),
                                (stud.RAZZ_TIE_PLAYERS, stud.razz_awards)):
            result = awards(players, 301)
            self.assertEqual(sum(result.values()), Fraction(301))
            self.assertTrue(all(isinstance(x, Fraction) for x in result.values()))

    def test_bad_duplicate_or_incomplete_card_sets_rejected(self):
        with self.assertRaises(ValueError):
            stud.seven_scores(('As',) * 7)
        with self.assertRaises(ValueError):
            stud.seven_scores(('As', '2c', '3d'))
        with self.assertRaises(ValueError):
            stud.stud8_awards({'A': stud.QUARTER_PLAYERS['A'], 'B': stud.QUARTER_PLAYERS['A']})
        with self.assertRaises(ValueError):
            stud.razz_awards(stud.RAZZ_TIE_PLAYERS, -20)

    def test_independent_turn17_high_and_low_evaluator_on_five_cards(self):
        for players in (stud.QUARTER_PLAYERS, stud.SCOOP_PLAYERS,
                        stud.VARIANT_PLAYERS, stud.RAZZ_TIE_PLAYERS):
            for hand in players.values():
                for five in combinations(hand, 5):
                    self.assertEqual(stud.rank_high_five(five), hilo.high_five(five))
                    expected = hilo.low_five(five)
                    actual = stud.ace_five_five(five)
                    if expected is not None:
                        self.assertEqual(actual, (0, *expected))
                    else:
                        self.assertTrue(actual[0] > 0 or actual[1] > 8)

    def test_9_original_guides_link_into_this_article(self):
        graph = poker_link_graph.scan(ROOT)
        record = next(row for row in graph['records'] if row['slug'] == self.slug)
        for source in ('stud-and-lowball-workshop', 'omaha-and-mixed-games',
                       'omaha-hi-lo-workshop', 'omaha-hilo-scoop-quarter-counterfeit',
                       'poker-math-reference', 'range-combinations', 'multiway-pot-workshop',
                       'reading-the-board', 'poker-rules-and-fair-play'):
            self.assertIn('/poker/' + source + '/', record['prose_inbound_guides'])
        for target in ('stud-and-lowball-workshop', 'omaha-hilo-scoop-quarter-counterfeit',
                       'poker-math-reference', 'poker-rules-and-fair-play',
                       'hand-rankings', 'multiway-pot-workshop'):
            self.assertIn('/poker/' + target + '/', record['prose_outbound_guides'])
        self.assertTrue(record['reachable_from_poker_entrypoints'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())


if __name__ == '__main__':
    unittest.main()
