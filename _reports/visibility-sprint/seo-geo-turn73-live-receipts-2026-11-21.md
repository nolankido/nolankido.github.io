# SEO/GEO Turn 73: per-URL exact-byte release receipts and fresh public content checks

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `d4c2a69fe25e817b46ee6db733f5b0c03fc30cd7` (Turn 72, merged PR #446).
**Scope:** Improve the existing read-only production release diagnostic and investigate the status of recent public reader routes. No new canonical page or additional analytics vendor.

## Decision

Turns 71 and 72 created useful reader routes and expanded strict release coverage, but the available `diagnose_live_crawl.py` output only reported an aggregate passing count and failures. It discarded the identities of successfully verified URLs. Without positive per-route evidence, a release reviewer could not readily say which newly changed page or worksheet was independently checked against current source, especially after mixed pass/inconclusive runs.

**Turn 73 retains a successful exact-byte receipt for each individual verified URL** without weakening the existing fail/inconclusive classification. A full public byte receipt still needs the script to run from a complete matching checkout with direct HTTP access. This tool environment cannot perform that run. No new traffic or ranking lift is asserted.

## New public retrieval evidence

A fresh, read-only external content retrieval with `ttl=0` was performed on November 21, independently of the previous cached search text:

- `https://nolankido.com/start-here/` returned its public main content containing the Turn 71 `start-release-proof` paragraph and link to `/technology/checking-ai-website-changes/`, including the disclaimer about AI speed and rankings. That paragraph was also found in the committed `start-here/index.html` and original source.
- `https://nolankido.com/poker/10bb/` returned the standalone written Playbook's text with its six-check lesson and stated scope.
- `https://nolankido.com/downloads/ten-bb-tournament-checklist.md` returned the readable Markdown sheet headed `Ten Big Blinds: Six-Check Tournament Decision Sheet`.

**Qualification:** The content extraction proves these paths could be retrieved and their expected content was present at inspection time. The extractor does not expose raw HTTP response bytes, a status-bearing GET receipt or a reproducible file-content SHA. Its normalized worksheet text is not the byte stream produced by GitHub Pages. Therefore **none of the above is an exact-byte release pass**. The earlier cached search extraction lacked the Start Here follow-up paragraph; the fresh extraction has it. This is a cache/source-freshness distinction, not proof of a prior deployment outage.

## Changes implemented

1. `_tests/diagnose_live_crawl.py`: retain a `verified_routes` mapping, keyed by URL path, only when `check_live.check()` has compared exact production bytes and confirmed the expected HTTP status. Record expected HTTP status, SHA-256 digest of the identical checked-out source bytes, successful attempt number and verifier result. Keep all previous total, failure, observed mismatch, inconclusive and diagnostics fields intact.
2. Add an optional repeatable `--only /path/` filter for a bounded release receipt. In default priority mode, the selection is restricted to already registered priority paths, whose full registration still must be valid. Duplicate and unknown selections fail closed. `--scope all` can explicitly select other registered public targets. No arbitrary URL fetching is allowed.
3. Add `_tests/test_turn73_live_byte_receipts.py` covering exact 200-byte success, valid expected 404, retry after DNS failure, mixed successful/inconclusive/observed-mismatch outcomes, invalid selections, priority restrictions, and no false positive from unavailable network.
4. Register the static tests in the existing manual `_scripts/local_release_checks.py`, and document the source/production boundary in `AGENTS.md`. No new scheduler, tracking, paid service or Actions workflows.

## Verification scope

| Gate | Status | Evidence boundary |
| --- | --- | --- |
| Start Here Turn 71 link publicly readable | **Observed content-level** | Fresh live text and source copy agree on the evidence route and disclaimer |
| 10 BB Playbook and Markdown worksheet publicly readable | **Observed content-level** | Fresh live read of both named URLs; no raw-byte comparison |
| New `verified_routes` and `--only` behavior | **Source-reviewed** | Authenticated connector readback confirms the exact code paths and registration |
| Synthetic receipt tests | **Authored, not executed** | Test module includes pass, mixed outcomes, retry and negative controls |
| Complete Python build, HTML5, full suite and Playwright | **Not run** | Complete checkout unavailable locally because github.com DNS resolution failed |
| Production status-and-byte checks | **Not run** | Needs matching checkout and status-bearing direct HTTP requests; the new JSON fields cannot substitute for actual execution |
| Search Console Web, Google AI, Bing AI, assistant referrals | **Unavailable** | Missing owner data cannot be reported as zero or ranking growth |

## Acceptance from a full matching checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn73_live_byte_receipts.py -v
py -3 -m unittest discover -s _tests -p test_turn38_live_evidence.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /start-here/ --only /poker/10bb/ --only /downloads/ten-bb-tournament-checklist.md --attempts 2 --interval 2
```

Accept only a returned `status: pass` with every requested route present under `verified_routes`. The `source_sha256` value is trustworthy as a live receipt only because `check_live.check` has first established exact response-body equality. A source hash by itself is not deployment proof. A DNS-only run must return `inconclusive` and leave `verified_routes` empty. The default `--scope priority` without `--only` retains full priority coverage.

## Sprint handoff

Publication discoverability and reader-specific verification have advanced. The original 25-turn and Turns 37–61 completion counts remain historical. **Still open:** complete executable current-source checks, browser/mobile user journeys, exact public-byte verification, measured performance, first-party Google and Bing search observations and sampled assistant-panel citations. The first complete possible post-sprint calendar month is December 2026 and has not yet occurred. No ranking increase, AI-citation gain or client/business outcome has been measured by this change.

**Next valuable turn:** execute the priority exact-byte receipt from a network-capable checkout; repair an actual mismatch if observed; then use free owner-private Search Console exports to prioritize one measured query/page improvement rather than adding duplicate article content.
