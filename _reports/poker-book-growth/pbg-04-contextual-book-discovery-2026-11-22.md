# PBG-04: Contextual poker-book links from free learning resources

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Sprint:** Poker Book Growth, Turn 04 of 25  
**Canonical book:** https://nolankido.com/books/how-to-play-no-limit-texas-holdem/  
**Retail link, supplied by author:** https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324  
**Result:** Six real contextual links committed and visible on live pages. Selected 11-route baseline changes from 3 pages with exact book links to 9.

## Why this improvement

The PBG-02 frozen cohort identified 11 existing poker learning pages, but only three had an exact unfragmented link to the book's canonical author page. The existing book landing page already offers the verified author-supplied Amazon href and a free sample decision. The missing stage was connecting learners who had just completed relevant instruction to that page without interrupting the free instruction.

The changes below are specifically written for each subject. They are optional and disclose that the book is the site's author's own work. No article pretends to be an independent review or requires a purchase to use its examples or worksheets.

## Source/public changes, exactly six routes

| Source route | Exact position of the added link | Reader-relevant purpose |
| --- | --- | --- |
| `/poker/free-poker-learning-path/` | After the six core lessons and before optional later study | Optional full-book path with a free book-page example, explicitly preserving all six free lessons |
| `/poker/holdem-basics/` | After the fictional deal-to-showdown explanation, before references | Connect beginner rules to position and optional further learning |
| `/poker/starting-hand-decisions/` | After the original eight scenarios and the short private study template, before sources | Optional preflop/position follow-up |
| `/poker/betting-and-pots/` | After the call/raise/side-pot examples, before references | Connect betting mechanics to ranges and pot prices |
| `/poker/beginner-practice/` | After the interactive practice and its free follow-up, before source notes | Optional continued reading, explicitly distinguishing full free drills from retail content |
| `/poker/poker-math-reference/` | After explanatory questions and before the outside-source directory | Connect pot odds to the book's original free river-call example |

Each addition is exactly one native `<a href="/books/how-to-play-no-limit-texas-holdem/">` within a single `<p class="poker-book-bridge">`. There are no Amazon external links in these articles and no new Umami events. The destination page owns the author's Kindle link and its existing `poker-book-kindle-amazon-click` event.

The following source and public pairs were updated:

- `_source/poker/free-poker-learning-path.html` and `poker/free-poker-learning-path/index.html`
- `_source/poker/holdem-basics.html` and `poker/holdem-basics/index.html`
- `_source/poker/starting-hand-decisions.html` and `poker/starting-hand-decisions/index.html`
- `_source/poker/betting-and-pots.html` and `poker/betting-and-pots/index.html`
- `_source/poker/beginner-practice.html` and `poker/beginner-practice/index.html`
- `_source/poker/poker-math-reference.html` and `poker/poker-math-reference/index.html`

All six pages retain their existing article content, guide navigation, fictional calculations, free worksheets and primary task routes. Their existing canonical URLs, publication/revision dates, layout, scripts and global CSS were not changed. No false freshness date was added for a bounded optional navigational link.

## Before/after cohort

The original [PBG-02 11-route snapshot](pbg-02-acquisition-route-baseline.json) remains intact. A separate [post-change route snapshot](pbg-04-contextual-link-coverage.json) records the same denominator and current HTML blob SHAs.

| Measure | Before | After |
| --- | ---: | ---: |
| Selected existing poker pages audited | 11 | 11 |
| Pages with at least one exact direct link to the book page | 3 | **9** |
| Pages with no such exact direct link | 8 | **2** |
| Newly linked pages from this turn | 0 | **6** |

The two remaining pages, `/poker/library/` and `/poker/study/`, are deliberately not changed by this turn. Their broad resource-discovery role is different from a beginner lesson and adding a generic promotion without relevance or user evidence could distract from their primary task. They can be reconsidered later if the data supports it.

Counts are **source-only navigational coverage**, not search impressions, visits, clicks, conversions, citations, Amazon product availability or sales.

## Special build-integrity adjustment

The first wording pass was longer. A source-versus-generated reading-time audit identified a risk that a few pages could cross the 225-words-per-minute editorial estimate boundary. We shortened four optional link paragraphs to keep the added copy light, preserve meaningful reader context and avoid unnecessary regeneration of library cards or reading-time headings.

This is a conservative source-level check, not a complete deterministic build check. Any run of `_scripts/build.py --check` still needs a full matching checkout and should be considered the final authority on generated reading estimates.

## Regression protection

Added `_tests/test_pbg04_poker_book_contextual_links.py` with 10 offline test methods and registered it under `_scripts/local_release_checks.py`. Tests protect:

1. Exactly one book link and exactly matching new paragraph in each source/public pair.
2. Native, same-site navigation with no direct Amazon links, added analytics attributes, misleading review/ranking language or fabricated outcomes.
3. Poker Foundations keeps the six-stage course before the optional continuation.
4. The other five book links follow relevant subject instruction and precede reference/help sections.
5. Free practice, preflop examples, pot/raise instruction, math reference and downloads remain accessible.
6. The Kindle ASIN and its single destination-page event are unchanged.
7. PBG-02's frozen 11-page sample remains comparable to PBG-04's exactly 9 linked pages.
8. Unobserved Google search, AI citation, Amazon-click and KDP outcomes remain JSON `null`.
9. Manual release runner includes the test and the owner prohibition on GitHub Actions is preserved.
10. The author page canonical and free exercise anchor are real.

## Verification actually done

- Read back all 12 modified source/public files after final edits; passed **47 static assertions** covering exact paragraph match, one direct link, first-party disclosure, absence of intrusive tracking and retention of original guidance anchors.
- Re-fetched all 11 selected public HTML repository paths and recorded **9 linked / 2 unlinked** plus current blob SHAs in the frozen after snapshot.
- Public page extraction after publication found the exact canonical book link on **all six** changed live URLs. This supports live navigational availability, not source-byte parity or search indexing.
- Read the book destination and retained author-provided ASIN `B0HSB98324` from prior sprint checks. No retailer-side purchase, price or format verification was performed in this turn.

**Not executed here:** full local Python suite, `_scripts/build.py --check`, full HTML5 and internal-link checks, Playwright mobile or keyboard QA, and exact HTTP response-byte comparison. The new regression module is authored and registered, but not falsely described as executed. Source/prose metrics and independent traffic metrics are separate.

## Required local acceptance checks

From a full matching local checkout, without GitHub Actions:

```powershell
py -3 -m unittest discover -s _tests -p test_pbg04_poker_book_contextual_links.py -v
py -3 -m unittest discover -s _tests -p test_pbg03_poker_book_landing.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

The production URL extraction confirms the links are reachable from the public page at this observation time. Only exact-byte diagnostics using the matching checkout can certify source-to-live parity.

## Next improvement, PBG-05

Validate the real Amazon click-through path and measurement, using the owner's Umami events and optional KDP/Amazon Attribution if the account supports it. If source dashboards are unavailable, retain nulls. Verify that the canonical book page and Amazon URL still work without analytics JavaScript and that no invented order counts or affiliate identifiers are added. Use first-party GSC page/query data as soon as a free verified report is accessible. Do not infer clicks from the 9/11 internal-link coverage.
