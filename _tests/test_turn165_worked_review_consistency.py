"""Turn 165: audit three completed poker reviews for accuracy and hindsight.

Source-bounded invariant checks. These validate the published reports and
record what is missing; they do not estimate pot equity, payout EV or ranges.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "ak": "downloads/poker-hand-review-example-ak.md",
    "64o": "downloads/poker-hand-review-example-64o.md",
    "77": "downloads/poker-hand-review-example-77.md",
}
RESULT_HEADINGS = {
    "ak": "## 6. Result, kept separate from both decisions",
    "64o": "## 6. Result, recorded only after the decision analysis",
    "77": "## 6. Result and later tournament outcome, kept separate",
}
REVEALS = {
    "ak": ("K-K", "Q-Q"),
    "64o": ("A-K suited", "6-4 offsuit won"),
    "77": ("A-T offsuit", "pocket sevens held", "$2,900", "$5,100"),
}
LITERAL_CHECKS = {
    "ak": (
        "61,000 / 6,000 = **10.17 BB**",
        "61,000 - 15,000 = approximately 46,000",
        "9,000",
        "3,000 / 6,000 / 6,000",
        "round 10 of 12, with 17 players remaining from 78 entries",
        "twelve-round",
        "ICM-based distribution",
        "not guarantee survival through the remaining rounds",
        "The official rules and calculation were not independently verified",
        "No contemporaneous at-table note is available",
        "No solver or ICM calculation is claimed",
    ),
    "64o": (
        "13 players remain; 10 places paid",
        "148,000 / 15,000 = 9.87 BB",
        "8,000",
        "140,000",
        "15,000 big-blind ante",
        "No contemporaneous at-table thought record",
        "no defensible numerical chip-EV or ICM verdict is available",
        "not the full calling range",
    ),
    "77": (
        "Four players remain at the final table",
        "585,000 / 30,000 = 19.5 BB",
        "75,000",
        "2.5 BB",
        "45,000 additional chips",
        "525,000",
        "big-blind ante",
        "button's opening range is not its calling range",
        "No contemporaneous at-table thought record is supplied",
        "no defensible numeric chip-EV or ICM verdict",
        "not the full calling range",
    ),
}
SOURCE_ANCHORS = {
    "ak": (
        "_source/poker/portland-meadows-standoff.html",
        ("standoff-first-decision", "standoff-second-decision", "standoff-showdown"),
    ),
    "64o": (
        "_source/poker/portland-meadows-ep1.html",
        ("hand-64o-record", "hand-64o-review"),
    ),
    "77": (
        "_source/poker/portland-meadows-ep1.html",
        ("hand-77-record", "hand-77-review"),
    ),
}


def review_errors(text_by_hand: dict[str, str]) -> list[str]:
    errors = []
    if set(text_by_hand) != set(PATHS):
        return ["Missing or extra worked hand reviews"]
    for hand, document in text_by_hand.items():
        headings = re.findall(r"(?m)^## ([1-7])\. ", document)
        if headings != list("1234567"):
            errors.append(hand + ": seven hand-review stages must be in order")
        sections = document.split(RESULT_HEADINGS[hand])
        if len(sections) != 2:
            errors.append(hand + ": expected a single separate result section")
            continue
        before, result = sections
        for reveal in REVEALS[hand]:
            if reveal in before:
                errors.append(hand + ": result leaked into decision: " + reveal)
            if reveal not in result:
                errors.append(hand + ": missing result evidence: " + reveal)
        for expected in LITERAL_CHECKS[hand]:
            if expected not in document:
                errors.append(hand + ": missing source fact or limitation: " + expected)
        if not all(token in document.lower() for token in (
            "unknown", "not", "reported", "decision", "after", "review"
        )):
            errors.append(hand + ": missing epistemic framing")
        if any(token in document for token in (
            "\u2014", "<script", "<iframe", "onclick=", "utm_source=",
            "verified solver solution", "guaranteed profitable"
        )):
            errors.append(hand + ": unsafe prose, code or unsupported verdict")

    ak_before = text_by_hand["ak"].split(RESULT_HEADINGS["ak"])[0]
    for hindsight in (
        "immediately after elimination", "after busting", "after he lost",
        "I called the additional amount and lost"
    ):
        if hindsight in ak_before:
            errors.append("ak: narrated outcome disclosed before the result section")
    if "conventional fixed-place payout ladder" not in ak_before:
        errors.append("ak: special survivor-only format was confused with normal payout ladder")
    if "players still holding chips" not in ak_before:
        errors.append("ak: round-12 survivor eligibility is missing")
    if "the exact payout formula" not in text_by_hand["ak"].lower():
        errors.append("ak: payout formula incorrectly presented as known")
    if any(word in text_by_hand["64o"].split(RESULT_HEADINGS["64o"])[0]
           for word in ("showed A-K", "actual caller held A-K")):
        errors.append("64o: caller hand disclosed during decision")
    if "opening and calling" not in text_by_hand["77"]:
        errors.append("77: opener/caller range distinction lost")
    return errors


class WorkedHandConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {
            hand: (ROOT / path).read_text(encoding="utf-8")
            for hand, path in PATHS.items()
        }

    def test_three_examples_preserve_evidence_and_outcome_separation(self):
        self.assertEqual(review_errors(self.docs), [])

    def test_facts_and_public_anchors_agree_with_original_hand_records(self):
        for hand, (source_path, anchors) in SOURCE_ANCHORS.items():
            source = (ROOT / source_path).read_text(encoding="utf-8")
            with self.subTest(hand=hand):
                for anchor in anchors:
                    self.assertEqual(source.count('id="' + anchor + '"'), 1)
        standoff = (ROOT / SOURCE_ANCHORS["ak"][0]).read_text(encoding="utf-8")
        for fact in (
            "stopped after twelve rounds",
            "those still holding chips then paid",
            "ICM-based calculation",
            "Round 10 of 12; 17 players remaining from 78 entries",
            "3,000 / 6,000 / 6,000",
        ):
            self.assertIn(fact, standoff)
        ep1 = (ROOT / SOURCE_ANCHORS["64o"][0]).read_text(encoding="utf-8")
        for fact in (
            "13 players remain with 10 paid",
            "8,000 / 15,000 / 15,000",
            "About 148,000",
            "Four players at the final table",
            "15,000 / 30,000 / 30,000",
            "About 585,000",
            "button raises to 75,000 total",
        ):
            self.assertIn(fact, ep1)

    def test_all_three_conversions_are_mathematically_correct(self):
        self.assertAlmostEqual(61000 / 6000, 10.17, places=2)
        self.assertEqual(61000 - 15000, 46000)
        self.assertEqual(15000 - 6000, 9000)
        self.assertAlmostEqual(148000 / 15000, 9.87, places=2)
        self.assertEqual(148000 - 8000, 140000)
        self.assertEqual(585000 / 30000, 19.5)
        self.assertEqual(585000 - 30000 - 30000, 525000)
        self.assertEqual(75000 - 30000, 45000)
        self.assertEqual(75000 / 30000, 2.5)

    def test_all_examples_remain_offsite_private_sheet_studies(self):
        blank = (ROOT / "downloads/poker-hand-review.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"(?m)^## [1-7]\. ", blank)), 7)
        for hand, path in PATHS.items():
            with self.subTest(hand=hand):
                self.assertIn("https://nolankido.com/" + path, blank)
                self.assertIn("https://nolankido.com/downloads/poker-hand-review.md",
                              self.docs[hand])
                self.assertIn("Keep", blank)
        for personal_value in ("61,000", "585,000", "148,000", "Nolan"):
            self.assertNotIn(personal_value, blank)

    def test_negative_controls_reject_hindsight_and_wrong_format(self):
        ak = self.docs["ak"]
        part = "The later narration describes Nolan initially viewing"
        bad = (
            ("ak", ak.replace(part, "Immediately after elimination, the narration describes Nolan initially viewing", 1)),
            ("ak", ak.replace("twelve-round", "ordinary fixed-placement", 1)),
            ("ak", ak.replace("round 10 of 12", "round 7 of 12", 1)),
            ("ak", ak.replace("The official rules and calculation were not independently verified",
                              "The official payout rules are fully verified", 1)),
            ("ak", ak.replace("## 6. Result, kept separate from both decisions",
                              "## 6. Revealed hands are in the decision", 1)),
            ("64o", self.docs["64o"].replace("## 5. Review the assumptions",
                                              "A-K suited was already known. ## 5. Review the assumptions", 1)),
            ("77", self.docs["77"].replace("## 5. Later review",
                                            "A-T offsuit was known. ## 5. Later review", 1)),
            ("77", self.docs["77"].replace("585,000 / 30,000 = 19.5 BB",
                                            "585,000 / 30,000 = 15 BB", 1)),
        )
        for idx, (hand, invalid) in enumerate(bad):
            with self.subTest(idx=idx, hand=hand):
                changed = dict(self.docs)
                changed[hand] = invalid
                self.assertTrue(review_errors(changed))


if __name__ == "__main__":
    unittest.main()
