"""Real-work promotion and reference paths without invented public content."""
from pathlib import Path
from unittest.mock import patch
from html.parser import HTMLParser
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_content
import poker_experience as experience
from test_poker_content import fixture, catalog_root


class IDs(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids = set(); self.feed(text)
    def handle_starttag(self, tag, attrs):
        value = dict(attrs).get('id')
        if value: self.ids.add(value)


class PokerExperienceTests(unittest.TestCase):
    def test_empty_catalog_is_learning_led_without_empty_feature(self):
        values = experience.supplement({'entries': []})
        self.assertEqual(values['poker_feature'], '')
        self.assertIn('/poker/follow-along/', values['poker_intro_action'])
        self.assertNotIn('youtube', values['poker_intro_action'])

    def test_illustrative_hands_and_unapproved_records_are_not_real_features(self):
        hand = fixture('hand', 'fictional'); story = fixture('story', 'unapproved')
        story['approved'] = False
        self.assertEqual(experience.real_entries({'entries': [hand, story]}), [])
        story['approved'] = 1
        self.assertEqual(experience.real_entries({'entries': [story]}), [])

    def test_latest_real_work_is_selected_deterministically(self):
        older = fixture('episode', 'older'); older['published'] = '2026-10-05'
        newer = fixture('hand', 'newer'); newer.update(published='2026-10-06', record_type='reconstructed')
        fictional = fixture('hand', 'latest-fiction'); fictional['published'] = '2026-10-07'
        values = experience.supplement({'entries': [older, fictional, newer]})
        self.assertIn('/poker/hands/newer/', values['poker_feature'])
        self.assertNotIn('latest-fiction', values['poker_feature'])
        self.assertEqual(values['poker_intro_action'], '')
        tied = fixture('story', 'z-story'); tied['published'] = newer['published']
        self.assertEqual(experience.real_entries({'entries': [newer, tied]})[0], tied)

    def test_feature_escapes_text_and_does_not_reveal_results_or_load_video(self):
        e = fixture(); e['title'] = '<script>unsafe</script>'; e['summary'] = '<b>Question</b>'
        feature = experience.supplement({'entries': [e]})['poker_feature']
        self.assertIn('&lt;script&gt;', feature)
        self.assertIn('&lt;b&gt;Question&lt;/b&gt;', feature)
        for text in ['<script>', 'Synthetic result', '<iframe', 'youtube.com', 'ytimg']:
            self.assertNotIn(text, feature)
        self.assertIn('Watch and read', feature)
        self.assertIn('/poker/episodes/test-episode/', feature)

    def test_feature_uses_only_the_approved_local_image(self):
        e = fixture('story', 'image-case')
        e['image'] = {'src': '/assets/poker/test-approved.png', 'alt': 'A & B', 'width': 800, 'height': 450}
        feature = experience.supplement({'entries': [e]})['poker_feature']
        self.assertIn('src="/assets/poker/test-approved.png"', feature)
        self.assertIn('alt="A &amp; B"', feature)
        self.assertIn('width="800" height="450"', feature)
        self.assertEqual(feature.count('<img'), 1)

    def test_guide_reference_uses_exact_path_and_accepts_a_section_anchor(self):
        e = fixture('hand', 'real-hand'); e['record_type'] = 'reconstructed'
        e['sources'] = [{'label': 'Price', 'url': 'https://nolankido.com/poker/pot-odds-workshop/#call-price'},
                        {'label': 'Other section', 'url': 'https://www.nolankido.com/poker/pot-odds-workshop/#facing-a-raise'}]
        result = experience.related_work({'entries': [e]}, '/poker/pot-odds-workshop/')
        self.assertEqual(result.count('href="/poker/hands/real-hand/"'), 1)
        self.assertIn('Reconstructed hand', result)
        self.assertEqual(experience.related_work({'entries': [e]}, '/poker/poker-math/'), '')

    def test_reference_does_not_guess_relationships_or_trust_lookalike_hosts(self):
        e = fixture('story', 'no-match')
        for url in ['https://nolankido.com.example.test/poker/study/',
                    'https://example.test/poker/study/', 'https://nolankido.com/poker/study/extra/',
                    'http://nolankido.com/poker/study/', 'https://user@nolankido.com/poker/study/']:
            e['sources'] = [{'label': 'Test', 'url': url}]
            with self.subTest(url=url):
                self.assertEqual(experience.related_work({'entries': [e]}, '/poker/study/'), '')
        e.pop('sources')
        self.assertEqual(experience.related_work({'entries': [e]}, '/poker/study/'), '')

    def test_fictional_hands_do_not_become_real_work_beside_a_guide(self):
        e = fixture('hand', 'fictional')
        e['sources'] = [{'label': 'Guide', 'url': 'https://nolankido.com/poker/study/'}]
        self.assertEqual(experience.related_work({'entries': [e]}, '/poker/study/'), '')

    def test_related_work_is_bounded_and_escaped(self):
        entries = []
        for i in range(5):
            e = fixture('story', 's-' + str(i)); e['title'] = '<b>Title</b>'
            e['sources'] = [{'label': 'Guide', 'url': 'https://nolankido.com/poker/study/'}]
            entries.append(e)
        result = experience.related_work({'entries': entries}, '/poker/study/')
        self.assertEqual(result.count('class="poker-content-card"'), 3)
        self.assertIn('/poker/stories/s-4/', result)
        self.assertNotIn('/poker/stories/s-0/', result)
        self.assertNotIn('<b>', result)

    def test_populated_build_places_real_feature_before_paths_and_links_back(self):
        e = fixture('hand', 'approved-test'); e['record_type'] = 'reconstructed'
        e['sources'] = [{'label': 'Review method', 'url': 'https://nolankido.com/poker/reviewing-a-hand/#after-the-session'}]
        with catalog_root([e]) as root, patch.object(build, 'ROOT', root), patch.object(build, 'SOURCE', root / '_source'):
            outputs = build.build_outputs(); home = outputs[Path('poker/index.html')]
            self.assertLess(home.index('id="featured-work"'), home.index('class="poker-paths"'))
            self.assertLess(home.index('id="watch"'), home.index('id="after-play"'))
            guide = outputs[Path('poker/reviewing-a-hand/index.html')]
            self.assertIn('/poker/hands/approved-test/', guide)
            self.assertIn('id="context-reading-title"', guide)
            self.assertEqual(outputs[Path('index.html')], (ROOT / 'index.html').read_text())
            self.assertEqual(outputs[Path('feed.xml')], (ROOT / 'feed.xml').read_text())

    def test_overview_and_existing_viewer_fragments_stay_available(self):
        outputs = build.build_outputs()
        home = outputs[Path('poker/index.html')]
        self.assertLess(home.index('id="watch"'), home.index('id="after-play"'))
        self.assertTrue({'watch', 'study', 'after-play', 'viewer-learning-title',
                         'poker-intro-title', 'poker-approach-title', 'poker-connect-title'} <= IDs(home).ids)
        start = outputs[Path('poker/start-here/index.html')]
        self.assertTrue({'viewer-library', 'viewer-essentials', 'viewer-next', 'heard-it',
                         'quick-start', 'situation', 'action', 'terms', 'interpretation',
                         'after-play-workshops'} <= IDs(start).ids)
        self.assertLess(start.index('id="quick-start"'), start.index('id="viewer-library"'))
        study = outputs[Path('poker/study/index.html')]
        self.assertLess(study.index('id="hand-review"'), study.index('id="workshops"'))
        self.assertLess(study.index('id="session-debrief"'), study.index('id="workshops"'))

    def test_catalog_validation_still_rejects_unapproved_and_future_entries(self):
        from datetime import date
        for change in [{'approved': False}, {'published': '2026-10-08'}]:
            e = fixture('story', 'blocked'); e.update(change)
            with catalog_root([e]) as root, self.assertRaises(ValueError):
                poker_content.load(root, as_of=date(2026, 10, 7))


if __name__ == '__main__':
    unittest.main()
