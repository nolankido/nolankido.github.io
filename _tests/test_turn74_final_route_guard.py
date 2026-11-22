"""Turn 74: a matching body is not proof of the requested canonical route.

Use an in-memory opener only. No public HTTP request, credentials, external
tools, CI or assumptions about actual current deployment are involved.
"""
from pathlib import Path
import sys
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import check_live
import diagnose_live_crawl


class Response:
    def __init__(self, status: int, body: bytes, final_url: str):
        self.code = status
        self._body = body
        self._url = final_url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, limit: int):
        return self._body[:limit]

    def geturl(self):
        return self._url


class Opener:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def open(self, request, timeout=12):
        self.requests.append(request)
        return self.response


class Turn74FinalRoute(unittest.TestCase):
    def inspect(self, route, expected, status, body, final_url):
        opener = Opener(Response(status, body, final_url))
        with patch.object(check_live.urllib.request, 'build_opener',
                          return_value=opener), \
             patch.object(check_live.time, 'time_ns', return_value=1234):
            result = check_live.check(route, expected)
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(opener.requests[0].get_method(), 'GET')
        self.assertEqual(opener.requests[0].full_url,
                         check_live.ORIGIN + route + '?release-check=1234')
        return result

    def test_matching_bytes_on_original_url_pass(self):
        self.assertEqual(self.inspect(
            '/start-here/', (200, b'<main>start</main>'), 200,
            b'<main>start</main>',
            'https://nolankido.com/start-here/?release-check=1234'),
            (True, 'HTTP 200; exact release bytes'))

    def test_query_stripping_does_not_fail_canonical_path(self):
        self.assertEqual(self.inspect(
            '/start-here/', (200, b'page'), 200, b'page',
            'https://nolankido.com/start-here/'),
            (True, 'HTTP 200; exact release bytes'))

    def test_redirect_to_different_path_cannot_claim_success(self):
        ok, reason = self.inspect(
            '/start-here/', (200, b'identical'), 200, b'identical',
            'https://nolankido.com/technology/')
        self.assertFalse(ok)
        self.assertEqual(reason,
                         'HTTP 200; final URL changed registered route')
        self.assertEqual(diagnose_live_crawl.classify_failure(reason),
                         'observed_mismatch')

    def test_html_file_alias_does_not_pass_for_directory_canonical(self):
        ok, reason = self.inspect(
            '/poker/10bb/', (200, b'guide'), 200, b'guide',
            'https://nolankido.com/poker/10bb/index.html')
        self.assertFalse(ok)
        self.assertIn('final URL changed registered route', reason)

    def test_expected_404_on_original_path_passes(self):
        self.assertEqual(self.inspect(
            '/review-no-such-page-20261005/', (404, b'error'), 404, b'error',
            'https://nolankido.com/review-no-such-page-20261005/'),
            (True, 'HTTP 404; exact release bytes'))

    def test_expected_404_redirect_to_another_error_path_fails(self):
        ok, reason = self.inspect(
            '/review-no-such-page-20261005/', (404, b'error'), 404, b'error',
            'https://nolankido.com/404.html')
        self.assertFalse(ok)
        self.assertIn('final URL changed registered route', reason)

    def test_status_mismatch_is_reported_before_any_redirect_question(self):
        self.assertEqual(self.inspect(
            '/books/', (200, b'expected'), 404, b'expected',
            'https://nolankido.com/404.html'),
            (False, 'HTTP 404, expected 200'))

    def test_byte_mismatch_still_fails_without_false_redirect_error(self):
        self.assertEqual(self.inspect(
            '/books/', (200, b'expected'), 200, b'other',
            'https://nolankido.com/books/'),
            (False, 'Response bytes do not match the checked-out release'))

    def test_redirect_handler_rejects_cross_origin_even_for_identical_bytes(self):
        handler = check_live.SameOriginRedirect()
        request = urllib.request.Request('https://nolankido.com/start-here/')
        with self.assertRaisesRegex(urllib.error.URLError, 'Unexpected cross-origin'):
            handler.redirect_request(
                request, None, 301, 'Moved', {},
                'https://www.nolankido.com/start-here/')

    def test_registered_static_asset_route_can_pass(self):
        self.assertEqual(self.inspect(
            '/downloads/ten-bb-tournament-checklist.md',
            (200, b'# worksheet'), 200, b'# worksheet',
            'https://nolankido.com/downloads/ten-bb-tournament-checklist.md'),
            (True, 'HTTP 200; exact release bytes'))

    def test_manual_runner_and_evidence_boundary(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn74_final_route_guard.py', runner)
        src = (ROOT / '_scripts/check_live.py').read_text(encoding='utf-8')
        self.assertIn('final_url = urlsplit(response.geturl())', src)
        self.assertIn('final_url.path != route', src)
        workflows = ROOT / '.github/workflows'
        self.assertFalse(workflows.exists() and any(
            p.suffix.lower() in ('.yaml', '.yml') for p in workflows.iterdir()
        ))


if __name__ == '__main__':
    unittest.main()
