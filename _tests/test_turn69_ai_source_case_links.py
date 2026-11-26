"""Turn 69: connect two AI source-check guides to the recorded editing case.

Source-backed internal learning paths only. No network, new page, visitor
tracking, actual personal records, or claims of measured time savings.
"""
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

ROUTES = {
    "summary": {
        "source": "_source/technology/check-ai-summary.html",
        "published": "technology/check-ai-summary/index.html",
        "path": "/technology/check-ai-summary/",
        "destination": "/technology/ai-weekly-reset/#notes-case-sources",
        "published_date": "2026-10-12",
    },
    "notes": {
        "source": "_source/technology/organize-public-notes.html",
        "published": "technology/organize-public-notes/index.html",
        "path": "/technology/organize-public-notes/",
        "destination": "/technology/ai-weekly-reset/#notes-case-checks",
        "published_date": "2026-10-27",
    },
}
UPDATED = "2026-11-21"
URL = "https://nolankido.com"


def excerpt(page: str):
    matches = re.findall(r'<p class="source-review-case-route">.*?</p>', page, re.S)
    if len(matches) != 1:
        raise ValueError("Expected one labeled link to independently checked editorial example")
    return matches[0]


def route_errors(page: str, destination: str):
    try:
        block = excerpt(page)
    except ValueError:
        return ["missing/duplicated contextual case link"]
    issues = []
    if block.count('href="' + destination + '"') != 1:
        issues.append("broken or duplicated link")
    if "<script" in block or "onclick=" in block or "utm_" in block:
        issues.append("unwanted runtime or tracking")
    if "time sav" not in block.lower():
        issues.append("missing no-productivity-claim boundary")
    if ("private calendar" not in block and "person's calendar" not in block):
        issues.append("missing non-private-source boundary")
    return issues


class Turn69SourceCaseLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = {kind: {
            key: (ROOT / data[key]).read_text(encoding="utf-8")
            for key in ("source", "published")
        } for kind, data in ROUTES.items()}
        cls.target = (ROOT / "technology/ai-weekly-reset/index.html").read_text(encoding="utf-8")
        cls.manifest = {p["path"]: p for p in json.loads(
            (ROOT / "_source/pages.json").read_text(encoding="utf-8")
        )}

    def test_two_distinct_relevant_links_and_exact_published_paragraphs(self):
        for kind, data in ROUTES.items():
            with self.subTest(kind=kind):
                source = self.texts[kind]["source"]
                page = self.texts[kind]["published"]
                self.assertEqual(route_errors(source, data["destination"]), [])
                self.assertEqual(route_errors(page, data["destination"]), [])
                self.assertEqual(excerpt(source), excerpt(page))
                self.assertEqual(source.count('href="' + data["destination"] + '"'), 1)
                self.assertEqual(page.count('href="' + data["destination"] + '"'), 1)
        self.assertIn("fictional", self.texts["summary"]["source"].lower())
        self.assertIn("an assistant organized eight working notes into a publication checklist", self.texts["notes"]["source"])

    def test_target_has_distinct_recorded_source_and_checks_sections(self):
        for data in ROUTES.values():
            target_id = data["destination"].split("#", 1)[1]
            self.assertEqual(self.target.count('id="' + target_id + '"'), 1)
        self.assertIn("AI Works, Human Decides", self.target)
        self.assertNotIn("This verified a private calendar", self.target)

    def test_original_canonicals_and_article_dates_are_preserved(self):
        xml = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual(len(list(xml)), 231)
        for kind, data in ROUTES.items():
            with self.subTest(kind=kind):
                page = self.texts[kind]["published"]
                record = self.manifest[data["path"]]
                self.assertEqual(record["date"], data["published_date"])
                self.assertEqual(record["updated"], UPDATED)
                self.assertIn('<link rel="canonical" href="' + URL + data["path"] + '">', page)
                self.assertEqual(page.count('property="article:modified_time" content="' + UPDATED + '"'), 1)
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                              page, re.S).group(1))
                self.assertEqual(schema["datePublished"], data["published_date"])
                self.assertEqual(schema["dateModified"], UPDATED)
                self.assertEqual(schema["url"], URL + data["path"])
                entry = [x for x in xml if x.findtext("{*}loc") == URL + data["path"]]
                self.assertEqual(len(entry), 1)
                self.assertEqual(entry[0].findtext("{*}lastmod"), UPDATED)

    def test_original_guides_keep_their_content_and_evidence_status(self):
        summary = self.texts["summary"]["source"]
        notes = self.texts["notes"]["source"]
        self.assertIn("Six problems, each tied to the source.", summary)
        self.assertIn("A review sequence for your own summary.", summary)
        self.assertIn("${summary_review_sheet}", summary)
        self.assertIn("fictional", summary.lower())
        self.assertIn("This page preserves the actual instruction", notes)
        self.assertIn("No timing", notes)
        self.assertIn("client data", excerpt(notes))

    def test_generator_matches_both_committed_article_outputs(self):
        outputs = build.build_outputs()
        for kind, data in ROUTES.items():
            with self.subTest(kind=kind):
                self.assertEqual(
                    outputs[Path(data["published"])],
                    self.texts[kind]["published"]
                )
        self.assertEqual(outputs[Path("sitemap.xml")],
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

    def test_wrong_fragment_lost_disclosure_and_duplicate_link_are_caught(self):
        for kind, data in ROUTES.items():
            original = self.texts[kind]["source"]
            link = data["destination"]
            block = excerpt(original)
            mutations = [
                original.replace(link, "/technology/ai-weekly-reset/#fake-section", 1),
                original.replace(block, block.replace("time sav", "hours earn"), 1),
                original.replace(block, block + block, 1),
                original.replace('<p class="source-review-case-route">',
                                 '<p class="unreviewed">', 1),
            ]
            for changed in mutations:
                with self.subTest(kind=kind):
                    self.assertTrue(route_errors(changed, link))

    def test_local_runner_no_actions_and_no_new_runtime(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn69_ai_source_case_links.py", runner)
        for values in self.texts.values():
            for source in values.values():
                self.assertNotIn(chr(0x2014), source)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            for p in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
