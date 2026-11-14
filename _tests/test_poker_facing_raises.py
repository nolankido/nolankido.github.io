"""Turn 04: audited preflop-response lesson and its native discovery routes."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_link_graph


class FacingRaisesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.slug = 'facing-preflop-raises'
        cls.route = '/poker/' + cls.slug + '/'
        cls.article = cls.outputs[Path('poker') / cls.slug / 'index.html']

    def test_article_is_findable_and_canonically_published(self):
        match = [p for p in self.pages if p['path'] == self.route]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]['date'], '2026-11-14')
        self.assertTrue(match[0]['poker_guide'])
        self.assertIn('https://nolankido.com/poker/facing-preflop-raises/', self.article)
        self.assertIn('"datePublished": "2026-11-14"', self.article)
        for route in ['poker/library/index.html', 'poker/find/index.html',
                      'poker/topics/strategy/index.html', 'poker/topics/learn/index.html',
                      'poker/topics/cash-games/index.html', 'sitemap.xml']:
            self.assertIn(self.route, self.outputs[Path(route)], route)

    def test_fictional_study_scope_and_teachable_answers_are_visible(self):
        self.assertIn('fictional teaching fixtures', self.article)
        self.assertIn('No actual opponent tendencies, solver solution', self.article)
        self.assertIn('Prepared with AI assistance', self.article)
        self.assertIn('2026 rules', self.article)
        self.assertEqual(self.article.count('class="poker-details viewer-question"'), 4)
        self.assertIn('to 15.5 BB total', self.article)
        self.assertIn('as a standalone preflop calling rule', self.article)
        self.assertNotIn('\N{EM DASH}', self.article)

    def test_hand_a_pot_and_spr_are_independently_correct(self):
        blind = Fraction(1, 2) + 1
        open_total = Fraction(5, 2)
        to_call = open_total
        to_threebet = 8
        self.assertEqual(blind + open_total, 4)
        self.assertEqual(blind + open_total + to_call, Fraction(13, 2))
        self.assertEqual(blind + open_total + to_threebet, 12)
        opener_adds = to_threebet - open_total
        self.assertEqual(opener_adds, Fraction(11, 2))
        final_pot = blind + 2 * to_threebet
        self.assertEqual(final_pot, Fraction(35, 2))
        self.assertEqual(Fraction(100 - to_threebet, final_pot), Fraction(184, 35))
        self.assertEqual(Fraction(25 - to_threebet, final_pot), Fraction(34, 35))
        for text in ('4 BB', '6.5 BB', '12 BB', '5.5 BB', '17.5 BB',
                     'SPR) is 92 / 17.5 ≈ 5.26', 'SPR = 17 / 17.5 ≈ 0.97'):
            self.assertIn(text, self.article)

    def test_hand_b_pot_fourbet_and_spr_are_independently_correct(self):
        button_open = Fraction(5, 2)
        bb_threebet = 9
        dead_sb = Fraction(1, 2)
        pot_now = button_open + bb_threebet + dead_sb
        call_more = bb_threebet - button_open
        fourbet_to = 22
        min_fourbet_total = bb_threebet + (bb_threebet - button_open)
        self.assertEqual(pot_now, 12)
        self.assertEqual(call_more, Fraction(13, 2))
        self.assertEqual(pot_now + call_more, Fraction(37, 2))
        self.assertEqual(min_fourbet_total, Fraction(31, 2))
        self.assertEqual(fourbet_to - button_open, Fraction(39, 2))
        self.assertEqual(pot_now + (fourbet_to - button_open), Fraction(63, 2))
        self.assertEqual(fourbet_to - bb_threebet, 13)
        self.assertEqual(2 * fourbet_to + dead_sb, Fraction(89, 2))
        self.assertEqual(Fraction(100 - fourbet_to, 2 * fourbet_to + dead_sb), Fraction(156, 89))
        self.assertEqual(Fraction(100 - bb_threebet, 2 * bb_threebet + dead_sb), Fraction(182, 37))
        self.assertEqual(call_more / (2 * bb_threebet + dead_sb), Fraction(13, 37))
        for text in ('18.5 BB', '31.5 BB', '44.5 BB', '15.5 BB',
                     '35.1%', 'SPR ≈ 4.92', 'SPR = 78 / 44.5 ≈ 1.75'):
            self.assertIn(text, self.article)

    def test_three_existing_articles_link_to_the_new_study_guide(self):
        graph = poker_link_graph.scan(ROOT)
        new = next(record for record in graph['records'] if record['slug'] == self.slug)
        for source in ('reading-preflop-charts', 'starting-hand-decisions',
                       'range-combinations'):
            self.assertIn('/poker/' + source + '/', new['prose_inbound_guides'])
        self.assertTrue(new['reachable_from_poker_entrypoints'])
        self.assertGreaterEqual(new['inbound_count'], 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
