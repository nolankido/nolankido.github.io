# SEO/GEO Turn 63: protect four public HTML study downloads in the HTML5 release gate

**Date:** November 21, 2026 (Pacific/Honolulu)  
**Base main:** `592e82ce23371965059b7368512a7266b95685d3` (merged Turn 62, PR #436)  
**Type:** Release assurance and learner-tool reliability. No visitor-facing content, canonical URL, sitemap entry, publication date, schema, analytics, or crawler directive changes.

## Confirmed coverage gap

Turn 62 added the separately authored `/poker/10bb/` page to the standard HTML5 inventory. A further read-only review of `_scripts/check_live.py` and `_tests/check_html5.py` found **four public, browser-facing HTML downloads** registered as exact-byte live targets but missing from the parser inventory.

| Registered HTML download | What it supports | Committed bytes at base | Existing robots directive |
| --- | --- | ---: | --- |
| `/downloads/poker-hand-review-practice-01.html` | Printable online hand-review practice | 12,899 | `noindex,follow` |
| `/downloads/poker-hand-review-practice-01-key.html` | Companion answer and reasoning key | 18,194 | `noindex,follow` |
| `/downloads/nolanpoker-local-video-qa.html` | Private local current-cut audio/video QA interface | 46,286 | `noindex,nofollow` |
| `/downloads/nolanpoker-public-youtube-review.html` | Public-video review worksheet/interface | 24,256 | `noindex,nofollow` |

All four are complete HTML documents with a doctype, head, body and main element, not arbitrary data attachments. The two video QA utilities contain browser scripts, so a syntactic HTML regression could affect genuine users even when the canonicals remain fine.

Previously, `_tests/check_html5.py` enumerated 225 manifest pages plus ten standalone page files, but not these four downloaded HTML documents. Its normal release gate could pass without parsing them.

## Implemented correction

1. Add `public_html_download_paths(root)` to `_tests/check_html5.py`. It derives downloads directly from the existing independent `check_live.targets(root)` inventory, not a second manually maintained list.
2. Reject invalid inventory status, path traversal, missing files, mismatch between release-registered bytes and on-disk bytes, and a purported HTML download without a document doctype.
3. Parse every registered `/downloads/*.html` document using the **same html5lib HTML5 parser** already required for public pages. Reject collisions with canonical page routes. Report canonical-page, download, and combined-document counts separately.
4. Add focused `_tests/test_turn63_public_html_downloads.py` coverage for the four known downloads, noindex policy, their exclusion from the sitemap, HTML5 parsing, an extra-closing-tag negative test, malformed/missing/non-HTML/mismatched file rejection, path-traversal rejection and default manual release-runner registration.
5. Register the new focused test in `_scripts/local_release_checks.py` and document the extra coverage in `AGENTS.md`. No GitHub Actions, paid service, automated schedule or visitor tracker was added.

**Expected local HTML5 validation inventory after this code change:** 235 canonical/utility site HTML documents (225 manifest-backed + ten other standalone) plus four downloadable noindex HTML documents, for **239 document paths total**. This is an intended scope, **not a claim that 239 documents have already passed the parser**. The four downloads are not made indexable and are not added to the sitemap.

## Scope of evidence actually inspected

- Base GitHub `main` confirmed at `592e82ce23371965059b7368512a7266b95685d3` before editing.
- Complete current `_scripts/check_live.py` code showed the four named HTML downloads in its fixed asset inventory.
- Complete current `_tests/check_html5.py` omitted downloadable HTML altogether.
- All four public files were fetched from GitHub through the authenticated connector and inspected. The minimal lexical preflight detected the existing doctypes, preserved robots meta, and matched opening/closing counts and nesting for common block-level tags after excluding script/style text. It reported **no block-level nesting discrepancy in this narrow scan**. This is **not** a successful HTML5 parse.
- A fresh read-only public content retrieval **successfully extracted all four live download pages** at their exact URLs and reported their matching original noindex policies. This confirms content-level reachability for these four files, but the extractor did not provide response status codes or raw bytes, so **HTTP/byte-exact release verification remains unproven**. A different prior attempt to read Python code downloads was inconclusive and is not used as evidence about these HTML files.
- There are no observed Search Console, AI citation, Bing AI or Umami changes attributable to this repository-only release hardening.

## Execution status and risks

**Completed:** source-level coverage analysis, exact bounded code changes, test declarations, GitHub branch review and documented verification steps.

**Not run:** the local Python `unittest` modules, strict HTML5 parser run, deterministic generator, full historical suite, browser QA or exact-byte network checker. The local execution container again failed DNS lookup of `github.com`; `html5lib` is not available there. Because the four documents have never been included in this HTML5 gate before, the first real execution may surface preexisting errors requiring a follow-up repair. Do not call that gate passed before executing it.

### Complete-checkout verification

On a network-capable checked-out copy of the current merged commit, with `requirements-test.txt` installed:

```powershell
py -3 -m unittest discover -s _tests -p test_turn63_public_html_downloads.py -v
py -3 -m unittest discover -s _tests -p test_turn62_html5_tenbb.py -v
py -3 -m unittest discover -s _tests -p test_turn34_release_integrity.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/build.py --check
py -3 _scripts/build_books.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2
```

The standalone HTML5 command should report `pages: 235`, `html_downloads: 4` and `html_documents: 239` **if the inventory remains unchanged**, plus `status: pass` only after a real successful parse. Those numbers are expectations, not measured results from this session.

## Next priority

Complete the current-source local release gate and fix any genuine parser or browser issue it reveals. When the execution environment cannot access a full checkout, report the blocker without mislabeling tests as passes. After a verified release, proceed to authenticated first-party search metrics and three reader-journey tests, rather than generating more speculative search pages.

**Relevant sources:** [Turn 61 evidence scorecard](seo-geo-turn61-release-and-evidence-scorecard-2026-11-20.md), [Turn 62 HTML5 Playbook fix](seo-geo-turn62-html5-tenbb-coverage-2026-11-20.md), `_scripts/check_live.py`, `_tests/check_html5.py`, `_scripts/local_release_checks.py`.
