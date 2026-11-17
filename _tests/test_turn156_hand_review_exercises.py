"""Turn 156: evidence-first review exercises in three documented tournament hands.

The questions ask readers to name missing decision inputs. Disclosed notes
verify facts and uncertainty rather than claiming solver or ICM answers.
"""
from __future__ import annotations

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

EP1_SOURCE = ROOT / poker_episode.SOURCE
STANDOFF_SOURCE = ROOT / poker_standoff_episode.SOURCE

EXERCISES = (
    {
        "section": "hand-64o-record",
        "id": "hand-64o-review",
        "after": "<h3>Thinking reported in the video</h3>",
        "prompt": "Ignore the winning runout.",
        "evidence": ("9.87 BB", "13 remained and 10 were paid",
                     "calling range", "The win does not prove"),
    },
    {
        "section": "hand-77-record",
        "id": "hand-77-review",
        "after": "<h3>Alternatives described in the narration</h3>",
        "prompt": "Set aside the double-up.",
        "evidence": ("calling, a smaller raise and shoving", "A-T offsuit",
                     "payout ladder", "does not establish"),
    },
    {
        "section": "standoff-second-decision",
        "id": "standoff-second-review",
        "after": "<p>These arithmetic checks explain why the second call",
        "prompt": "Treat the first call and the later decision separately.",
        "evidence": ("15,000 had already gone in", "46,000 remained",
                     "10.2 BB before flat-calling",
                     "neither the eventual showdown".capitalize()),
    },
)

DISCLOSURE_SUMMARY = "Reveal the evidence check, not a solver answer"


def section(markup: str, anchor: str) -> str:
    results = re.findall(
        r'<section id="' + re.escape(anchor) + r'"[^>]*>(.*?)</section>',
        markup, re.S,
    )
    if len(results) != 1:
        raise ValueError("Missing or duplicate documented hand section: " + anchor)
    return results[0]


def exercise_errors(markup: str, record: dict) -> list[str]:
    errors = []
    scope = section(markup, record["section"])
    if markup.count('id="' + record["id"] + '"') != 1:
        errors.append("Missing or duplicate evidence check ID")
    pattern = (
        r'<aside class="poker-hand-review-check" aria-label="[^"]+">'
        r'\s*<p><strong>Reader exercise:</strong>(.*?)</p>'
        r'\s*<details class="poker-details" id="' + re.escape(record["id"]) + r'">'
        r'<summary>' + re.escape(DISCLOSURE_SUMMARY) + r'</summary>'
        r'\s*<p>(.*?)</p>\s*</details>\s*</aside>'
    )
    matches = list(re.finditer(pattern, scope, re.S))
    if len(matches) != 1:
        return errors + ["The visible prompt or collapsed native disclosure is missing"]
    match = matches[0]
    prompt, evidence = match.group(1), match.group(2)
    if record["prompt"] not in prompt:
        errors.append("Outcome-independent question is missing")
    for expected in record["evidence"]:
        if expected not in evidence:
            errors.append("Missing source-limited evidence: " + expected)
    if scope.index("</dl>") > match.start() or scope.index(record["after"]) < match.end():
        errors.append("Exercise not between the hand ledger and the analysis")
    if "range" not in prompt and "ranges" not in prompt and "missing" not in prompt and "payout" not in prompt:
        errors.append("Reader exercise does not request an unknown input")
    if any(text in match.group(0) for text in (
        "—", "<script", "<iframe", "<form", "utm_", "onclick=",
        "guaranteed optimal", "proved correct", "verified solver", "video chapter",
    )):
        errors.append("Executable or unsupported definitive claim")
    return errors


class DocumentedHandExerciseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ep1_source = EP1_SOURCE.read_text(encoding="utf-8")
        cls.standoff_source = STANDOFF_SOURCE.read_text(encoding="utf-8")
        cls.ep1_public = (ROOT / poker_episode.OUTPUT).read_text(encoding="utf-8")
        cls.standoff_public = (ROOT / poker_standoff_episode.OUTPUT).read_text(encoding="utf-8")

    def test_one_accessible_disclosed_check_per_hand_in_source_and_page(self):
        for index, record in enumerate(EXERCISES):
            authored = self.ep1_source if index < 2 else self.standoff_source
            published = self.ep1_public if index < 2 else self.standoff_public
            with self.subTest(section=record["section"]):
                self.assertEqual(exercise_errors(authored, record), [])
                self.assertEqual(exercise_errors(published, record), [])
                start = '<aside class="poker-hand-review-check"'
                scope1 = section(authored, record["section"])
                scope2 = section(published, record["section"])
                self.assertEqual(
                    scope1[scope1.index(start):scope1.index("</aside>") + len("</aside>")],
                    scope2[scope2.index(start):scope2.index("</aside>") + len("</aside>")],
                )
                self.assertNotIn('<details open', scope1)
        self.assertEqual(self.ep1_source.count('class="poker-hand-review-check"'), 2)
        self.assertEqual(self.standoff_source.count('class="poker-hand-review-check"'), 1)

    def test_standalone_builders_and_public_registries_remain_exact(self):
        self.assertEqual(self.ep1_public, build_poker_episode.render())
        self.assertEqual(self.standoff_public, build_standoff_episode.render())
        for registry, public, published_date in (
            (poker_episode, self.ep1_public, "2026-11-02"),
            (poker_standoff_episode, self.standoff_public, "2026-11-04"),
        ):
            with self.subTest(route=registry.ROUTE):
                info = registry.record(ROOT)
                self.assertEqual(info["date"], published_date)
                self.assertEqual(info["modified"], "2026-11-16")
                self.assertEqual(public.count("<h1 "), 1)
                self.assertEqual(public.count('aria-label="Breadcrumb"'), 1)
                self.assertIn('article:modified_time" content="2026-11-16"', public)
                schema = json.loads(re.search(
                    r'<script type="application/ld\+json">(.*?)</script>', public, re.S
                ).group(1))
                self.assertEqual(schema["datePublished"], published_date)
                self.assertEqual(schema["dateModified"], "2026-11-16")
                self.assertEqual(schema["url"], registry.URL)
                self.assertNotIn("—", public)

    def test_original_study_links_metadata_feeds_and_sitemap_survive(self):
        self.assertIn('href="/poker/six-to-ten-bb-tournament-decisions/"',
                      section(self.ep1_source, "hand-64o-record"))
        self.assertIn('href="/poker/short-stack-decisions/"',
                      section(self.ep1_source, "hand-77-record"))
        self.assertIn('href="/poker/short-stack-decisions/"',
                      section(self.standoff_source, "standoff-second-decision"))
        source_ledger = json.loads(
            (ROOT / "downloads/portland-meadows-ep1-scene-claims.json").read_text(encoding="utf-8")
        )
        self.assertEqual(source_ledger["reviewed_record_date"], "2026-11-04")
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        mod = {r.findtext(ns + "loc"): r.findtext(ns + "lastmod") for r in sitemap}
        for record in (poker_episode, poker_standoff_episode):
            self.assertEqual(mod[record.URL], "2026-11-16")
        for feed in ("poker/feed.xml", "writing.xml"):
            document = ET.fromstring((ROOT / feed).read_text(encoding="utf-8"))
            for registry in (poker_episode, poker_standoff_episode):
                items = [
                    item for item in document.findall("./channel/item")
                    if item.findtext("link") == registry.URL
                ]
                self.assertEqual(len(items), 1)

    def test_removed_questions_false_verdicts_and_moved_prompts_are_detected(self):
        bad = (
            (self.ep1_source.replace('id="hand-64o-review"', 'id="broken-anchor"', 1),
             EXERCISES[0]),
            (self.ep1_source.replace("The win does not prove", "The win proves", 1),
             EXERCISES[0]),
            (self.ep1_source.replace("Set aside the double-up.", "The shove was optimal.", 1),
             EXERCISES[1]),
            (self.standoff_source.replace(
                "Treat the first call and the later decision separately.",
                "The first call forced the second call.", 1,
             ), EXERCISES[2]),
            (self.standoff_source.replace(DISCLOSURE_SUMMARY,
                                          "Reveal a solver solution", 1), EXERCISES[2]),
        )
        for index, (markup, record) in enumerate(bad):
            with self.subTest(index=index):
                self.assertTrue(exercise_errors(markup, record))


if __name__ == "__main__":
    unittest.main()
