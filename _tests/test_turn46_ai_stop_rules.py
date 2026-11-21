"""Turn 46: one canonical AI reliability guide, four evidence-specific stop rules.

Source and generated-page tests only. These never run a model, submit a review,
pay a provider, edit a video or check a live search ranking.
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
SOURCE = ROOT / "_source/technology/check-ai-answers.html"
PUBLIC = ROOT / "technology/check-ai-answers/index.html"
WORKSHEET = ROOT / "downloads/ai-stop-rules-field-guide.md"
DEEP = "/technology/check-ai-answers/#review-stop-rules"
ID = "review-stop-rules"
CASE_LINKS = (
    "/technology/checking-ai-website-changes/#case-source-diff",
    "/technology/local-ai-review-replies/#reply-operator-decision",
    "/technology/rightsreceipt-ai-licensing/#rightsreceipt-software-proof",
    "/technology/ai-poker-video-evidence/#poker-ai-approval",
)
sys.path.insert(0, str(ROOT / "_scripts"))


class Links(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self.ids = []
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a":
            self.anchors.append((data.get("href"), "download" in data))


def block(document):
    hits = re.findall(
        r'<section class="review-boundary" id="review-stop-rules" '
        r'aria-labelledby="review-stop-rules-title">(.*?)</section>',
        document, re.S)
    if len(hits) != 1:
        raise ValueError("Expected exactly one source-backed stop-rule section")
    return hits[0]


def failures(document):
    try:
        section = block(document)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    actual = re.findall(
        r'<tr><th scope="row"><a href="([^"]+)"', section)
    if actual != list(CASE_LINKS):
        errors.append("Wrong source links or wrong case order")
    if Links(section).anchors.count(
        ("/downloads/ai-stop-rules-field-guide.md", True)) != 1:
        errors.append("Missing or repeated downloadable record")
    for token in (
        "PROCEED IN SCOPE", "REVISE AND RECHECK",
        "HOLD", "STOP USING AI FOR THIS TASK",
        "347-test pass", "malformed closing tag",
        "two missed financial offers", "quotation overflag",
        "Germany-only synthetic request", "payment responses were simulated",
        "not the current published video's audio and graphics",
        "workflow time calculator", "six-case reply productivity pilot has not been run",
        "green, narrow test is not authorization",
    ):
        if token.lower() not in section.lower():
            errors.append("Missing evidence scope: " + token)
    if chr(0x2014) in section:
        errors.append("New content contains an em dash")
    return errors


class CrossCaseStopRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")
        cls.worksheet = WORKSHEET.read_text(encoding="utf-8")

    def test_one_synthesis_and_same_source_rendered_block(self):
        self.assertEqual(failures(self.source), [])
        self.assertEqual(failures(self.public), [])
        self.assertEqual(block(self.source), block(self.public))
        for document in (self.source, self.public):
            self.assertEqual(document.count('id="' + ID + '"'), 1)
            self.assertEqual(document.count('href="#' + ID + '"'), 1)
            self.assertLess(document.index('id="review-fast-method"'),
                            document.index('id="' + ID + '"'))
            self.assertLess(document.index('id="' + ID + '"'),
                            document.index('id="review-claim-map"'))

    def test_four_public_cases_are_distinct_references_not_one_accuracy_statistic(self):
        section = block(self.source)
        self.assertEqual(section.count('<th scope="row">'), 4)
        self.assertIn("Historical 347-test pass", section)
        self.assertIn("constructed probes", section)
        self.assertIn("Real local-model inference", section)
        self.assertIn("proposed labels", section)
        self.assertNotIn("error rate", section)
        for path in CASE_LINKS:
            route, fragment = path.split("#", 1)
            target = ROOT / route.lstrip("/") / "index.html"
            self.assertTrue(target.is_file(), path)
            self.assertIn('id="' + fragment + '"', target.read_text(encoding="utf-8"))

    def test_failure_conditions_are_not_proceed_permissions(self):
        section = block(self.source)
        for wrong in (
            section.replace("payment responses were simulated",
                            "payment is independently verified"),
            section.replace("HOLD unsupported promises",
                            "Approve unsupported promises"),
            section.replace("HOLD unverified overlays",
                            "Publish any graphic without checks"),
            section.replace(CASE_LINKS[2], "/technology/rightsreceipt-ai-licensing/#missing"),
        ):
            with self.subTest(wrong=wrong[-65:]):
                self.assertTrue(failures(self.source.replace(section, wrong, 1)))

    def test_worksheet_is_a_practical_and_private_release_receipt(self):
        text = self.worksheet
        for phrase in ("## The four decisions", "## Four cases, four non-interchangeable gates",
                       "## A six-gate release method", "## Worked stop-rule decisions",
                       "## Private decision receipt", "## Provenance and limits",
                       "PROCEED IN SCOPE", "REVISE AND RECHECK", "HOLD",
                       "STOP USING AI FOR THIS TASK", "Actual result on this version",
                       "Full task cost", "approval for this exact saved version"):
            self.assertIn(phrase.lower(), text.lower())
        self.assertIn("paired six-case review-reply study is **not completed**", text)
        self.assertIn("historical website and model checks", text)
        self.assertIn("private decision receipt", text.lower())
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn("real customer identities", text)

    def test_four_evidence_sources_and_version_caveats_in_worksheet(self):
        for path in CASE_LINKS:
            self.assertIn("nolankido.com" + path, self.worksheet)
        for assertion in ("347 unit/content tests", "missed reimbursement and gift-card offers",
                          "Germany only", "current",
                          "synthetic", "simulated", "human", "unverified",
                          "not supply a combined", "no new model inference"):
            with self.subTest(assertion=assertion):
                self.assertIn(assertion.lower(), self.worksheet.lower())

    def test_historical_article_identity_and_revised_lastmod(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        items = [x for x in pages if x["path"] == "/technology/check-ai-answers/"]
        self.assertEqual(len(items), 1)
        page = items[0]
        self.assertEqual((page["date"], page["updated"]), ("2026-10-12", "2026-11-20"))
        self.assertIn("four-case AI reliability and stop-rule matrix", page["revision"])
        self.assertIn('"datePublished": "2026-10-12"', self.public)
        self.assertIn('"dateModified": "2026-11-20"', self.public)
        self.assertIn('article:modified_time" content="2026-11-20"', self.public)
        self.assertIn('Revision, <time datetime="2026-11-20">November 20, 2026</time>',
                      self.public)
        self.assertIn("About 24 min read", self.public)
        self.assertEqual(self.public.count(
            '<link rel="canonical" href="https://nolankido.com/technology/check-ai-answers/">'), 1)
        root = ElementTree.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        matches = [x for x in root if x.findtext("{*}loc")
                   == "https://nolankido.com/technology/check-ai-answers/"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext("{*}lastmod"), page["updated"])

    def test_original_six_examples_and_article_structure_preserved(self):
        for document in (self.source, self.public):
            for id_ in ("review-research", "review-numbers", "review-summary",
                        "review-writing", "review-code", "review-advice",
                        "review-claim-map", "review-search-advice",
                        "review-poker-solver-claim", "review-completed-record"):
                self.assertEqual(document.count('id="' + id_ + '"'), 1)
            self.assertEqual(document.count('<details class="review-example" id="'), 6)
        self.assertEqual(len(re.findall(r'<h2\b', self.source)), 9)
        self.assertEqual(len(re.findall(r'<h2\b', self.public)), 10)
        self.assertIn("not a completed visibility result", self.source)
        self.assertIn("No actual hand, opponent range or showdown win probability",
                      self.source)

    def test_hub_links_to_stable_same_canonical_and_preserves_metadata(self):
        for path in ("_source/technology/home.html", "technology/index.html"):
            html = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(html.count('href="' + DEEP + '"'), 1)
            self.assertIn('href="/technology/check-ai-answers/"', html)
        manifest = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        hub = next(p for p in manifest if p["id"] == "technology")
        self.assertEqual(hub["updated"], "2026-11-20")

    def test_public_download_registered_exact_bytes(self):
        import check_live
        route = "/downloads/ai-stop-rules-field-guide.md"
        self.assertEqual(check_live.targets(ROOT)[route], (200, WORKSHEET.read_bytes()))

    def test_generated_outputs_match_deterministic_builder(self):
        import build
        generated = build.build_outputs()
        for filename in ("technology/check-ai-answers/index.html", "technology/index.html",
                         "sitemap.xml"):
            with self.subTest(file=filename):
                self.assertEqual(generated[Path(filename)],
                                 (ROOT / filename).read_text(encoding="utf-8"))

    def test_release_checklist_and_no_github_actions(self):
        local = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn46_ai_stop_rules.py", local)
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(p.suffix in (".yml", ".yaml")
                         for p in folder.iterdir() if p.is_file()))


if __name__ == "__main__":
    unittest.main()
