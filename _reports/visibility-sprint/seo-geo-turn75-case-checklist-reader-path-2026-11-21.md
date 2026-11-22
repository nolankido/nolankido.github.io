# SEO/GEO Turn 75: put the proven AI-release checklist on the reader's evidence path

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting `main`:** `6451e26c7a1a241eab7a61282d6e39f8f7531e75` (Turn 74, PR #448).
**Affected canonical:** https://nolankido.com/technology/checking-ai-website-changes/
**Goal:** Make an already published, source-backed practical AI artifact directly reachable near the top of its own flagship case without a new page or fabricated performance claim.

## Reader problem found

Turn 71 linked Start Here directly to the real website-repair case and promised a free release checklist. The destination case's reusable Markdown runbook was linked only near the end of the full document, **12,769 characters into the 13,032-character source**, about 98% through the article body. The top evidence note instead linked the pre-repair code, repaired code, an archived test record, and a parser reproduction. The existing runbook was published and independently registered for exact-byte release checking, so this was a visibility/wayfinding problem, not a missing asset or unsupported claim.

## Change implemented

1. Move the **existing** paragraph containing `/downloads/website-check-offline-runbook.md` from the bottom of the `#case-source-diff` section to directly after the pinned early original-repair evidence note, before the article's `entry-jumps` navigation.
2. Add only the scoped presentational class `small-copy case-checklist-early` on that moved paragraph, reusing existing styles. Retain its original words, `download` attribute, free file destination and explicit limitations. No new call to AI, client outcome, test count, article section, schema, sitemap URL or link target.
3. Make the identical move in `_source/technology/checking-ai-website-changes.html` and committed output `technology/checking-ai-website-changes/index.html`, leaving the pinned proof paragraph completely untouched.
4. Add seven local static/negative-control regressions in `_tests/test_turn75_early_case_checklist.py`, integrate them with the existing manual release runner and add a source ownership note to AGENTS.md.

## Source-level verification completed

| Evidence | Before | Updated branch |
| --- | --- | --- |
| Runbook link in 13,032-character case body | Character 12,769, ~98% through | Character 1,630, ~12% through |
| Number of runbook links on case | 1 | 1 |
| Position | In final pinned-source section | Immediately after early source proof, before navigation |
| Original pinned source proof | Intact | Byte-identical |
| Source and published early paragraph | Not early | Exact matching markup on both |
| Case source content words | 1,336 via simple HTML-strip count | 1,336, unchanged |
| Major headings / canonical / publication-date copy | Existing | Unchanged |
| Reported reading estimate | About 6 min | Still about 6 min |

The 1,336-word count is a simple source-text comparison used solely to show this is a **relocation**, not a rewritten article. It is not an independently timed reading study. Source and rendered page have different character positions because rendered HTML includes the shell, metadata and other generated navigation. One live public visitor still needs to fetch the deployed update before we can claim that the early link is serving from production.

## Validation limitations

**Completed:** GitHub main/branch source comparison, existence of original published runbook, source/public paragraph equality, exactly one retained download route, early placement, heading count and pinned evidence consistency. Authenticated GitHub PR and commit evidence is recorded.

**Not executed:** The complete local deterministic builder, full Python/unittest suite, HTML5 parser, Playwright 320 px and keyboard study, status-bearing exact-byte public release verifier. The current container could not resolve `github.com` for a complete checkout. Existing tests authored here are not represented as passing. A GitHub merge is not itself a deployment receipt.

**Search outcomes unchanged:** Google Search clicks/impressions, AI feature visibility, Bing AI citations, assistant referrals and actual user completion were not measured. Do not claim the moved link improved rankings or conversions. November remains a mixed release month; the first fully post-release calendar period will be December 2026, after it ends and data settle.

## Required next checks

```powershell
py -3 -m unittest discover -s _tests -p test_turn75_early_case_checklist.py -v
py -3 -m unittest discover -s _tests -p test_turn42_repair_proof_path.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /technology/checking-ai-website-changes/ --only /downloads/website-check-offline-runbook.md --attempts 2 --interval 2
```

After deployment, a fresh noncached retrieval of the public case can confirm **content-level publication**, while only the status-bearing exact-byte checker can verify checked-out-source-to-live parity.

## Sprint status and handoff

**Advanced:** A first-time practical AI reader now has a more direct route to inspectable, reproducible work; no duplication or misleading outcome claims were introduced. The original 37–61 sprint and Turns 62–74 have already delivered substantial site structure, case evidence, book/poker discovery and release safeguards.

**Still open:** Executable full current-source release checks, narrow/mobile reader journeys, actual source-to-live byte parity, authenticated owner-private first-party search metrics, frozen assistant citation panel, measured performance, and verification of book retail editions.

**Next meaningful turn:** Prioritize an actual executable release and 320 px visitor completion check; after that, use real Search Console query/page data to select a controlled on-page improvement rather than publishing more generic content.
