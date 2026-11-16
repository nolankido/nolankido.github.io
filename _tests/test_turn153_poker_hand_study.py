"""Turn 153: map only source-documented NolanPoker hands to study guides.

No guide link is a hand-specific solver verdict, ICM solution, official
result, or current-cut audiovisual verification.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

SOURCE = ROOT / "_source/poker/home.html"
PUBLIC = ROOT / "poker/index.html"
BRIDGE = re.compile(
    r'<section class="poker-hand-study-path" id="nolanpoker-hand-study" '
    r'aria-labelledby="nolanpoker-hand-study-title">([\s\S]*?)</section>'
)
PAIRS = (
    (
        "/poker/episodes/portland-meadows-ep1/#hand-64o-record",
        "6-4 offsuit at approximately 9.87 BB near the bubble",
        "/poker/six-to-ten-bb-tournament-decisions/",
        "study 6–10 BB shoves and other options",
    ),
    (
        "/poker/episodes/portland-meadows-ep1/#hand-77-record",
        "Pocket sevens at approximately 19.5 BB, four-handed",
        "/poker/short-stack-decisions/",
        "study the 10–20 BB tournament decision framework",
    ),
    (
        "/poker/episodes/portland-meadows-standoff/#standoff-second-decision",
        "A-K at approximately 10.2 BB before a flat-call, then facing two shoves",
        "/poker/short-stack-decisions/",
        "review call-price and ICM assumptions",
    ),
)


def hand_study_errors(document: str) -> list[str]:
    errors = []
    matched = list(BRIDGE.finditer(document))
    if len(matched) != 1:
        return ["hand-study bridge missing or repeated"]
    section = matched[0].group(1)
    if document.count('id="nolanpoker-hand-study-title"') != 1:
        errors.append("bridge accessible label missing or repeated")
    if not document.count('href="#nolanpoker-hand-study"') == 2:
        errors.append("both original companion video cards need the study shortcut")
    card_area = re.search(
        r'<div class="poker-content-grid">([\s\S]*?)</div>\s*'
        r'<p class="small-copy">External video availability can change\.',
        document,
    )
    if not card_area:
        errors.append("existing video gallery boundary changed")
    else:
        cards = re.findall(
            r'<article class="poker-content-card"(?: id="[^"]+")?>(.*?)</article>',
            card_area.group(1), re.S,
        )
        if len(cards) != 6:
            errors.append("original six-video gallery count changed")
        elif (
            'href="#nolanpoker-hand-study"' not in cards[1]
            or 'href="#nolanpoker-hand-study"' not in cards[2]
            or any('href="#nolanpoker-hand-study"' in c for i, c in enumerate(cards) if i not in (1, 2))
        ):
            errors.append("only the two source-companion cards should cross-link to study")
    if not (
        document.index('class="poker-player-profile-link"') <
        matched[0].start() <
        document.index('id="nolanpoker-video-notes"')
    ):
        errors.append("bridge must follow videos and precede the provenance note")
    items = re.findall(r'<li>(.*?)</li>', section, re.S)
    if len(items) != len(PAIRS):
        errors.append("must identify exactly three source-documented decisions")
    else:
        for item, (hand_url, hand_label, guide_url, guide_label) in zip(items, PAIRS):
            links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', item)
            if links != [(hand_url, hand_label), (guide_url, guide_label)]:
                errors.append("incorrect hand-to-guide link, label, or order")
    if (
        'These guides do not solve these exact tournament hands.' not in section
        or 'None of the three documented hands above is a confirmed 3–5 BB hand.' not in section
        or 'An outcome or retrospective read does not prove the best action.' not in section
    ):
        errors.append("the hand reconstruction and solver limits must remain explicit")
    if section.count('href="/poker/three-to-five-bb-tournament-decisions/"') != 1:
        errors.append("3–5 BB guide must be separate from the documented hand examples")
    if any(text in section for text in ("—", "guaranteed", "solver proves", "<script", "<iframe", "utm_", "onclick=")):
        errors.append("new unverified claim or executable content")
    return errors


class NolanPokerHandStudyBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")

    def test_identical_accessible_hand_study_bridge_in_both_pages(self):
        for document in (self.source, self.public):
            with self.subTest(rendered=document is self.public):
                self.assertEqual(hand_study_errors(document), [])
        self.assertEqual(BRIDGE.search(self.source).group(0),
                         BRIDGE.search(self.public).group(0))
        self.assertNotIn("—", BRIDGE.search(self.public).group(0))

    def test_source_records_support_each_number_and_anchor(self):
        deepstack = (ROOT / "_source/poker/portland-meadows-ep1.html").read_text(encoding="utf-8")
        standoff = (ROOT / "_source/poker/portland-meadows-standoff.html").read_text(encoding="utf-8")
        self.assertIn('id="hand-64o-record"', deepstack)
        self.assertIn('id="hand-77-record"', deepstack)
        self.assertIn("9.87", deepstack)
        self.assertIn("19.5", deepstack)
        self.assertIn('id="standoff-second-decision"', standoff)
        self.assertIn("61,000", standoff)
        self.assertIn("6,000", standoff)
        self.assertIn("46,000", standoff)
        for guide in {entry[2] for entry in PAIRS} | {
            "/poker/three-to-five-bb-tournament-decisions/"
        }:
            with self.subTest(guide=guide):
                self.assertTrue((ROOT / guide.lstrip("/") / "index.html").is_file())

    def test_compiled_source_and_revision_remain_consistent(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.public)
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        poker = next(page for page in pages if page["path"] == "/poker/")
        self.assertEqual(poker["updated"], "2026-11-16")
        self.assertIn('"dateModified": "2026-11-16"', self.public)

    def test_broken_hand_guide_pair_and_missing_source_boundary_are_detected(self):
        mutations = (
            self.source.replace('id="nolanpoker-hand-study"', 'id="different-target"', 1),
            self.source.replace('href="/poker/six-to-ten-bb-tournament-decisions/"',
                                'href="/poker/not-a-guide/"', 1),
            self.source.replace("approximately 19.5 BB", "approximately 4 BB", 1),
            self.source.replace("These guides do not solve these exact tournament hands.",
                                "A solver proves every shove.", 1),
            self.source.replace("None of the three documented hands above is a confirmed 3–5 BB hand.",
                                "The first hand was played with 3 BB.", 1),
        )
        for index, variant in enumerate(mutations):
            with self.subTest(index=index):
                self.assertTrue(hand_study_errors(variant))


if __name__ == "__main__":
    unittest.main()
