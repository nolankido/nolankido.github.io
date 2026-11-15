"""Turn 16: PLO-high blocker deal-space and paired-board showdown guards."""

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

SCRIPT = ROOT / 'downloads/poker-plo-flush-pair-enumerator.py'
spec = spec_from_file_location('poker_plo_flush_pair', SCRIPT)
plo = module_from_spec(spec)
spec.loader.exec_module(plo)
prior_spec = spec_from_file_location('poker_plo_wrap', ROOT / 'downloads/poker-plo-wrap-enumerator.py')
prior = module_from_spec(prior_spec)
prior_spec.loader.exec_module(prior)


class PLOFlushPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slug = 'plo-nut-flush-paired-board'
        cls.route = f'/poker/{cls.slug}/'
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_manifest_search_topics_and_feeds(self):
        items = [p for p in self.pages if p['path'] == self.route]
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['poker_guide'])
        self.assertEqual(items[0]['date'], '2026-11-15')
        self.assertIn('https://nolankido.com' + self.route, self.article)
        self.assertIn('"datePublished": "2026-11-15"', self.article)
        for path in ('poker/library/index.html', 'poker/find/index.html',
                     'poker/topics/variants/index.html',
                     'poker/topics/strategy/index.html',
                     'poker/feed.xml', 'writing.xml', 'sitemap.xml'):
            self.assertTrue(self.route in self.outputs[Path(path)], path)

    def test_sources_and_editorial_limits(self):
        for source in ('pokerstars.com/poker/games/omaha/',
                       'pokerstars.com/poker/learn/lesson/plo-rules/',
                       'wsoponline.com/mi/learn-to-play-poker/omaha/rules/'):
            self.assertIn(source, self.article)
        for phrase in ('exactly two', 'exactly three', 'fictional',
                       'not a PLO population frequency',
                       'not an official house ruling',
                       'Prepared with AI assistance',
                       'No table action', '45 unknown cards',
                       '52 − 12 = 40', '148,995', '25,830', '31,185',
                       '6,699', '9 / 40 = 22.5%', '10 / 40 = 25%'):
            self.assertIn(phrase.lower(), self.article.lower(), phrase)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_accessibility_and_offline_downloads(self):
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 8)
        self.assertEqual(self.article.count(
            'class="short-stack-table" role="region" tabindex="0"'), 3)
        self.assertEqual(self.article.count('class="short-stack-scroll-hint"'), 3)
        self.assertIn('poker-short-stack.css?v=', self.article)
        for name in ('poker-plo-flush-pair-enumerator.py', 'poker-plo-flush-after-play.md'):
            self.assertIn('/downloads/' + name, self.article)
            self.assertTrue((ROOT / 'downloads' / name).is_file())
        for anchor in ('#plo-flush-rule', '#plo-flush-blocker', '#plo-flush-deals',
                       '#plo-flush-set', '#plo-flush-pair', '#plo-flush-review',
                       '#plo-flush-practice', '#plo-flush-download'):
            self.assertIn(anchor, self.article)

    def test_one_private_spade_is_not_a_flush(self):
        self.assertLess(plo.omaha_high(plo.ACE_BLOCKER_HERO, plo.MONOTONE_FLOP)[0], 5)
        self.assertEqual(plo.omaha_high(plo.SET_HERO, plo.TURN_BOARD)[0], 5)
        with self.assertRaises(ValueError):
            plo.omaha_high(('As', 'Kh', 'Qd', 'Jc'), ('As', '8s', '3s'))

    def test_four_card_space_not_merely_two_spade_pairs(self):
        self.assertEqual(comb(45, 4), 148995)
        expected_blocked = (comb(9, 2) * comb(36, 2) +
                            comb(9, 3) * comb(36, 1) + comb(9, 4))
        expected_unblocked = (comb(10, 2) * comb(35, 2) +
                              comb(10, 3) * comb(35, 1) + comb(10, 4))
        self.assertEqual(expected_blocked, 25830)
        self.assertEqual(expected_unblocked, 31185)
        self.assertEqual(plo.four_card_flush_holdings(plo.ACE_BLOCKER_HERO)['flush'],
                         expected_blocked)
        self.assertEqual(plo.four_card_flush_holdings(plo.NO_SPADE_HERO)['flush'],
                         expected_unblocked)

    def test_ace_flush_holding_count_by_complement(self):
        self.assertEqual(comb(44, 3) - comb(35, 3), 6699)
        self.assertEqual(plo.four_card_flush_holdings(plo.ACE_BLOCKER_HERO)['ace_flush'], 0)
        self.assertEqual(plo.four_card_flush_holdings(plo.NO_SPADE_HERO)['ace_flush'], 6699)
        self.assertEqual(len(plo.remaining(plo.NO_SPADE_HERO, plo.MONOTONE_FLOP)), 45)

    def test_paired_board_redraw_exact_river_cards(self):
        result = plo.faceup_rivers(plo.SET_HERO, plo.SET_RIVAL)
        expected = {'Qc', '8c', '8d', '8h', '3c', '3d', '3h', '7c', '7s'}
        self.assertEqual(set(result['rival']), expected)
        self.assertEqual((len(result['hero']), len(result['rival']), len(result['tie'])),
                         (31, 9, 0))
        self.assertEqual(len(plo.remaining(plo.SET_HERO, plo.SET_RIVAL, plo.TURN_BOARD)), 40)

    def test_seven_blocker_change_one_river_only(self):
        with_blocker = plo.faceup_rivers(plo.SET_HERO, plo.SET_RIVAL)
        no_blocker = plo.faceup_rivers(plo.NO_SEVEN_BLOCK_HERO, plo.SET_RIVAL)
        self.assertEqual(len(no_blocker['rival']), 10)
        self.assertEqual(set(no_blocker['rival']) - set(with_blocker['rival']), {'7h'})
        self.assertEqual((len(no_blocker['hero']), len(no_blocker['tie'])), (30, 0))

    def test_board_pair_not_automatically_a_full_house(self):
        different_rival = plo.faceup_rivers(plo.SET_HERO, plo.ONE_QUEEN_RIVAL)
        self.assertEqual((len(different_rival['hero']), len(different_rival['rival']),
                          len(different_rival['tie'])), (40, 0, 0))
        river_board = plo.TURN_BOARD + ('8h',)
        self.assertLess(plo.omaha_high(plo.ONE_QUEEN_RIVAL, river_board),
                        plo.omaha_high(plo.SET_HERO, river_board))

    def test_prior_independent_omaha_evaluator_agrees_on_every_river(self):
        # The Turn 15 script independently implements five-card high and Omaha selection.
        for hero, rival in ((plo.SET_HERO, plo.SET_RIVAL),
                            (plo.NO_SEVEN_BLOCK_HERO, plo.SET_RIVAL),
                            (plo.SET_HERO, plo.ONE_QUEEN_RIVAL)):
            for river in plo.remaining(hero, rival, plo.TURN_BOARD):
                board = plo.TURN_BOARD + (river,)
                self.assertEqual(plo.omaha_high(hero, board),
                                 prior.best_omaha_high(hero, board), river)
                self.assertEqual(plo.omaha_high(rival, board),
                                 prior.best_omaha_high(rival, board), river)

    def test_inbound_and_outbound_learning_paths(self):
        graph = poker_link_graph.scan(ROOT)
        record = next(r for r in graph['records'] if r['slug'] == self.slug)
        for source in ('plo-wrap-redraw-blockers', 'omaha-and-mixed-games',
                       'omaha-hi-lo-workshop', 'range-combinations',
                       'reading-the-board', 'poker-math-reference',
                       'flush-and-redraw', 'stud-and-lowball-workshop'):
            self.assertIn('/poker/' + source + '/', record['prose_inbound_guides'])
        self.assertIn('/poker/plo-wrap-redraw-blockers/', record['prose_outbound_guides'])
        self.assertIn(self.route, (ROOT / '_source/poker/study.html').read_text())


if __name__ == '__main__':
    unittest.main()
