"""Mobile-first entry to the existing, bounded homepage evidence path."""
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import turn39_home_shortcut_history as history
import turn40_poker_video_history as successor

PARENT = history.PARENT
NAV = re.compile(r'<nav class="link-row identity-actions"[^>]*>.*?</nav>', re.S)
SHORTCUT = '<a class="text-link" href="#home-proof-title">Check the evidence <span aria-hidden="true">→</span></a>'
NAV_LINKS = [
    '/technology/#ai-works-human-decides',
    '#home-proof-title',
    '/technology/#technology-projects',
    '/poker/#watch',
    '/about/',
]


def errors(page: str) -> list[str]:
    issues = []
    navs = NAV.findall(page)
    if len(navs) != 1:
        return ['missing or duplicate homepage hero navigation']
    nav = navs[0]
    links = re.findall(r'<a\b[^>]*href="([^"]+)"', nav)
    if links != NAV_LINKS:
        issues.append('unexpected hero navigation order or target')
    if nav.count(SHORTCUT) != 1 or page.count(SHORTCUT) != 1:
        issues.append('missing, duplicate or mislabeled evidence shortcut')
    if page.count('id="home-proof-title"') != 1:
        issues.append('unresolved or duplicate evidence fragment')
    if 'class="section folio-row identity-selection home-proof"' not in page:
        issues.append('shortcut does not lead to its existing evidence section')
    if nav.count('<script') or nav.count('onclick='):
        issues.append('non-native hero navigation')
    if page.find('id="home-proof-title"') >= 0 and page.index(navs[0]) > page.index('id="home-proof-title"'):
        issues.append('evidence shortcut appears after its destination')
    return issues


class HomepageEvidenceShortcutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/home.html').read_text(encoding='utf-8')
        cls.page = (ROOT / 'index.html').read_text(encoding='utf-8')

    def test_second_visible_hero_action_is_native_shortcut_to_real_evidence(self):
        for text in (self.source, self.page):
            with self.subTest(output=text[:30]):
                self.assertEqual(errors(text), [])
                nav = NAV.search(text).group()
                self.assertIn('aria-label="Explore Nolan Kido', nav)
                self.assertIn('class="button"', nav)
        self.assertEqual(NAV.search(self.source).group(), NAV.search(self.page).group())

    def test_one_exact_insertion_preserves_all_existing_homepage_content(self):
        for name, current in (('_source/home.html', self.source), ('index.html', self.page)):
            with self.subTest(file=name):
                previous = subprocess.check_output(['git', 'show', PARENT + ':' + name], cwd=ROOT)
                self.assertEqual(current.count(SHORTCUT), 1)
                self.assertEqual(current.replace(SHORTCUT, '', 1).encode('utf-8'), previous)

    def test_build_and_published_byte_inventory_agree(self):
        self.assertEqual(build.build_outputs()[Path('index.html')], self.page)
        self.assertEqual(check_live.targets()['/'], (200, self.page.encode('utf-8')))
        self.assertEqual(self.page.count('rel="canonical" href="https://nolankido.com/"'), 1)
        self.assertEqual(self.page.count('"@type": "WebPage"'), 1)

    def test_native_44_pixel_tap_target_and_no_scripting(self):
        css = (ROOT / 'assets/site-core.css').read_text(encoding='utf-8')
        self.assertIn('.text-link, .button { display: inline-flex;', css)
        self.assertIn('min-height: 44px', css)
        self.assertNotIn('<script', NAV.search(self.page).group())
        self.assertNotIn('tabindex=', NAV.search(self.page).group())

    def test_bad_targets_placement_and_labels_fail_closed(self):
        for mutated in (
            self.page.replace(SHORTCUT, '', 1),
            self.page.replace('#home-proof-title">Check', '#unverified-evidence">Check', 1),
            self.page.replace('Check the evidence', 'Click here', 1),
            self.page.replace(SHORTCUT, SHORTCUT + SHORTCUT, 1),
            self.page.replace('id="home-proof-title"', 'id="missing-proof-title"', 1),
            self.page.replace(SHORTCUT, '', 1).replace('</nav>', SHORTCUT + '</nav>', 1),
        ):
            with self.subTest(sample=mutated[:50]):
                self.assertTrue(errors(mutated))


class HomepageEvidenceShortcutHistoryTests(unittest.TestCase):
    def test_only_exact_reviewed_revisions_rewind(self):
        for name, (old_hash, new_hash) in history.records()['files'].items():
            with self.subTest(path=name):
                now = (ROOT / name).read_bytes()
                previous = subprocess.check_output(['git', 'show', PARENT + ':' + name], cwd=ROOT)
                self.assertEqual(history.blob(successor.before(name, now)), new_hash)
                self.assertEqual(history.blob(previous), old_hash)
                self.assertEqual(history.before(name, now), previous)
                self.assertEqual(history.before(ROOT / name, now.decode()), previous.decode())

    def test_unrecognized_modifications_are_never_hidden(self):
        for name in history.records()['files']:
            now = (ROOT / name).read_bytes()
            self.assertEqual(history.before(name, now + b'ALTERED'), now + b'ALTERED')
            self.assertEqual(history.before('other/' + name, now), now)


if __name__ == '__main__':
    unittest.main()
