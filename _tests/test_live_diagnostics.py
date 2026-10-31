"""Exercise standalone public-response diagnostics without network access."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagnose_live_crawl as diagnostics


class LiveDiagnosticsTests(unittest.TestCase):
    def test_priority_scope_uses_exact_bytes_and_retries_without_false_passes(self):
        values = {route: (200, b'page') for route in diagnostics.PRIORITY}
        outcomes = [(False, 'URLError')] * len(values) + [(True, 'HTTP 200; exact release bytes')] * len(values)
        with patch('diagnose_live_crawl.check_live.targets', return_value=values), \
             patch('diagnose_live_crawl.check_live.check', side_effect=outcomes) as check, \
             patch('diagnose_live_crawl.time.sleep') as wait, \
             patch('diagnose_live_crawl.inspect_transport') as transport:
            report = diagnostics.audit('priority', 2, 2, 1)
        self.assertEqual((report['total'], report['passed'], report['failed']), (len(values), len(values), 0))
        self.assertTrue(report['exact_byte_comparison'])
        self.assertEqual(check.call_count, len(values) * 2)
        wait.assert_called_once_with(2)
        transport.assert_not_called()

    def test_failure_stays_failure_even_if_later_get_responds(self):
        with patch('diagnose_live_crawl.check_live.targets', return_value={'/': (200, b'page')}), \
             patch('diagnose_live_crawl.check_live.check', return_value=(False, 'URLError')), \
             patch('diagnose_live_crawl.inspect_transport', return_value='separate diagnostic HTTP 200 (bytes not compared)'):
            report = diagnostics.audit('all', 1, 0, 1)
        self.assertEqual((report['passed'], report['failed']), (0, 1))
        self.assertEqual(report['failures']['/'], 'URLError')
        self.assertIn('bytes not compared', report['transport_diagnostics']['/'])


if __name__ == '__main__':
    unittest.main()
