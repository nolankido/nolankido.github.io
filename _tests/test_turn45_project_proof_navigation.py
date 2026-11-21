"""Turn 45: practical AI hub paths lead to RightsReceipt's pinned code proof.

Zero network calls. Check source, generated HTML, route registration and limits.
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
DEEP_ROUTE = "/technology/rightsreceipt-ai-licensing/#rightsreceipt-software-proof"
RECEIPT = "/downloads/rightsreceipt-local-software-acceptance.md"
CASES = (
    ("_source/projects.html", "projects/index.html", "projects-public",
     "Inspect the proof, not just the pitch:"),
    ("_source/ai-in-real-life.html", "ai-in-real-life/index.html",
     "real-life-rightsreceipt", "Read the full analysis:"),
)
sys.path.insert(0, str(ROOT / "_scripts"))


class LinkParser(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            values = dict(attrs)
            self.links.append((values.get("href"), "download" in values))


def section(text: str, identifier: str) -> str:
    marker = '<section class="section folio-row" id="' + identifier + '"'
    if text.count(marker) != 1:
        raise ValueError("Expected one project section: " + identifier)
    start = text.index(marker)
    end = text.find("</section>", start)
    if end < 0:
        raise ValueError("Missing section close")
    return text[start:end + len("</section>")]


def action_paragraph(text: str, label: str) -> str:
    matches = re.findall(r'<p class="small-copy"><strong>' +
                         re.escape(label) + r'</strong>.*?</p>', text, re.S)
    if len(matches) != 1:
        raise ValueError("Expected a single contextual proof route")
    return matches[0]


def errors(visible: str) -> list[str]:
    result = []
    links = LinkParser(visible).links
    if links.count((DEEP_ROUTE, False)) != 1:
        result.append("Missing or duplicated pinned-code destination")
    if links.count((RECEIPT, True)) != 1:
        result.append("Missing or duplicated downloadable worksheet")
    if "simulat" not in visible.lower() and "inject" not in visible.lower():
        result.append("No simulated-payment caveat")
    return result


class Turn45ProofNavigationTests(unittest.TestCase):
    def test_contextual_links_in_two_public_hubs_with_source_parity(self):
        for source, generated, section_id, label in CASES:
            with self.subTest(section_id=section_id):
                src = section((ROOT / source).read_text(encoding="utf-8"), section_id)
                out = section((ROOT / generated).read_text(encoding="utf-8"), section_id)
                before, after = action_paragraph(src, label), action_paragraph(out, label)
                self.assertEqual(before, after)
                self.assertEqual(errors(before), [])
                self.assertLess(src.index(label), len(src))
                self.assertNotIn(chr(0x2014), before)

    def test_missing_links_or_misleading_scope_fail_closed(self):
        source, _, section_id, label = CASES[0]
        paragraph = action_paragraph(
            section((ROOT / source).read_text(encoding="utf-8"), section_id), label)
        for bad in (
            paragraph.replace(DEEP_ROUTE, "/technology/rightsreceipt-ai-licensing/#missing-proof"),
            paragraph.replace(RECEIPT + '" download', RECEIPT + '"'),
            paragraph.replace("injects payment-like responses", "accepts real customer payments"),
        ):
            with self.subTest(change=bad[-80:]):
                self.assertTrue(errors(bad))

    def test_actual_proof_anchor_and_public_worksheet_exist(self):
        for path in ("_source/technology/rightsreceipt-ai-licensing.html",
                     "technology/rightsreceipt-ai-licensing/index.html"):
            content = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(content.count('id="rightsreceipt-software-proof"'), 1)
            self.assertIn("simulated", content.lower())
        receipt = ROOT / RECEIPT.lstrip("/")
        self.assertTrue(receipt.is_file())
        self.assertIn("node scripts/judge-console-real-smoke.mjs", receipt.read_text(encoding="utf-8"))
        import check_live
        self.assertEqual(check_live.targets(ROOT)[RECEIPT], (200, receipt.read_bytes()))

    def test_reader_has_existing_routes_to_both_hubs(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        technology = (ROOT / "technology/index.html").read_text(encoding="utf-8")
        self.assertIn('href="/projects/"', home)
        self.assertIn('href="/ai-in-real-life/"', technology)
        for _, pub, _, _ in CASES:
            self.assertIn('href="' + DEEP_ROUTE + '"', (ROOT / pub).read_text(encoding="utf-8"))

    def test_canonicals_sitemap_and_revisions_are_preserved(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        expected = {
            "/projects/": "2026-11-18",
            "/ai-in-real-life/": "2026-11-20",
            "/technology/rightsreceipt-ai-licensing/": "2026-11-13",
        }
        root = ElementTree.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        urls = [node.text for node in root.findall("{*}url/{*}loc")]
        for route, modified in expected.items():
            with self.subTest(route=route):
                records = [p for p in pages if p["path"] == route]
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0].get("updated", records[0].get("date")), modified)
                self.assertEqual(urls.count("https://nolankido.com" + route), 1)
                html = (ROOT / route.strip("/") / "index.html").read_text(encoding="utf-8")
                self.assertEqual(html.count(
                    '<link rel="canonical" href="https://nolankido.com' + route + '">'), 1)

    def test_two_hubs_do_not_become_duplicate_articles(self):
        for source, published, _, _ in CASES:
            for path in (source, published):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertNotIn("genuine PayPal payment completed", text)
                self.assertNotIn("production customer adoption verified", text)
                self.assertNotIn(chr(0x2014), text)

    def test_generated_hub_pages_match_site_builder(self):
        import build
        outputs = build.build_outputs()
        for _, public, _, _ in CASES:
            with self.subTest(path=public):
                self.assertEqual(outputs[Path(public)],
                                 (ROOT / public).read_text(encoding="utf-8"))

    def test_no_automatic_ci_and_release_check_registered(self):
        local = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn45_project_proof_navigation.py", local)
        workflow = ROOT / ".github/workflows"
        self.assertFalse(workflow.exists() and any(
            p.is_file() and p.suffix in (".yml", ".yaml")
            for p in workflow.iterdir()))


if __name__ == "__main__":
    unittest.main()
