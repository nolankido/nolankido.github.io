"""Turn 4 three-interest homepage paths and exact historic-release boundary."""
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import build
import homepage_turn04_history as history
import homepage_growth_history
import later_release_history
import visibility_discovery_history
import visibility_sprint_history

PATHS = (
    '/technology/#ai-works-human-decides',
    '/technology/#technology-projects',
    '/poker/#watch',
    '/about/',
)


class HomepageTurn04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.html = cls.outputs[Path('index.html')]

    def test_first_screen_links_all_three_aims_to_published_anchors(self):
        hero = self.html.split('id="visibility-projects-title"', 1)[0]
        self.assertIn('<h1 id="home-title">Nolan Kido</h1>', hero)
        self.assertIn('AI Works Human Decides', hero)
        self.assertIn('I also build software tools and play tournament poker.', hero)
        nav = re.search(r'<nav class="link-row identity-actions"[^>]*>(.*?)</nav>', hero, re.S)
        self.assertIsNotNone(nav)
        self.assertIn('aria-label="Explore Nolan Kido\'s work and interests"', nav.group(0))
        links = re.findall(r'<a\b[^>]*href="([^"]+)"', nav.group(1))
        self.assertEqual(links, list(PATHS))
        self.assertEqual(len(set(links)), len(links))
        for link in links:
            url = urlsplit(link)
            page = build.output_path(url.path)
            with self.subTest(link=link):
                self.assertIn(page, self.outputs)
                if url.fragment:
                    self.assertIn('id="' + url.fragment + '"', self.outputs[page])
        self.assertNotIn('WSOP ring', hero)
        self.assertNotIn('Hawaii Dental', hero)
        self.assertNotIn('headshot', hero)

    def test_mobile_links_keep_native_wrap_and_keyboard_targets(self):
        css = (ROOT / 'assets/site-core.css').read_text(encoding='utf-8')
        self.assertIn('.link-row { display: flex; flex-wrap: wrap;', css)
        self.assertIn('.text-link, .button { display: inline-flex;', css)
        self.assertIn('min-height: 44px;', css)
        self.assertNotIn('onclick=', self.html.split('id="visibility-projects-title"', 1)[0])
        self.assertLess(self.html.index('class="link-row identity-actions"'),
                        self.html.index('id="visibility-projects-title"'))
        self.assertLess(self.html.index('id="visibility-projects-title"'),
                        self.html.index('id="selected-reading-title"'))
        self.assertLess(self.html.index('id="selected-reading-title"'),
                        self.html.index('id="destinations-title"'))

    def test_only_exact_home_source_and_output_are_reversible(self):
        self.assertEqual(set(history.REVISIONS), {'_source/home.html', 'index.html'})
        for name, (previous_sha, current_sha) in history.REVISIONS.items():
            current = (ROOT / name).read_bytes()
            with self.subTest(path=name):
                self.assertEqual(history.digest(current), current_sha)
                old = history.before(name, current)
                self.assertEqual(history.digest(old), previous_sha)
                self.assertEqual(history.before(name, old), old)
                self.assertEqual(history.before(ROOT / name, current.decode()), old.decode())
                for changed in (current + b'UNREVIEWED', b'UNREVIEWED' + current, current[1:]):
                    self.assertIs(history.before(name, changed), changed)
                self.assertIs(history.before('unknown/' + name, current), current)

    def test_older_output_and_source_inventories_see_the_approved_predecessor(self):
        for name in history.REVISIONS:
            current = (ROOT / name).read_bytes()
            old = history.before(name, current)
            for release in (visibility_discovery_history, visibility_sprint_history,
                            later_release_history, homepage_growth_history):
                with self.subTest(path=name, release=release.__name__):
                    self.assertEqual(release.outputs({Path(name): current}),
                                     release.outputs({Path(name): old}))
                    self.assertEqual(release.source_records({name: current}),
                                     release.source_records({name: old}))
                    mutated = current + b'UNREVIEWED'
                    self.assertEqual(release.outputs({Path(name): mutated}),
                                     {Path(name): mutated})
                    self.assertEqual(release.source_records({name: mutated}),
                                     {name: mutated})

    def test_corrupted_predecessor_digest_is_rejected(self):
        name = '_source/home.html'
        current = (ROOT / name).read_bytes()
        with patch.dict(history.REVISIONS, {name: ('0' * 64, history.digest(current))}):
            with self.assertRaisesRegex(ValueError, 'predecessor digest'):
                history.before(name, current)


if __name__ == '__main__':
    unittest.main()
