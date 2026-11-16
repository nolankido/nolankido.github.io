"""Keep useful, source-bounded first-video choices accessible without JavaScript.

The three shortcuts jump to already published cards. This does not infer
view counts, viewer preferences, independent footage review, or new results.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build

HUB = ROOT / "_source/poker/home.html"
CSS = ROOT / "assets/poker-discovery.css"
NAV_OPEN = '<nav class="poker-video-chooser" aria-label="Choose a NolanPoker starting video">'
GRID_OPEN = '<div class="poker-content-grid">'
CHOICES = (
    ("nolanpoker-deepstack", "A short-stack comeback", "qABaiIcvvpU", "Portland Meadows / Deepstack"),
    ("nolanpoker-standoff", "An A-K decision", "I75GOBVXij4", "Portland Meadows / Evening Stand Off"),
    ("nolanpoker-south-point", "A casino visit", "-Wm1i70Z3Bs", "South Point / NolanPoker"),
)


def choice_errors(html: str, css: str) -> list[str]:
    errors: list[str] = []
    section = re.search(
        r'<section class="poker-public-video-list".*?'
        r'(<nav class="poker-video-chooser".*?</nav>.*?)'
        r'<section class="poker-video-source-note"',
        html, re.S,
    )
    if not section or html.count(NAV_OPEN) != 1:
        return ["the labeled first-video choice navigation is missing"]
    area = section.group(1)
    nav = re.search(r'(<nav class="poker-video-chooser".*?</nav>)', area, re.S)
    if not nav or GRID_OPEN not in area:
        return errors + ["the navigation or video grid is missing"]
    nav_text = nav.group(1)
    if area.index(nav_text) > area.index(GRID_OPEN):
        errors.append("choices must come before the video cards")
    options = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', nav_text)
    if options != [(target, label) for target, label, _, _ in CHOICES]:
        errors.append("three truthful, distinct video choices are required")
    if 'New here? Start with:' not in nav_text:
        errors.append("first-time viewing context is missing")
    if any(marker in nav_text for marker in ("<script", "onclick=", "utm_", "youtube.com/")):
        errors.append("choice navigation must stay local and untracked")

    pre_card = html.split('<section class="poker-public-video-list"', 1)[-1].split(GRID_OPEN, 1)[0]
    visible_intro = re.sub(r'<[^>]*>', ' ', pre_card)
    if len(visible_intro.split()) > 100:
        errors.append("too much copy before a visitor reaches a video")
    if 'not official results' not in pre_card or 'href="#nolanpoker-video-notes"' not in pre_card:
        errors.append("verification limits must be visible before the choices")

    for target, _, video_id, category in CHOICES:
        if html.count(f'id="{target}"') != 1:
            errors.append("missing or duplicate destination: " + target)
        card = re.search(
            rf'<article class="poker-content-card" id="{target}">(.*?)</article>',
            area, re.S,
        )
        if not card or category not in card.group(1) or f'watch?v={video_id}"' not in card.group(1):
            errors.append("choice does not arrive at its matching video card: " + target)

    for required in (
        '.page-poker #watch .poker-video-chooser { display:flex; flex-wrap:wrap;',
        '.page-poker #watch .poker-video-chooser a { display:inline-flex; align-items:center; min-height:44px;',
        '.page-poker #watch .poker-video-chooser a:focus-visible { outline:3px solid var(--red);',
        '.page-poker #watch .poker-content-card[id] { scroll-margin-top:8rem;',
        '.page-poker #watch .poker-content-card:target { outline:3px solid var(--red);',
    ):
        if required not in css:
            errors.append("missing responsive, keyboard or arrival styling: " + required[:56])
    return errors


class FirstVideoChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HUB.read_text(encoding="utf-8")
        cls.published = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")

    def test_three_labeled_shortcuts_arrive_at_matching_cards(self):
        for html in (self.source, self.published):
            with self.subTest(rendered=html is self.published):
                self.assertEqual(choice_errors(html, self.css), [])
                self.assertNotIn("\u2014", html)
        self.assertEqual(self.published.count(NAV_OPEN), 1)

    def test_compiled_page_has_real_revision_date_and_no_new_service(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.published)
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        revision = next(p["updated"] for p in pages if p["path"] == "/poker/")
        self.assertEqual(revision, "2026-11-16")
        self.assertIn('"dateModified": "' + revision + '"', self.published)
        self.assertNotIn('youtube.com/embed', self.published)

    def test_dead_anchor_misleading_choice_and_unusable_navigation_fail(self):
        nav = self.source.split(NAV_OPEN, 1)[1].split("</nav>", 1)[0]
        moved = self.source.replace(NAV_OPEN + nav + "</nav>", "", 1)
        moved = moved.replace(GRID_OPEN, GRID_OPEN + NAV_OPEN + nav + "</nav>", 1)
        mutations = (
            (self.source.replace('href="#nolanpoker-deepstack"', 'href="#missing-video"', 1), self.css),
            (self.source.replace('id="nolanpoker-deepstack"', 'id="nolanpoker-south-point"', 1), self.css),
            (self.source.replace('A short-stack comeback', 'Official tournament result', 1), self.css),
            (self.source.replace('watch?v=I75GOBVXij4"', 'watch?v=notTheRightVideo"', 1), self.css),
            (self.source.replace('aria-label="Choose a NolanPoker starting video"', '', 1), self.css),
            (moved, self.css),
            (self.source, self.css.replace('.page-poker #watch .poker-video-chooser a:focus-visible', '.page-poker #watch .poker-video-chooser a:hover', 1)),
            (self.source, self.css.replace('.page-poker #watch .poker-content-card:target', '.page-poker #watch .poker-content-card:hover', 1)),
        )
        for index, (html, css) in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertTrue(choice_errors(html, css))


if __name__ == "__main__":
    unittest.main()
