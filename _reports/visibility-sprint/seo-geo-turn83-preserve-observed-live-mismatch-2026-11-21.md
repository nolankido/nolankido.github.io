# SEO/GEO Turn 83: preserve direct release mismatches even when later network requests fail

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `5a0ccb1433279e0c442c28ce93e1e9127b6d7fd3` (Turn 82, merged PR #456).
**Scope:** Correctness of existing manual, read-only live deployment diagnostics. No new page, tracking, canonical URL, worksheet, search claim, scheduled monitoring or GitHub Actions.

## Reproducible defect

The existing `_tests/diagnose_live_crawl.py` stores only the most recent failed result for a route in `failures[route]`. Its classification happens after the retries end. This permits an observed release mismatch to be hidden by a later transport problem:

1. First attempt to a registered worksheet returns `Response bytes do not match the checked-out release`. This is an actual checked response mismatch.
2. Second attempt returns `URLError` because of a DNS, TLS or network problem.
3. Before the fix, `failures[route]` is overwritten by `URLError`, so the final result is `inconclusive`. A genuine observed HTTP/body difference disappears from the failure receipt.

The minimal original two-message overwrite was executed locally and produced exactly this misleading `inconclusive` classification. The persistent mismatch is a **failure unless a later successful GET actually proves the exact expected response**. A later network failure cannot disprove the earlier mismatch; equally, the mismatch does not establish its root cause or permanence.

## Implemented source correction

1. Keep `failures` as the **strongest observed failed evidence** on each still-pending route. A status/byte mismatch outranks a later inconclusive transport error. A newer status/byte mismatch may replace an older one.
2. Add `latest_failures` to record the actual last failed attempt separately. Only this latest transport outcome can trigger `inspect_transport()`, whose evidence is explicitly a different request and **not a source-byte comparison**.
3. On a later exact status, final-path and byte success, clear both failure dictionaries for that route. Keep `verified_routes.source_sha256`, `verified_attempt` and receipt evidence tied to the completed pass. Continue to retry only pending routes.
4. Fail closed for empty registered target inventory and validate scope, attempts, interval and workers even for direct Python calls that bypass the argument parser. No empty 0/0 pass is allowed.
5. Add eleven synthetic regression test methods in `_tests/test_turn83_observed_mismatch_retention.py`; register them with the already manual local release runner. Include unchanged baseline tests for ordinary byte and expected 404 passes, prior-network-then-mismatch, selective checks and no Actions.

## Isolated executable validation

The updated `classify_failure`, `exit_code` and `audit` source slice was read from the authenticated GitHub branch, then reproduced in an isolated Python file. Both copies had exactly **4,874 characters** and the same **FNV32 checksum `bb7349d1`**. This is a corruption-detection check on the copied source, not a cryptographic provenance signature.

Executed twelve isolated function-level tests of the actual source logic with synthetic reply sequences, mocked transport diagnostics, and no public network calls:

| Scenario | Expected and observed |
| --- | --- |
| Byte mismatch then DNS error | FAIL; retain mismatch and latest DNS error |
| HTTP 404 when expected 200, then timeout | FAIL; retain observed HTTP mismatch |
| DNS error then byte mismatch | FAIL; later observed mismatch governs |
| Byte mismatch then DNS error then exact status/byte match | PASS at third attempt; clear failure history |
| Network errors only | INCONCLUSIVE; no invented HTTP failure |
| Two routes, one exact and one mismatched | FAIL only still-pending mismatched route |
| Empty registered inventory | Explicit ValueError; not a 0/0 PASS |
| Invalid direct-call scope or retry settings | Explicit ValueError without requests |
| A newer HTTP mismatch after an earlier byte mismatch | FAIL with latest direct observation |
| Selected-route exact pass | Correctly scoped, not a whole-site pass |
| Expected 404 document | Exact known 404 can PASS |
| Missing required priority target | Explicit ValueError |

**Result: 12/12 isolated function-level tests passed.** These tests verify local classification logic only. The eleven newly authored repository `unittest` methods have not yet been run from a full current repository checkout; they include source/runner file checks unavailable to the isolated harness.

## Remaining release gates

```powershell
py -3 -m unittest discover -s _tests -p test_turn83_observed_mismatch_retention.py -v
py -3 -m unittest discover -s _tests -p test_turn82_publication_retry_window.py -v
py -3 -m unittest discover -s _tests -p test_turn73_live_byte_receipts.py -v
py -3 -m unittest discover -s _tests -p test_live_diagnostics.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /downloads/ten-bb-tournament-checklist.md --attempts 8 --interval 15 --workers 1
```

The final command checks one registered release target only; it does not certify every page or download. Its public request and exact-byte result were **not executed** in this isolated environment, where `github.com` is unreachable from the container. Production body correctness may be separately observed by content extraction, but that extraction must not be called an exact byte receipt. This turn does not rerun Search Console, AI citation, mobile or other user-journey checks.

## Sprint status

**Advanced:** release diagnostics now preserve durable negative evidence across unstable transport, an important safeguard for truthful claims about the website and downloaded educational materials. The change tightens quality assurance without publishing a speculative SEO page. The committed sitemap inventory remains 230 distinct canonical URLs, not confirmed indexed pages.

**Still open:** executable full current-source release suite, raw status-bearing source-to-live byte receipts across all priority routes, 320px reader journeys, page performance and authenticated first-party Google/Bing/assistant visibility data. The GSC Wizard account previously returned `payment_required`; no subscription was initiated. No traffic, indexing, conversion or ranking gain is claimed.

**Next priority:** run the complete repository tests and the now more trustworthy release diagnostic in a network-capable checkout. Investigate any observed mismatch before proceeding with additional unmeasured page changes.
