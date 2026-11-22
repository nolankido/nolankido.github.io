"""Turn 82: bounded manual wait for published bytes, with no false passes.

All HTTP observations below are mocked. The public site is checked only by
an operator running the separate GET verifier against a complete checkout.
No scheduler, GitHub Actions, forms, accounts or external test services.
"""
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from hashlib import sha256
from unittest.mock import call, patch
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import diagnose_live_crawl as live

WORKSHEET = '/downloads/ten-bb-tournament-checklist.md'
MISMATCH = 'Response bytes do not match the checked-out release'
PASS = 'HTTP 200; exact release bytes'


class Turn82ManualPublicationWindow(unittest.TestCase):
    def audit_cases(self, inventory, observations, *, attempts=2, interval=2,
                    only=None):
        with patch.object(live.check_live, 'targets', return_value=inventory), \
             patch.object(live.check_live, 'check', side_effect=observations) as check, \
             patch.object(live, 'inspect_transport',
                          return_value='URLError: blocked') as diagnose, \
             patch.object(live.time, 'sleep') as sleep:
            result = live.audit('all', attempts, interval, 1, only=only)
        return result, check.call_args_list, sleep.call_args_list, diagnose.call_count

    def test_stale_bytes_can_pass_only_after_fresh_matching_response(self):
        body = b'# checked-out complete worksheet'
        report, checks, sleeps, diagnostics = self.audit_cases(
            {WORKSHEET: (200, body)},
            [(False, MISMATCH), (False, MISMATCH), (True, PASS)],
            attempts=8, interval=15, only=[WORKSHEET])
        self.assertEqual((len(checks), len(sleeps), diagnostics), (3, 2, 0))
        self.assertEqual(sleeps, [call(15), call(15)])
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['selection'], 'explicit')
        self.assertEqual((report['attempts_configured'], report['attempts_used'],
                          report['retry_interval_seconds']), (8, 3, 15))
        self.assertEqual(report['total'], 1)
        self.assertEqual(report['verified_routes'][WORKSHEET]['verified_attempt'], 3)
        self.assertEqual(report['verified_routes'][WORKSHEET]['source_sha256'],
                         sha256(body).hexdigest())
        self.assertEqual(live.exit_code(report), 0)

    def test_persistent_byte_mismatch_is_not_reclassified_as_transient(self):
        report, checks, sleeps, diagnostics = self.audit_cases(
            {WORKSHEET: (200, b'new')}, [(False, MISMATCH)] * 8,
            attempts=8, interval=30)
        self.assertEqual((len(checks), len(sleeps), diagnostics), (8, 7, 0))
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['attempts_used'], 8)
        self.assertEqual(report['verified_routes'], {})
        self.assertEqual(report['observed_failure_routes'], [WORKSHEET])
        self.assertEqual(live.exit_code(report), 1)

    def test_network_only_failure_remains_inconclusive_after_max_wait(self):
        report, checks, sleeps, diagnostics = self.audit_cases(
            {WORKSHEET: (200, b'expected')}, [(False, 'URLError')] * 8,
            attempts=8, interval=15)
        self.assertEqual((len(checks), len(sleeps), diagnostics), (8, 7, 1))
        self.assertEqual(report['status'], 'inconclusive')
        self.assertEqual(report['observed_failure_routes'], [])
        self.assertEqual(report['inconclusive_routes'], [WORKSHEET])
        self.assertEqual(report['verified_routes'], {})
        self.assertEqual(live.exit_code(report), 2)

    def test_completed_targets_are_never_rechecked_while_others_wait(self):
        routes = {'/start-here/': (200, b'home'), WORKSHEET: (200, b'work')}
        # One worker preserves deterministic task order in this mock.
        report, checks, sleeps, _ = self.audit_cases(
            routes,
            [(True, PASS), (False, MISMATCH), (True, PASS)],
            attempts=8, interval=15)
        self.assertEqual([args.args[0] for args in checks],
                         ['/start-here/', WORKSHEET, WORKSHEET])
        self.assertEqual(sleeps, [call(15)])
        self.assertEqual(report['verified_routes']['/start-here/']['verified_attempt'], 1)
        self.assertEqual(report['verified_routes'][WORKSHEET]['verified_attempt'], 2)
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['attempts_used'], 2)

    def test_quick_defaults_still_have_same_bounded_values(self):
        result = {'status': 'pass', 'total': 1}
        with patch.object(live, 'audit', return_value=result) as mock_audit, \
             redirect_stdout(StringIO()):
            self.assertEqual(live.main(['--scope', 'all', '--only', WORKSHEET]), 0)
        mock_audit.assert_called_once_with('all', 2, 2, 2, only=[WORKSHEET])

    def test_extended_long_window_is_explicitly_supported(self):
        result = {'status': 'pass', 'total': 1}
        with patch.object(live, 'audit', return_value=result) as mock_audit, \
             redirect_stdout(StringIO()):
            self.assertEqual(live.main([
                '--scope', 'all', '--only', WORKSHEET,
                '--attempts', '8', '--interval', '30', '--workers', '1']), 0)
        mock_audit.assert_called_once_with('all', 8, 30, 1, only=[WORKSHEET])

    def test_attempt_and_interval_ceiling_fail_closed_before_network(self):
        for arguments in (
            ['--attempts', '0'], ['--attempts', '9'],
            ['--interval', '-1'], ['--interval', '31'],
            ['--workers', '5']):
            with self.subTest(arguments=arguments), \
                 patch.object(live, 'audit') as mock_audit, \
                 redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as exc:
                    live.main(arguments)
                self.assertEqual(exc.exception.code, 2)
                mock_audit.assert_not_called()

    def test_scope_and_target_selection_stay_explicit(self):
        report, checks, sleeps, _ = self.audit_cases(
            {'/': (200, b'home'), WORKSHEET: (200, b'work')},
            [(True, PASS)], attempts=8, interval=15, only=[WORKSHEET])
        self.assertEqual(report['total'], 1)
        self.assertEqual(report['selection'], 'explicit')
        self.assertEqual(list(report['verified_routes']), [WORKSHEET])
        self.assertEqual(len(checks), 1)
        self.assertEqual(sleeps, [])

    def test_existing_manual_runner_and_read_only_policy(self):
        script = (ROOT / '_tests/diagnose_live_crawl.py').read_text(
            encoding='utf-8')
        self.assertIn('choices=range(1, 9), default=2', script)
        self.assertIn('choices=range(0, 31), default=2', script)
        self.assertIn("'attempts_used': index + 1", script)
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn82_publication_retry_window.py', runner)
        self.assertIn('test_turn73_live_byte_receipts.py', runner)
        self.assertIn("glob('*_browser.py')", runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            file.is_file() and file.suffix.lower() in ('.yaml', '.yml')
            for file in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
