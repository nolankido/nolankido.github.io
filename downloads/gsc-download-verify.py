#!/usr/bin/env python3
"""Read-only HTTP and byte check of NolanKido's pinned public GSC comparator.

Standard-library Python 3.10+. Does not write files, run downloaded content,
collect personal data, authenticate, or launch a browser. Two fixed HTTPS GETs:
the public website and a pinned, published GitHub raw-file control.
The published expected hash is for the comparator frozen at GitHub commit
b0a419f51096df3b7b12ee471edb09a5e2aa4312; a later intentional comparator
revision must update this expectation and its tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

EXPECTED_SHA256 = "805be287f6e57906e1be096a3a806e58fe1cd7eabc7484d0f311f2cbc3417da7"
PINNED_COMMIT = "b0a419f51096df3b7b12ee471edb09a5e2aa4312"
SITE_URL = "https://nolankido.com/downloads/gsc-period-compare.py"
SOURCE_URL = ("https://raw.githubusercontent.com/nolankido/nolankido.github.io/"
              + PINNED_COMMIT + "/downloads/gsc-period-compare.py")
LIMIT = 256 * 1024


class FixedOriginRedirect(HTTPRedirectHandler):
    """Allow an HTTPS redirect only within the host we explicitly requested."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        original = urlsplit(req.full_url)
        redirected = urlsplit(newurl)
        if (original.scheme != "https" or redirected.scheme != "https" or
                redirected.netloc != original.netloc or
                redirected.username is not None or redirected.password is not None):
            raise URLError("unsafe_redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check(url: str, timeout: int = 12) -> dict:
    """A single public GET. Only a real HTTP status and matching bytes can PASS."""
    if url not in (SITE_URL, SOURCE_URL):
        raise ValueError("unregistered URL")
    req = Request(url, headers={"User-Agent": "NolanKidoPublicReleaseVerify/1.0",
                                "Cache-Control": "no-cache", "Accept-Encoding": "identity"},
                  method="GET")
    opener = build_opener(FixedOriginRedirect())
    result = {"url": url, "http_status": None, "sha256": None,
              "bytes": None, "outcome": None, "matches_pinned": None}
    try:
        with opener.open(req, timeout=timeout) as response:
            result["http_status"] = response.status
            body = response.read(LIMIT + 1)
    except HTTPError as error:
        result["http_status"] = error.code
        error.close()
        result["outcome"] = "http_error"
        return result
    except (URLError, OSError) as error:
        result["outcome"] = ("unsafe_redirect" if "unsafe_redirect" in str(error)
                             else "network_unavailable")
        return result

    if result["http_status"] != 200:
        result["outcome"] = "http_error"
    elif len(body) > LIMIT:
        result["outcome"] = "body_too_large"
    else:
        result["bytes"] = len(body)
        result["sha256"] = hashlib.sha256(body).hexdigest()
        result["matches_pinned"] = result["sha256"] == EXPECTED_SHA256
        result["outcome"] = "exact_bytes" if result["matches_pinned"] else "byte_mismatch"
    return result


def report(site: dict, source: dict | None) -> dict:
    if site["outcome"] == "exact_bytes":
        conclusion, exit_code = "site_verified", 0
    elif site["outcome"] in ("http_error", "byte_mismatch", "body_too_large"):
        conclusion, exit_code = "site_does_not_match_pinned_release", 1
    else:
        conclusion, exit_code = "site_status_inconclusive", 2
    return {"expected_sha256": EXPECTED_SHA256,
            "pinned_git_commit": PINNED_COMMIT,
            "site": site, "pinned_github_control": source,
            "conclusion": conclusion, "exit_code": exit_code,
            "interpretation": (
                "An HTTP 200 and exact SHA-256 prove this single public file matched "
                "the pinned comparator at check time, not search indexing, ranking or traffic. "
                "A GitHub control result does not replace the public-site test. "
                "HTTP failures are observed HTTP statuses; network errors are inconclusive."
            )}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=12, help="network timeout in seconds, 3 to 30")
    parser.add_argument("--skip-github-control", action="store_true",
                        help="check only the public site, not the pinned GitHub control")
    args = parser.parse_args(argv)
    if not 3 <= args.timeout <= 30:
        parser.error("--timeout must be 3..30 seconds")
    site = check(SITE_URL, timeout=args.timeout)
    source = None if args.skip_github_control else check(SOURCE_URL, timeout=args.timeout)
    result = report(site, source)
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
