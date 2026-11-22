# SEO/GEO Turn 74: prevent redirected pages from falsely passing production release verification

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting `main`:** `09073ae2a0247fb0f45aaebff62b80958ef799b3` (Turn 73, merged PR #447).
**Affected code:** `_scripts/check_live.py`, source-only regression tests, manual release registration and repository operating rules.

## Why this is a real verification defect

The existing production verification compares a registered route's expected status and exact checked-out bytes against the body served by `urllib.request`. It also allows safe same-origin redirects. Prior to this turn, it did **not** check `response.geturl()` against the route requested. If `/start-here/` redirected to another path that returned the same response bytes, the verifier could mark `/start-here/` as a correct deployed route. That is a false-positive for a reader-facing canonical URL or download path. The problem concerns the **verification method**, not a proven current production redirect.

The Turn 73 JSON receipts would have propagated this false-positive as a per-URL passing result. A canonical path must be verified independently of page-body equality.

## Change made

1. Read the final response URL inside the existing `check_live.check()` HTTP response context. Continue to compare expected and actual status and exact response bytes.
2. Require the final response to remain HTTPS on `nolankido.com` and on the **same registered path**. Harmless query removal is allowed, including removal of the `?release-check=` cache-busting parameter.
3. Return the observed-mismatch classification message `HTTP 200; final URL changed registered route` (or the actual HTTP status) for a changed final path, origin or scheme, even if the body is identical. The existing `diagnose_live_crawl.classify_failure()` recognizes the `HTTP ` prefix as an observed mismatch, not DNS ambiguity.
4. Apply the same rule to the expected 404 negative-control route: a matching 404 body served from `/404.html` does not prove the original requested unknown URL still serves its own error page.
5. Add `_tests/test_turn74_final_route_guard.py` with eleven in-memory mock-response tests, including original route, query stripping, path hop, index-file alias, different origin, expected and redirected 404, status mismatch, byte mismatch, real worksheet path, redirect handler cross-origin block, and the manual-runner policy. Register it in the existing local release checklist.

## Verification actually completed

| Evidence | Result | Interpretation |
| --- | --- | --- |
| Original source inspected through authenticated GitHub | **Confirmed** | The original `check_live.check()` compared status/body but not final URL |
| Modified file and test code committed in PR branch | **Confirmed** | One bounded production verifier guard and negative-control test module |
| Isolated Python execution of the updated checking logic | **9 of 9 behavioral scenarios passed** | Exercise of the same guard and outcomes outside a full site checkout, not full repo tests |
| Regression test module | **11 tests authored; full module not run** | Requires importing the actual repository dependencies from a complete checkout |
| Existing canonical sitemap entries | **Not changed** | No new or removed page, schema, article date, redirect policy, or sitemap URL |
| Live HTTP status, final URL, exact public bytes | **Not checked by direct verifier** | Local container cannot resolve `github.com`; remote public content extraction is not a substitute for raw HTTP response verification |
| Complete build, HTML5, internal links, all Python and mobile Chromium tests | **Not run** | Full checkout not available in this environment; local Chromium also blocks loopback HTTP |
| Google/Bing/AI source visibility | **Unavailable** | Cannot assert clicks, impressions, index coverage or AI citations |

### Isolated outcome details

The local standalone behavioral harness used a mocked read-only urllib opener and the same conditional route guard. All nine candidates behaved as expected: matching original route accepted; query stripped but same path accepted; changed path rejected; `index.html` alias rejected; changed origin rejected; matching 404 accepted; redirected 404 rejected; HTTP status mismatch rejected; byte mismatch rejected. These are constructed cases and **not** observations of the production website.

## Full-checkout acceptance commands

```powershell
py -3 -m unittest discover -s _tests -p test_turn74_final_route_guard.py -v
py -3 -m unittest discover -s _tests -p test_turn73_live_byte_receipts.py -v
py -3 -m unittest discover -s _tests -p test_turn38_live_evidence.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /start-here/ --only /poker/10bb/ --only /downloads/ten-bb-tournament-checklist.md --attempts 2 --interval 2
```

Accept `verified_routes` only where the report says `status: pass` and every requested URL is explicitly present with a same-path, same-origin exact-byte pass. A path-changing redirect is a confirmed release mismatch and must be repaired, not waived by matching bytes. An environment-only DNS error remains inconclusive; never report it as a 404.

## Sprint status and next gate

**Advancement:** release integrity for the entire 230-URL source-registered inventory, especially canonical article paths, book routes and real workbook downloads. This turn raises the standard of actual future release proof. It does not show that any current route is broken or that rankings have changed.

**Still open:** executable complete-checkout tests; live source-to-response receipts; mobile task completion; authentic Google/Bing search metrics; frozen assistant citation panel; measured performance and authentic retailer edition metadata. Do not add a duplicate automation or GitHub Actions.

**Next high-value improvement:** execute the strict live verifier in an environment with direct HTTP and the matching checkout, repair any observed redirect or byte mismatch, then use first-party query/page data to prioritize content updates.
