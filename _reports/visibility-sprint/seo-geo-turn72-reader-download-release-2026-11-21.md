# SEO/GEO Turn 72: make three reader journeys and all claimed downloads release-verifiable

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `24134d25ac9cb9077487d16d8eb10998331b6949` (Turn 71, PR #445)
**Scope:** Existing canonical pages and their release verification. No additional article or invented search evidence.

## Verified release-check gap

The public `/poker/10bb/` standalone written guide links a free six-check Markdown worksheet at `/downloads/ten-bb-tournament-checklist.md`, as well as its exact-fraction Python checker. The read-only production-byte inventory in `_scripts/check_live.py` registered the Python checker but **did not register that Markdown worksheet**. Thus a matching Playbook HTML release and registered checker could pass without verifying the exact worksheet bytes readers actually receive. The source file exists, so this is a coverage failure, not evidence of a broken production URL.

Turn 71 added a direct reader link from `/start-here/` to the historical AI website repair and authored a five-route 320 px layout test, but it did not test actual three-step keyboard/download journeys. The existing priority production diagnostic also omitted the recent Start Here link and the three worksheet destinations.

## Implemented this turn

1. Introduce `WORKSHEET` into the existing `tenbb_companion` owner registration. Fail closed if the worksheet file is missing or the written guide no longer links to it. Preserve the 10 BB guide's canonical URL, its original publication date, source methods and ICM calculations.
2. Add `downloads/ten-bb-tournament-checklist.md` to `_scripts/check_live.py` as a fixed public expected 200-byte target, beside the already registered ICM Python download.
3. Extend the existing `_tests/diagnose_live_crawl.py` priority scope with `/start-here/`, the actual AI repair case, the dated visibility evidence case, the AI workflow pilot, the AI repair checklist, the 10 BB worksheet and its Python checker. Existing exact-byte classification still separates observed HTTP/byte failures from inconclusive transport errors.
4. Add `_tests/visibility_three_reader_journeys_browser.py` for offline, keyboard-only navigation on Home and Start Here to the independently source-checked AI repair and its downloadable runbook; Books catalog to `One Workflow at a Time` and the free worksheet; Poker hub to the written 10 BB guide and six-check worksheet. It checks 320, 390 and 1440 CSS pixel widths, with JavaScript both disabled and enabled, using a local-only HTTP server, actual checked-in assets, download-completion events and exact local resource bytes. All non-loopback browser requests are blocked.
5. Add `test_turn72_reader_release_coverage.py` regression and negative-control cases; update the original Turn 38 priority contract, register the new static module with the existing manual runner and document source boundaries in AGENTS.md. The browser file is opt-in through the preexisting `*_browser.py` discovery with `--browser`.

## Verification evidence

| Gate | Status | Evidence / limit |
| --- | --- | --- |
| Playbook worksheet link and actual file | Confirmed in authenticated GitHub source | Written guide links to `/downloads/ten-bb-tournament-checklist.md`; the asset is present in the public repository |
| Previous release coverage gap | Confirmed | Before this turn `_scripts/check_live.py` contained the Python checker but zero occurrences of the worksheet path |
| New required worksheet, production target and priority routes | Static code verified | Source changes add fail-closed file/link checks and exact-byte expectations; execution remains outstanding |
| Three actual browser journeys | Authored, not run against repo | Script exercises keyboard focus, Enter navigation, native download event, HTTP 200 and local byte equality |
| Isolated Chromium loopback probe in this execution environment | Blocked | The sandbox reported `net::ERR_BLOCKED_BY_ADMINISTRATOR` at 127.0.0.1. This is not a website error or a passing browser test |
| Current-source unit/build/search/HTML5 test suite | Not run | A complete checkout is unavailable from this container owing to external DNS failure |
| Live HTTP exact bytes for the changed destinations | Not run | A merged commit or a stale/cached public text view is not a status-bearing byte receipt |
| Google Search Console Web, Google AI, Bing AI and assistant referrals | Unavailable | No authenticated settled export; do not invent numbers or classify missing as zero |

## Required full-checkout acceptance

From the current merged branch in a network-capable Windows/Python environment with installed Playwright/Chromium:

```powershell
py -3 -m unittest discover -s _tests -p test_turn72_reader_release_coverage.py -v
py -3 -m unittest discover -s _tests -p test_turn38_live_evidence.py -v
py -3 -m unittest discover -s _tests -p test_turn52_10bb_playbook.py -v
py -3 _tests/visibility_three_reader_journeys_browser.py
py -3 _tests/visibility_core_journeys_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2
```

A pass in the local three-journey browser script does **not** prove a matching production release. The last command makes actual public GETs and must report `pass`, `fail`, or `inconclusive` from the latest checked-out source. The updated priority audit tests public worksheets as well as HTML. Investigate real failures; never suppress them or enable GitHub Actions.

## Sprint position after Turn 72

**Advanced:** release and navigation coverage, source-backed educational downloads, three separate practical visitor tasks. **Still open:** verified complete local release run, mobile Chromium checks on the current site, actual matching live bytes, first-party search data and frozen assistant panel measurements, measured performance, and verified retail editions. The unchanged 230-URL sitemap remains a source/publication inventory, not indexing or search traffic. December 2026 remains the first full potential post-sprint month, not yet measurable on this date.

**Next high-value turn:** execute or unblock actual current-source release/browser tests, remediate any observed failure, then collect no-cost owner-private search query/page exports. Do not add generic pages or another automated schedule just to advance a turn number.
