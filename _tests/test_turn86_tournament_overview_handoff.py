"""Turn 86: a tournament-overview reader can reach existing 10 BB study.

This is an offline source/output regression. It cannot certify the current
public deployment, browser interactivity, search performance or video content.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import poker_finder

SOURCE = ROOT / "_source/poker/tournaments.html"
PUBLISHED = ROOT / "poker/tournaments/index.html"
PLAYBOOK = ROOT / "poker/10bb/index.html"
WORKSHEET = ROOT / "downloads/ten-bb-tournament-checklist.md"

ORIGINAL_HEAD = (
    '<nav class="article-navigation" aria-label="Continue learning">'
    '<a href="/poker/poker-math/">Next: percentages without false certainty</a>'
)
NEW_HEAD = (
    '<nav class="article-navigation" aria-label="Continue learning">'
    '<a href="/poker/10bb/#six-checks-title">'
    'After-play study: written 10 BB Playbook</a>'
    '<a href="/downloads/ten-bb-tournament-checklist.md" download>'
    'Download blank 10 BB worksheet</a>'
    '<a href="/poker/poker-math/">Next: percentages without false certainty</a>'
)
NAV = re.compile(r'<nav class="article-navigation" aria-label="Continue learning">.*?</nav>', re.S)


class LinkCollector(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


class Turn86TournamentToTenBB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLISHED.read_text(encoding="utf-8")
        cls.playbook = PLAYBOOK.read_text(encoding="utf-8")

    def test_reading_handoff_is_identical_in_author_source_and_public_html(self):
        source_nav = NAV.findall(self.source)
        public_nav = NAV.findall(self.public)
        self.assertEqual(len(source_nav), 1)
        self.assertEqual(source_nav, public_nav)
        self.assertTrue(source_nav[0].startswith(NEW_HEAD))
        self.assertEqual(self.source.count('href="/poker/10bb/#six-checks-title"'), 1)
        self.assertEqual(self.public.count('href="/poker/10bb/#six-checks-title"'), 1)

    def test_both_targets_are_real_public_resources(self):
        links = LinkCollector(NAV.search(self.source).group()).links
        urls = [link["href"] for link in links]
        self.assertIn("/poker/10bb/#six-checks-title", urls)
        self.assertIn("/downloads/ten-bb-tournament-checklist.md", urls)
        worksheet = next(link for link in links if link["href"].endswith(".md"))
        self.assertIn("download", worksheet)
        self.assertIn('id="six-checks-title"', self.playbook)
        self.assertTrue(WORKSHEET.is_file())
        self.assertIn("six", WORKSHEET.read_text(encoding="utf-8").lower())

    def test_original_navigation_and_page_identity_remain(self):
        public_nav = NAV.search(self.public).group()
        for route in ("/poker/poker-math/", "/poker/start-here/#viewer-library",
                      "/downloads/poker-viewer-reference.md", "/contact/"):
            self.assertIn('href="' + route + '"', public_nav)
        self.assertIn('rel="canonical" href="https://nolankido.com/poker/tournaments/"', self.public)
        self.assertIn('<meta property="article:published_time" content="2026-10-05">', self.public)
        self.assertIn('<meta property="article:modified_time" content="2026-10-05">', self.public)
        self.assertEqual(len(re.findall(r'<loc>https://nolankido.com/poker/tournaments/</loc>',
                                        (ROOT / "sitemap.xml").read_text(encoding="utf-8"))), 1)

    def test_navigation_does_not_change_searchable_article_or_spoil_answers(self):
        self.assertEqual(self.source.count(NEW_HEAD), 1)
        historic = self.source.replace(NEW_HEAD, ORIGINAL_HEAD)
        # The native Poker Finder intentionally skips <nav> content. No new
        # searchable paragraphs, snippets or 301-card index bytes are needed.
        self.assertEqual(
            poker_finder.GuideText(historic).sections,
            poker_finder.GuideText(self.source).sections)
        self.assertNotIn("10 BB Playbook", " ".join(
            x["text"] for x in poker_finder.GuideText(self.source).sections))
        self.assertEqual(self.public.count('aria-label="Continue learning"'), 1)

    def test_current_site_builder_reproduces_public_tournament_page(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("poker/tournaments/index.html")], self.public)

    def test_no_new_actions_for_navigation(self):
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml")
            for p in actions.iterdir()))


if __name__ == "__main__":
    unittest.main()
