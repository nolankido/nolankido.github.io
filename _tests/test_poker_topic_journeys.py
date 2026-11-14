"""Poker topic and library routes must remain editorial, complete and accessible."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_library
import poker_resources
import poker_topics


class TopicJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.guides = poker_library.load(ROOT, cls.pages)
        cls.resources = poker_resources.load(ROOT)
        cls.topics = poker_topics.load(ROOT, cls.pages, cls.guides, cls.resources)

    def test_all_ten_subjects_offer_distinct_four_way_routes(self):
        self.assertEqual(len(self.topics), 10)
        for topic in self.topics:
            routes = poker_topics.learning_routes(topic)
            self.assertEqual([route['stage'] for route in routes],
                             ['Start', 'Deepen', 'Practice', 'Sources'], topic['id'])
            self.assertEqual(len({route['href'] for route in routes}), 4, topic['id'])
            self.assertEqual(routes[-1]['href'], poker_topics.finder_url(topic, 'resource'))
            self.assertTrue(all(route['title'] and route['label'] for route in routes))
            self.assertTrue(all(route['href'].startswith('/poker/') for route in routes))
            markup = poker_topics.detail(topic)
            self.assertEqual(markup.count('class="topic-journey-stage"'), 4, topic['id'])
            self.assertIn('aria-label="Learning routes for ', markup)
            for route in routes:
                self.assertIn(route['href'].replace('&', '&amp;'), markup)

    def test_library_uses_same_topic_route_data_without_javascript(self):
        markup = poker_topics.supplement(self.topics)['poker_library_subject_routes']
        self.assertEqual(markup.count('class="library-subject"'), 10)
        self.assertEqual(markup.count('class="library-subject-routes"'), 10)
        self.assertEqual(markup.count('<li><span>'), 40)
        self.assertNotIn('<script', markup)
        source = (ROOT / '_source/poker/library.html').read_text(encoding='utf-8')
        self.assertIn('id="subject-routes"', source)
        self.assertIn('${poker_library_subject_routes}', source)

    def test_missing_or_cross_topic_practice_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '_source/poker/topics.json'
            path.parent.mkdir(parents=True)
            data = json.loads((ROOT / '_source/poker/topics.json').read_text(encoding='utf-8'))
            data['entries'][0]['journey']['practice']['guide'] = 'tournament-trip-budget'
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'distinct member guide'):
                poker_topics.load(Path(directory), self.pages, self.guides, self.resources)


if __name__ == '__main__':
    unittest.main()
