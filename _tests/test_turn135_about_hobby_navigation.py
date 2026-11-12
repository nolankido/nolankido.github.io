"""Turn 135: the About menu offers a native route to its new personal section."""

from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


NAV_PATTERN = re.compile(r'<nav class="about-jump-nav"[^>]*>(.*?)</nav>', re.S)
HEADING = '<h2 id="wine-games-and-life">Wine, games, and the rest of life</h2>'
EXPECTED_LINKS = [
    ("about-evidence-title", "Evidence"),
    ("what-matters-in-the-work", "My approach"),
    ("about-interests", "Other interests"),
    ("wine-games-and-life", "Wine and games"),
    ("try-the-work", "Try the work"),
    ("public-work-elsewhere", "Public profiles"),
]


def nav_errors(html: str) -> list[str]:
    errors: list[str] = []
    match = NAV_PATTERN.search(html)
    if not match:
        return ["About profile menu is missing"]
    links = re.findall(r'<a href="#([^"#]+)">([^<]+)</a>', match.group(1))
    if links != EXPECTED_LINKS:
        errors.append("About menu must expose six ordered, readable native anchors")
    if html.count(HEADING) != 1 or html.count('id="wine-games-and-life"') != 1:
        errors.append("Wine and games heading must be a unique native destination")
    if not (html.find('href="#wine-games-and-life"') < html.find(HEADING)):
        errors.append("Section menu must precede its destination")
    if "\u2014" in match.group(1):
        errors.append("About menu copy must not contain an em dash")
    return errors


class AboutHobbyNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        cls.public = (ROOT / "about/index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/about-reader.css").read_text(encoding="utf-8")

    def test_all_about_menu_links_have_unique_native_headings(self):
        for html in (self.source, self.public):
            with self.subTest(kind="source" if html == self.source else "generated"):
                self.assertEqual(nav_errors(html), [])
                for target, _label in EXPECTED_LINKS:
                    self.assertEqual(html.count('id="' + target + '"'), 1)
                    self.assertIn('<h2 id="' + target + '">', html)

    def test_mobile_menu_has_two_columns_and_readable_touch_targets(self):
        self.assertRegex(self.css, r'@media\s*\(max-width:\s*480px\)')
        self.assertIn('grid-template-columns: repeat(2, minmax(0, 1fr))', self.css)
        self.assertIn('min-height: 44px', self.css)
        self.assertIn('flex-wrap: wrap', self.css)
        self.assertIn('overflow-wrap: anywhere', self.css)
        self.assertIn('.page-about #wine-games-and-life:target {', self.css)
        self.assertIn('outline: 2px solid var(--red)', self.css)
        self.assertIn('scroll-margin-top: 7rem', self.css)

    def test_existing_home_route_and_honest_limits_are_preserved(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/about/#wine-games-and-life"', home)
        for html in (self.source, self.public):
            for limit in (
                "not claims to wine credentials, public game releases, or verified AI outcomes",
                "Some work and much of ordinary life belong outside a public website",
            ):
                self.assertIn(limit, html)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.public)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/about/">', self.public)

    def test_generated_page_matches_source_build(self):
        self.assertEqual(build.build_outputs()[Path("about/index.html")], self.public)

    def test_mutations_cannot_hide_missing_or_broken_navigation(self):
        for damaged in (
            self.source.replace('<li><a href="#wine-games-and-life">Wine and games</a></li>', '', 1),
            self.source.replace('href="#wine-games-and-life"', 'href="#wine-and-games"', 1),
            self.source.replace(HEADING, '<h2>Wine, games, and the rest of life</h2>', 1),
            self.source.replace('Wine and games</a>', 'Wine and games</a><a href="#wine-games-and-life">Wine and games</a>', 1),
        ):
            with self.subTest(damage=damaged[:80]):
                self.assertTrue(nav_errors(damaged))


if __name__ == "__main__":
    unittest.main()
