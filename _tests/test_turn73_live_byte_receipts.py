"""Turn 73: bounded, source-pinned receipts for real public byte checks.

All observations here are synthetic. The production diagnostic must perform
fresh status-bearing GETs before its verified_routes are evidence of deployment.
"""
from hashlib import sha256
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import diagnose_live_crawl as live


class Turn73LiveReceipts(unittest.TestCase):
    def inspect(self, inventory, observations, *, only=None, scope='all', attempts=1):
        with patch.object(live.check_live, 'targets', return_value=inventory), \
             patch.object(live.check_live, 'check', side_effect=observations) as check, \
             patch.object(live, 'inspect_transport', return_value='URLError: blocked') as diagnose, \
             patch.object(live.time, 'sleep'):
            result = live.audit(scope, attempts, 0, 1, only=only)
        return result, check.call_count, diagnose.call_count

    def test_exact_success_retains_route_status_hash_and_attempt(self):
        inventory = {'/start-here/': (200, b'<h1>source</h1>')}
        result, calls, probes = self.inspect(
            inventory, [(True, 'HTTP 200; exact release bytes')],
            only=['/start-here/'])
        self.assertEqual((result['status'], result['passed'], result['failed']),
                         ('pass', 1, 0))
        self.assertEqual((calls, probes), (1, 0))
        self.assertEqual(result['selection'], 'explicit')
        self.assertEqual(result['verified_routes'], {
            '/start-here/': {
                'http_status': 200,
                'source_sha256': sha256(b'<h1>source</h1>').hexdigest(),
                'verified_attempt': 1,
                'evidence': 'HTTP 200; exact release bytes',
            }
        })
        self.assertEqual(live.exit_code(result), 0)

    def test_expected_404_is_a_valid_exact_response(self):
        result, _, _ = self.inspect(
            {'/known-missing/': (404, b'known-error-document')},
            [(True, 'HTTP 404; exact release bytes')])
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['verified_routes']['/known-missing/']['http_status'], 404)
        self.assertEqual(result['observed_failure_routes'], [])

    def test_retry_receipt_does_not_claim_first_attempt_passed(self):
        result, calls, probes = self.inspect(
            {'/books/': (200, b'books')},
            [(False, 'URLError'), (True, 'HTTP 200; exact release bytes')],
            attempts=2)
        self.assertEqual((calls, probes), (2, 0))
        self.assertEqual(result['verified_routes']['/books/']['verified_attempt'], 2)
        self.assertEqual(result['status'], 'pass')

    def test_inconclusive_and_mismatch_never_receive_verified_receipts(self):
        inventory = {
            '/start-here/': (200, b'start'),
            '/books/': (200, b'book'),
            '/poker/10bb/': (200, b'playbook'),
        }
        results = [
            (True, 'HTTP 200; exact release bytes'),
            (False, 'URLError'),
            (False, 'Response bytes do not match the checked-out release'),
        ]
        report, calls, probes = self.inspect(inventory, results)
        self.assertEqual((calls, probes), (3, 1))
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['passed'], 1)
        self.assertEqual(report['failed'], 2)
        self.assertEqual(set(report['verified_routes']), {'/start-here/'})
        self.assertEqual(report['inconclusive_routes'], ['/books/'])
        self.assertEqual(report['observed_failure_routes'], ['/poker/10bb/'])
        self.assertEqual(live.exit_code(report), 1)

    def test_selected_routes_cannot_hide_unknowns_or_duplicates(self):
        inventory = {'/': (200, b'home'), '/books/': (200, b'book')}
        for choices, pattern in [
            (['/books/', '/books/'], 'Duplicate'),
            (['/not-registered/'], 'Unknown selected release route'),
        ]:
            with self.subTest(only=choices):
                with patch.object(live.check_live, 'targets', return_value=inventory):
                    with self.assertRaisesRegex(ValueError, pattern):
                        live.audit('all', 1, 0, 1, only=choices)

    def test_only_does_not_mutate_inventory_or_expand_scope(self):
        inventory = {'/': (200, b'home'), '/books/': (200, b'book')}
        result, calls, _ = self.inspect(
            inventory, [(True, 'HTTP 200; exact release bytes')],
            only=['/books/'])
        self.assertEqual((calls, result['total']), (1, 1))
        self.assertEqual(set(result['verified_routes']), {'/books/'})
        self.assertEqual(set(inventory), {'/', '/books/'})

    def test_dns_is_not_a_false_zero_or_http_failure(self):
        report, calls, probes = self.inspect(
            {'/downloads/ten-bb-tournament-checklist.md': (200, b'worksheet')},
            [(False, 'URLError')])
        self.assertEqual((calls, probes), (1, 1))
        self.assertEqual(report['status'], 'inconclusive')
        self.assertEqual(report['verified_routes'], {})
        self.assertEqual(report['observed_failed'], 0)
        self.assertEqual(live.exit_code(report), 2)

    def test_priority_selection_requires_registered_priority_routes(self):
        with patch.object(live, 'PRIORITY', ('/', '/books/')), \
             patch.object(live.check_live, 'targets',
                          return_value={'/': (200, b'home'), '/books/': (200, b'book')}), \
             patch.object(live.check_live, 'check',
                          return_value=(True, 'HTTP 200; exact release bytes')) as check:
            report = live.audit('priority', 1, 0, 1, only=['/books/'])
        self.assertEqual(check.call_count, 1)
        self.assertEqual(report['verified_routes']['/books/']['http_status'], 200)
        self.assertEqual(report['selection'], 'explicit')

    def test_no_new_workflow_and_registered_local_runner(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn73_live_byte_receipts.py', runner)
        self.assertIn("glob('*_browser.py')", runner)
        script = (ROOT / '_tests/diagnose_live_crawl.py').read_text(encoding='utf-8')
        for marker in ("'verified_routes'", "'source_sha256'", "'verified_attempt'",
                       "parser.add_argument('--only'", "'selection'"):
            self.assertIn(marker, script)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.suffix.lower() in ('.yaml', '.yml') for p in actions.iterdir()))


if __name__ == '__main__':
    unittest.main()
