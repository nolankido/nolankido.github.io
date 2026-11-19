"""Turn 17: a source-linked, human-authorized customer reply answer."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import check_live

ROUTE = "/technology/local-ai-review-replies/"
URL = "https://nolankido.com" + ROUTE
GATE = "reply-owner-gate"
LOG = "/downloads/review-reply-owner-approval-checklist.md"
PIN = "1c5e0487c331d5202410c9f342557d9355951c3a"


class PageLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))


def gate_section(html):
    marker = f'<section class="section folio-row" aria-labelledby="{GATE}">'
    parts = html.split(marker, 1)
    return parts[1].split("</section>", 1)[0] if len(parts) == 2 else ""


def gate_errors(html):
    section = gate_section(html)
    if not section:
        return ["missing owner decision section"]
    errors = []
    links = PageLinks(section).hrefs
    for link in (
        "#reply-example", "#reply-evaluation-limits", LOG,
        "/technology/review-reply-evidence-audit/#reply-audit-boundaries",
        f"https://github.com/nolankido/reviewReplyWriter/blob/{PIN}/docs/OWNER_FIRST_WORKFLOW.md",
    ):
        if links.count(link) != 1:
            errors.append("missing or repeated evidence or worksheet link: " + link)
    for marker in (
        "<strong>Short answer:</strong>",
        "what the customer actually wrote",
        "what the owner authorized",
        "saved draft claims",
        "not a public reply",
        "double-billing example",
        "reported duplicate charge",
        "unanswered question",
        "reimburse the charge",
        "send a gift card",
        "synthetic probes, not new model mistakes",
        "does not automatically send a response",
        "Keep completed copies private",
        "not evidence of real cafe adoption",
    ):
        if marker not in section:
            errors.append("missing key fact or scope: " + marker)
    if "\u2014" in section:
        errors.append("em dash in new section")
    return errors


class ReviewReplyOwnerGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/technology/local-ai-review-replies.html").read_text()
        cls.public = (ROOT / "technology/local-ai-review-replies/index.html").read_text()
        cls.log = (ROOT / LOG.lstrip("/")).read_text()

    def test_direct_answer_and_native_routes(self):
        for html in (self.source, self.public):
            with self.subTest(generated=html is self.public):
                self.assertEqual(gate_errors(html), [])
                self.assertIn('id="reply-task">Can a small business safely use AI to answer customer reviews?', html)
                self.assertIn("<strong>Only with a human approval step.</strong>", html)
                self.assertIn('href="#reply-owner-gate"', html)
                self.assertLess(html.find('id="reply-example"'), html.find('id="reply-owner-gate"'))
                self.assertLess(html.find('id="reply-owner-gate"'), html.find('id="reply-boundary"'))
                for ident in ("reply-task", "reply-example", GATE, "reply-boundary", "reply-failure", "reply-sources"):
                    self.assertEqual(PageLinks(html).ids.count(ident), 1)
        for hub_file in ("_source/technology/home.html", "technology/index.html",
                         "_source/resources.html", "resources/index.html"):
            hub = (ROOT / hub_file).read_text()
            self.assertIn('href="' + ROUTE + "#" + GATE + '"', hub)
        self.assertIn('href="' + LOG + '" download', (ROOT / "resources/index.html").read_text())

    def test_checklist_registered_and_source_bounded(self):
        self.assertEqual(check_live.targets()[LOG], (200, self.log.encode("utf-8")))
        for marker in (
            "## Example: reported double charge, no refund authorized",
            "reported double charge; unanswered bill question",
            "## A second example: a clean automated screen can miss a claim",
            "not additional archived Gemma outputs",
            "## Blank owner decision record",
            "Approve exact saved text / Revise and recheck / Hold for manual handling",
            "Keep actual customer reviews, owner policies, private notes",
        ):
            self.assertIn(marker, self.log)
        self.assertIn(PIN, self.log)
        self.assertNotIn("\u2014", self.log)

    def test_offline_negative_controls_confirm_stated_checker_limits(self):
        run = subprocess.run([sys.executable, str(ROOT / "downloads/reply-audit-boundary-probes.py"), "--self-test"],
                             capture_output=True, text=True, check=False, cwd=ROOT)
        self.assertEqual(run.returncode, 0, run.stderr)
        data = json.loads(run.stdout)
        self.assertEqual((data["probe_count"], data["matches"], data["mismatches"]), (4, 1, 3))
        self.assertEqual(data["model_outputs_created"], 0)
        failed = {p["probe"] for p in data["probes"] if not p["matches_editorial_expectation"]}
        self.assertEqual(failed, {"reimbursement_not_detected", "gift_card_not_detected", "quoted_warning_overflagged"})

    def test_original_case_identity_preserved(self):
        manifest = json.loads((ROOT / "_source/pages.json").read_text())
        cases = [p for p in manifest if p["path"] == ROUTE]
        self.assertEqual(len(cases), 1)
        self.assertEqual((cases[0]["date"], cases[0]["updated"]), ("2026-10-27", "2026-11-18"))
        self.assertTrue(cases[0]["evidence_article"])
        self.assertIn("Free checklist", cases[0]["description"])
        self.assertIn('<link rel="canonical" href="' + URL + '">', self.public)
        schemas = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        articles = [schema for schema in schemas if schema.get("@type") == "Article"]
        self.assertEqual(len(articles), 1)
        self.assertEqual((articles[0]["datePublished"], articles[0]["dateModified"]), ("2026-10-27", "2026-11-18"))
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        entries = [node for node in sitemap if node.findtext("{*}loc") == URL]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].findtext("{*}lastmod"), "2026-11-18")

    def test_overclaims_and_source_breaks_fail_closed(self):
        broken = (
            self.source.replace("synthetic probes, not new model mistakes", "real model failures", 1),
            self.source.replace("does not automatically send a response", "automatically sends a response", 1),
            self.source.replace("not evidence of real cafe adoption", "proof of real cafe adoption", 1),
            self.source.replace("reimburse the charge", "refund the charge", 1),
            self.source.replace('href="' + LOG + '"', 'href="/downloads/no-checklist.md"', 1),
        )
        for changed in broken:
            with self.subTest(changed=changed != self.source):
                self.assertNotEqual(changed, self.source)
                self.assertTrue(gate_errors(changed))


if __name__ == "__main__":
    unittest.main()
