"""Turn 137: the home evidence card exposes the inspectable project example."""

from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


PROOF = re.compile(
    r'<section class="section folio-row identity-selection home-proof"'
    r' aria-labelledby="home-proof-title">(.*?)</section>', re.S,
)
AI_CARD = re.compile(
    r'<article class="identity-reading"><p class="note-category">'
    r'Practical AI / Reproducible audit</p>(.*?)</article>', re.S,
)
PROJECT_ROUTE = (
    '<p class="home-evidence-project-route"><a '
    'href="/technology/local-ai-review-replies/#reply-example">'
    'See the project\'s fictional double-charge example '
    '<span aria-hidden="true">→</span></a></p>'
)
CASE_HEADING = '<h2 id="reply-example">Keep the double charge and the unanswered question visible.</h2>'
AUDIT_CAVEAT = "not measured client outcomes or a general error rate."


def bridge_errors(home: str, case: str) -> list[str]:
    problems = []
    proof = PROOF.search(home)
    if not proof:
        return ["homepage proof section is missing"]
    card = AI_CARD.search(proof.group(1))
    if not card:
        return ["practical AI evidence card is missing"]
    body = card.group(1)
    if body.count(PROJECT_ROUTE) != 1:
        problems.append("project example route missing or repeated in AI evidence card")
    if body.count('<h3><a href="/technology/review-reply-evidence-audit/">') != 1:
        problems.append("independent audit must remain the primary evidence route")
    if AUDIT_CAVEAT not in body or body.find(AUDIT_CAVEAT) > body.find(PROJECT_ROUTE):
        problems.append("source caveat must precede the project example link")
    if case.count('id="reply-example"') != 1 or case.count(CASE_HEADING) != 1:
        problems.append("project example native destination missing or duplicated")
    if 'Fictional customer / Actual application example' not in case:
        problems.append("case no longer labels its example as fictional")
    if 'The application\'s <a href="https://github.com/nolankido/reviewReplyWriter/' not in case:
        problems.append("project example lost its public source link")
    for claim in ("not feedback from a real cafe", "The owner still has to decide"):
        if claim not in case:
            problems.append("project example lost its human-review limit")
    if '\u2014' in body or 'Real customer' in body or '<script' in body:
        problems.append("new route adds unverified claims, scripts or prohibited punctuation")
    return problems


class HomeProjectEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home_source = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.case_source = (ROOT / "_source/technology/local-ai-review-replies.html").read_text(encoding="utf-8")
        cls.case = (ROOT / "technology/local-ai-review-replies/index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/first-steps.css").read_text(encoding="utf-8")

    def test_proof_audit_and_project_example_are_different_credible_paths(self):
        for home, case in ((self.home_source, self.case_source), (self.home, self.case)):
            self.assertEqual(bridge_errors(home, case), [])
            self.assertEqual(home.count('href="/technology/local-ai-review-replies/#reply-example"'), 2)
            self.assertEqual(PROOF.search(home).group(1).count('class="identity-reading"'), 3)

    def test_secondary_project_route_has_reachable_touch_and_keyboard_focus(self):
        self.assertIn('.page-home .identity-reading .home-evidence-project-route { margin-top: 12px; }', self.css)
        self.assertIn('.page-home .home-evidence-project-route a { display: inline-flex;', self.css)
        self.assertIn('min-height: 44px;', self.css)
        self.assertIn('.page-home .home-evidence-project-route a:focus-visible', self.css)
        self.assertIn('outline: 3px solid var(--red);', self.css)
        self.assertIn('overflow-wrap: anywhere;', self.css)
        self.assertNotIn('javascript:', PROJECT_ROUTE)

    def test_source_build_and_content_versioned_stylesheet_are_consistent(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("index.html")], self.home)
        self.assertEqual(outputs[Path("creative/index.html")], (ROOT / "creative/index.html").read_text())
        version = sha256(self.css.encode()).hexdigest()[:12]
        for file in (ROOT / "index.html", ROOT / "creative/index.html"):
            self.assertIn(f'href="/assets/first-steps.css?v={version}"', file.read_text())
        self.assertNotIn("/assets/first-steps.css", (ROOT / "technology/index.html").read_text())

    def test_preserves_public_metadata_and_original_modification_dates(self):
        pages = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text())}
        self.assertEqual(pages["/"]["updated"], "2026-11-13")
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        dates = {node.findtext("{*}loc"): node.findtext("{*}lastmod") for node in sitemap}
        self.assertEqual(dates["https://nolankido.com/"], "2026-11-13")
        self.assertEqual(self.home.count('rel="canonical" href="https://nolankido.com/"'), 1)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.home)

    def test_negative_controls_detect_missing_and_misleading_project_routes(self):
        for home, case in (
            (self.home_source.replace(PROJECT_ROUTE, "", 1), self.case_source),
            (self.home_source.replace("#reply-example", "#missing-example", 1), self.case_source),
            (self.home_source.replace("fictional double-charge", "Real customer double-charge", 1), self.case_source),
            (self.home_source.replace(AUDIT_CAVEAT, "proved real customer results.", 1), self.case_source),
            (self.home_source, self.case_source.replace(CASE_HEADING, '<h2>Example</h2>', 1)),
            (self.home_source, self.case_source.replace("not feedback from a real cafe", "real customer feedback", 1)),
        ):
            with self.subTest(home_changed=home != self.home_source):
                self.assertTrue(bridge_errors(home, case))


if __name__ == "__main__":
    unittest.main()
