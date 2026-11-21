# SEO/GEO improvement Turn 38: Live publication verification and priority smoke checks

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Site:** https://nolankido.com/  
**Repository:** https://github.com/nolankido/nolankido.github.io  
**Baseline main:** `0e831bc1aafaf422cb037a5c6783b5aba3a43de6`  
**Roadmap:** Turn 38 of the new 25-turn roadmap (numbered 37 through 61).

## Goal

Check whether the latest public website release is discoverable and served at its expected canonical URLs, especially the books, the 10 BB poker companion and downloads. Repair a release-checking gap if observed. Do not confuse a content-extraction failure, DNS failure, or browser redirect with an observed HTTP 404.

## Live observations: November 20

Independent, non-authenticated, read-only retrievals of the custom domain returned the following **content-level** observations. The content service did not supply HTTP status codes or raw response bytes for successful fetches, so these are **not exact-byte production receipts**.

| Live target | Observation | Limit |
| --- | --- | --- |
| `/` | Retrieved expected Nolan Kido homepage, canonical `https://nolankido.com/` | HTML-extracted, not byte-equal |
| `/about/` | Retrieved profile content with expected self-canonical | HTML-extracted |
| `/technology/` | Retrieved practical AI projects hub with expected self-canonical | HTML-extracted |
| `/ai-in-real-life/` | Retrieved practical AI portfolio with expected self-canonical | HTML-extracted |
| `/books/` | Retrieved newly created author catalog with expected self-canonical | HTML-extracted |
| `/books/one-workflow-at-a-time/` | Retrieved first book page, matching expected canonical | HTML-extracted |
| `/books/how-to-play-no-limit-texas-holdem/` | Retrieved second book page, matching expected canonical | HTML-extracted |
| `/poker/10bb/` | Retrieved 10 BB guide with expected self-canonical | HTML-extracted |
| `/technology/ai-website-visibility/` | Retrieved the website improvement case with expected self-canonical | HTML-extracted |
| `/poker/`, `/contact/` | Retrieved expected pages and canonicals | HTML-extracted |
| `/sitemap.xml` | Retrieved sitemap, reported as 229 URLs | This alone does not prove indexing |
| `/robots.txt` | Retrieved allow rule and main sitemap link | This alone does not prove crawl success |
| `/downloads/one-workflow-ai-pilot-worksheet.md` | Retrieved readable Markdown worksheet | No byte-level verification |
| `/downloads/holdem-river-call-check-worksheet.md` | Retrieved readable Markdown worksheet | No byte-level verification |
| `/downloads/ai-answer-sprint-25-prompts.csv` | Retrieved readable CSV prompt sample | No byte-level verification |
| `/review-no-such-page-20261005/` | Independent retriever explicitly returned `page_not_found`, HTTP 404 | Expected negative control |
| `/_source/site.json` | Independent retriever explicitly returned `page_not_found`, HTTP 404 | Expected source-exclusion control |
| `/downloads/gsc-period-compare.py` | `target_unreachable` in content service; browser displayed blank content or returned to home | **Inconclusive. No observed HTTP status** |
| `/downloads/gsc-download-verify.py` | `target_unreachable` in content service | **Inconclusive. No observed HTTP status** |

A separate browser visit to the comparator was deliberately read-only. Its navigation tool reported visiting the target but did not expose an HTTP response status, response bytes or a reliable content document; the page view became blank or showed the homepage. It cannot establish success, redirect, 404, or a hosting misconfiguration. Do not modify hosting based on that observation alone.

The model's container also returned DNS `Temporary failure in name resolution` for `nolankido.com`, `github.com` and `raw.githubusercontent.com`. Its attempted direct HTTPS checks therefore failed **before HTTP**. It did not observe an HTTP 404 or 200 from the container.

## Improvement implemented

The existing manual diagnostic `_tests/diagnose_live_crawl.py` was preserved as a GET-only, exact expected-byte comparison tool but upgraded in two ways:

1. The *priority* verification scope now covers the complete current author book catalog, both individual books, their original Markdown worksheets, the AI portfolio, 10 BB poker guide, **both** Search Console Python utilities, normal core pages, sitemap/robots and the deliberate 404 negative control. It rejects absent entries from the release inventory rather than silently dropping them.
2. Its JSON verdict now separates `observed_failure_routes` (an actual status or byte mismatch) from `inconclusive_routes` (DNS, transport failure, or an unclassified error). The report preserves the legacy `failed` unresolved count and transport diagnostic details for compatibility.
   - `status=pass`, exit **0**: all selected URLs matched status **and** exact bytes.
   - `status=fail`, exit **1**: at least one observed HTTP/status or byte mismatch, even if other routes are also inconclusive.
   - `status=inconclusive`, exit **2**: one or more unresolved transport-only outcomes and no observed mismatch.

A new `_tests/test_turn38_live_evidence.py` supplies 11 offline regression scenarios, including a full-checkout test that all priority routes are actually registered, and synthetic negative controls for current priority scope, missing registration, HTTP 404 versus DNS, response bytes, retry recovery, mixed outcomes and the intentional 404 route. It is now registered in the local release checklist. `AGENTS.md` gives the exact manual command and the evidence interpretation.

**Complete checkout command (network-capable machine):**

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/build_books.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_turn38_live_evidence.py -v
py -3 _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2
```

The independent comparator-only verifier remains available as `downloads/gsc-download-verify.py`. It can provide a more focused status and SHA-256 receipt where direct network access works.

## Verification limits

- Repository commits, branch sources, and PR diff can be inspected through the authenticated GitHub connection.
- Live page content and canonical metadata were independently retrieved.
- The new Python tests are committed but **not run against a complete checkout in this session**. No claim of passing the full local Python, HTML5 or Playwright suites is made.
- No exact response-byte production comparison has completed for the current entire priority inventory.
- The Python download publication question remains **inconclusive**, not a confirmed site 404.
- No Google Search Console clicks, impressions, indexing, AI citations, or business outcomes have been measured.

## Acceptance debt and next step

If a direct `GET` of the Python files from a network-capable environment returns observed HTTP 404 or bytes not matching the committed source, investigate publishing path and host behavior against that evidence. If only DNS or crawler errors appear, keep the status inconclusive. Do not invent a production outage or weaken exact-byte checks.

**Next roadmap turn:** Turn 39, establish first-party Google and Bing/Umami visibility baselines. The unexecuted full-checkout and exact-byte tests remain a release-qualification item, not a reason to invent evidence or purchase another tracking service.

## Restrictions

No GitHub Actions, hosted CI, cron, paid APIs, new tracking, personal-data export, credential use, or background task was introduced. Existing original article dates, public URLs and metadata were not changed by this turn.
