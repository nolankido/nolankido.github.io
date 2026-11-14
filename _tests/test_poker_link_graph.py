"""The Poker link graph distinguishes meaningful guide prose from navigation."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import poker_link_graph


class PokerLinkGraphTests(unittest.TestCase):
    def test_graph_excludes_nav_related_cards_and_page_sharing(self):
        html = b'''<!doctype html><main>
          <header><p><a href="/poker/a/">Header</a></p></header>
          <article><p>Compare <a href="/poker/b/#example">the example</a>.</p>
          <nav><p><a href="/poker/c/">Nav</a></p></nav>
          <aside class="reader-related"><p><a href="/poker/d/">Card</a></p></aside>
          <section><ul><li><a href="/poker/e/">Follow-up</a></li></ul></section></article>
          <div class="page-share-wrap"><p><a href="/poker/f/">Share</a></p></div>
          </main>'''
        parser = poker_link_graph.links(html)
        self.assertEqual(len(parser.main_links), 6)
        self.assertEqual(parser.prose_links, ['/poker/b/#example', '/poker/e/'])

    def test_local_route_does_not_count_an_external_lookalike(self):
        self.assertEqual(poker_link_graph.local_route('/poker/reading-the-board/#draws', '/poker/poker-math/'),
                         '/poker/reading-the-board/')
        self.assertIsNone(poker_link_graph.local_route('https://nolankido.com.evil.test/poker/', '/poker/'))
        self.assertIsNone(poker_link_graph.local_route('https://example.com/poker/', '/poker/'))

    def test_all_library_guides_reachable_and_counts_are_consistent(self):
        report = poker_link_graph.scan(ROOT)
        self.assertGreaterEqual(report['guides'], 60)
        self.assertEqual(report['unreachable_guides'], [])
        self.assertEqual(len(report['records']), report['guides'])
        self.assertEqual(report['weak_guides_at_most_one_inbound'], 0)
        self.assertGreater(report['guide_prose_edges'], 0)
        self.assertEqual(report['guide_prose_edges'],
                         sum(record['outbound_count'] for record in report['records']))
        for record in report['records']:
            self.assertNotIn(record['route'], record['prose_inbound_guides'])
            self.assertNotIn(record['route'], record['prose_outbound_guides'])


if __name__ == '__main__':
    unittest.main()
