"""Keep the NolanPoker video choice visible and legible before its source ledger.

Local-only contract. No YouTube analytics, footage claims, cookies or network
lookups are necessary to check the visitor route and evidence boundaries.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import build_player_profile

GALLERY_START = '<section class="poker-public-video-list"'
CARDS = '<div class="poker-content-grid">'
NOTES = '<section class="poker-video-source-note" id="nolanpoker-video-notes"'
TITLE = 'id="nolanpoker-video-notes-title"'
PROMPT = '<p class="poker-video-prompt">'
CSS_FILE = ROOT / "assets/poker-discovery.css"


def gallery_errors(html: str, css: str) -> list[str]:
    errors = []
    if html.count('id="watch"') != 1 or html.count(GALLERY_START) != 1:
        return ["missing or duplicate video section"]
    area = html.split('id="watch"', 1)[1].split('id="standoff-ak-source-review"', 1)[0]
    if not all(marker in area for marker in (PROMPT, CARDS, NOTES, TITLE)):
        return ["gallery, prompt or visible provenance note missing"]
    if not (area.index(PROMPT) < area.index(CARDS) < area.index(NOTES)):
        errors.append("the long source explanation must follow the videos")
    pre_card = area.split(CARDS, 1)[0]
    visible_intro = re.sub(r'<[^>]*>', ' ', pre_card)
    if len(visible_intro.split()) > 100:
        errors.append("too much explanatory prose before the first video")
    if 'href="#nolanpoker-video-notes"' not in pre_card:
        errors.append("the early source note shortcut is missing")
    if area.count('id="nolanpoker-video-notes"') != 1:
        errors.append("source ledger needs one anchored target")
    if 'aria-labelledby="nolanpoker-video-notes-title"' not in area:
        errors.append("source ledger needs an accessible heading")
    if 'The South Point video title and channel identity were checked' not in area:
        errors.append("public metadata boundary was removed")
    if 'their current titles, cuts and chapter times have not been independently verified' not in area:
        errors.append("archived Portland Meadows caveat was removed")
    if 'This upload is not evidence for the separately listed Lucky 300 result' not in area:
        errors.append("South Point videos could be confused with independently listed results")
    if 'href="/poker/nolan-kido/"' not in area:
        errors.append("the independent player record is no longer reachable")
    if '.page-poker #watch .poker-content-card h4 {' not in css:
        errors.append("video H4 headings have no intentional typography")
    if 'font:700 clamp(1.25rem,1.6vw,1.5rem)/1.3 var(--sans)' not in css:
        errors.append("video headings lost their readable responsive scale")
    if '.page-poker #watch :is(.poker-content-card h4 a,.poker-video-prompt a):focus-visible' not in css:
        errors.append("focus styling is missing from video titles or source shortcut")
    if '.page-poker #watch .poker-content-card h4 a { display:inline-block; min-height:44px;' not in css:
        errors.append("video title links lost their touch target")
    return errors


class NolanPokerGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/poker/home.html").read_text(encoding="utf-8")
        cls.html = (ROOT / "poker/index.html").read_text(encoding="utf-8")
        cls.css = CSS_FILE.read_text(encoding="utf-8")

    def test_video_choice_precedes_long_source_note_in_source_and_page(self):
        for html in (self.source, self.html):
            with self.subTest(published=html is self.html):
                self.assertEqual(gallery_errors(html, self.css), [])
                self.assertNotIn("\u2014", html)
        self.assertEqual(self.html.count('id="nolanpoker-video-notes"'), 1)

    def test_built_pages_share_the_current_standalone_stylesheet(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.html)
        self.assertEqual(build_player_profile.render(), (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8"))
        version = sha256(CSS_FILE.read_bytes()).hexdigest()[:12]
        tag = '/assets/poker-discovery.css?v=' + version
        for file in ("poker/index.html", "poker/library/index.html", "poker/nolan-kido/index.html"):
            with self.subTest(page=file):
                text = (ROOT / file).read_text(encoding="utf-8")
                self.assertIn(tag, text)
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        self.assertEqual(next(p["updated"] for p in pages if p["path"] == "/poker/"), "2026-11-12")
        self.assertIn('"dateModified": "2026-11-12"', self.html)
        self.assertIn('"dateModified": "2026-11-12"', (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8"))

    def test_dead_source_jump_buried_links_and_unstyled_headings_fail(self):
        mutations = (
            (self.source.replace('href="#nolanpoker-video-notes"', 'href="#missing-notes"', 1), self.css),
            (self.source.replace(NOTES, '<section class="other-note" id="missing-notes"', 1), self.css),
            (self.source.replace(CARDS, '<p>' + 'Long explanation. ' * 75 + '</p>' + CARDS, 1), self.css),
            (self.source, self.css.replace('.page-poker #watch .poker-content-card h4 {', '.page-poker #watch .poker-content-card h3 {', 1)),
            (self.source, self.css.replace('.page-poker #watch :is(.poker-content-card h4 a,.poker-video-prompt a):focus-visible', '.page-poker #watch :is(.poker-content-card h4 a,.poker-video-prompt a):hover', 1)),
        )
        for html, css in mutations:
            with self.subTest(content_change=html != self.source):
                self.assertTrue(gallery_errors(html, css))


if __name__ == "__main__":
    unittest.main()
