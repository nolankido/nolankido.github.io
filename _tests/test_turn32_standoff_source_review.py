"""Turn 32: actual archived A-K narration, source limits, and offline checks.

These tests do not compare the uploaded YouTube video with the final v9 edit.
"""
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

from reviewed_release import read as reviewed_bytes
import turn32_standoff_source_history as history

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import check_live
import turn33_standoff_companion_history as turn33

SOURCE = ROOT / "_source/poker/home.html"
PUBLIC = ROOT / "poker/index.html"
LEDGER = ROOT / "downloads/portland-meadows-standoff-ak-source-ledger.json"
CHECKER = ROOT / "downloads/portland-meadows-standoff-ak-gate.py"
ANCHOR = '<section class="poker-standoff-source-note" id="standoff-ak-source-review"'
BASE = history.PARENT
RELEASE = "04a452d5806799778d7ae040549ffceec78871af"
COMPANION_RELEASE = "80170a3909e2a70fcbbb34ea667953b2af77e45f"
VIDEOS = (
    "https://www.youtube.com/watch?v=qABaiIcvvpU",
    "https://www.youtube.com/watch?v=I75GOBVXij4",
    "https://www.youtube.com/watch?v=edNSD5BjIV8",
)


def source_section(text):
    if text.count(ANCHOR) != 1:
        raise AssertionError("Stand Off source section is missing or repeated")
    start = text.index(ANCHOR)
    return text[start:text.index("</section>", start) + len("</section>")]


def video_cards(text):
    """Count only videos in the Watch grid, not other Poker hub cards."""
    matches = re.findall(
        r'<section class="poker-public-video-list".*?'
        r'<div class="poker-content-grid">(.*?)</div>', text, re.S
    )
    if len(matches) != 1:
        raise AssertionError("Expected one public-video grid")
    return re.findall(r'<article class="poker-content-card">.*?</article>',
                      matches[0], re.S)


def gate(*args):
    return subprocess.run([sys.executable, str(CHECKER), *map(str, args)],
                          capture_output=True, text=True)


class Balance(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unmatched HTML element " + tag)


class StandOffSourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_new_section_equals_public_poker_html_and_uses_native_structure(self):
        section = source_section(self.source)
        self.assertEqual(section, source_section(self.public))
        self.assertEqual(self.public.count('id="standoff-ak-source-review"'), 1)
        self.assertEqual(self.public.count('id="standoff-ak-source-review-title"'), 1)
        self.assertEqual(section.count("<li>"), 4)
        self.assertIn("Decision 1", section)
        self.assertIn("Decision 2", section)
        self.assertIn("Later hotel review", section)
        self.assertIn("17 of 78", section)
        self.assertIn('href="/downloads/portland-meadows-standoff-ak-source-ledger.json" download', section)
        self.assertIn('href="/downloads/portland-meadows-standoff-ak-gate.py" download', section)
        self.assertNotIn("<script", section)
        self.assertNotIn("<iframe", section)
        self.assertNotIn("<form", section)
        self.assertNotIn("\u2014", section)
        parsed = Balance()
        parsed.feed(section)
        self.assertEqual(parsed.stack, [])

    def test_video_hub_keeps_original_links_and_newer_companion_boundaries(self):
        original = reviewed_bytes(
            RELEASE, "poker/index.html", history.BLOBS["poker/index.html"][1]
        ).decode("utf-8")
        companion = reviewed_bytes(
            COMPANION_RELEASE, "poker/index.html",
            turn33.BLOBS["poker/index.html"][1]
        ).decode("utf-8")

        self.assertEqual(len(video_cards(original)), 3)
        self.assertIn("Episode 2 has a more limited source review", original)
        self.assertIn("not a timecode-verified companion for the current YouTube cut", original)
        self.assertEqual(len(video_cards(companion)), 3)
        self.assertIn("Episodes 1 and 2 each have a written companion", companion)
        self.assertIn("The first two videos have written companions", companion)

        current_cards = video_cards(self.public)
        self.assertGreaterEqual(len(current_cards), 3)
        for url in VIDEOS:
            self.assertEqual(sum('href="' + url + '"' in card
                                 for card in current_cards), 1, url)
        self.assertIn('href="#standoff-ak-source-review"', self.public)
        self.assertIn("Neither text claims frame-by-frame verification", self.public)
        self.assertIn('href="/poker/episodes/portland-meadows-ep1/"', self.public)
        self.assertIn('href="/poker/episodes/portland-meadows-standoff/"', self.public)
        for url in ("https://www.youtube.com/watch?v=bxpaM_1mWPE",
                    "https://www.youtube.com/watch?v=HE7VDvO9gDU"):
            self.assertEqual(sum('href="' + url + '"' in card
                                 for card in current_cards), 1, url)
        self.assertNotIn("JToB7upHqEM", self.public)

    def test_recorded_actions_and_arithmetic_are_bounded(self):
        d = self.ledger
        self.assertEqual(d["schema_version"], 1)
        self.assertEqual(d["public_video_url"], VIDEOS[1])
        self.assertFalse(d["current_cut_reviewed"])
        self.assertFalse(d["frame_accurate_video_chapters_verified"])
        self.assertFalse(d["event"]["payout_amount_known"])
        e = d["event"]
        hand = d["decision"]
        self.assertEqual((e["sb_chips"], e["bb_chips"], e["bb_ante_chips"]),
                         (3000, 6000, 6000))
        self.assertEqual((e["clock_observation_players_left"],
                          e["clock_observation_entries"]), (17, 78))
        self.assertEqual(hand["hero_position"], "button")
        self.assertEqual(hand["hole_cards_reported"], "A-K")
        self.assertEqual(hand["starting_stack_approx_chips"] -
                         hand["opener_raise_to_chips"], hand["after_flat_approx_chips"])
        self.assertEqual(hand["bb_additional_to_call_before_jam_chips"],
                         hand["opener_raise_to_chips"] - hand["bb_previous_blind_chips"])
        self.assertEqual(hand["hero_calls_additional_approx_chips"], 46000)
        self.assertEqual([hand["big_blind_revealed"], hand["opener_revealed"]],
                         ["K-K", "Q-Q"])
        self.assertFalse(hand["full_board_verified"])
        self.assertFalse(hand["villain_card_suits_verified"])
        self.assertFalse(hand["solver_verdict_verified"])
        self.assertIn("retrospective hypothesis", hand["later_read"])
        self.assertIn("not an independently checked current YouTube cut", d["source_kind"])

    def test_gate_passes_record_and_synthetic_negative_controls(self):
        valid = gate("--check", LEDGER)
        self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)
        data = json.loads(valid.stdout)
        self.assertEqual(data["result"], "no_targeted_flags")
        self.assertEqual(data["flag_count"], 0)
        synthetic = gate("--self-test")
        self.assertEqual(synthetic.returncode, 0, synthetic.stderr + synthetic.stdout)
        controls = json.loads(synthetic.stdout)
        self.assertTrue(controls["passed"])
        self.assertEqual(len(controls["cases"]), 7)
        self.assertTrue(controls["synthetic"])

    def test_record_tampering_is_flagged_and_invalid_json_is_rejected(self):
        variations = (
            ("current_cut_reviewed", True, "UNVERIFIED_AS_FACT"),
            ("hole_cards_reported", "A-Q", "SOURCE_CONFLICT"),
            ("villain_card_suits_verified", True, "UNVERIFIED_AS_FACT"),
            ("after_flat_approx_chips", 42000, "STACK_ARITHMETIC"),
            ("opener_revealed", "A-A", "SOURCE_CONFLICT"),
            ("later_read", "This was mathematically proven.", "MISSING_BOUNDARY"),
        )
        with TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            for key, changed, wanted in variations:
                with self.subTest(field=key):
                    item = deepcopy(self.ledger)
                    target = item if key == "current_cut_reviewed" else item["decision"]
                    target[key] = changed
                    path.write_text(json.dumps(item), encoding="utf-8")
                    result = gate("--check", path)
                    self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                    self.assertIn(wanted, {flag["code"] for flag in json.loads(result.stdout)["findings"]})
            path.write_text("{bad", encoding="utf-8")
            invalid = gate("--check", path)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("Input error", invalid.stderr)

    def test_original_poker_revision_and_current_sitemap_dates_are_coherent(self):
        pages = build.public_pages()
        poker = next(p for p in pages if p["id"] == "poker")
        self.assertGreaterEqual(poker["updated"], "2026-11-04")
        schema = json.loads(re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            self.public
        ).group(1))
        self.assertEqual(schema["dateModified"], poker["updated"])
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/">',
                      self.public)
        old = reviewed_bytes(
            BASE, "sitemap.xml", history.BLOBS["sitemap.xml"][0]
        ).decode("utf-8")
        new = reviewed_bytes(
            RELEASE, "sitemap.xml", history.BLOBS["sitemap.xml"][1]
        ).decode("utf-8")
        current = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

        def dates(content):
            entries = [(row.findtext(ns + "loc"), row.findtext(ns + "lastmod"))
                       for row in ET.fromstring(content)]
            self.assertEqual(len(entries), len({url for url, _ in entries}))
            return dict(entries)

        before, after, today = dates(old), dates(new), dates(current)
        self.assertEqual(set(before), set(after))
        self.assertEqual({name for name in before if before[name] != after[name]},
                         {"https://nolankido.com/poker/"})
        self.assertEqual(after["https://nolankido.com/poker/"], "2026-11-04")
        self.assertEqual(today["https://nolankido.com/poker/"], poker["updated"])

    def test_compiled_poker_hub_and_read_only_downloads(self):
        generated = build.build_outputs()
        self.assertEqual(generated[Path("poker/index.html")], self.public)
        self.assertEqual(generated[Path("sitemap.xml")],
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        targets = check_live.targets()
        for f in (LEDGER, CHECKER):
            url = "/" + f.relative_to(ROOT).as_posix()
            self.assertEqual(targets[url], (200, f.read_bytes()))


if __name__ == "__main__":
    unittest.main()
