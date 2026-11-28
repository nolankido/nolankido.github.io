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
                    "three proposed labels",
                    "https://www.youtube.com/watch?v=qABaiIcvvpU"):
            self.assertIn(key, ledger)
        self.assertIn("downloads/nolanpoker-content-production-evidence-ledger.md",
                      read("_scripts/check_live.py"))
        self.assertNotIn(chr(0x2014), ledger)
        self.assertNotIn(chr(0x2014), source)

    def test_public_transcript_checkpoint_is_limited_to_text(self):
        audit = json.loads(read("downloads/portland-meadows-public-transcript-audit-2026-11-20.json"))
        source = read("_source/ai-in-real-life.html")
        built = read("ai-in-real-life/index.html")
        historical = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        self.assertEqual(audit["video_url"], historical["video_url"])
        self.assertEqual(audit["audit_date_hawaii"], "2026-11-20")
        self.assertEqual([item["timecode"] for item in audit["observations"]],
                         ["04:20", "06:27", "07:12", "08:08", "08:52"])
        self.assertEqual([item["seconds"] for item in audit["observations"]],
                         [260, 387, 432, 488, 532])
        self.assertTrue(audit["viewer_transcript_available"])
        self.assertTrue(audit["current_public_transcript_passages_inspected"])
        for key in ("current_public_cut_audio_audited",
                    "current_public_cut_frames_audited",
                    "current_public_cut_graphics_audited",
                    "current_public_cut_full_runtime_confirmed",
                    "current_public_cut_human_release_approval",
                    "transcript_timecodes_cross_checked_against_playing_media"):
            self.assertFalse(audit[key], key)
        for key in ("current_public_cut_timestamps_checked",
                    "current_public_cut_graphics_checked", "human_release_approval"):
            self.assertFalse(historical[key])
        self.assertEqual(source.count('id="real-life-creator-transcript"'), 1)
        begin = '<section class="section folio-row" id="real-life-creator"'
        end = '<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(begin, 1)[1].split(end, 1)[0],
                         built.split(begin, 1)[1].split(end, 1)[0])
        for marker in ("4:20", "6:27", "7:12", "8:08", "8:52",
                       "sign-in verification prompt", "not scene positions independently checked",
                       "/downloads/portland-meadows-public-transcript-audit-2026-11-20.json"):
            self.assertIn(marker, source)
        self.assertIn("## F. November 20 read-only transcript checkpoint",
                      read("downloads/nolanpoker-content-production-evidence-ledger.md"))
        self.assertIn("downloads/portland-meadows-public-transcript-audit-2026-11-20.json",
                      read("_scripts/check_live.py"))
        self.assertEqual(source.count("<h2 "), 9)
        self.assertNotIn(chr(0x2014), source)

    def test_offline_current_cut_qa_workstation_is_private_and_fail_closed(self):
        tool = read("downloads/nolanpoker-local-video-qa.html")
        source = read("_source/ai-in-real-life.html")
        built = read("ai-in-real-life/index.html")
        self.assertTrue(tool.startswith("<!doctype html>"))
        self.assertIn('content="noindex,nofollow"', tool)
        self.assertIn("connect-src 'none'", tool)
        self.assertIn("media-src blob:", tool)
        self.assertIn('<input id="local-file" type="file"', tool)
        self.assertEqual(tool.count('<article class="checkpoint" data-scene='), 5)
        self.assertEqual(tool.count('<option value="unreviewed">Not reviewed</option>'), 5)
        self.assertIn("A PASS requires a readable local video", tool)
        self.assertIn("current_video_independently_verified_by_tool:false", tool)
        self.assertIn("identity_independently_proven_by_tool:false", tool)
        self.assertIn("reviewer_reported_checklist_complete", tool)
        for item in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage",
                     "sendBeacon", "<script src=", "<iframe"):
            self.assertNotIn(item, tool)
        self.assertEqual(source.count('id="real-life-creator-local-mp4-qa"'), 1)
        start = '<section class="section folio-row" id="real-life-creator"'
        end = '<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(start, 1)[1].split(end, 1)[0],
                         built.split(start, 1)[1].split(end, 1)[0])
        self.assertIn('href="/downloads/nolanpoker-local-video-qa.html"', source)
        self.assertIn("downloads/nolanpoker-local-video-qa.html", read("_scripts/check_live.py"))
        self.assertEqual(source.count("<h2 "), 9)
        historical = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        for key in ("current_public_cut_timestamps_checked",
                    "current_public_cut_graphics_checked", "human_release_approval"):
            self.assertFalse(historical[key])
        transcript = json.loads(read("downloads/portland-meadows-public-transcript-audit-2026-11-20.json"))
        self.assertFalse(transcript["current_public_cut_audio_audited"])
        self.assertFalse(transcript["current_public_cut_frames_audited"])
        self.assertIn("## G. Offline current-cut audiovisual QA workstation",
                      read("downloads/nolanpoker-content-production-evidence-ledger.md"))
        self.assertNotIn(chr(0x2014), source)
        self.assertNotIn(chr(0x2014), tool)

    def test_local_video_qa_v2_fingerprint_and_continuous_scene_evidence(self):
        import shutil
        import subprocess
        html = read("downloads/nolanpoker-local-video-qa.html")
        self.assertIn("nolanpoker-local-current-cut-qa-v2", html)
        self.assertIn('id="hash-file"', html)
        self.assertIn('id="file-fingerprint"', html)
        self.assertIn("connect-src 'none'", html)
        self.assertIn("media-src blob:", html)
        self.assertIn("function makeSHA256()", html)
        self.assertIn("BigInt(bytesRead)*8n", html)
        self.assertIn("sha256_local:sha256Digest", html)
        self.assertIn("sha256_match_to_public_file_independently_verified:false", html)
        self.assertIn("identity_independently_proven_by_tool:false", html)
        self.assertIn("const allComplete=hasFile&&checksumReady&&coversTranscript&&identity", html)
        self.assertIn("c.querySelector('.notes').value.trim().length>=12", html)
        self.assertIn("position<video.duration", html)
        self.assertIn("fileGeneration++", html)
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage",
                          "sessionStorage", "sendBeacon", "<script src="):
            self.assertNotIn(forbidden, html)
        self.assertIn("Verification upgrade:", read("_source/ai-in-real-life.html"))
        self.assertIn("## H. Local media fingerprint and continuous evidence gate",
                      read("downloads/nolanpoker-content-production-evidence-ledger.md"))
        for key in ("current_public_cut_timestamps_checked",
                    "current_public_cut_graphics_checked", "human_release_approval"):
            old_record = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
            self.assertFalse(old_record[key])
        if shutil.which("node"):
            result = subprocess.run(["node", str(ROOT / "_tests/nolanpoker_local_video_sha256_smoke.cjs")],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_v3_report_resume_never_restores_previous_approvals(self):
        import shutil
        import subprocess
        tool = read("downloads/nolanpoker-local-video-qa.html")
        self.assertIn("nolanpoker-local-current-cut-qa-v3", tool)
        self.assertIn('id="resume-report"', tool)
        self.assertIn("function validateSavedReview(", tool)
        self.assertIn("resumeInput.addEventListener('change'", tool)
        self.assertIn("raw.file.sha256_local !== currentSHA", tool)
        self.assertIn("raw.file.size_bytes !== currentSize", tool)
        self.assertIn("c.querySelector('.decision').value='unreviewed'", tool)
        self.assertIn("c.querySelector('.audio').checked=false", tool)
        self.assertIn("c.querySelector('.visual').checked=false", tool)
        self.assertIn("resume_prior_pass_and_release_approvals_cleared", tool)
        self.assertIn("checksumReady", tool)
        self.assertIn("connect-src 'none'", tool)
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage",
                          "sendBeacon", "<script src="):
            self.assertNotIn(forbidden, tool)
        self.assertIn("Resume an unfinished review:", read("_source/ai-in-real-life.html"))
        self.assertIn("## I. Checksum-bound review resumption",
                      read("downloads/nolanpoker-content-production-evidence-ledger.md"))
        for k in ("current_public_cut_timestamps_checked",
                  "current_public_cut_graphics_checked", "human_release_approval"):
            scene_record = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
            self.assertFalse(scene_record[k])
        if shutil.which("node"):
            p = subprocess.run(["node", str(ROOT / "_tests/nolanpoker_qa_resume_smoke.cjs")],
                               capture_output=True, text=True, check=False)
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_public_youtube_video_review_does_not_require_mp4(self):
        import shutil
        import subprocess
        html = read("downloads/nolanpoker-public-youtube-review.html")
        source = read("_source/ai-in-real-life.html")
        output = read("ai-in-real-life/index.html")
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("nolanpoker-public-youtube-qa-v1", html)
        self.assertIn("qABaiIcvvpU", html)
        self.assertIn("frame-src 'none'", html)
        self.assertIn("connect-src 'none'", html)
        self.assertIn("noindex,nofollow", html)
        self.assertEqual(html.count('<article class="checkpoint" data-scene='), 6)
        for sec in (31,260,387,432,488,532):
            self.assertIn('https://www.youtube.com/watch?v=qABaiIcvvpU&t='+str(sec)+'s', html)
        self.assertIn("archived_v12_metadata_unverified_in_current_cut", html)
        self.assertIn("public_video_frames_independently_verified_by_tool:false", html)
        self.assertIn("independent_external_certification:false", html)
        self.assertIn("function validateSaved(raw)", html)
        for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, html)
        self.assertIn('id="real-life-creator-public-youtube"', source)
        self.assertIn('href="/downloads/nolanpoker-public-youtube-review.html"', source)
        self.assertEqual(source.count("<h2 "), 9)
        begin = '<section class="section folio-row" id="real-life-creator"'
        end = '<section class="section folio-row" id="real-life-everyday"'
        self.assertEqual(source.split(begin,1)[1].split(end,1)[0],
                         output.split(begin,1)[1].split(end,1)[0])
        self.assertIn("downloads/nolanpoker-public-youtube-review.html",
                      read("_scripts/check_live.py"))
        self.assertIn("## J. Source-linked public YouTube viewing path",
                      read("downloads/nolanpoker-content-production-evidence-ledger.md"))
        original = json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        for key in ("current_public_cut_timestamps_checked",
                    "current_public_cut_graphics_checked", "human_release_approval"):
            self.assertFalse(original[key])
        self.assertNotIn(chr(0x2014), source)
        if shutil.which("node"):
            r = subprocess.run(["node", str(ROOT / "_tests/nolanpoker_public_youtube_qa_smoke.cjs")],
                               capture_output=True, text=True, check=False)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_case_index_matches_visible_links_and_collection_schema(self):
        import re
        from visibility_projects import REAL_LIFE_CASES, real_life_case_markup, real_life_case_schema
        origin = 'https://nolankido.com'
        canonical = origin + '/ai-in-real-life/'
        source = read('_source/ai-in-real-life.html')
        output = read('ai-in-real-life/index.html')
        block = real_life_case_markup()
        for document in (source, output):
            self.assertEqual(document.count(block), 1)
            self.assertEqual(document.count('id="real-life-case-index"'), 1)
        record = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                      output, re.S).group(1))
        seed = {key: value for key, value in record.items() if key != 'mainEntity'}
        self.assertEqual(real_life_case_schema(seed, source, origin), record)
        self.assertNotIn('mainEntity', seed)
        items = record['mainEntity']['itemListElement']
        self.assertEqual(len(items), 6)
        self.assertEqual([item['position'] for item in items], list(range(1, 7)))
        self.assertEqual([(item['url'].removeprefix(origin), item['name']) for item in items],
                         list(REAL_LIFE_CASES))
        manifest = json.loads(read('_source/pages.json'))
        for path, label in REAL_LIFE_CASES:
            with self.subTest(path=path):
                pages = [p for p in manifest if p['path'] == path and not p.get('noindex')]
                self.assertEqual(len(pages), 1)
                self.assertIn(f'<link rel="canonical" href="{origin + path}">',
                              read(path.lstrip('/') + 'index.html'))

    def test_case_index_rejects_missing_conflicting_and_hidden_records(self):
        from visibility_projects import real_life_case_markup, real_life_case_schema
        origin = 'https://nolankido.com'
        record = {'@type': 'CollectionPage', 'url': origin + '/ai-in-real-life/'}
        block = real_life_case_markup()
        for mutated in ('', block + block,
                        block.replace('/technology/dinner-on-time/', '/technology/missing/'),
                        block.replace('cooking-planner simulation', 'proven productivity'),
                        block.replace('<p id=', '<p hidden id=')):
            with self.subTest(mutated=mutated), self.assertRaises(ValueError):
                real_life_case_schema(record, mutated, origin)
        for wrong in ({**record, '@type': 'Article'},
                      {**record, 'url': origin + '/projects/'},
                      {**record, 'mainEntity': {}}):
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                real_life_case_schema(wrong, block, origin)

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
