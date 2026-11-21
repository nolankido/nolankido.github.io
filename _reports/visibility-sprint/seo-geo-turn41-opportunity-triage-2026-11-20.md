# SEO/GEO Turn 41: Evidence-ranked search opportunities and one verified reader-path fix

**Site:** https://nolankido.com/  
**Date:** November 20, 2026 (Pacific/Honolulu)  
**Starting main commit:** `1293493711ad4643eb84c6d8f76232c36b868303`  
**Roadmap position:** Turn 41 of Turns 37 through 61.

## Executive finding

The previous Turns 37 to 40 strengthened technical release auditing, private search-performance intake and a reproducible assistant-answer citation panel. They did **not** produce actual first-party Google/Bing rankings, impressions, clicks or an eligible completed 25-question assistant-answer panel. There is no defensible basis for ranking content by traffic, query frequency, CTR, citation rate or observed uplift in this turn.

What *can* be ranked today is the site's **editorial improvement opportunity**: a known user task, a distinctive existing canonical page, the strength and limitations of available public evidence, a source-verifiable reader-path weakness and the cost/risk of correcting it. This turns the new sprint toward quality and reader success instead of adding more measurement tooling or speculative keyword pages.

## Evidence inspected

1. `_reports/visibility-sprint/seo-geo-turn04-query-opportunity-map-2026-11-17.md` listed twelve hypothetical reader intents and distinct destinations.
2. `_reports/visibility-sprint/seo-geo-turn05-30-page-quality-audit-2026-11-17.md` reported thirty directly fetched pages and a bounded editorial assessment, with a few historic improvement candidates. Its search-demand measures were unavailable.
3. `_reports/visibility-sprint/seo-geo-turn11-technology-reader-paths-2026-11-18.md` shipped the Technology hub's eight task routes. Do not duplicate them just to add content.
4. Turn 40's single public Perplexity answer pilot used an unconfirmed exact version of frozen NB01, so it is excluded from any benchmark denominator. It is a qualitative topic signal, **not** a 0% provider citation rate.
5. The current `main` source and deployed HTML were inspected for key practical AI, project, poker and author pages. All **twelve chosen pages** are existing published HTML targets in the GitHub tree. External page retrieval confirmed that the first-live guide and its hand-flow/ranking prerequisites were each accessible on their canonical paths.
6. The first-live source still lacked direct `/poker/holdem-basics/` and `/poker/hand-rankings/` links, exactly the narrow reader-path weakness noted in the earlier Turn 05 audit. Another historical issue, the initial duplicate H1/H2 label in the six-to-ten-BB guide, had already been corrected by later work, so it is **not** reopened.

These are source/content observations, not public search-engine performance or a user study. A route in `sitemap.xml` or a successful content fetch does not prove indexing or recommendation.

## Ranked opportunities: editorial judgment, not measured demand

See the accompanying [canonical, 12-row machine-readable ledger](seo-geo-turn41-priority-ledger-2026-11-20.csv). The ledger contains no invented click/impression/citation values. The order prioritizes *original evidence*, *useful reader tasks*, *clarity of proof*, *low-risk source improvements*, and the stated focus on Nolan Kido's practical AI expertise.

| Editorial rank | Destination | Why it matters | Specific next decision |
| ---: | --- | --- | --- |
| 1 | `/technology/checking-ai-website-changes/` | First-person, source-checkable website defect and independent repair evidence | Make the verified source, failing case, corrected result and limits exceptionally easy to inspect, preserving actual record |
| 2 | `/technology/check-ai-answers/` | Direct answers, independent checks and source-backed educational examples | Protect original checklist; improve only on a verified reader or citation issue, not an incomplete pilot |
| 3 | `/technology/local-ai-review-replies/` | Bounded review-reply trials with owner approval and real evidence limitations | Test cold-reader route to rejection/approval details before rewriting |
| 4 | `/technology/ai-time-savings/` | Existing real calculator with clear fictional examples and complete-cost method | Verify worked math and first-screen output rather than claim unmeasured AI productivity |
| 5 | `/poker/first-live-tournament/` | High-intent beginner task and previously confirmed missing direct prerequisites | **Shipped** a contextual rules-and-hand-ranking link pair |
| 6 | `/poker/six-to-ten-bb-tournament-decisions/` | Distinct ICM teaching, bounded recorded hand and original math | Preserve prize-equity versus chip-odds context and solver limits |
| 7 | `/projects/` | Connects person's claimed competence to inspectable artifacts | Inspect evidence clicks rather than fabricate product adoption |
| 8 | `/about/` | Source-linked person identity, research publication and projects | Check public-profile identity consistency, no invented endorsements |
| 9 | `/technology/local-ai-gaming-laptop/` | Practical local-model setup with honesty about which tests were on which hardware | Wait for a same-device real comparison before publishing performance claims |
| 10 | `/technology/ai-book-continuity-checker/` | Source-linked archived editorial report with false positives as well as findings | Keep claim to passage to decision path concise |
| 11 | `/poker/poker-math/` | Checkable numerical examples for a common beginner task | Preserve verified calculation and reading clarity |
| 12 | `/poker/episodes/portland-meadows-ep1/` | Distinctive firsthand public tournament experience | Keep retrospect, sourced arithmetic, and video cut separate |

A lower rank here does **not** mean less Google demand or less traffic. Actual measured search activity may reorder these priorities when valid account data become available.

## Actual user-visible improvement

**Confirmed gap:** `_source/poker/first-live-tournament.html` already offered a broader Getting Started guide but did not directly link a novice to hand order/positions or hand rankings. Both real target guides exist and resolve under the same site.

**Changed source:** `_source/poker/first-live-tournament.html`  
**Changed published output:** `poker/first-live-tournament/index.html`

Extended one short existing paragraph after the first-outing six-step plan. It now directly links:

- `/poker/holdem-basics/` as an accessible walk-through of a complete hand, positions and blinds.
- `/poker/hand-rankings/` as the standard hand-ranking primer.

It explicitly says these are **before-play, off-table** learning links, not help during a tournament hand. The guide's original October 8 article publication date and meaningful October 27 modification date remain unchanged, because this is a narrow contextual navigation addition rather than a substantive article revision. Canonical URL, metadata, guide plan, external rules references, original source caveats, author identity and the sitemap URL inventory are unchanged. No new SEO article was created.

This release addresses one verified friction point; it does **not** establish that an actual reader clicked or benefited from the links.

## Verification and limits

- Both new links were applied as one identical paragraph replacement to the editable source and committed rendered HTML. The old paragraph occurred once in each.
- A Git tree review confirmed all twelve ranked destinations have a committed published HTML target. The two intended prerequisite pages also have existing canonical routes.
- Added `_tests/test_turn41_evidence_opportunities.py` with six source-level regressions for unique editorial ranks and source fields, all twelve sitemap/canonical routes, exactly-one contextual prerequisite link per destination, unchanged original article dates, the already shipped fix recorded in the ledger, and the no-GitHub-Actions rule.
- Registered the tests in `_scripts/local_release_checks.py`.
- Updated `_reports/visibility-sprint/query-map.md` to refer to the new follow-on evidence-ranked ledger rather than replacing the original November 17 hypotheses.

**Execution boundary:** The complete repository checkout could not be obtained in this execution environment because `github.com` DNS failed. The full static rebuild, full HTML5 parser, entire unit suite, Playwright mobile checks and public exact-byte comparison were **not run**. Static Git source and generated text were inspected, but do not substitute that for a passing complete `python _scripts/build.py --check`.

From a complete local checkout, run:

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_turn41_evidence_opportunities.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /poker/first-live-tournament/ --attempts 3 --interval 5
```

A mismatching generated page or canonical must be repaired rather than described as a passed release. Search Console/Bing/Umami actual metrics remain **unavailable**, not measured as zero. The case of an assistant citing another source is not proof of zero site citations.

## Next improvement

**Turn 42:** Strengthen the first-ranked, original AI-assisted website repair case. Concentrate on a simple reader path from problem to original source to independent failing test to corrected output, with exact public links and honest limits. Do not invent time savings, SEO traffic, AI citation success, testimonials, or code tests that were never run.

No GitHub Actions, cron, new tracker, paid API, private analytics or unverified case outcome was introduced.
