"""Offline review handoff remains scoped, tamper-evident and non-authorizing."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("poker_review_round", ROOT / "_reports/poker-transfer/review_round.py")
module = module_from_spec(SPEC)
SPEC.loader.exec_module(module)
TEST_SHA = "5" * 40


class QualifiedReviewRoundTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="poker-review-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.packet = self.base / "packet"

    def prepare(self, mode="triage", case_list=None):
        module.make_packet(self.packet, mode=mode, case_list=case_list, source_commit=TEST_SHA)
        return json.loads((self.packet / "manifest.json").read_text()), json.loads(
            (self.packet / "review-record.json").read_text()
        )

    def update_record(self, data):
        (self.packet / "review-record.json").write_text(json.dumps(data) + "\n")

    def complete_fixture(self, record):
        """Only synthetic test data in a temporary directory, not a human review."""
        record["reviewer"] = {
            "private_id": "SIMULATED-TEST-ONLY",
            "qualification": "synthetic test fixture",
            "conflicts": "synthetic test fixture",
            "signed_date": "2026-10-16",
            "attestation_reference": "NOT-A-REAL-SIGNATURE",
        }
        record["course_review"] = {
            "decision": "accept",
            "evidence_reference": "SYNTHETIC-TEST-ONLY",
        }
        for case in record["cases"]:
            for field in module.DIMENSIONS:
                case[field] = "accept"
            case["disposition"] = "accept"
            case["independent_evidence"] = "synthetic test evidence, not a human review"
            case["reasoning_point_evidence"] = ["synthetic point 1", "synthetic point 2", "synthetic point 3"]
        self.update_record(record)

    def test_triage_is_exactly_eighteen_and_answers_remain_separate(self):
        manifest, record = self.prepare()
        self.assertEqual(manifest["case_ids"], module.TRIAGE_IDS)
        self.assertEqual(len(manifest["entries"]), 18)
        self.assertEqual(len(record["cases"]), 18)
        questions = (self.packet / "01-independent-questions.md").read_text()
        key = (self.packet / "02-facilitator-key.md").read_text()
        self.assertIn("### S1-A:", questions)
        self.assertIn("### S6-G:", questions)
        self.assertNotIn("**Likely misconception:**", questions)
        self.assertIn("**Likely misconception:**", key)
        self.assertEqual(questions.count("Poker Foundations transfer task"), 18)
        self.assertEqual(key.count("**Likely misconception:**"), 18)
        self.assertEqual(module.audit_packet(self.packet)["status"], "human_review_pending")
        self.assertFalse(module.audit_packet(self.packet)["release_authorized"])

    def test_full_mode_contains_all_seventy_two_and_is_still_pending(self):
        manifest, record = self.prepare("full")
        self.assertEqual(manifest["case_ids"], module.EXPECTED_IDS)
        self.assertEqual(len(record["cases"]), 72)
        self.assertEqual(module.audit_packet(self.packet)["total_cases"], 72)
        self.assertEqual(module.audit_packet(self.packet)["case_dispositions"]["unreviewed"], 72)

    def test_custom_scope_never_implies_full_coverage(self):
        manifest, _ = self.prepare("custom", "S1-A,S4-J")
        self.assertEqual(manifest["case_ids"], ["S1-A", "S4-J"])
        self.assertEqual(module.audit_packet(self.packet)["total_cases"], 2)
        with self.assertRaises(module.ReviewError):
            module.select("custom", "S1-A,S1-A")
        with self.assertRaises(module.ReviewError):
            module.select("custom", "S1-A,../../passwords")
        with self.assertRaises(module.ReviewError):
            module.select("triage", "S1-A")
        with self.assertRaises(module.ReviewError):
            module.select("full", "S1-A")

    def test_assembled_reviewer_documents_are_fingerprint_bound(self):
        for name in ("01-independent-questions.md", "02-facilitator-key.md", "03-review-form.md"):
            destination = self.base / name.replace(".", "-")
            module.make_packet(destination, source_commit=TEST_SHA)
            target = destination / name
            target.write_text(target.read_text() + "\nUnapproved packet change.\n")
            with self.assertRaises(module.ReviewError):
                module.audit_packet(destination)

    def test_record_is_exactly_bound_to_a_manifest(self):
        manifest, _ = self.prepare()
        self.assertEqual(manifest["case_source_sha256"],
                         hashlib.sha256((module.FOLDER / "cases.json").read_bytes()).hexdigest())
        manifest["qualified_review_decision"] = "accept"
        (self.packet / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_changed_source_is_rejected_even_if_old_review_record_is_unchanged(self):
        self.prepare()
        folder_copy = self.base / "source-copy"
        shutil.copytree(module.FOLDER, folder_copy)
        case_file = folder_copy / "cases.json"
        text = case_file.read_text()
        self.assertIn('"draft-qualified-human-review-pending"', text)
        case_file.write_text(text.replace(
            '"draft-qualified-human-review-pending"', '"tampered"', 1
        ))
        with patch.object(module, "FOLDER", folder_copy):
            with self.assertRaises(module.ReviewError):
                module.audit_packet(self.packet)

    def test_changed_question_is_rejected_after_packet_was_prepared(self):
        self.prepare()
        folder_copy = self.base / "source-copy"
        shutil.copytree(module.FOLDER, folder_copy)
        card = folder_copy / "cards" / "S1-A.md"
        card.write_text(card.read_text() + "\nUnapproved edit.\n")
        with patch.object(module, "FOLDER", folder_copy):
            with self.assertRaises(module.ReviewError):
                module.audit_packet(self.packet)

    def test_incomplete_criteria_cannot_be_accepted(self):
        _, record = self.prepare()
        record["cases"][0]["disposition"] = "accept"
        record["cases"][0]["independent_evidence"] = "SYNTHETIC"
        self.update_record(record)
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_acceptance_requires_case_specific_evidence(self):
        _, record = self.prepare()
        for dimension in module.DIMENSIONS:
            record["cases"][0][dimension] = "accept"
        record["cases"][0]["disposition"] = "accept"
        self.update_record(record)
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_accepted_case_requires_all_three_independent_reasoning_points(self):
        _, record = self.prepare()
        for dimension in module.DIMENSIONS:
            record["cases"][0][dimension] = "accept"
        record["cases"][0]["disposition"] = "accept"
        record["cases"][0]["independent_evidence"] = "synthetic summary"
        record["cases"][0]["reasoning_point_evidence"] = ["point 1", "", "point 3"]
        self.update_record(record)
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_open_issue_cannot_coexist_with_case_acceptance(self):
        _, record = self.prepare()
        self.complete_fixture(record)
        record["cases"][0]["open_issue_ids"] = ["ISSUE-123"]
        self.update_record(record)
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_wrong_case_binding_cannot_be_reused_as_approval(self):
        _, record = self.prepare()
        self.complete_fixture(record)
        record["cases"][0]["case_sha256"] = record["cases"][1]["case_sha256"]
        self.update_record(record)
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_simulated_triage_completion_cannot_authorize_publication(self):
        _, record = self.prepare()
        self.complete_fixture(record)
        result = module.audit_packet(self.packet)
        self.assertEqual(result["status"], "scoped_review_recorded_not_full_approval")
        self.assertFalse(result["release_authorized"])
        self.assertEqual(result["case_dispositions"]["accept"], 18)

    def test_simulated_full_review_remains_unverified_and_non_authorizing(self):
        _, record = self.prepare("full")
        self.complete_fixture(record)
        result = module.audit_packet(self.packet)
        self.assertEqual(result["status"], "full_review_record_claimed_authentication_required")
        self.assertFalse(result["release_authorized"])
        self.assertEqual(result["case_dispositions"]["accept"], 72)

    def test_missing_course_review_is_an_explicit_separate_blocker(self):
        _, record = self.prepare("full")
        self.complete_fixture(record)
        record["course_review"] = {"decision": "unreviewed", "evidence_reference": ""}
        self.update_record(record)
        self.assertEqual(module.audit_packet(self.packet)["status"], "course_review_pending")

    def test_review_date_and_conflicts_are_required_for_completion(self):
        _, record = self.prepare("full")
        self.complete_fixture(record)
        record["reviewer"]["conflicts"] = ""
        self.update_record(record)
        self.assertEqual(module.audit_packet(self.packet)["status"], "human_review_pending")
        record["reviewer"]["signed_date"] = "not-a-date"
        self.update_record(record)
        with self.assertRaises(module.ReviewError):
            module.audit_packet(self.packet)

    def test_never_write_private_records_inside_public_repo_or_overwrite(self):
        inside = ROOT / "_reports" / "poker-transfer" / "_private_review_fixture"
        with self.assertRaises(module.ReviewError):
            module.make_packet(inside, source_commit=TEST_SHA)
        self.assertFalse(inside.exists())
        self.packet.mkdir()
        (self.packet / "existing.txt").write_text("keep this")
        with self.assertRaises(module.ReviewError):
            module.make_packet(self.packet, source_commit=TEST_SHA)
        self.assertEqual((self.packet / "existing.txt").read_text(), "keep this")

    def test_audit_pending_has_nonzero_cli_exit(self):
        self.prepare()
        from contextlib import redirect_stdout
        from io import StringIO
        with redirect_stdout(StringIO()) as output:
            exit_code = module.main(["audit", "--packet", str(self.packet)])
        self.assertEqual(exit_code, 2)
        self.assertIn("human_review_pending", output.getvalue())


if __name__ == "__main__":
    unittest.main()
