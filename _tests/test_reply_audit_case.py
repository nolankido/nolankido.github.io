"""Independent public AI reply audit, reproducible without GitHub Actions or model calls."""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import shutil
import subprocess
import sys
import unittest
from test_site import ROOT, build, Page

import reply_audit_case
import build_reply_audit_case
import site_find
import player_find
import follow


class IndependentReplyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article = (ROOT / reply_audit_case.OUTPUT).read_text(encoding="utf-8")
        cls.source = (ROOT / reply_audit_case.SOURCE).read_text(encoding="utf-8")

    def test_source_matches_compiler_and_public_identity(self):
        self.assertEqual(self.article, build_reply_audit_case.render())
        self.assertIn(self.source, self.article)
        self.assertEqual(reply_audit_case.record(ROOT)["path"], reply_audit_case.ROUTE)
        page = Page(self.article)
        self.assertEqual(len(page.tags("h1")), 1)
        self.assertEqual(len(page.tags("main")), 1)
        self.assertEqual([a.get("href") for a in page.tags("link")
                          if a.get("rel") == "canonical"], [reply_audit_case.URL])
        self.assertNotIn("—", self.article)
        self.assertNotIn("<iframe", self.article)
        self.assertNotIn("human approval performed", self.source.lower())

    def test_public_examples_and_negative_controls_are_reproducible(self):
        result = subprocess.run([sys.executable, str(ROOT / reply_audit_case.TOOL),
                                 "--self-test"], cwd=ROOT, text=True,
                                capture_output=True, check=False, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["originals_screened"], 3)
        self.assertEqual(report["originals_with_targeted_flags"], 0)
        self.assertEqual(report["controls_intentionally_mutated"], 3)
        self.assertEqual(report["controls_flagged"], 3)
        self.assertFalse(report["human_approval_performed"])
        self.assertEqual(report["real_model_calls_this_run"], 0)
        self.assertEqual(report["network_requests_this_run"], 0)
        self.assertEqual({x["control"] for x in report["negative_controls"]},
                         {"remove_wait_duration", "remove_unanswered_question", "invent_refund"})

    def test_find_sitemap_feeds_have_one_canonical_article(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("sitemap.xml")],
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        for path in ("technology/index.html", "technology/local-ai-review-replies/index.html"):
            self.assertIn('href="' + reply_audit_case.ROUTE + '"',
                          (ROOT / path).read_text(encoding="utf-8"))
        items = player_find.add(ROOT, site_find.entries(ROOT, build.public_pages()))
        self.assertEqual([x["path"] for x in items].count(reply_audit_case.ROUTE), 1)
        self.assertIn('href="' + reply_audit_case.ROUTE + '"',
                      outputs[Path("find/index.html")])
        self.assertEqual(outputs[Path("find/index.html")],
                         (ROOT / "find/index.html").read_text(encoding="utf-8"))
        locations = [x.text for x in ET.fromstring(outputs[Path("sitemap.xml")]).iter()
                     if x.tag.endswith("}loc")]
        self.assertEqual(locations.count(reply_audit_case.URL), 1)
        for name in ("technology/feed.xml", "writing.xml"):
            actual = (ROOT / name).read_text(encoding="utf-8")
            self.assertEqual(actual, outputs[Path(name)])
            items = ET.fromstring(actual).findall("./channel/item")
            entries = [x for x in items if x.findtext("link") == reply_audit_case.URL]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].findtext("guid"), reply_audit_case.URL)
            self.assertEqual(entries[0].findtext("pubDate"),
                             "Tue, 03 Nov 2026 00:00:00 GMT")
        combined = follow.combined(outputs, build.public_pages(), "https://nolankido.com", ROOT)
        self.assertEqual(combined, outputs[follow.OUTPUT])

    def test_broken_canonical_source_and_tool_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for path in (reply_audit_case.SOURCE, reply_audit_case.OUTPUT,
                         reply_audit_case.TOOL, Path("technology/index.html")):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertIsNotNone(reply_audit_case.record(root))
            html = root / reply_audit_case.OUTPUT
            current = html.read_text(encoding="utf-8")
            modified = current.replace('rel="canonical" href="' + reply_audit_case.URL + '"',
                                       'rel="canonical" href="https://invalid.example/"', 1)
            html.write_text(modified, encoding="utf-8")
            with self.assertRaises(ValueError):
                reply_audit_case.record(root)
            html.write_text(current.replace("<head>", '<head><meta name="robots" content="noindex">', 1),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                reply_audit_case.record(root)
            html.write_text(current, encoding="utf-8")
            (root / reply_audit_case.TOOL).unlink()
            with self.assertRaises(ValueError):
                reply_audit_case.record(root)

    def test_offline_script_has_no_external_or_paid_transport(self):
        tool = (ROOT / reply_audit_case.TOOL).read_text(encoding="utf-8")
        for bad in ("import socket", "import urllib", "import requests",
                    "import subprocess", "OPENAI_API_KEY", "github.actions"):
            self.assertNotIn(bad, tool)
        self.assertIn("human_approval_performed", tool)
        self.assertIn("NEGATIVE CONTROLS", tool)


if __name__ == "__main__":
    unittest.main()
