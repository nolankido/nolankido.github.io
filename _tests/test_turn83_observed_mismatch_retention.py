"""Turn 83: a later network failure cannot erase an observed release mismatch.

The HTTP responses here are synthetic. Exact production bytes still require
the current-source manual verifier to perform public GETs. No Actions or
other scheduled worker is introduced.
"""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch, call
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import diagnose_live_crawl as live

WORKSHEET = '/downloads/ten-bb-tournament-checklist.md'
START = '/start-here/'
MISMATCH = 'Response bytes do not match the checked-out release'
HTTP_MISMATCH = 'HTTP 404, expected 200'
EXACT = 'HTTP 200; exact release bytes'


class Turn83FailureEvidenceRetention(unittest.TestCase):
    def scenario(self, inventory, replies, *, attempts=2, only=None):
        with patch.object(live.check_live, 'targets', return_value=inventory), \
             patch.object(live.check_live, 'check', side_effect=replies) as check, \
             patch.object(live, 'inspect_transport',
                          return_value='separate diagnostic HTTP 200 (bytes not compared)') as diag, \
             patch.object(live.time, 'sleep') as sleep:
            result = live.audit('all', attempts, 0, 1, only=only)
        return result, check.call_args_list, diag.call_args_list, sleep.call_args_list

    def test_observed_byte_mismatch_then_dns_failure_is_still_a_failure(self):
        body = b'# the published release source'
        result, checks, diag, _ = self.scenario(
            {WORKSHEET: (200, body)}, [(False, MISMATCH), (False, 'URLError')])
        self.assertEqual(len(checks), 2)
        self.assertEqual(len(diag), 1)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['observed_failure_routes'], [WORKSHEET])
        self.assertEqual(result['inconclusive_routes'], [])
        self.assertEqual(result['failures'][WORKSHEET], MISMATCH)
        self.assertEqual(result['latest_failures'][WORKSHEET], 'URLError')
        self.assertIn('bytes not compared', result['transport_diagnostics'][WORKSHEET])
        self.assertEqual(result['verified_routes'], {})
        self.assertEqual(live.exit_code(result), 1)

    def test_direct_http_status_mismatch_survives_later_timeout(self):
        result, checks, diag, _ = self.scenario(
            {WORKSHEET: (200, b'current')},
            [(False, HTTP_MISMATCH), (False, 'OSError')])
        self.assertEqual(len(checks), 2)
        self.assertEqual(len(diag), 1)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['failures'][WORKSHEET], HTTP_MISMATCH)
        self.assertEqual(result['latest_failures'][WORKSHEET], 'OSError')
        self.assertEqual(result['observed_failed'], 1)

    def test_later_observed_mismatch_replaces_prior_transport_failure(self):
        result, checks, diag, _ = self.scenario(
            {WORKSHEET: (200, b'current')},
            [(False, 'URLError'), (False, MISMATCH)])
        self.assertEqual(len(checks), 2)
        self.assertEqual(len(diag), 0)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['failures'][WORKSHEET], MISMATCH)
        self.assertEqual(result['latest_failures'][WORKSHEET], MISMATCH)

    def test_eventual_exact_match_clears_both_historical_error_fields(self):
        source = b'# new worksheet'
        result, checks, diag, _ = self.scenario(
            {WORKSHEET: (200, source)},
            [(False, MISMATCH), (False, 'URLError'), (True, EXACT)],
            attempts=3)
        self.assertEqual(len(checks), 3)
        self.assertEqual(len(diag), 0)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['failures'], {})
        self.assertEqual(result['latest_failures'], {})
        self.assertEqual(result['verified_routes'][WORKSHEET], {
            'http_status': 200,
            'source_sha256': sha256(source).hexdigest(),
            'verified_attempt': 3,
            'evidence': EXACT,
        })
        self.assertEqual(live.exit_code(result), 0)

    def test_network_only_reports_inconclusive_without_inventing_a_404(self):
        result, _, diag, _ = self.scenario(
            {WORKSHEET: (200, b'expected')},
            [(False, 'URLError'), (False, 'OSError')])
        self.assertEqual(result['status'], 'inconclusive')
        self.assertEqual(result['observed_failure_routes'], [])
        self.assertEqual(result['inconclusive_routes'], [WORKSHEET])
        self.assertEqual(result['failures'][WORKSHEET], 'OSError')
        self.assertEqual(result['latest_failures'][WORKSHEET], 'OSError')
        self.assertEqual(len(diag), 1)
        self.assertEqual(live.exit_code(result), 2)

    def test_independent_routes_do_not_share_stale_failure_evidence(self):
        inventory = {START: (200, b'start'), WORKSHEET: (200, b'work')}
        result, checks, _, _ = self.scenario(inventory, [
            (True, EXACT), (False, MISMATCH),
            (False, 'URLError')])
        self.assertEqual([x.args[0] for x in checks], [START, WORKSHEET, WORKSHEET])
        self.assertEqual(result['verified_routes'][START]['verified_attempt'], 1)
        self.assertEqual(result['observed_failure_routes'], [WORKSHEET])
        self.assertEqual(result['failures'][WORKSHEET], MISMATCH)
        self.assertEqual(result['latest_failures'][WORKSHEET], 'URLError')
        self.assertEqual(result['status'], 'fail')

    def test_no_public_target_must_not_pass_as_zero_of_zero(self):
        with patch.object(live.check_live, 'targets', return_value={}), \
             patch.object(live.check_live, 'check') as check:
            with self.assertRaisesRegex(ValueError, 'no registered targets'):
                live.audit('all', 2, 0, 1)
            check.assert_not_called()

    def test_direct_audit_rejects_unbounded_configuration_without_requests(self):
        for scope, attempts, interval, workers in [
            ('typo', 2, 2, 1), ('all', 0, 2, 1),
            ('all', 9, 2, 1), ('all', 2, -1, 1),
            ('all', 2, 31, 1), ('all', 2, 2, 0),
            ('all', 2, 2, 5)]:
            with self.subTest(scope=scope, attempts=attempts,
                              interval=interval, workers=workers), \
                 patch.object(live.check_live, 'targets') as targets:
                with self.assertRaises(ValueError):
                    live.audit(scope, attempts, interval, workers)
                targets.assert_not_called()

    def test_last_observed_mismatch_is_not_turned_into_a_network_probe(self):
        result, _, diag, _ = self.scenario(
            {WORKSHEET: (200, b'content')},
            [(False, MISMATCH), (False, HTTP_MISMATCH)])
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['failures'][WORKSHEET], HTTP_MISMATCH)
        self.assertEqual(result['latest_failures'][WORKSHEET], HTTP_MISMATCH)
        self.assertEqual(len(diag), 0)

    def test_scoped_checks_are_not_mistaken_for_release_wide_passes(self):
        result, checks, _, _ = self.scenario(
            {START: (200, b'start'), WORKSHEET: (200, b'work')},
            [(True, EXACT)], only=[WORKSHEET])
        self.assertEqual(len(checks), 1)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['selection'], 'explicit')
        self.assertEqual(list(result['verified_routes']), [WORKSHEET])

    def test_existing_manual_runner_and_no_new_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn83_observed_mismatch_retention.py', runner)
        self.assertIn('test_turn82_publication_retry_window.py', runner)
        diagnostic = (ROOT / '_tests/diagnose_live_crawl.py').read_text(
            encoding='utf-8')
        self.assertIn("'latest_failures':", diagnostic)
        self.assertIn("'source_sha256': sha256(expected_body).hexdigest()", diagnostic)
        self.assertIn("Release audit has no registered targets", diagnostic)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yml', '.yaml')
            for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
