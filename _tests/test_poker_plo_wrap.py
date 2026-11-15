"""Turn 15: PLO-high legal-hand, card-removal and published-fixture guards."""

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph

SCRIPT = ROOT / 'downloads/poker-plo-wrap-enumerator.py'
spec = spec_from_file_location('poker_plo_wrap', SCRIPT)
plo = module_from_spec(spec)
spec.loader.exec_module(plo)


class PLOWrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'plo-wrap-redraw-blockers'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_manifest_and_generated_discovery(self):
        matches = [page for page in self.pages if page['path'] == self.route]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['date'], '2026-11-15')
        self.assertTrue(matches[0]['poker_guide'])
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for path in ('poker/library/index.html', 'poker/find/index.html',
                     'poker/topics/variants/index.html',
                     'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertTrue(self.route in self.outputs[Path(path)], path)
        self.assertIn('/poker/topics/variants/',
                      self.outputs[Path('poker/topics/index.html')])

    def test_explicit_source_and_scope(self):
        for phrase in ('exactly two', 'exactly three', '52 − 7 = 45',
                       '14 / 41 = 34.15%', '11 / 40 = 27.5%',
                       '29 / 40 = 72.5%', 'not guaranteed winning outs',
                       'fictional', 'Prepared with AI assistance',
                       'not Omaha hi-lo', 'not a recommended bet'):
            self.assertIn(phrase.lower(), self.article.lower(), phrase)
        for source in ('pokerstars.com/poker/games/omaha/',
                       'pokerstars.com/poker/learn/lesson/plo-rules/',
                       'wsoponline.com/mi/learn-to-play-poker/omaha/rules/'):
            self.assertIn(source, self.article)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_accessible_no_script_learning(self):
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count(
            'class="short-stack-table" role="region" tabindex="0"'), 2)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 2)
        self.assertIn('poker-short-stack.css?v=', self.article)
        self.assertIn('/downloads/poker-plo-wrap-enumerator.py', self.article)
        self.assertIn('/downloads/poker-plo-after-play-review.md', self.article)
        for anchor in ('#plo-construction', '#plo-wrap', '#plo-blockers',
                       '#plo-redraw', '#plo-decisions', '#plo-practice', '#plo-download'):
            self.assertIn(anchor, self.article)

    def test_five_card_ranking_handles_flush_wheel_and_full_house(self):
        plo.run_checks()
        self.assertEqual(plo.five_card_high(('As', '2d', '3c', '4s', '5h')), (4, 5))
        self.assertEqual(plo.five_card_high(('Ts', 'Js', 'Qs', 'Ks', 'As')), (8, 14))
        self.assertGreater(plo.five_card_high(('2h', '2c', '2s', '3s', '3d')),
                           plo.five_card_high(('Ah', 'Kh', 'Qh', 'Jh', '8h')))

    def test_holdem_four_board_flush_is_illegal_in_omaha(self):
        score = plo.best_omaha_high(('As', 'Kd', 'Qc', 'Jh'),
                                    ('2s', '7s', '9s', 'Js', '3d'))
        self.assertLess(score[0], 5)
        with self.assertRaisesRegex(ValueError, 'duplicated'):
            plo.best_omaha_high(('As', 'Kd', 'Qc', 'Jh'),
                                ('As', '7s', '9s'))

    def test_wrap_ranks_confirmed_independently_from_exposed_cards(self):
        original = plo.wrap_next_card_completions()
        expected = {rank + suit for rank, n in {'K': 4, 'Q': 3, '9': 3,
                                               '8': 3, '7': 3}.items()
                    for suit in 'cdhs'
                    if rank + suit not in set(plo.WRAP_HERO + plo.WRAP_FLOP)}
        self.assertEqual(set(original), expected)
        self.assertEqual(len(expected), 16)
        self.assertEqual(len(plo.remaining_cards(plo.WRAP_HERO, plo.WRAP_FLOP)), 45)
        self.assertEqual(Counter(card[0] for card in original),
                         Counter({'K': 4, 'Q': 3, '9': 3, '8': 3, '7': 3}))

    def test_blocked_cards_change_both_numerator_and_denominator(self):
        blocked = plo.wrap_next_card_completions(plo.BLOCKER_OPPONENT)
        self.assertEqual(set(plo.wrap_next_card_completions()) - set(blocked),
                         {'Kd', 'Qd'})
        self.assertEqual(len(blocked), 14)
        self.assertEqual(len(plo.remaining_cards(
            plo.WRAP_HERO, plo.WRAP_FLOP, plo.BLOCKER_OPPONENT)), 41)

    def test_redraw_unique_cards_and_no_ties(self):
        result = plo.redraw_river_outcomes()
        self.assertEqual(set(result['opponent']),
                         {'2c', '3c', '4c', '5c', '6c', '7c',
                          '9c', 'Jc', 'Qc', 'Qd', 'Qh'})
        self.assertEqual((len(result['opponent']), len(result['hero']),
                          len(result['tie'])), (11, 29, 0))
        self.assertEqual(len(set(sum((list(v) for v in result.values()), []))), 40)
        self.assertEqual(plo.best_omaha_high(plo.WRAP_HERO, plo.REDRAW_TURN), (4, 12))

    def test_inbound_links_and_no_missing_primary_topic(self):
        graph = poker_link_graph.scan(ROOT)
        record = next(r for r in graph['records'] if r['slug'] == self.slug)
        for source in ('omaha-and-mixed-games', 'omaha-hi-lo-workshop',
                       'poker-math-reference', 'reading-the-board',
                       'flush-and-redraw'):
            self.assertIn('/poker/' + source + '/', record['prose_inbound_guides'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())


if __name__ == '__main__':
    unittest.main()
