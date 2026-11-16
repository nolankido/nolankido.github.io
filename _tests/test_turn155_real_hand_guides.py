"""Turn 155: source-limited real-hand reading routes inside fictional-stack guides.

The guides' worked examples remain fictional. Hand reports link to separately
published, archived-source companions. Navigation does not certify a shove,
showdown range, current-cut timestamp, an ICM result or a solver output.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import poker_finder
import poker_library
import poker_reading

GUIDES = (
    {
        "slug": "six-to-ten-bb-tournament-decisions",
        "published": "2026-11-15",
        "minutes": 19,
        "nav_label": "Source-documented hand for further reading",
        "anchors": ("bridge-real-hand",),
        "hand_links": ("/poker/episodes/portland-meadows-ep1/#hand-64o-record",),
        "caveats": ("not one of the fictional exercises", "Neither the win nor these action trees supply a solved verdict."),
    },
    {
        "slug": "short-stack-decisions",
        "published": "2026-10-06",
        "minutes": 16,
        "nav_label": "Source-documented tournament decisions for further reading",
        "anchors": ("deepstack-real-sevens", "standoff-real-ak"),
        "hand_links": (
            "/poker/episodes/portland-meadows-ep1/#hand-77-record",
            "/poker/episodes/portland-meadows-standoff/#standoff-second-decision",
        ),
        "caveats": (
            "the outcome does not establish the best play",
            "The pre-flat stack is not the later stack at risk.",
            "without asserting solver results.",
        ),
    },
)


def source(name):
    return (ROOT / "_source/poker" / (name + ".html")).read_text(encoding="utf-8")


def page(name):
    return (ROOT / "poker" / name / "index.html").read_text(encoding="utf-8")


def case_navigation(markup: str, config: dict) -> str | None:
    pattern = (
        r'<nav class="viewer-learning-paths" aria-label="' +
        re.escape(config["nav_label"]) + r'">([\s\S]*?)</nav>'
    )
    matches = re.findall(pattern, markup)
    return matches[0] if len(matches) == 1 else None


def route_errors(markup: str, config: dict) -> list[str]:
    body = case_navigation(markup, config)
    if body is None:
        return ["missing or duplicate source-bounded hand navigation"]
    errors = []
    for anchor in config["anchors"]:
        if markup.count(f'id="{anchor}"') != 1 or f'id="{anchor}"' not in body:
            errors.append("a real-hand arrival anchor is missing or repeated")
    found = re.findall(r'<a href="([^"]+)">', body)
    if found != list(config["hand_links"]):
        errors.append("wrong hand companion, fragment or number of destinations")
    for statement in config["caveats"]:
        if statement not in body:
            errors.append("the original account and solved-strategy limits must remain visible")
    if body.count("<article>") != len(config["hand_links"]):
        errors.append("every documented hand needs its own reading card")
    if any(value in body for value in ("—", "<script", "<iframe", "onclick=", "utm_", "t=6:08")):
        errors.append("no tracking, current-cut timecodes or executable content")
    return errors


class RealHandStudyGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        cls.outputs = build.build_outputs()

    def test_source_and_published_nav_are_identical_and_source_bounded(self):
        for guide in GUIDES:
            with self.subTest(slug=guide["slug"]):
                src = source(guide["slug"])
                html = page(guide["slug"])
                self.assertEqual(route_errors(src, guide), [])
                self.assertEqual(route_errors(html, guide), [])
                self.assertEqual(case_navigation(src, guide), case_navigation(html, guide))
                self.assertNotIn("—", src + html)
                self.assertEqual(poker_library.minutes(src), guide["minutes"])
                # The linked hand is navigation, not part of the guide's fictional
                # question set or its indexed text.
                before = re.sub(
                    r'<nav class="viewer-learning-paths" aria-label="' +
                    re.escape(guide["nav_label"]) + r'">[\s\S]*?</nav>\s*',
                    '', src, count=1,
                )
                self.assertEqual(poker_finder.GuideText(src).sections,
                                 poker_finder.GuideText(before).sections)
                self.assertEqual(
                    poker_reading.VisibleHeadings(src).headings,
                    poker_reading.VisibleHeadings(before).headings
                )

    def test_hand_links_point_to_exact_existing_documented_records(self):
        receipts = {
            "/poker/episodes/portland-meadows-ep1/#hand-64o-record": ("9.87", "A-K suited"),
            "/poker/episodes/portland-meadows-ep1/#hand-77-record": ("19.5", "75,000"),
            "/poker/episodes/portland-meadows-standoff/#standoff-second-decision": ("46,000", "15,000"),
        }
        for url, numbers in receipts.items():
            with self.subTest(url=url):
                route, anchor = url.split("#")
                doc = (ROOT / route.lstrip("/") / "index.html").read_text(encoding="utf-8")
                self.assertEqual(doc.count(f'id="{anchor}"'), 1)
                for value in numbers:
                    self.assertIn(value, doc)
                self.assertTrue(any(url in case_navigation(source(g["slug"]), g)
                                    for g in GUIDES))

    def test_manifest_public_html_and_sitemap_have_current_revision(self):
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        entries = {
            item.findtext(ns + "loc"): item.findtext(ns + "lastmod") for item in sitemap
        }
        for guide in GUIDES:
            slug = guide["slug"]
            url = f"/poker/{slug}/"
            entry = next(p for p in self.pages if p["path"] == url)
            html = page(slug)
            with self.subTest(slug=slug):
                self.assertEqual(entry["date"], guide["published"])
                self.assertEqual(entry["updated"], "2026-11-16")
                self.assertEqual(entries["https://nolankido.com" + url], "2026-11-16")
                self.assertIn('article:modified_time" content="2026-11-16"', html)
                self.assertIn('About ' + str(guide["minutes"]) + ' min read', html)
                self.assertIn('Updated <time datetime="2026-11-16">November 16, 2026</time>', html)
                schema_match = re.search(
                    r'<script type="application/ld\+json">([\s\S]*?)</script>', html
                )
                self.assertIsNotNone(schema_match)
                schema = json.loads(schema_match.group(1))
                self.assertEqual(schema["datePublished"], guide["published"])
                self.assertEqual(schema["dateModified"], "2026-11-16")
                self.assertEqual(schema["url"], "https://nolankido.com" + url)
                self.assertEqual(self.outputs[Path("poker") / slug / "index.html"], html)
        middle = next(x for x in self.pages if x["path"] == "/poker/short-stack-decisions/")
        self.assertIn(middle["revision"], page("short-stack-decisions"))

    def test_rss_publication_dates_and_hand_history_dates_not_reset(self):
        routes = {g["slug"]: g["published"] for g in GUIDES}
        for feed in ("poker/feed.xml", "writing.xml"):
            root = ET.fromstring((ROOT / feed).read_text(encoding="utf-8"))
            for slug, original in routes.items():
                url = "https://nolankido.com/poker/" + slug + "/"
                matching = [
                    item for item in root.findall("./channel/item")
                    if item.findtext("link") == url
                ]
                self.assertEqual(len(matching), 1)
                dt = datetime.combine(date.fromisoformat(original),
                                      datetime.min.time(), tzinfo=timezone.utc)
                self.assertEqual(matching[0].findtext("pubDate"),
                                 format_datetime(dt, usegmt=True))
        self.assertIn(
            'datetime="2026-11-04"',
            (ROOT / "_source/poker/portland-meadows-ep1.html").read_text(encoding="utf-8")
        )

    def test_incorrect_destinations_and_claims_fail_the_focused_contract(self):
        for guide in GUIDES:
            src = source(guide["slug"])
            first = guide["hand_links"][0]
            with self.subTest(slug=guide["slug"]):
                self.assertTrue(route_errors(src.replace(first, "/poker/nowhere/", 1), guide))
                self.assertTrue(route_errors(
                    src.replace(guide["caveats"][0], "This hand is a confirmed optimal play.", 1),
                    guide,
                ))
                self.assertTrue(route_errors(
                    src.replace('aria-label="' + guide["nav_label"] + '"',
                                'aria-label="Missing source caveat"', 1),
                    guide,
                ))


if __name__ == "__main__":
    unittest.main()
