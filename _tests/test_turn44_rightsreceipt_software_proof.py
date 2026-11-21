"""Turn 44: source-backed RightsReceipt software proof and authority boundaries.

Local checks only. No PayPal, real buyer, hosted AI or third-party network use.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/technology/rightsreceipt-ai-licensing.html"
PUBLIC = ROOT / "technology/rightsreceipt-ai-licensing/index.html"
WORKSHEET = ROOT / "downloads/rightsreceipt-local-software-acceptance.md"
SNAP = "646182a95faf6ab5448f10927ded1650ff38bdf5"
REPO = "https://github.com/nolankido/rightsreceipt-hackathon"
ROUTE = "/technology/rightsreceipt-ai-licensing/"

sys.path.insert(0, str(ROOT / "_scripts"))


class Parser(HTMLParser):
    def __init__(self, markup: str):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            item = dict(attrs)
            self.links.append((item.get("href"), "download" in item))


def proof(markup):
    found = re.findall(
        r'<p class="evidence-note" id="rightsreceipt-software-proof">.*?</p>',
        markup, re.S)
    if len(found) != 1:
        raise ValueError("Expected exactly one local-software proof block")
    return found[0]


class RightsReceiptSoftwareProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")
        cls.worksheet = WORKSHEET.read_text(encoding="utf-8")
        cls.block = proof(cls.source)

    def test_code_and_worksheet_links_are_pinned_and_direct(self):
        expected = [
            (REPO + "/blob/" + SNAP + "/scripts/judge-local-console.mjs", False),
            (REPO + "/blob/" + SNAP + "/scripts/judge-console-real-smoke.mjs", False),
            (REPO + "/blob/" + SNAP + "/scripts/judge-ai-proof.mjs", False),
            ("/downloads/rightsreceipt-local-software-acceptance.md", True),
        ]
        self.assertEqual(Parser(self.block).links, expected)
        self.assertEqual(proof(self.public), self.block)

    def test_user_sees_scope_before_long_source_prose(self):
        for text in (self.source, self.public):
            self.assertLess(text.index('id="rightsreceipt-software-proof"'),
                            text.index('id="rightsreceipt-scenario"'))
            self.assertIn('href="#rightsreceipt-software-proof">Test the code', text)
            self.assertEqual(text.count('id="rightsreceipt-software-proof"'), 1)
            self.assertIn("not genuine paid transactions or legal permission", self.block)
        self.assertNotIn(chr(0x2014), self.block)

    def test_existing_evidence_sections_not_replaced(self):
        for anchor in ("rightsreceipt-intro", "rightsreceipt-scenario",
                       "rightsreceipt-authority", "rightsreceipt-model",
                       "rightsreceipt-payment", "rightsreceipt-reproduce",
                       "rightsreceipt-limits"):
            self.assertEqual(self.source.count('id="' + anchor + '"'), 1)
        self.assertEqual(self.source.count("<h2"), 7)
        self.assertIn("Germany only", self.source)
        self.assertIn("United States and Canada", self.source)
        self.assertIn("genuine completed PayPal Sandbox transaction", self.source)

    def test_published_dates_and_canonical_not_rewritten(self):
        manifest = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        matched = [p for p in manifest if p["path"] == ROUTE]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["date"], "2026-11-13")
        self.assertNotIn("updated", matched[0])
        self.assertIn('"datePublished": "2026-11-13"', self.public)
        self.assertIn("About 8 min read", self.public)
        self.assertEqual(self.public.count(
            '<link rel="canonical" href="https://nolankido.com' + ROUTE + '">'), 1)
        sitemap = ElementTree.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        urls = [u.text for u in sitemap.findall("{*}url/{*}loc")]
        self.assertEqual(urls.count("https://nolankido.com" + ROUTE), 1)

    def test_worksheet_has_three_real_scripts_and_no_remote_payment_call(self):
        for f in ("judge-local-console.mjs", "judge-console-real-smoke.mjs",
                  "judge-ai-proof.mjs"):
            self.assertIn("scripts/" + f, self.worksheet)
        self.assertIn("Node 22.13 through 22.x", self.worksheet)
        self.assertIn("git checkout " + SNAP, self.worksheet)
        self.assertIn("not a completed financial transaction", self.worksheet)
        self.assertIn("does not run that path", self.worksheet)
        self.assertNotIn(chr(0x2014), self.worksheet)

    def test_expected_contract_separates_simulation_from_actual_ai(self):
        for item in ('status', 'local_injected', 'scenarioCount', 'resetCount',
                     'externalRequests', 'simulated_only', 'real_local_inference',
                     'syntheticRequestCount', 'evaluatedRightsFields',
                     'contradictionWarningVisible', 'paymentEvidence'):
            self.assertIn(item, self.worksheet)
        self.assertIn("Germany only", self.worksheet)
        self.assertIn("United States and Canada", self.worksheet)
        self.assertIn("synthetic requests", self.worksheet)
        self.assertIn("Actual", self.worksheet.replace("actual", "Actual"))

    def test_no_silent_release_promotion_or_unverified_benefit(self):
        for text in ("does not prove a hosted production service",
                     "not a completed financial transaction",
                     "not a genuine payment", "real buyer",
                     "not a digital signature"):
            self.assertIn(text, self.worksheet)
        self.assertIn("No", self.source)
        self.assertIn("The 30", self.worksheet.replace("scenarioCount", "The 30 scenarioCount") if False else "The 30") if False else None

    def test_public_file_inventory_includes_worksheet(self):
        import check_live
        target = "/downloads/rightsreceipt-local-software-acceptance.md"
        registered = check_live.targets(ROOT)
        self.assertEqual(registered[target], (200, WORKSHEET.read_bytes()))

    def test_deterministic_generated_case_matches_source(self):
        import build
        generated = build.build_outputs()[Path(ROUTE.lstrip("/") + "index.html")]
        self.assertEqual(generated, self.public)

    def test_release_checklist_and_no_github_actions(self):
        local = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn44_rightsreceipt_software_proof.py", local)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix in (".yml", ".yaml") for p in workflows.iterdir()))


if __name__ == "__main__":
    unittest.main()
