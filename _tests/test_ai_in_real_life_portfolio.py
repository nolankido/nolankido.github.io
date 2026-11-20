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
        self.assertEqual(record["updated"], "2026-11-20")
        self.assertNotIn("date", record)
        self.assertFalse(record.get("noindex"))
        self.assertFalse(record.get("evidence_article"))
        source = read("_source/ai-in-real-life.html")
        self.assertEqual(source.count("<h2 "), 9)
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

    def test_real_machine_measurements_and_unmeasured_pilot(self):
        from csv import DictReader
        from io import StringIO
        observed = json.loads(read("downloads/local-ai-test-record.json"))
        self.assertEqual([r["case_elapsed_ms"] for r in observed["results"]], [19536, 18157, 19325])
        self.assertEqual(observed["human_assessments_recorded"], 0)
        self.assertIsNone(observed["unmeasured"]["manual_baseline_minutes"])
        source = read("_source/ai-in-real-life.html")
        page = read("ai-in-real-life/index.html")
        for fragment in ('id="real-life-business-measured"', 'id="real-life-business-pilot"',
                         "19.536 seconds", "18.157 seconds", "19.325 seconds", "19.006 seconds",
                         "not measured human time saved", "remain <strong>unmeasured</strong>"):
            self.assertIn(fragment, source)
            self.assertIn(fragment, page)
        for name in ("review-reply-paired-pilot-instructions.md", "review-reply-paired-pilot-blank.csv"):
            self.assertIn('/downloads/' + name, source)
        records = list(DictReader(StringIO(read("downloads/review-reply-paired-pilot-blank.csv"))))
        self.assertEqual([r["case_id"] for r in records],
                         ["RP01", "RP02", "RP03", "RP04", "RP05", "RP06"])
        for row in records:
            for key in ("manual_minutes", "ai_preparation_minutes", "ai_review_minutes",
                        "ai_repair_minutes", "quality_status"):
                self.assertEqual(row[key], "")
        instructions = read("downloads/review-reply-paired-pilot-instructions.md")
        self.assertIn("no paired observations", instructions)
        self.assertIn("NOT been run", instructions)
        self.assertNotIn(chr(0x2014), instructions)

    def test_browser_pilot_requires_real_measurements(self):
        import hashlib
        import shutil
        import subprocess
        source = read("_source/ai-in-real-life.html")
        built = read("ai-in-real-life/index.html")
        self.assertEqual(source.count('id="real-life-pilot-workspace"'), 1)
        self.assertEqual(built.count('id="real-life-pilot-workspace"'), 1)
        self.assertEqual(source.count('data-rr-case="RP'), 6)
        self.assertEqual(source.count('data-rr-field="manual_minutes"'), 6)
        self.assertEqual(source.count('data-rr-field="confirmed"'), 6)
        self.assertIn('id="rr-pilot-actions" hidden', source)
        self.assertIn("does not generate AI replies", source)
        for asset in ("review-reply-pilot.css", "review-reply-pilot.js"):
            expected = hashlib.sha256((ROOT / "assets" / asset).read_bytes()).hexdigest()[:12]
            self.assertIn("/assets/" + asset + "?v=" + expected, built)
            self.assertNotIn("/assets/" + asset, read("index.html"))
            self.assertIn("assets/" + asset, read("_scripts/check_live.py"))
        script = read("assets/review-reply-pilot.js")
        for forbidden in ("fetch(", "localStorage", "sessionStorage", "sendBeacon"):
            self.assertNotIn(forbidden, script)
        self.assertIn("Missing is not zero", script)
        self.assertIn("qualityGateMet", script)
        self.assertIn("window.addEventListener(\'pagehide\'", script)
        self.assertIn("window.addEventListener(\'pageshow\'", script)
        self.assertIn('autocomplete="off"', built)
        self.assertIn("review-reply-paired-observations.csv", script)
        if shutil.which("node"):
            result = subprocess.run(["node", str(ROOT / "_tests/review_reply_pilot_smoke.cjs")],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rightsreceipt_submission_and_human_authority_are_bounded(self):
        source = read("_source/ai-in-real-life.html")
        html = read("ai-in-real-life/index.html")
        start = '<section class="section folio-row" id="real-life-rightsreceipt"'
        after = '<section class="section folio-row" id="real-life-business"'
        self.assertEqual(source.count(start), 1)
        self.assertEqual(source.split(start, 1)[1].split(after, 1)[0],
                         html.split(start, 1)[1].split(after, 1)[0])
        for marker in (
            "https://devpost.com/software/rightsreceipt",
            "https://www.youtube.com/watch?v=AzUeM4lXyuA",
            "646182a95faf6ab5448f10927ded1650ff38bdf5",
            'paymentEvidence: "simulated_only"',
            "24 rights-field comparisons",
            "USD 425.00",
            "not independently rerun",
            "do <strong>not</strong> establish",
            "/technology/rightsreceipt-ai-licensing/",
            "real PayPal Sandbox payment",
        ):
            self.assertIn(marker, source)
        self.assertIn('href="/ai-in-real-life/#real-life-rightsreceipt"', read("index.html"))
        self.assertEqual(source.count('id="real-life-rightsreceipt-title"'), 1)
        self.assertIn('"real-life-rightsreceipt-title"', read("find/index.html"))

    def test_creator_source_to_screen_publication_chain(self):
        source = read("_source/ai-in-real-life.html")
        html = read("ai-in-real-life/index.html")
        record = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        a = '<section class="section folio-row" id="real-life-creator"'
        b = '<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.count(a), 1)
        self.assertEqual(source.split(a, 1)[1].split(b, 1)[0],
                         html.split(a, 1)[1].split(b, 1)[0])
        self.assertEqual(source.count("<h2 "), 9)
        self.assertEqual(record["video_url"], "https://www.youtube.com/watch?v=qABaiIcvvpU")
        self.assertEqual(record["companion_url"], "https://nolankido.com/poker/episodes/portland-meadows-ep1/")
        self.assertFalse(record["current_public_cut_graphics_checked"])
        self.assertFalse(record["current_public_cut_timestamps_checked"])
        self.assertFalse(record["human_release_approval"])
        self.assertEqual(len(record["scenes"]), 3)
        self.assertAlmostEqual(record["scenes"][0]["reported_stack_chips"] /
                               record["scenes"][0]["big_blind_chips"], 9.8666667, places=5)
        self.assertEqual(record["scenes"][1]["reported_stack_chips"] /
                         record["scenes"][1]["big_blind_chips"], 19.5)
        self.assertEqual(record["scenes"][2]["received_after_deal_usd"], 2900)
        for required in (
            'id="real-life-creator-chain"',
            'id="real-life-creator-numbers"',
            'id="real-life-creator-distribution"',
            "not establish that AI edited the final video",
            "seven deliberately seeded conflicts",
            "not</strong> errors observed in the upload",
            "/downloads/nolanpoker-content-production-evidence-ledger.md",
            "/downloads/poker-vlog-truth-to-screen-qa.md",
            "/downloads/reserve-day1-public-source-ledger.json",
            "/technology/ai-poker-video-evidence/#poker-ai-draft",
        ):
            self.assertIn(required, source)
        self.assertIn('href="/ai-in-real-life/#real-life-creator"', read("index.html"))
        ledger = read("downloads/nolanpoker-content-production-evidence-ledger.md")
        for key in ("current_public_cut_graphics_checked: false",
                    "human_release_approval: false",
                    "148000 / 15000",
                    "585000 / 30000",
                    "a proposed",
                    "https://www.youtube.com/watch?v=qABaiIcvvpU"):
            self.assertIn(key, ledger)
        self.assertIn("downloads/nolanpoker-content-production-evidence-ledger.md",
                      read("_scripts/check_live.py"))
        self.assertNotIn(chr(0x2014), ledger)
        self.assertNotIn(chr(0x2014), source)

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
