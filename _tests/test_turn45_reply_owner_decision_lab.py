"""Turn 45: human review-reply decisions versus narrow lexical screen results.

All live data is fictional or previously public. Tests do not post replies,
make model calls or contact customers.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/technology/local-ai-review-replies.html"
OUTPUT = ROOT / "technology/local-ai-review-replies/index.html"
CHECKLIST = ROOT / "downloads/review-reply-owner-approval-checklist.md"
PROBE = ROOT / "downloads/reply-audit-boundary-probes.py"
LEGACY = ROOT / "downloads/review-reply-independent-audit.py"
ROUTE = "/technology/local-ai-review-replies/"
sys.path.insert(0, str(ROOT / "_scripts"))


def gate(source: str) -> str:
    marker = '<section class="section folio-row" aria-labelledby="reply-owner-gate">'
    parts = source.split(marker)
    if len(parts) != 2:
        raise ValueError("Missing or duplicate owner-gate section")
    return parts[1].split("</section>", 1)[0]


def proof_paragraph(content: str) -> str:
    hits = re.findall(
        r'<p class="evidence-note" id="reply-operator-decision">.*?</p>', content, re.S
    )
    if len(hits) != 1:
        raise ValueError("Expected one and only one specific decision rehearsal")
    return hits[0]


class OwnerDecisionLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.output = OUTPUT.read_text(encoding="utf-8")
        cls.checklist = CHECKLIST.read_text(encoding="utf-8")

    def test_rehearsal_in_source_and_rendered_page_identical(self):
        proof = proof_paragraph(self.source)
        self.assertEqual(proof, proof_paragraph(self.output))
        for document in (self.source, self.output):
            self.assertIn('href="#reply-operator-decision">Try the decision gate</a>', document)
            self.assertLess(document.index('id="reply-owner-gate"'),
                            document.index('id="reply-operator-decision"'))
            self.assertLess(document.index('id="reply-operator-decision"'),
                            document.index('id="reply-boundary"'))
        self.assertIn("We will reimburse the charge.", proof)
        self.assertIn("unauthorized offer", proof)
        self.assertIn("synthetic tests, not new Gemma output", proof)
        self.assertNotIn(chr(0x2014), proof)

    def test_one_owner_checklist_link_and_one_probes_link_within_gate(self):
        section = gate(self.source)
        self.assertEqual(section.count(
            'href="/downloads/review-reply-owner-approval-checklist.md" download'), 1)
        self.assertEqual(section.count(
            'href="/downloads/reply-audit-boundary-probes.py" download'), 1)
        self.assertIn("HOLD / REVISE / APPROVE decision gate", section)
        for route in ("#reply-example", "#reply-evaluation-limits"):
            self.assertIn('href="' + route + '"', section)

    def test_operator_decisions_are_not_checker_approvals(self):
        doc = self.checklist
        self.assertLess(doc.index("## Operator decision gate"),
                        doc.index("## Example: reported double charge"))
        for label in ("**HOLD**", "**REVISE**", "**APPROVE EXACT TEXT**",
                      "**REVIEW IN CONTEXT**"):
            self.assertIn(label, doc)
        self.assertIn("We will reimburse the charge.", doc)
        self.assertIn("We will send a gift card.", doc)
        self.assertIn("Please do not write 'we have issued a refund' without approval.", doc)
        self.assertIn("A clean automatic result alone never reaches the final row.", doc)
        self.assertIn("any subsequent edit voids the earlier approval", doc)
        self.assertNotIn(chr(0x2014), doc)

    def test_actual_offline_negative_controls_expose_two_misses_one_false_alarm(self):
        p = subprocess.run([sys.executable, str(PROBE), "--self-test"],
                           cwd=ROOT, capture_output=True, text=True, check=False, timeout=18)
        self.assertEqual(p.returncode, 0, p.stderr)
        outcome = json.loads(p.stdout)
        self.assertEqual((outcome["probe_count"], outcome["matches"], outcome["mismatches"]),
                         (4, 1, 3))
        self.assertEqual(outcome["model_outputs_created"], 0)
        self.assertEqual(outcome["remote_requests_made"], 0)
        self.assertEqual(outcome["business_approvals_performed"], 0)
        by_name = {row["probe"]: row for row in outcome["probes"]}
        self.assertTrue(by_name["explicit_refund_detected"]["observed_commitment_or_omission_flag"])
        self.assertFalse(by_name["reimbursement_not_detected"]["observed_commitment_or_omission_flag"])
        self.assertFalse(by_name["gift_card_not_detected"]["observed_commitment_or_omission_flag"])
        self.assertTrue(by_name["quoted_warning_overflagged"]["observed_commitment_or_omission_flag"])

    def test_reported_sources_and_missing_pilot_remain_distinct(self):
        doc = self.checklist
        self.assertIn("three model-written replies on fictional reviews", doc.lower())
        self.assertIn("zero model calls and zero human owner assessments", doc.lower())
        self.assertIn("the paired trial has **not been run**", doc)
        self.assertIn("19.536, 18.157 and 19.325 seconds", doc)
        self.assertIn("GitHub-hosted Ubuntu CPU runner", doc)
        self.assertIn("cannot estimate general accuracy", doc)

    def test_no_relabeling_of_model_vs_synthetic_evidence(self):
        for phrase in ("29 non-AI template drafts",
                       "Actual model calls", "Human owner assessments",
                       "not a 96.7% safety rate",
                       "synthetic probes, not new model mistakes"):
            self.assertIn(phrase.lower(), self.source.lower())
        self.assertIn("four-probe offline reproduction", self.source)
        self.assertIn("not new Gemma output", self.source)

    def test_existing_article_date_sections_and_routes_unmodified(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        p = next(x for x in pages if x["path"] == ROUTE)
        self.assertEqual((p["date"], p["updated"]), ("2026-10-27", "2026-11-18"))
        self.assertIn('"datePublished": "2026-10-27"', self.output)
        self.assertIn('"dateModified": "2026-11-18"', self.output)
        self.assertIn("About 14 min read", self.output)
        self.assertIn('<link rel="canonical" href="https://nolankido.com' + ROUTE + '">', self.output)
        self.assertEqual(self.source.count('<h2'), 13)
        root = ElementTree.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        matching = [x for x in root.findall("{*}url/{*}loc")
                    if x.text == "https://nolankido.com" + ROUTE]
        self.assertEqual(len(matching), 1)

    def test_download_and_probe_already_have_read_only_release_targets(self):
        import check_live
        registered = check_live.targets(ROOT)
        for file in (CHECKLIST, PROBE, LEGACY):
            path = "/" + file.relative_to(ROOT).as_posix()
            self.assertEqual(registered[path], (200, file.read_bytes()))

    def test_deterministic_article_html_equals_builder(self):
        import build
        expected = build.build_outputs()[Path("technology/local-ai-review-replies/index.html")]
        self.assertEqual(expected, self.output)

    def test_release_checklist_and_no_cicd(self):
        s = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn45_reply_owner_decision_lab.py", s)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml")
            for p in actions.iterdir()))


if __name__ == "__main__":
    unittest.main()
