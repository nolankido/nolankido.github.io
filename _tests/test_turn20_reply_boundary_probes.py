"""Turn 20: demonstrate lexical reply-screen limits with reproducible synthetic probes."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from test_site import ROOT
import build_reply_audit_case
import turn20_reply_boundaries_history as history


class Turn20ReplyBoundaryTests(unittest.TestCase):
    def test_article_source_and_published_html_are_kept_in_sync(self):
        source = (ROOT / "_source/technology/review-reply-evidence-audit.html").read_text(encoding="utf-8")
        public = (ROOT / "technology/review-reply-evidence-audit/index.html").read_text(encoding="utf-8")
        self.assertEqual(public, build_reply_audit_case.render())
        self.assertIn(source, public)
        self.assertEqual(source.count(history.INSERTION), 1)
        self.assertEqual(public.count(history.INSERTION), 1)
        self.assertEqual(source.count('id="reply-audit-boundaries"'), 1)
        self.assertNotIn("\u2014", source)
        self.assertNotIn("<script", source.lower())
        self.assertNotIn("<iframe", source.lower())
        self.assertIn('/downloads/reply-audit-boundary-probes.py', source)

    def test_boundary_probes_are_accurate_about_their_own_limits(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "downloads/reply-audit-boundary-probes.py"), "--self-test"],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["probe_count"], 4)
        self.assertEqual((report["matches"], report["mismatches"]), (1, 3))
        self.assertEqual(report["model_outputs_created"], 0)
        self.assertEqual(report["remote_requests_made"], 0)
        self.assertEqual(report["business_approvals_performed"], 0)
        by_id = {row["probe"]: row for row in report["probes"]}
        self.assertEqual({name: row["observed_commitment_or_omission_flag"]
                          for name, row in by_id.items()}, {
            "explicit_refund_detected": True,
            "reimbursement_not_detected": False,
            "gift_card_not_detected": False,
            "quoted_warning_overflagged": True,
        })
        self.assertTrue(all(not row["targeted_fact_omissions"] for row in by_id.values()))
        self.assertEqual(history.blob((ROOT / "downloads/reply-audit-boundary-probes.py").read_bytes()),
                         history.ADDED["downloads/reply-audit-boundary-probes.py"])

    def test_predecessor_is_exact_and_refuses_unrecognized_mutations(self):
        for path, (previous_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                raw = (ROOT / path).read_bytes()
                self.assertEqual(history.blob(raw), current_sha)
                previous = history.before(path, raw)
                self.assertEqual(history.blob(previous), previous_sha)
                self.assertEqual(history.before(path, previous), previous)
                self.assertEqual(history.before(path, raw + b"unknown"), raw + b"unknown")
                self.assertEqual(history.before("unknown/" + path, raw), raw)


if __name__ == "__main__":
    unittest.main()
