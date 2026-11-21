"""Turn 42: the original AI website repair is inspectable from first-screen evidence.

Source-only tests and a builder check. No public requests, credentials or CI.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/technology/checking-ai-website-changes.html"
OUTPUT = ROOT / "technology/checking-ai-website-changes/index.html"
RECORD = ROOT / "downloads/website-check-evidence.json"

sys.path.insert(0, str(ROOT / "_scripts"))


class Links(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            d = dict(attrs)
            self.links.append((d.get("href"), "download" in d))


def proof_block(html: str) -> str:
    blocks = re.findall(
        r'<p class="evidence-note"><strong>Follow the original repair:</strong>.*?</p>',
        html, flags=re.S)
    if len(blocks) != 1:
        raise ValueError("Expected one and only one visible original repair proof path")
    return blocks[0]


def trail_errors(html: str, record: dict) -> list[str]:
    errors = []
    try:
        block = proof_block(html)
    except ValueError as exc:
        return [str(exc)]
    closure = record["source_closure"]
    before = ("https://github.com/nolankido/nolankido.github.io/blob/"
              + closure["pre_repair_ref"] + "/" + closure["path"])
    after = ("https://github.com/nolankido/nolankido.github.io/blob/"
             + closure["repaired_ref"] + "/" + closure["path"])
    expected = [
        (before, False),
        (after, False),
        ("/downloads/website-check-evidence.json", True),
        ("/downloads/website-check-reproduction.py", True),
        ("#case-source-diff", False),
    ]
    if Links(block).links != expected:
        errors.append("Evidence paths or source order disagree with pinned record")
    for text in ("pre-repair source", "repaired source", "archived test record",
                 "reduced parser reproduction", "directly verified source endings",
                 "historical test counts"):
        if text not in block:
            errors.append("Evidence-boundary label missing: " + text)
    if "—" in block:
        errors.append("Unexpected em dash in new proof navigation")
    return errors


class WebsiteRepairProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.output = OUTPUT.read_text(encoding="utf-8")
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_source_and_published_proof_are_identical_and_early(self):
        source = proof_block(self.source)
        built = proof_block(self.output)
        self.assertEqual(source, built)
        for page in (self.source, self.output):
            self.assertLess(page.index(source), page.index('<div class="entry-jumps">'))
            self.assertLess(page.index(source), page.index('id="case-evidence"'))
        self.assertEqual(trail_errors(self.source, self.record), [])

    def test_original_pinned_source_refs_and_error_class_are_retained(self):
        closure = self.record["source_closure"]
        self.assertEqual(closure["pre_repair_ref"], "2bf8908339e06f604cea00f0254494e17171ecf4")
        self.assertEqual(closure["repaired_ref"], "73782caa4697204690c679626b36427c28201234")
        self.assertEqual(closure["pre_repair_last_line"], "</div></div></section>")
        self.assertEqual(closure["repaired_last_line"], "</div></section>")
        self.assertEqual(self.record["pre_repair"]["html5_error"]["code"], "end-tag-too-early")
        self.assertEqual(self.record["pre_repair"]["html5_error"]["tag"], "div")
        self.assertEqual(self.record["pre_repair"]["unit_content_tests_passed"], 347)
        self.assertEqual(self.record["published"]["matched_targets"], 235)
        self.assertIn("not re-executed", self.record["limitations"][-1])

    def test_modified_record_or_wrong_link_is_detected(self):
        block = proof_block(self.source)
        bad = self.source.replace(block, block.replace("2bf8908339e06f604cea00f0254494e17171ecf4", "0" * 40))
        self.assertTrue(trail_errors(bad, self.record))
        bad = self.source.replace(block, block.replace("archived test record", "guaranteed rankings"))
        self.assertTrue(trail_errors(bad, self.record))
        bad = self.source.replace(block, block + block)
        self.assertTrue(trail_errors(bad, self.record))

    def test_evidence_local_downloads_stay_registered_and_read_only(self):
        import check_live
        paths = ("/downloads/website-check-reproduction.py",
                 "/downloads/website-check-evidence.json")
        targets = check_live.targets(ROOT)
        for route in paths:
            self.assertEqual(targets[route], (200, (ROOT / route.lstrip("/")).read_bytes()))
        self.assertIn('href="#case-source-diff"', self.source)

    def test_original_article_publication_and_headings_preserved(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        page = next(p for p in pages if p["id"] == "ai-website-verification")
        self.assertEqual((page["date"], page["updated"]), ("2026-10-11", "2026-11-18"))
        self.assertEqual(self.output.count('<link rel="canonical" href="https://nolankido.com/technology/checking-ai-website-changes/">'), 1)
        self.assertIn('"datePublished": "2026-10-11"', self.output)
        self.assertIn('"dateModified": "2026-11-18"', self.output)
        self.assertIn("About 6 min read", self.output)
        for marker in ("case-summary", "case-evidence", "case-reproduce",
                       "case-method", "case-limits", "case-source-diff"):
            self.assertEqual(self.source.count('id="' + marker + '"'), 1)

    def test_primary_case_body_matches_build_outputs(self):
        import build
        actual = build.build_outputs()[Path("technology/checking-ai-website-changes/index.html")]
        self.assertEqual(actual, self.output)

    def test_release_checklist_registers_this_regression_without_actions(self):
        source = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("'test_turn42_repair_proof_path.py'", source)
        self.assertFalse((ROOT / ".github/workflows").exists() and any(
            p.suffix.lower() in {".yaml", ".yml"} for p in
            (ROOT / ".github/workflows").iterdir() if p.is_file()))


if __name__ == "__main__":
    unittest.main()
