# SEO/GEO Turn 79: an optional, honest path from Poker Foundations to the 10 BB Playbook

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `5ea58e267afa691b912aba37a7f05607efd23a22` (Turn 78, PR #452).
**Goal:** Continue a practical poker reader journey from the free beginner course into deeper tournament decisions, without republishing content, inventing video availability or implying a solver recommendation.

## Confirmed navigation gap

Start Here now points directly to both the free six-lesson Poker Foundations course and the standalone written 10 BB Playbook, but the course's own `#course-finish` menu did not link to the 10 BB guide. It offered four coherent paths for beginners: more practice, first-game preparation, a viewer guide, and further cash-game or tournament preparation. The 10 BB Playbook already links back to the free course, so the two educational stages lacked a useful forward connection.

## Implementation

1. Preserve those four original completion options and add one **optional** fifth choice at the end of the existing `#course-finish` list. It points to `/poker/10bb/#six-checks`, an existing section of the written Playbook, and says to use it after a reader can explain the cards, action and call price. The linked three-player ICM example is fictional, not a solver verdict for a real hand. No financial or competitive results are claimed.
2. Update the real owner source `_source/poker/beginner-learning-path.html` and the paired rendered `poker/free-poker-learning-path/index.html` with the **same literal menu block**. Preserve the core six lessons, browser practice tools, actual page identities, October 8 publication date, October 16 last substantive revision metadata, and the original reading estimate. This is a supplemental navigation handoff, not a rewritten lesson.
3. Extend the offline `_tests/visibility_core_journeys_browser.py` from five to **six important routes**, adding `/poker/free-poker-learning-path/` at 320, 390, 768 and 1440 CSS pixels and 200% enlarged-text checks at the two narrow widths. The planned visual assessment count rises from 30 to 36. Check the course-to-Playbook link and the destination's actual section ID before running those viewports.
4. Add `_tests/test_turn79_course_to_tenbb.py` with eight static, builder-parity, source-provenance, real-resource and adversarial negative-control tests. Register it with the existing manual `_scripts/local_release_checks.py` and explain the source ownership in AGENTS.md.

## Evidence completed

| Assertion | Observation | Status boundary |
| --- | --- | --- |
| Old course completion menu | Four native actions; no `href="/poker/10bb/#six-checks"` | Authenticated main source |
| Updated course completion menu | Same original four actions, one new fifth action | Authenticated branch source and committed public HTML |
| Source/public new course menu | Exact literal block match | Authenticated source readback; generator has not run here |
| Playbook target | `id="six-checks"` exists, with published worksheet and source checks | Existing published site source |
| Reciprocal beginner route | Playbook already links to `/poker/free-poker-learning-path/` | Existing source, not a newly created backlink |
| Reading estimate | About 50 min in both committed HTML versions | Source-level observation, not independently timed |
| Offline reflow script | Six routes and 36 intended viewport passes | **Script authored, not executed** |
| Static regression methods | Eight | **Authored, not executed** against full checkout |
| Full builder, HTML5, internal links and Chromium | Unavailable | Complete GitHub checkout blocked in this container by DNS |
| Live 320px production audit | Not completed | Read-only browser tool cannot set viewport width or run mobile keyboard checks |
| Google, Bing and assistant discovery gains | Unavailable | No first-party observed clicks, citations or traffic comparison |

## Fresh public read-only browser context

A live desktop-width check of `/start-here/` in this same improvement turn confirmed the **Turn 78** links to the Poker Foundations course and 10 BB guide are present. The browser reported that exact 320px emulation was unavailable. Its approximate 980-1000px observation cannot be called a mobile validation, and a site-wide overflow result at that desktop width cannot prove no 320px clipping. No credential, form, checkout or user data was submitted. This bounded observation was recorded separately from the changed course's source review.

## Local acceptance from a complete current checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn79_course_to_tenbb.py -v
py -3 _tests/visibility_core_journeys_browser.py
py -3 _tests/entrypoints_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /poker/10bb/ --attempts 2 --interval 2
```

The last command is a **limited** verification of the written Playbook only; it does not certify the generated beginner course, which requires the full or appropriately selected registered release inventory. If a real mobile failure or output mismatch is observed, fix it before claiming completion. Do not weaken existing checks to get a passing count. No GitHub Actions, paid tool or scheduled background task is authorized.

## Sprint assessment

**Advanced:** the two useful, free Poker learning levels now connect in both directions. The transition has a clear educational prerequisite and honest ICM limitations. Canonical page count and site scope do not grow through duplicate content.

**Still open:** executable full current-source tests; 320px reader journeys; source-to-public exact byte verification; authenticated GSC and Bing page/query performance; the frozen AI answer citation panel; representative measured Lighthouse/performance data; verified book retail edition metadata. December 2026 remains the first potential complete postsprint month, not yet elapsed.

**Next highest-value action:** obtain a full network-capable checkout and run the mobile/browser/release test gates, then prioritize one page based on real owner-private query/page data rather than an unmeasured SEO guess.
