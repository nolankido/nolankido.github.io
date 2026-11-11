"""Turn 127: truthful first-screen evidence summaries on two standalone AI cases."""

from hashlib import sha256
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build_local_laptop_case
import build_reply_audit_case


CASES = (
    {
        "slug": "local-ai-gaming-laptop",
        "title": "laptop-snapshot-title",
        "labels": ["On this laptop", "Measured elsewhere", "Try the check"],
        "anchors": ["#laptop-evidence", "#laptop-measure"],
        "facts": ["No timed model benchmark", "GitHub-hosted Ubuntu CPU runner, not the MSI laptop",
                  "no new laptop performance result"],
        "lastmod": "2026-11-02",
        "render": build_local_laptop_case.render,
    },
    {
        "slug": "review-reply-evidence-audit",
        "title": "reply-snapshot-title",
        "labels": ["Observed", "Known misses", "Not established"],
        "anchors": ["#reply-audit-source", "#reply-audit-boundaries", "#reply-audit-reproduce"],
        "facts": ["zero targeted flags", "three flags", "two missed unsupported offers",
                  "one quotation flagged in error", "No new model calls, human approval"],
        "lastmod": "2026-11-05",
        "render": build_reply_audit_case.render,
    },
)


def snapshot_errors(source: str, case: dict) -> list[str]:
    errors = []
    marker = '<aside class="case-evidence-snapshot" aria-labelledby="' + case["title"] + '">'
    if source.count(marker) != 1:
        return ["missing or duplicated labeled snapshot"]
    block = source.split(marker, 1)[1].split("</aside>", 1)[0]
    if '<h3 id="' + case["title"] + '">Evidence at a glance</h3>' not in block:
        errors.append("missing labeled heading")
    if re.findall(r"<dt>([^<]+)</dt>", block) != case["labels"]:
        errors.append("missing, extra or reordered evidence categories")
    if re.findall(r'href="(#[^"]+)"', block) != case["anchors"]:
        errors.append("missing or misdirected evidence links")
    for fact in case["facts"]:
        if block.count(fact) != 1:
            errors.append("changed bounded claim: " + fact)
    if source.index(marker) > source.index('<nav class="entry-jumps"'):
        errors.append("snapshot appears after long-form navigation")
    for anchor in case["anchors"]:
        if source.count('id="' + anchor[1:] + '"') != 1:
            errors.append("missing or duplicate source destination: " + anchor)
    return errors


class StandaloneCaseSnapshotsTests(unittest.TestCase):
    def test_summaries_are_visible_accurate_and_compiled_from_source(self):
        for case in CASES:
            with self.subTest(case=case["slug"]):
                source = (ROOT / "_source/technology" / (case["slug"] + ".html")).read_text(encoding="utf-8")
                html = (ROOT / "technology" / case["slug"] / "index.html").read_text(encoding="utf-8")
                self.assertEqual(snapshot_errors(source, case), [])
                self.assertIn(source, html)
                self.assertEqual(case["render"](), html)
                self.assertEqual(html.count('class="case-evidence-snapshot"'), 1)
                self.assertNotIn(chr(0x2014), source)

    def test_one_content_versioned_stylesheet_and_mobile_print_fallback(self):
        css_path = ROOT / "assets/standalone-evidence-snapshot.css"
        css = css_path.read_text(encoding="utf-8")
        version = sha256(css_path.read_bytes()).hexdigest()[:12]
        link = f'<link rel="stylesheet" href="/assets/standalone-evidence-snapshot.css?v={version}">'
        for case in CASES:
            html = (ROOT / "technology" / case["slug"] / "index.html").read_text(encoding="utf-8")
            self.assertEqual(html.count(link), 1)
        for needed in ("minmax(0, 1fr)", "@media (max-width: 600px)", "@media print",
                       "overflow-wrap: anywhere", "gap: .5rem 1.25rem", "min-height: 44px",
                       ".page-local-ai-gaming-laptop .entry-jumps",
                       ".page-review-reply-evidence-audit .entry-jumps"):
            self.assertIn(needed, css)

    def test_dates_and_canonical_routes_are_unchanged(self):
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        dates = {row.findtext("{*}loc"): row.findtext("{*}lastmod") for row in sitemap}
        for case in CASES:
            url = "https://nolankido.com/technology/" + case["slug"] + "/"
            html = (ROOT / "technology" / case["slug"] / "index.html").read_text(encoding="utf-8")
            self.assertEqual(dates[url], case["lastmod"])
            self.assertIn('<link rel="canonical" href="' + url + '">', html)
            self.assertIn('"dateModified": "' + case["lastmod"] + '"', html)

    def test_unsupported_summary_or_broken_evidence_link_is_rejected(self):
        for case in CASES:
            source = (ROOT / "_source/technology" / (case["slug"] + ".html")).read_text(encoding="utf-8")
            for bad in (
                source.replace(case["facts"][0], "Proven success on a new laptop benchmark", 1),
                source.replace('href="' + case["anchors"][0] + '"', 'href="#unsupported-result"', 1),
                source.replace('<aside class="case-evidence-snapshot"', '<aside class="generic-snapshot"', 1),
            ):
                with self.subTest(case=case["slug"], bad=bad[:80]):
                    self.assertTrue(snapshot_errors(bad, case))


if __name__ == "__main__":
    unittest.main()
