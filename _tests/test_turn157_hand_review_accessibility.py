"""Turn 157: standalone-only hand-review layout and direct lesson journeys.

Static contracts run with the manual release checklist. The optional
poker_hand_review_browser.py covers 320-1440 px and keyboard activation using
offline Chromium and intercepted requests. No remote tests or GitHub Actions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build_poker_episode
import build_standoff_episode
import poker_episode
import poker_standoff_episode
from test_turn156_hand_review_exercises import EXERCISES, exercise_errors

STYLE = ROOT / "assets/poker-hand-review.css"
ROUTES = (
    (
        "hand-64o-review",
        "/poker/six-to-ten-bb-tournament-decisions/#bridge-sb",
    ),
    (
        "hand-77-review",
        "/poker/short-stack-decisions/#depths",
    ),
    (
        "standoff-second-review",
        "/poker/short-stack-decisions/#icm-call",
    ),
)


def versioned_style() -> str:
    source = STYLE.read_bytes()
    blob = b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    return f'/assets/poker-hand-review.css?v={hashlib.sha1(blob).hexdigest()[:12]}'


def journey_errors(ep1: str, standoff: str, style: str) -> list[str]:
    errors: list[str] = []
    if not style.startswith("/* Source-documented NolanPoker"):
        errors.append("missing locally scoped style provenance")
    for selector in (
        ".poker-episode-companion .poker-hand-review-check",
        ".poker-details > summary:focus-visible",
        ".poker-details > p",
        ".poker-hand-review-next a",
        "scroll-margin-top: 10rem",
    ):
        if selector not in style:
            errors.append("missing layout, focus or arrival CSS: " + selector)
    if 'min-height: 44px' not in style or 'padding: .1rem 1rem 1rem' not in style:
        errors.append("small-screen tap target or answer inset was lost")
    if 'max-width: 100%' not in style or 'overflow-wrap: anywhere' not in style:
        errors.append("horizontal overflow defenses were removed")
    for index, (anchor, destination) in enumerate(ROUTES):
        document = ep1 if index < 2 else standoff
        marker = f'<details class="poker-details" id="{anchor}">'
        if document.count(marker) != 1:
            errors.append("missing or duplicate native disclosure " + anchor)
            continue
        subsection = document[document.index(marker):]
        aside_end = subsection.find('</aside>')
        if aside_end < 0:
            errors.append("unclosed review container")
            continue
        subsection = subsection[:aside_end]
        actual = re.findall(
            r'<p class="poker-hand-review-next"><a href="([^"]+)">([^<]+)</a></p>',
            subsection,
        )
        if len(actual) != 1 or actual[0][0] != destination or not actual[0][1].startswith("Continue: "):
            errors.append("missing or incorrect direct lesson action " + anchor)
        if "Reveal the evidence check, not a solver answer" not in subsection:
            errors.append("original source-limited disclosure missing " + anchor)
    for route, expected in (
        (ep1, 2),
        (standoff, 1),
    ):
        if route.count('class="poker-hand-review-next"') != expected:
            errors.append("extraneous or missing next-study links")
    return errors


class PokerHandReviewAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ep1_source = (ROOT / poker_episode.SOURCE).read_text(encoding="utf-8")
        cls.standoff_source = (ROOT / poker_standoff_episode.SOURCE).read_text(encoding="utf-8")
        cls.ep1_page = (ROOT / poker_episode.OUTPUT).read_text(encoding="utf-8")
        cls.standoff_page = (ROOT / poker_standoff_episode.OUTPUT).read_text(encoding="utf-8")
        cls.style = STYLE.read_text(encoding="utf-8")

    def test_navigation_style_scope_and_original_evidence_are_preserved(self):
        self.assertEqual(journey_errors(self.ep1_source, self.standoff_source, self.style), [])
        self.assertEqual(journey_errors(self.ep1_page, self.standoff_page, self.style), [])
        for index, record in enumerate(EXERCISES):
            with self.subTest(record=record["id"]):
                authored = self.ep1_source if index < 2 else self.standoff_source
                published = self.ep1_page if index < 2 else self.standoff_page
                self.assertEqual(exercise_errors(authored, record), [])
                self.assertEqual(exercise_errors(published, record), [])
        self.assertNotIn("—", self.ep1_source + self.standoff_source + self.style)
        self.assertNotIn("javascript:", self.ep1_source + self.standoff_source)

    def test_standalone_pages_match_manual_builders_and_versioned_css(self):
        stylesheet = versioned_style()
        for published in (self.ep1_page, self.standoff_page):
            self.assertEqual(published.count('href="' + stylesheet + '"'), 1)
            self.assertEqual(published.count('<h1 '), 1)
            self.assertIn('article:modified_time" content="2026-11-16"', published)
        self.assertEqual(build_poker_episode.render(), self.ep1_page)
        self.assertEqual(build_standoff_episode.render(), self.standoff_page)
        for path in ("poker/index.html", "poker/library/index.html"):
            self.assertNotIn(
                "poker-hand-review.css",
                (ROOT / path).read_text(encoding="utf-8")
            )

    def test_matching_lesson_fragments_exist_in_committed_pages(self):
        for anchor, target in ROUTES:
            route, fragment = target.split("#")
            with self.subTest(origin=anchor, destination=target):
                lesson = ROOT / route.lstrip("/") / "index.html"
                self.assertTrue(lesson.is_file())
                self.assertEqual(
                    lesson.read_text(encoding="utf-8").count(f'id="{fragment}"'), 1
                )

    def test_publication_identity_sitemap_and_feeds_not_reset(self):
        for registry, source, published in (
            (poker_episode, self.ep1_source, "2026-11-02"),
            (poker_standoff_episode, self.standoff_source, "2026-11-04"),
        ):
            with self.subTest(route=registry.ROUTE):
                record = registry.record(ROOT)
                self.assertEqual(record["date"], published)
                self.assertEqual(record["modified"], "2026-11-16")
                self.assertIn(f'datetime="{published}"', source)
        ledger = json.loads(
            (ROOT / "downloads/portland-meadows-ep1-scene-claims.json").read_text(encoding="utf-8")
        )
        self.assertEqual(ledger["reviewed_record_date"], "2026-11-04")
        document = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        sitemap = {item.findtext(ns + "loc"): item.findtext(ns + "lastmod") for item in document}
        for registry in (poker_episode, poker_standoff_episode):
            self.assertEqual(sitemap[registry.URL], "2026-11-16")
        for feed in ("poker/feed.xml", "writing.xml"):
            feed_xml = ET.fromstring((ROOT / feed).read_text(encoding="utf-8"))
            links = [item.findtext("link") for item in feed_xml.findall("./channel/item")]
            self.assertEqual(links.count(poker_episode.URL), 1)
            self.assertEqual(links.count(poker_standoff_episode.URL), 1)

    def test_broken_next_links_and_missing_focus_styles_fail(self):
        mutations = (
            (
                self.ep1_source.replace(
                    "/poker/six-to-ten-bb-tournament-decisions/#bridge-sb",
                    "/poker/nonexistent/#bridge-sb", 1
                ),
                self.standoff_source,
                self.style,
            ),
            (
                self.ep1_source.replace("Continue: study 10–20 BB tournament decisions",
                                        "Unverified result", 1),
                self.standoff_source,
                self.style,
            ),
            (
                self.ep1_source,
                self.standoff_source.replace(
                    "/poker/short-stack-decisions/#icm-call", "/poker/incorrect/", 1
                ),
                self.style,
            ),
            (
                self.ep1_source,
                self.standoff_source,
                self.style.replace(".poker-details > summary:focus-visible", ".poker-details summary:hover", 1),
            ),
            (
                self.ep1_source,
                self.standoff_source,
                self.style.replace("padding: .1rem 1rem 1rem", "padding: 0", 1),
            ),
        )
        for index, (ep1, standoff, style) in enumerate(mutations):
            with self.subTest(index=index):
                self.assertTrue(journey_errors(ep1, standoff, style))


if __name__ == "__main__":
    unittest.main()
