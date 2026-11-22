# SEO/GEO Turn 78: connect first-visit poker readers to two real learning levels

**Date:** November 21, 2026 (Pacific/Honolulu)
**Starting main:** `de06ee6ef808f0cffed45759629ace82a470c3ac` (Turn 77, PR #451).
**Public entry:** https://nolankido.com/start-here/
**Scope:** Improve the existing Start Here reader pathway and keyboard acceptance coverage. No new pages, backlinks, invented outcomes, paid analytics, cron, or Actions.

## Reader problem

Start Here already provided four useful first tasks, including first-tournament logistics, and the Poker interest card offered a viewer introduction and a Poker finder. It did **not** provide a direct link to the site's original, already published six-lesson beginner course or to the separate written 10 BB tournament guide. A reader who wanted to study decisions had to navigate further before discovering the actual course. This is a bounded discoverability opportunity, not a claimed ranking or user-conversion failure.

## Implemented

1. Add one readable paragraph immediately after the existing four-item Start Here task list. It offers two meaningful paths, explicitly distinguishing a beginner's six-lesson Poker Foundations course with card/betting practice from the written 10 BB Playbook with answered questions, a free decision worksheet, and a fictional reproducible ICM example. Its final sentence prohibits interpreting a study example as a solver verdict for a real hand.
2. Add exactly the same paragraph in `_source/start-here.html` and committed `start-here/index.html`, using the pre-existing `small-copy` style. The four existing task list elements and the AI workflow pilot remain unchanged. Neither `entrypoints.json` nor a prior baseline was rewritten.
3. Extend the existing `_tests/entrypoints_browser.py` native keyboard visitor journeys with direct Start Here to `/poker/free-poker-learning-path/` and to `/poker/10bb/` navigation, with site JavaScript **both enabled and disabled**. Update that browser suite's per-mode route count from 28 to 30; no external requests or forms are made by the script.
4. Add eight focused source, target, metadata, negative-control and deterministic-build contract tests in `_tests/test_turn78_poker_reader_handoff.py`. Register with the pre-existing manual release runner, and document ownership in AGENTS.md.

## What was actually verified

| Check | Result | Interpretation |
| --- | --- | --- |
| Old first-visit direct course links | 0 for each of the two routes | Authenticated main Start Here HTML inspection |
| New direct links | Exactly 1 per route in Start Here source and published HTML | Authenticated branch readback |
| Paragraph copy source/output | Identical | Single reader handoff, not two different marketing claims |
| Four existing native task shortcuts | Unchanged | No additional task list item, historical counts remain 4 |
| Both destination pages exist | Yes | Real published beginner course and written 10 BB Playbook; no invented video URL |
| Beginner course facts | Source-checked | Existing six connected lessons, no new video publication claim |
| Playbook facts | Source-checked | Existing standalone written guide, worksheet and reproducible fictional ICM check |
| Browser test code | Updated | Both new paths tested by keyboard Enter in JS-on and JS-off loops; **not executed** |
| New focused unit tests | Authored, eight methods | Include true build equality check; **not executed** in this isolated environment |
| Full build, HTML5, internal-link and Playwright release suite | Not run | Complete GitHub checkout blocked by DNS; no green suite is asserted |
| Exact production source-byte parity | Not run | A GitHub code merge is not a public HTTP verification receipt |
| Search clicks, indexing, AI citations or subscriptions | Unavailable | No measured uplift is claimed; zero cannot replace missing data |

## Acceptance from a complete current checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn78_poker_reader_handoff.py -v
py -3 _tests/entrypoints_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope priority --only /start-here/ --only /poker/10bb/ --attempts 2 --interval 2
```

The direct beginner course URL is a registered public source page, but the limited last command checks only two priority routes. A full release must use the default priority scope and ultimately all registered targets. Separately test 320 px and keyboard completion, including the new course route. Do not weaken assertions if tests reveal a real defect.

## Sprint status

**Advanced:** first-visit paths now give poker beginners and tournament students specific free learning destinations without pretending that unpublished course videos or solver verdicts exist. Site architecture is more useful without adding generic SEO articles or changing the historical 230-URL sitemap inventory.

**Still open:** full current-release suite and real mobile checks, source-to-production byte receipts, authenticated owner Search Console/Bing query/page observations, frozen 25-question assistant citation panel, performance measurement, and verified book retailers. December 2026 is not yet a completed post-sprint month.

**Next priority:** Execute the existing checks in a network-capable checkout; repair observed failures; use measured query-page data for the next substantive on-page relevance experiment.
