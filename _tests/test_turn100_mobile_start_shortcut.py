"""Reach the practical homepage choices before stacked evidence on small screens."""
from hashlib import sha256
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


SHORTCUT = (
    '<p class="mobile-start-shortcut"><a href="#selected-reading-title">'
    'Want to try something now? Jump to a free tool and examples '
    '<span aria-hidden="true">↓</span></a></p>'
)
HERO_NAV = re.compile(r'<nav class="link-row identity-actions".*?</nav>', re.S)
PROOF = '<section class="section folio-row identity-selection home-proof"'
CHOICES = '<section class="section folio-row identity-selection" aria-labelledby="selected-reading-title">'


def errors(page: str) -> list[str]:
    issues = []
    if page.count(SHORTCUT) != 1:
        issues.append("missing or duplicate native mobile shortcut")
        return issues
    if page.count('id="selected-reading-title"') != 1:
        issues.append("mobile shortcut destination is missing or ambiguous")
    if not (page.index(SHORTCUT) < page.index(PROOF) < page.index(CHOICES)):
        issues.append("mobile shortcut does not bypass the stacked evidence cards")
    match = HERO_NAV.search(page)
    if not match or SHORTCUT in match.group():
        issues.append("mobile shortcut must not change the reviewed five hero actions")
    if 'onclick=' in SHORTCUT or '<script' in SHORTCUT:
        issues.append("shortcut must be native without JavaScript")
    if '\u2014' in SHORTCUT:
        issues.append("em dash in public content")
    return issues


class MobileHomepageShortcutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        cls.public = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/first-steps.css").read_text(encoding="utf-8")

    def test_native_jump_precedes_stacked_evidence_and_keeps_desktop_hero(self):
        for page in (self.source, self.public):
            with self.subTest(page=page[:50]):
                self.assertEqual(errors(page), [])
                self.assertEqual(len(re.findall(r'<a\b[^>]*href=', HERO_NAV.search(page).group())), 5)
        self.assertIn(SHORTCUT, self.public)

    def test_css_only_exposes_it_when_three_evidence_cards_stack(self):
        self.assertIn('.page-home .mobile-start-shortcut { display: none; }', self.css)
        self.assertRegex(self.css, r'@media \(max-width: 900px\)\s*\{\s*'
                          r'\.page-home \.mobile-start-shortcut \{ display: block;')
        self.assertIn('.page-home .mobile-start-shortcut a { display: inline-flex;', self.css)
        self.assertIn('min-height: 44px', self.css)
        self.assertIn('.page-home .mobile-start-shortcut a:focus-visible', self.css)
        self.assertIn('.identity-readings { grid-template-columns: minmax(0, 1fr);',
                      (ROOT / "assets/hubs.css").read_text(encoding="utf-8"))

    def test_built_home_uses_current_stylesheet_fingerprint(self):
        expected = sha256((ROOT / "assets/first-steps.css").read_bytes()).hexdigest()[:12]
        self.assertIn(f'/assets/first-steps.css?v={expected}', self.public)
        self.assertEqual(build.build_outputs()[Path("index.html")], self.public)

    def test_missing_duplicate_or_moved_shortcut_is_caught(self):
        cases = (
            self.public.replace(SHORTCUT, "", 1),
            self.public.replace(SHORTCUT, SHORTCUT + SHORTCUT, 1),
            self.public.replace(SHORTCUT, "", 1).replace(PROOF, PROOF + SHORTCUT, 1),
            self.public.replace('id="selected-reading-title"', 'id="missing-start-title"', 1),
        )
        for changed in cases:
            with self.subTest(change=changed[:50]):
                self.assertTrue(errors(changed))


if __name__ == "__main__":
    unittest.main()
