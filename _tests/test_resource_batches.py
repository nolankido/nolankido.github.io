"""Batch history remains distinct from live listings and never schedules work."""
import json
from pathlib import Path
import unittest
from test_site import ROOT, build
import poker_resources


class ResourceBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = {e['id']: e for e in poker_resources.load(ROOT)}
        cls.backlog = json.loads((ROOT / '_source/poker/RESOURCE_BACKLOG.json').read_text())
        cls.record = (ROOT / '_source/poker/RESOURCE_BATCH_002.md').read_text()

    def test_resolved_candidates_keep_original_and_accepted_destinations(self):
        unresolved = {e['id'] for e in self.backlog['candidates']}
        for item in self.backlog['resolved']:
            self.assertNotIn(item['id'], unresolved)
            self.assertEqual(item['status'], 'accepted')
            self.assertNotEqual(item['previous_url'], item['url'])
            self.assertEqual(self.entries[item['id']]['url'], item['url'])
            self.assertEqual(self.entries[item['id']]['review_method'], 'page')

    def test_research_briefs_are_actionable_plans_not_published_entries(self):
        priorities = []
        for item in self.backlog['research_batches']:
            self.assertEqual(item['status'], 'planned')
            self.assertNotIn(item['id'], self.entries)
            self.assertTrue(item['question'] and item['acceptance'] and item['queries'])
            priorities.append(item['priority'])
        self.assertEqual(len(priorities), len(set(priorities)))
        self.assertTrue(priorities)

    def test_batch_keeps_review_limits_and_historical_context(self):
        for phrase in ['other 61 existing resources were not', 'not scheduled jobs',
                       'No videos were played to completion', 'not an inspection of every theorem']:
            self.assertIn(phrase, self.record)
        for ident, phrase in [('mit-theory', '2015'), ('mit-holdem', '2016'),
                              ('pokerbank-videos', 'no longer updated'), ('av-aivat', 'preprint')]:
            entry = self.entries[ident]
            self.assertIn(phrase, (entry['title'] + ' ' + entry['kind'] + ' ' + entry['notes']).lower())
        self.assertEqual(self.entries['satellite-masterclass']['access'], 'Paid')
        self.assertEqual(self.entries['tda-rules']['review_method'], 'page')
        self.assertIn('September 7, 2026', self.entries['tda-rules']['notes'])

    def test_unresolved_candidates_and_working_documents_are_not_rendered(self):
        outputs = build.build_outputs()
        page = outputs[Path('poker/resources/index.html')]
        for candidate in self.backlog['candidates']:
            self.assertNotIn('id="resource-' + candidate['id'] + '"', page)
        for name in ['RESOURCE_BATCH_002.md', 'RESOURCE_BACKLOG.json', 'RESOURCE_PROCESS.md']:
            self.assertNotIn(name, outputs[Path('sitemap.xml')])
            self.assertNotIn(name, page)


if __name__ == '__main__':
    unittest.main()
