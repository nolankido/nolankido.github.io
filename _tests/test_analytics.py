"""Umami installation contracts; these checks never contact analytics servers."""
from pathlib import Path
import unittest
from test_site import Page, ROOT, build

SRC = 'https://cloud.umami.is/script.js'
WEBSITE_ID = '51bfd4d7-08ac-4299-924b-621af60fa7f1'

class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.html = {path: content for path, content in cls.outputs.items() if path.suffix == '.html'}

    def test_exactly_one_approved_tracker_in_every_head(self):
        self.assertGreater(len(self.html), 0)
        for path, content in self.html.items():
            with self.subTest(path=str(path)):
                scripts = Page(content).tags('script')
                trackers = [a for a in scripts if a.get('src') == SRC]
                self.assertEqual(len(trackers), 1)
                self.assertEqual(sum('data-website-id' in a for a in scripts), 1)
                tracker = trackers[0]
                self.assertEqual(tracker['data-website-id'], WEBSITE_ID)
                self.assertIn('defer', tracker)
                self.assertEqual(tracker['data-domains'], 'nolankido.com,www.nolankido.com')
                for key in ('data-do-not-track', 'data-exclude-search', 'data-exclude-hash'):
                    self.assertEqual(tracker[key], 'true')
                self.assertNotIn('data-auto-track', tracker)
                self.assertNotIn('data-performance', tracker)
                head = content.split('</head>', 1)[0]
                self.assertEqual(sum(a.get('src') == SRC for a in Page(head).tags('script')), 1)

    def test_future_pages_inherit_the_shared_tracker(self):
        layout = (ROOT / '_source/layout.html').read_text(encoding='utf-8')
        self.assertEqual(layout.count(SRC), 1)
        for path in (ROOT / '_source').rglob('*.html'):
            if path.name != 'layout.html':
                self.assertNotIn(SRC, path.read_text(encoding='utf-8'), str(path))

    def test_pageviews_only_without_form_or_custom_event_instrumentation(self):
        for path, content in self.html.items():
            with self.subTest(path=str(path)):
                self.assertNotIn('data-umami-event', content)
                self.assertNotIn('umami.track(', content)
                self.assertNotIn('umami.identify(', content)
                self.assertNotIn('data-replay', content)
        contact = (ROOT / 'assets/contact.js').read_text(encoding='utf-8')
        self.assertNotIn('umami', contact.lower())

    def test_privacy_notice_matches_the_installation(self):
        content = self.outputs[Path('privacy/index.html')]
        for expected in ('Updated October 6, 2026', 'Umami Cloud', 'pageviews only', 'Do Not Track', 'https://umami.is/privacy'):
            self.assertIn(expected, content)
        self.assertNotIn('does not add advertising pixels, behavioral analytics', content)
        privacy = next(page for page in build.public_pages() if page['path'] == '/privacy/')
        self.assertEqual(privacy['updated'], '2026-10-06')

if __name__ == '__main__':
    unittest.main()
