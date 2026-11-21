"""Turn 43: a published written case is not an approved current-video edit.

Offline source, claim, date and release-inventory checks. Network requests are
not part of this suite. Human review status is preserved, not invented.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/technology/ai-poker-video-evidence.html"
OUTPUT = ROOT / "technology/ai-poker-video-evidence/index.html"
RECEIPT = ROOT / "downloads/nolanpoker-content-production-receipt.md"
CLAIMS = ROOT / "downloads/portland-meadows-ep1-scene-claims.json"
COMPANION = ROOT / "_source/poker/portland-meadows-ep1.html"
ROUTE = "/technology/ai-poker-video-evidence/"
RECEIPT_ROUTE = "/downloads/nolanpoker-content-production-receipt.md"

sys.path.insert(0, str(ROOT / "_scripts"))


def arrival_paragraph(page: str) -> str:
    match = re.findall(
        r'<p class="small-copy" id="poker-ai-publication-status">.*?</p>',
        page, re.S,
    )
    if len(match) != 1:
        raise ValueError("Need exactly one bounded published-versus-proposed notice")
    return match[0]


class PublishedContentWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = OUTPUT.read_text(encoding="utf-8")
        cls.receipt = RECEIPT.read_text(encoding="utf-8")
        cls.claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
        cls.companion = COMPANION.read_text(encoding="utf-8")

    def test_early_publication_scope_has_exact_source_output_parity(self):
        a, b = arrival_paragraph(self.source), arrival_paragraph(self.public)
        self.assertEqual(a, b)
        for page in (self.source, self.public):
            self.assertLess(page.index("poker-ai-publication-status"),
                            page.index('id="poker-ai-source"'))
            self.assertIn('href="#poker-ai-publication-status"', page)
            self.assertEqual(page.count(RECEIPT_ROUTE), 1)
            self.assertIn(RECEIPT_ROUTE + '" download', a)
        self.assertIn("captions <em>as proposals</em>", a)
        self.assertIn("not as verified graphics in the current video", a)
        self.assertIn("the still-open video approval gate", a)

    def test_no_new_duplicate_article_or_original_section_loss(self):
        for name in ("poker-ai-case-intro", "poker-ai-source", "poker-ai-draft",
                     "poker-ai-check", "poker-ai-approval", "poker-ai-reuse"):
            self.assertEqual(self.source.count('id="' + name + '"'), 1)
        self.assertEqual(len(re.findall(r'<h2\b', self.source)), 6)
        self.assertEqual(self.source.count('data-poker-ai-caption="'), 3)
        self.assertEqual(self.source.count("<details"), 3)
        self.assertEqual(self.source.count("</details>"), 3)
        self.assertIn("not</strong> been independently reviewed", self.source)

    def test_original_publication_dates_canonicals_and_estimate_survive(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        matched = [p for p in pages if p["path"] == ROUTE]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["id"], "ai-poker-video-evidence")
        self.assertEqual((matched[0]["date"], matched[0]["updated"]),
                         ("2026-11-04", "2026-11-19"))
        self.assertEqual(self.public.count(
            '<link rel="canonical" href="https://nolankido.com' + ROUTE + '">'), 1)
        self.assertIn('"datePublished": "2026-11-04"', self.public)
        self.assertIn('"dateModified": "2026-11-19"', self.public)
        self.assertIn("About 9 min read", self.public)
        self.assertIn('datetime="2026-11-02"', self.companion)

    def test_receipt_is_a_real_stage_by_stage_publishing_account(self):
        sections = ["## 1. Preserve the original material before drafting",
                    "## 2. Assign AI a bounded writing task",
                    "## 3. Check the facts with a separately inspectable method",
                    "## 4. Separate editorial verification from human authorization",
                    "## 5. Publish only the deliverable that met its evidentiary scope"]
        positions = [self.receipt.index(title) for title in sections]
        self.assertEqual(positions, sorted(positions))
        for route in ("/technology/ai-poker-video-evidence/",
                      "/poker/episodes/portland-meadows-ep1/",
                      "/downloads/portland-meadows-ep1-scene-claims.json",
                      "/downloads/poker-vlog-fact-gate.py",
                      "/downloads/poker-vlog-truth-to-screen-qa.md"):
            self.assertIn("nolankido.com" + route, self.receipt)
        self.assertIn("da8de1e4022490c851a618778c564cedaf70f03c", self.receipt)

    def test_structured_evidence_has_no_current_video_approval(self):
        for key in ("current_public_cut_timestamps_checked",
                    "current_public_cut_graphics_checked",
                    "confirmed_board_runouts", "human_release_approval"):
            self.assertIs(self.claims[key], False)
            self.assertIn("`" + key + ": false`", self.receipt)
        self.assertEqual(self.claims["published_companion_date"], "2026-11-02")
        self.assertEqual(self.claims["reviewed_record_date"], "2026-11-04")
        self.assertEqual(len(self.claims["scenes"]), 3)
        self.assertIn("not a full independent check", self.receipt)
        self.assertIn("not a certificate of caption accuracy", self.receipt)

    def test_reported_stack_math_and_amount_disclaimer_are_precise(self):
        first, second, payment = self.claims["scenes"]
        self.assertAlmostEqual(first["reported_stack_chips"] / first["big_blind_chips"],
                               first["stack_bb_display"], places=2)
        self.assertEqual(second["reported_stack_chips"] / second["big_blind_chips"], 19.5)
        self.assertEqual(second["button_open_to_chips"] / second["big_blind_chips"], 2.5)
        self.assertEqual(payment["advertised_first_usd"], 5100)
        self.assertEqual(payment["received_after_deal_usd"], 2900)
        self.assertFalse(payment["net_profit_claimed"])
        self.assertIn("reported $2,900 is gross, not net profit", self.receipt)
        self.assertIn("seven seeded conflicts", self.receipt)
        self.assertIn("not a fresh current-video scan", self.receipt)

    def test_release_inventory_includes_public_receipt_exact_bytes(self):
        import check_live
        inventory = check_live.targets(ROOT)
        self.assertIn(RECEIPT_ROUTE, inventory)
        self.assertEqual(inventory[RECEIPT_ROUTE], (200, RECEIPT.read_bytes()))
        self.assertNotIn(chr(0x2014), self.receipt)
        self.assertNotIn(chr(0x2014), arrival_paragraph(self.source))

    def test_existing_fact_gate_reprotection_is_not_weakened(self):
        self.assertIn("/downloads/poker-vlog-fact-gate.py", self.receipt)
        self.assertIn("/downloads/poker-vlog-truth-to-screen-qa.md", self.receipt)
        self.assertIn("not parse prose captions", self.receipt)
        self.assertIn("The present audio", self.receipt)
        self.assertIn("AI-assisted", self.receipt)

    def test_deterministic_article_build_matches_committed_page(self):
        import build
        built = build.build_outputs()[Path("technology/ai-poker-video-evidence/index.html")]
        self.assertEqual(built, self.public)

    def test_local_release_gate_has_no_github_actions(self):
        local = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("'test_turn43_published_content_receipt.py'", local)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.suffix.lower() in {".yml", ".yaml"} for p in actions.iterdir() if p.is_file()))


if __name__ == "__main__":
    unittest.main()
