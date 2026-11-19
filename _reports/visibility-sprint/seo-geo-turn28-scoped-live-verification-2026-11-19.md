# SEO/GEO/AEO improvement Turn 28: targeted public-download verification

**Date:** November 19, 2026 (Pacific/Honolulu)

**Scope:** Extend the site's existing manual public verifier so a release can check one registered download without probing the entire site. This is follow-up work to [Turn 27](seo-geo-turn27-comparator-release-check-2026-11-19.md), not another 25-turn sprint entry.

## Why this is necessary

Turn 26 merged the no-cost private Search Console comparison script. Turn 27 repaired its unit-test import path and added the script to the manual public verification inventory. The remaining question was whether `https://nolankido.com/downloads/gsc-period-compare.py` actually returns HTTP 200 with the exact committed source bytes.

Observations were **inconclusive and contradictory**: a browser-style agent displayed a not-found page for the new Python download, an older Python download, and a control CSV; a separate page retrieval successfully read that control CSV but reported the Python URLs unreachable. The model's working container could not resolve `nolankido.com` for a direct curl. None of these results establishes a trustworthy HTTP status and body-byte comparison for the new script. No hosting configuration is changed without that evidence.

## Change

The existing `_scripts/check_live.py` now accepts repeatable `--only /registered/route` arguments. It selects entries exclusively from the already-built public release inventory, rejecting unknown or duplicate routes, including any off-origin URL. The original fixed HTTPS origin, same-origin redirect restriction, GET-only requests, HTTP status and byte-equality checks remain unchanged. Without `--only`, the full-site check behaves as before.

Use a complete repository checkout with network access:

```sh
python _scripts/check_live.py --only /downloads/gsc-period-compare.py --attempts 3 --interval 5
```

An exact matching response reports `PASS /downloads/gsc-period-compare.py: HTTP 200; exact release bytes`. A non-200 response or mismatching content reports FAIL. Network errors are inconclusive, not automatically 404s. A `--only` filter limits network requests, but the local inventory still reads generated files from the checked-out repository before selecting routes.

The README and AGENTS.md now explain the scoped command, the fallback interpretation and the separation between publication checks and SEO outcomes. No GitHub Actions, scheduled checks, paid services, data collection or new public-site content were added.

## Tests and limitations

The new `_tests/test_turn28_release_scope.py` contains seven scoped tests for selecting one or multiple routes, preserving byte expectations, rejecting duplicate and unknown/off-origin input, maintaining the default full-scope behavior, verifying CLI wiring and retaining the existing HTTP/body guards.

The seven new tests passed in an isolated repository-shaped fixture. The nine comparator tests and four Turn 27 distribution tests also passed in that fixture: 20 of 20 focused tests. The fixture tested the targeted source excerpt and did **not** contain the entire website checkout. The full site build, historic test suite, browser layout suite and live HTTP-bytes verifier were not run from the model container this turn.

This modification equips a definitive manual check; it does not itself prove custom-domain deployment. Search Console performance and AI-answer citations remain unmeasured because the paid GSC Wizard connector trial has ended and no authenticated owner export was available.

## Exact next acceptance criterion

Run the scoped command from a complete network-enabled checkout. Record the exact result and exit code. Only a successful HTTP 200 with matching expected bytes is a passing live publication result. Investigate any reproducible non-200 status or body mismatch before modifying hosting. Keep source and private Search Console exports separate from public performance claims.
