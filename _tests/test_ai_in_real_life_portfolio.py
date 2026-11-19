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
