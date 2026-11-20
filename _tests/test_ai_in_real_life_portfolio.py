"""Regressions for the public AI in Real Life portfolio."""
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

class AIRealLifeTests(unittest.TestCase):
    def test_source_and_manifest(self):
        pages = json.loads(read("_source/pages.json"))
        matches = [p for p in pages if p.get("id") == "ai-in-real-life" or p.get("path") == "/ai-in-real-life/"]
        self.assertEqual(len(matches), 1)
        record = matches[0]
        self.assertEqual(record["source"], "ai-in-real-life.html")
        self.assertEqual(record["section"], "technology")
        self.assertEqual(record["updated"], "2026-11-19")
        self.assertNotIn("date", record)
        self.assertFalse(record.get("noindex"))
        self.assertFalse(record.get("evidence_article"))
        source = read("_source/ai-in-real-life.html")
        self.assertEqual(source.count("<h2 "), 8)
        self.assertNotIn(chr(0x2014), source)
        for link in ("/technology/checking-ai-website-changes/", "/technology/local-ai-review-replies/",
                     "/technology/ai-book-continuity-checker/", "/technology/ai-poker-video-evidence/",
                     "/technology/dinner-on-time/", "/technology/ai-workflow-pilot/"):
            self.assertIn('href="' + link + '"', source)

    def test_flagship_website_case_is_source_verified(self):
        source = read("_source/ai-in-real-life.html")
        output = read("ai-in-real-life/index.html")
        evidence = json.loads(read("downloads/website-check-evidence.json"))
        start = '<section class="section folio-row" id="real-life-software"'
        end = '<section class="section folio-row" id="real-life-business"'
        self.assertIn(start, source)
        self.assertEqual(source.split(start, 1)[1].split(end, 1)[0],
                         output.split(start, 1)[1].split(end, 1)[0])
        self.assertEqual(source.count('id="real-life-software-evidence"'), 1)
        self.assertIn(str(evidence["pre_repair"]["unit_content_tests_passed"]), source)
        self.assertIn(str(evidence["repaired"]["browser_suites_passed"]), source)
        self.assertIn(str(evidence["published"]["matched_targets"]), source)
        for key in ("pre_repair_ref", "repaired_ref"):
            self.assertIn(evidence["source_closure"][key], source)
        for link in ("/downloads/website-check-evidence.json",
                     "/downloads/website-check-offline-runbook.md",
                     "/technology/checking-ai-website-changes/"):
            self.assertIn('href="' + link, source)
        self.assertIn("Not established:", source)
        self.assertIn("not the full archived release", source)

    def test_generated_outputs_and_discovery(self):
        outputs = build.build_outputs()
        for path in ("index.html", "technology/index.html", "ai-in-real-life/index.html",
                     "find/index.html", "sitemap.xml"):
            with self.subTest(path=path):
                self.assertEqual(outputs[Path(path)], read(path))
        page = read("ai-in-real-life/index.html")
        self.assertEqual(page.count('<h1 class="page-title">'), 1)
        self.assertIn('rel="canonical" href="https://nolankido.com/ai-in-real-life/"', page)
        self.assertIn('"@type": "CollectionPage"', page)
        for path in ("index.html", "technology/index.html", "find/index.html"):
            self.assertIn('href="/ai-in-real-life/"', read(path))
        urls = [item.findtext("{*}loc") for item in ET.fromstring(read("sitemap.xml"))]
        self.assertEqual(urls.count("https://nolankido.com/ai-in-real-life/"), 1)
        self.assertIn('"ai-in-real-life":', read("find/index.html"))

if __name__ == "__main__":
    unittest.main()
