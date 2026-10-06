"""Live checker unit tests use fake responses, never public requests."""
from io import BytesIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import URLError
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import check_live

class Response(BytesIO):
    def __init__(self, code, body):
        super().__init__(body)
        self.code = code

class LiveCheckTests(unittest.TestCase):
    def test_exact_success_and_read_only_method(self):
        with patch('check_live.urllib.request.build_opener') as factory:
            factory.return_value.open.return_value = Response(200, b'page')
            self.assertTrue(check_live.check('/', (200, b'page'))[0])
            request = factory.return_value.open.call_args.args[0]
            self.assertEqual(request.get_method(), 'GET')
            self.assertIsNone(request.data)
            self.assertFalse(request.has_header('Authorization'))

    def test_status_and_content_mismatch_fail(self):
        for status, body in [(200, b'old'), (404, b'page'), (500, b'page')]:
            with patch('check_live.urllib.request.build_opener') as factory:
                factory.return_value.open.return_value = Response(status, body)
                self.assertFalse(check_live.check('/', (200, b'page'))[0])

    def test_network_failure_is_not_success(self):
        with patch('check_live.urllib.request.build_opener') as factory:
            factory.return_value.open.side_effect = URLError('unreachable')
            self.assertFalse(check_live.check('/', (200, b'page'))[0])

    def test_paths_and_excluded_source(self):
        values = check_live.targets()
        self.assertEqual(len(values), 35)
        self.assertEqual(values['/_source/site.json'], (404, (ROOT / '404.html').read_bytes()))
        self.assertEqual(values['/contact/'][0], 200)
        for route in ['//another.example/', 'https://example.com/', '/?other=1']:
            self.assertFalse(check_live.check(route, (200, b''))[0])
        self.assertNotIn('https://submit-form.com/uPlTgRTAR', values)

if __name__ == '__main__':
    unittest.main(verbosity=2)
