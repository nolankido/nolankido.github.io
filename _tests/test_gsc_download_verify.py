"""Synthetic offline regression tests for the fixed-origin release verifier."""
from __future__ import annotations

import hashlib
import importlib.util
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
import unittest
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gsc_download_verify", ROOT / "downloads/gsc-download-verify.py")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class Response:
    def __init__(self, data=b"ok", status=200):
        self.status = status
        self.stream = BytesIO(data)
    def read(self, n):
        return self.stream.read(n)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class Open:
    def __init__(self, result):
        self.result = result
    def open(self, request, timeout):
        assert request.get_method() == "GET"
        assert request.full_url in (verifier.SITE_URL, verifier.SOURCE_URL)
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


class VerifierTests(unittest.TestCase):
    def test_pinned_sha256_matches_real_published_script(self):
        source = ROOT / "downloads/gsc-period-compare.py"
        self.assertTrue(source.is_file())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), verifier.EXPECTED_SHA256)
        self.assertEqual(len(verifier.EXPECTED_SHA256), 64)

    def test_matching_200_passes(self):
        content = b"verified sample"
        with patch.object(verifier, "EXPECTED_SHA256", hashlib.sha256(content).hexdigest()), \
             patch.object(verifier, "build_opener", return_value=Open(Response(content))):
            got = verifier.check(verifier.SITE_URL)
            self.assertEqual(got["outcome"], "exact_bytes")
            self.assertEqual(got["bytes"], len(content))
            self.assertEqual(verifier.report(got, None)["exit_code"], 0)

    def test_nonmatching_200_is_byte_mismatch(self):
        with patch.object(verifier, "build_opener", return_value=Open(Response(b"other"))):
            got = verifier.check(verifier.SITE_URL)
            self.assertEqual(got["http_status"], 200)
            self.assertEqual(got["outcome"], "byte_mismatch")
            self.assertEqual(verifier.report(got, None)["exit_code"], 1)

    def test_genuine_http_404_is_not_a_network_error(self):
        error = HTTPError(verifier.SITE_URL, 404, "Not Found", {}, None)
        with patch.object(verifier, "build_opener", return_value=Open(error)):
            got = verifier.check(verifier.SITE_URL)
            self.assertEqual(got["http_status"], 404)
            self.assertEqual(got["outcome"], "http_error")
            self.assertIsNone(got["sha256"])

    def test_dns_failure_remains_inconclusive(self):
        with patch.object(verifier, "build_opener", return_value=Open(URLError("dns failed"))):
            got = verifier.check(verifier.SITE_URL)
            self.assertEqual(got["outcome"], "network_unavailable")
            self.assertIsNone(got["http_status"])
            self.assertEqual(verifier.report(got, None)["exit_code"], 2)

    def test_body_limit_is_enforced(self):
        with patch.object(verifier, "build_opener", return_value=Open(Response(b"x" * (verifier.LIMIT + 1)))):
            got = verifier.check(verifier.SITE_URL)
            self.assertEqual(got["outcome"], "body_too_large")
            self.assertIsNone(got["sha256"])

    def test_urls_are_allowlisted(self):
        with self.assertRaisesRegex(ValueError, "unregistered"):
            verifier.check("http://evil.test")

    def test_cross_origin_redirect_is_refused(self):
        handler = verifier.FixedOriginRedirect()
        class Request:
            full_url = verifier.SITE_URL
        with self.assertRaises(URLError):
            handler.redirect_request(Request(), None, 302, "", {}, "https://evil.example/script.py")

    def test_https_downgrade_is_refused(self):
        handler = verifier.FixedOriginRedirect()
        class Request:
            full_url = verifier.SITE_URL
        with self.assertRaises(URLError):
            handler.redirect_request(Request(), None, 302, "", {}, "http://nolankido.com/script.py")

    def test_github_control_does_not_override_site_failure(self):
        site = {"outcome": "http_error", "http_status": 404}
        github = {"outcome": "exact_bytes", "http_status": 200}
        got = verifier.report(site, github)
        self.assertEqual(got["exit_code"], 1)
        self.assertEqual(got["conclusion"], "site_does_not_match_pinned_release")

    def test_no_control_opt_out(self):
        site = {"outcome": "exact_bytes"}
        self.assertEqual(verifier.report(site, None)["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
