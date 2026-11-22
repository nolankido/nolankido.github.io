"""Turn 38: offline tests for the priority live-response audit and honest outcomes.

All HTTP observations are synthetic. No public network requests occur here.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_tests"))
import diagnose_live_crawl as diagnostics


class Turn38LiveEvidenceTests(unittest.TestCase):
    def run_cases(self, outcomes, inventory=None, scope="all", attempts=1):
        if inventory is None:
            inventory = {"/": (200, b"original")}
        with patch.object(diagnostics.check_live, "targets", return_value=inventory), \
             patch.object(diagnostics.check_live, "check", side_effect=outcomes) as check, \
             patch.object(diagnostics, "inspect_transport", return_value="URLError: DNS failure") as probe, \
             patch.object(diagnostics.time, "sleep"):
            result = diagnostics.audit(scope, attempts, 0, 1)
        return result, check.call_count, probe.call_count

    def test_priority_scope_includes_recent_books_and_key_downloads(self):
        routes = diagnostics.PRIORITY
        self.assertEqual(len(routes), len(set(routes)))
        expected = {
            "/", "/about/", "/start-here/", "/technology/", "/ai-in-real-life/",
            "/technology/checking-ai-website-changes/",
            "/technology/ai-website-visibility/", "/technology/ai-workflow-pilot/",
            "/books/", "/books/one-workflow-at-a-time/",
            "/books/how-to-play-no-limit-texas-holdem/",
            "/poker/free-poker-learning-path/", "/poker/10bb/",
            "/downloads/one-workflow-ai-pilot-worksheet.md",
            "/downloads/holdem-river-call-check-worksheet.md",
            "/downloads/website-check-offline-runbook.md",
            "/downloads/ten-bb-tournament-checklist.md",
            "/downloads/ten-bb-playbook-icm-verify.py",
            "/downloads/gsc-period-compare.py",
            "/downloads/gsc-download-verify.py",
            "/robots.txt", "/sitemap.xml",
            "/review-no-such-page-20261005/",
        }
        self.assertTrue(expected.issubset(routes))

    def test_current_inventory_registers_all_priority_targets(self):
        # This is deliberately a full-checkout source inventory test, not HTTP.
        inventory = diagnostics.check_live.targets(ROOT)
        missing = sorted(set(diagnostics.PRIORITY) - set(inventory))
        self.assertEqual(missing, [])

    def test_priority_scope_requires_every_registered_target(self):
        with patch.object(diagnostics.check_live, "targets", return_value={"/": (200, b"ok")}):
            with self.assertRaisesRegex(ValueError, "Priority release targets are not registered"):
                diagnostics.audit("priority", 1, 0, 1)

    def test_priority_scope_complete_synthetic_pass(self):
        inventory = {route: (200, b"same") for route in diagnostics.PRIORITY}
        inventory["/review-no-such-page-20261005/"] = (404, b"known-404")
        observed = [(True, f"HTTP {status}; exact release bytes")
                    for status, _ in inventory.values()]
        result, calls, probes = self.run_cases(
            observed, inventory=inventory, scope="priority")
        self.assertEqual(calls, len(inventory))
        self.assertEqual(probes, 0)
        self.assertEqual((result["status"], result["passed"], result["failed"]),
                         ("pass", len(inventory), 0))
        self.assertEqual(diagnostics.exit_code(result), 0)

    def test_dns_failure_has_no_claimed_http_status(self):
        result, calls, probes = self.run_cases([(False, "URLError")])
        self.assertEqual((calls, probes), (1, 1))
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["inconclusive_routes"], ["/"])
        self.assertEqual(result["observed_failure_routes"], [])
        self.assertEqual(result["observed_failed"], 0)
        self.assertEqual(diagnostics.exit_code(result), 2)

    def test_http_404_for_expected_200_is_observed_failure(self):
        result, _, probes = self.run_cases([(False, "HTTP 404, expected 200")])
        self.assertEqual(probes, 0)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["observed_failure_routes"], ["/"])
        self.assertEqual(result["inconclusive_routes"], [])
        self.assertEqual(diagnostics.exit_code(result), 1)

    def test_exact_byte_mismatch_is_observed_failure(self):
        result, _, _ = self.run_cases(
            [(False, "Response bytes do not match the checked-out release")])
        self.assertEqual(result["observed_failed"], 1)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(diagnostics.exit_code(result), 1)

    def test_unknown_transport_message_is_not_invented_http_failure(self):
        result, _, _ = self.run_cases([(False, "unclassified transport problem")])
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["observed_failed"], 0)

    def test_retry_that_reaches_exact_bytes_passes(self):
        result, calls, probes = self.run_cases(
            [(False, "URLError"), (True, "HTTP 200; exact release bytes")], attempts=2)
        self.assertEqual((calls, probes), (2, 0))
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["failed"], 0)

    def test_mixed_observed_and_unknown_is_fail_with_separate_counts(self):
        inventory = {"/": (200, b"one"), "/books/": (200, b"two")}
        result, _, _ = self.run_cases(
            [(False, "HTTP 404, expected 200"), (False, "URLError")],
            inventory=inventory)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["observed_failure_routes"], ["/"])
        self.assertEqual(result["inconclusive_routes"], ["/books/"])
        self.assertEqual(diagnostics.exit_code(result), 1)

    def test_expected_negative_control_404_can_pass_when_checker_verifies_bytes(self):
        route = "/review-no-such-page-20261005/"
        result, _, _ = self.run_cases(
            [(True, "HTTP 404; exact release bytes")],
            inventory={route: (404, b"known-404")})
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["observed_failure_routes"], [])
        self.assertEqual(diagnostics.exit_code(result), 0)


if __name__ == "__main__":
    unittest.main()
