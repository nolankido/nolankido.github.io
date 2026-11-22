# SEO/GEO Turn 82: verify recent public content and make deployment waiting explicit

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `fd2da70e4014546cf5c738aad07fda98ea26abc3` (Turn 81, PR #455).
**Scope:** Release diagnostics and a dated evidence receipt. No public article, worksheet, sitemap, schema, JS, CSS or metadata is changed.

## The production question that motivated this turn

Turn 81's merged GitHub source contained an expanded 10 BB Markdown worksheet, but the first two public text retrievals immediately afterward still showed the earlier, shorter sheet, even when a query parameter was appended. That was an observed source-versus-public-content difference at the time of retrieval. It was **not** proof of an HTTP 404, a failed GitHub Pages deployment or a permanent serving error. Source-only checks, search crawls and stale cached text must not be described as exact deployment receipts.

## What later public retrieval now establishes

Fresh public, cache-busted, content-level retrieval of `https://nolankido.com/downloads/ten-bb-tournament-checklist.md?release-check=turn82-20261121-1` returned the new section **Reproduce the prize-value comparison**, the exact `$1696/21` call-win prize value and the `55%` sensitivity answer `$62.42`. The earlier old-sheet extraction was about 2,789 characters; the new text extraction is about 6,220 characters. These are extractor text lengths, not original response byte counts or a download-performance measurement.

A second fresh, independent read across three public routes returned:

| Route | New release marker observed in retrieved content | What is and is not confirmed |
| --- | --- | --- |
| `/about/` | **Original poker instruction, separate from tournament results** | Turn 80's new evidence links are content-retrievable; not a mobile or source-byte check |
| `/poker/free-poker-learning-path/` | **After the basics** and **Written 10 BB Playbook** | Turn 79's native course completion bridge is content-retrievable; no 320px interaction executed |
| `/downloads/ten-bb-tournament-checklist.md` | **Reproduce the prize-value comparison**, `$1696/21`, `$62.42` | Turn 81's expanded Markdown content is retrievable; no status-bearing byte comparison |

GitHub reports three successful internal Pages check runs on Turn 81's merge commit: `build` completed **2026-11-22T08:13:08Z**, `report-build-status` **08:13:15Z**, and `deploy` **08:13:24Z**. Their run details are linked in GitHub at `https://github.com/nolankido/nolankido.github.io/actions/runs/45001734400`. These checks establish GitHub's build/deploy job outcomes, **not** that every CDN edge immediately served each file. No repository-authored `.github/workflows` files were added in this turn.

The old result followed by the new result is consistent with transient publication or cache lag. Its cause is **not established**. Do not assign a Cloudflare, GitHub Pages or extractor fault without an actual status/headers/edge trace.

## Bounded code improvement

1. Expand the existing manually invoked `_tests/diagnose_live_crawl.py` argument bounds from **1 to 4 attempts** and **0 to 10 seconds** to **1 to 8 attempts** and **0 to 30 seconds**. Keep the original fast defaults at **2 attempts, 2 seconds, 2 workers**. Maximum configured wait between attempts is **7 × 30 = 210 seconds**, plus bounded public GET time.
2. Make the diagnostic JSON record `attempts_configured`, `attempts_used` and `retry_interval_seconds`. The existing `verified_routes` still records only actual status-bearing exact-byte passes, with the expected HTTP status, matching checked-out source SHA-256 and the precise `verified_attempt`.
3. Preserve the three outcome classifications. A byte mismatch after the last check is a **fail**, a DNS/TLS/timeout failure is **inconclusive**, and a later true exact-byte match is a **pass at that later attempt**. Never infer that an earlier mismatch was necessarily caused by deployment propagation.
4. Add nine synthetic regression methods in `_tests/test_turn82_publication_retry_window.py`, covering successive stale responses followed by success, persistent mismatch, persistent DNS failure, selective retry, original defaults, extended CLI configuration, bounded rejection of impossible parameters, explicit scoped results, and the existing manual-runner/no-workflow policy. Register in `_scripts/local_release_checks.py` and document limits in `AGENTS.md`.

## Verification evidence and limits

| Gate | Result | Evidence |
| --- | --- | --- |
| Turn 81 content visible in public extraction | **Pass, content-level** | Two fresh text retrievals, one of them across multiple routes |
| Turn 79 and Turn 80 visible markers | **Pass, content-level** | Fresh course/About text retrieval with release-check query parameters |
| Turn 81 GitHub Pages build/deploy check runs | **Success** | Authenticated GitHub commit check-run records, UTC timestamps above |
| New retry CLI defaults/ceilings and receipt fields | **Committed in branch** | Authenticated source comparison after changes |
| New mock-response regressions | **Nine tests authored** | Not yet executed from a complete repository checkout |
| Full current-source builder, HTML5, all Python tests, browser 320px | **Not run** | Container cannot resolve `github.com`, preventing a complete checkout; previously available browser could not set exact 320px width |
| Status-bearing raw public bytes and headers | **Not acquired** | Text extraction is normalized; no actual verified-route JSON yet |
| Google/Bing queries, impressions or AI citations | **Unavailable** | GSC Wizard trial expired; no subscription enabled and missing is not zero |

## Manual acceptance and a useful long-window command

```powershell
py -3 -m unittest discover -s _tests -p test_turn82_publication_retry_window.py -v
py -3 -m unittest discover -s _tests -p test_turn73_live_byte_receipts.py -v
py -3 -m unittest discover -s _tests -p test_turn38_live_evidence.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /downloads/ten-bb-tournament-checklist.md --attempts 8 --interval 15 --workers 1
```

That final command is a **selected-route** public exact-byte release diagnostic, not a complete site audit. Its maximum configured sleep window is seven intervals of 15 seconds, 105 seconds, plus the duration of public GETs. Run the default priority scope and the `--scope all` audit separately when validating a full release. Once executed, archive the actual JSON and distinguish any inconclusive network result from a byte mismatch. Do not change the authoring repository solely to force a matching hash.

## Sprint assessment

**Resolved:** the immediate concern that Turn 81's expanded worksheet was not publicly retrievable. Content now appears on the live website and the corresponding Pages deployment checks succeeded.

**Advanced:** the existing public-byte diagnostic can now wait through a deliberately configured, bounded publication window and reports how many attempts were used. This improves release evidence without increasing the number of articles or adding background monitoring.

**Still open:** true matching source-to-response byte receipts across all priority routes, a full runnable local release check, 320px usability and performance checks, authenticated Google/Bing/AI search observations and independent book-retailer edition verification.

**Next priority:** execute the new diagnostic with a matching checkout and network access. If the response is stable and exactly matches the current source, retain the real receipt. Then focus the next content turn on measured query-page opportunities rather than adding more unmeasured SEO copy.
