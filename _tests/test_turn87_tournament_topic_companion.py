"""Turn 87: surface only a published 10 BB manual companion in tournament topics.

No new guide count, no search index change, no duplicated Article or fake solver
claim. This is an offline source and generated-output regression test.
"""
from pathlib import Path
from unittest.mock import patch
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_library
import poker_resources
import poker_topics
import tenbb_companion

TOPIC_OUTPUT = ROOT / 'poker/topics/tournaments/index.html'
FINDER_OUTPUT = ROOT / 'poker/find/index.html'
PLAYBOOK = ROOT / tenbb_companion.OUTPUT
WORKSHEET = ROOT / tenbb_companion.WORKSHEET
BLOCK = poker_topics.TOURNAMENT_STANDALONE


class Turn87TournamentTopicCompanion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.guides = poker_library.load(ROOT, cls.pages)
        cls.resources = poker_resources.load(ROOT)
        cls.topics = poker_topics.load(ROOT, cls.pages, cls.guides, cls.resources)
        cls.tournament = next(t for t in cls.topics if t['id'] == 'tournaments')
        cls.public = TOPIC_OUTPUT.read_text(encoding='utf-8')

    def test_published_companion_is_real_and_has_both_required_files(self):
        approved = tenbb_companion.record(ROOT)
        self.assertEqual(approved['route'], '/poker/10bb/')
        self.assertTrue(PLAYBOOK.is_file())
        self.assertTrue(WORKSHEET.is_file())
        self.assertIn('id="six-checks-title"', PLAYBOOK.read_text(encoding='utf-8'))
        self.assertIn('Six-Check Tournament Decision Sheet', WORKSHEET.read_text(encoding='utf-8'))

    def test_tournament_detail_uses_one_validated_standalone_block(self):
        fresh = poker_topics.detail(self.tournament, ROOT)
        self.assertEqual(fresh.count(BLOCK), 1)
        self.assertEqual(self.public.count(BLOCK), 1)
        self.assertIn('href="/poker/10bb/#six-checks-title"', BLOCK)
        self.assertIn('href="/downloads/ten-bb-tournament-checklist.md" download', BLOCK)
        self.assertLess(fresh.index('aria-label="Learning routes for Tournaments"'),
                        fresh.index(BLOCK))
        self.assertLess(fresh.index(BLOCK), fresh.index('<div class="topic-columns">'))

    def test_no_manifest_guide_or_external_source_count_inflation(self):
        self.assertEqual(len(self.tournament['guides']), 20)
        self.assertEqual(len(self.tournament['resources']), 13)
        self.assertIn('All 20 guides on this topic', self.public)
        self.assertIn('All 13 outside sources', self.public)
        self.assertIn('not counted among the catalog guides below', BLOCK)
        self.assertEqual(FINDER_OUTPUT.read_text(encoding='utf-8').count(
            'data-id="standalone-tenbb"'), 1)
        self.assertIn('301 entries available.', FINDER_OUTPUT.read_text(encoding='utf-8'))

    def test_other_topic_detail_and_shared_topic_index_do_not_get_manual_block(self):
        index = (ROOT / 'poker/topics/index.html').read_text(encoding='utf-8')
        self.assertNotIn('tournament-written-playbook', index)
        for other in self.topics:
            if other['id'] == 'tournaments':
                continue
            self.assertNotIn('tournament-written-playbook',
                             poker_topics.detail(other, ROOT), other['id'])
            self.assertNotIn('tournament-written-playbook',
                             (ROOT / 'poker/topics' / other['id'] / 'index.html')
                             .read_text(encoding='utf-8'), other['id'])

    def test_missing_manual_approval_fails_closed_only_in_tournament_topic(self):
        other = next(t for t in self.topics if t['id'] == 'strategy')
        with patch.object(poker_topics.tenbb_companion, 'record',
                          side_effect=ValueError('required worksheet missing')) as gate:
            with self.assertRaisesRegex(ValueError, 'required worksheet missing'):
                poker_topics.detail(self.tournament, ROOT)
            self.assertNotIn('tournament-written-playbook',
                             poker_topics.detail(other, ROOT))
            self.assertEqual(gate.call_count, 1)

    def test_unexpected_companion_route_fails_closed(self):
        with patch.object(poker_topics.tenbb_companion, 'record',
                          return_value={'route': '/not-the-playbook/'}):
            with self.assertRaisesRegex(ValueError, 'changed canonical route'):
                poker_topics.detail(self.tournament, ROOT)

    def test_existing_published_topic_identity_stays_unchanged(self):
        html = self.public
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/topics/tournaments/">', html)
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', html)
        self.assertIn('"dateModified": "2026-10-08"', html)
        self.assertEqual((ROOT / 'sitemap.xml').read_text(encoding='utf-8').count(
            '<loc>https://nolankido.com/poker/topics/tournaments/</loc>'), 1)
        self.assertNotIn('<script', BLOCK)

    def test_deterministic_builder_reproduces_committed_tournament_topic(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path('poker/topics/tournaments/index.html')], self.public)
        self.assertEqual(outputs[Path('poker/find/index.html')],
                         FINDER_OUTPUT.read_text(encoding='utf-8'))

    def test_release_runner_and_owner_no_actions_rule(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn87_tournament_topic_companion.py', runner)
        script = (ROOT / '_scripts/build.py').read_text(encoding='utf-8')
        self.assertIn('poker_topics.detail(topic, ROOT)', script)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yml', '.yaml')
            for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
