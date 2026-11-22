# SEO/GEO Turn 84: connect the Poker Library and Study Desk to the original written 10 BB Playbook

**Date:** November 22, 2026 (Pacific/Honolulu)
**Starting main:** `3b9fd3253f7e850a1ecf5a0d48c6388190528ff2` (Turn 83, PR #457).
**Canonical pages improved:** `/poker/library/` and `/poker/study/`.
**Existing resource destinations:** `/poker/10bb/#six-checks` and `/downloads/ten-bb-tournament-checklist.md`.

## Verified reader discovery gap

Authenticated GitHub main-source inspection found zero direct links to the manual standalone `/poker/10bb/` Playbook from either the main Poker Library or the after-play Study Desk. The Library advertised **75 free guide cards**, with four separate featured long-read cards. Those counts are correct for its existing manifest-owned filtered catalog, but the separately published 10 BB guide is outside that catalog. The Study Desk's tournament learning route had four useful links, none of them the standalone answered 10 BB exercises. Visitors had to navigate through other pages, even though these two resources are purpose-built for finding poker study materials.

## Implemented improvement

1. **Poker Library:** One clearly labeled standalone companion paragraph immediately after the original four in-depth long reads and before the filterable 75-guide catalog. It links the already published written Playbook's `#six-checks` section and its six-check Markdown worksheet. It explicitly says the resource is separately published rather than counted among filtered cards.
2. **Poker Study Desk:** One small follow-up paragraph within the existing tournament-study article, after its four original ordered steps. It directs readers to the same Playbook and worksheet for after-play review.
3. **Evidence limits:** The Playbook offers six decision checks, six answered practice questions, and a reproducible **fictional** ICM example. The links do not certify a solver range for an actual opponent, suggest at-table assistance, claim a video is published, or imply a tournament profit.
4. **Source ownership:** Identical paragraphs were added to `_source/poker/library.html` and `poker/library/index.html`, and to `_source/poker/study.html` and `poker/study/index.html`. No HTML shell changes, new JS/CSS, changed canonical metadata, new URLs, modified worksheets or guide-count changes.
5. **Regression safeguards:** Added nine focused source/public, real-target, catalog integrity, original tasks, metadata, builder parity, negative-control and no-Action tests in `_tests/test_turn84_standalone_poker_discovery.py`, registered with the existing manual release checklist, and documented source ownership in `AGENTS.md`.

## Verification performed

| Item | Result | Boundary |
| --- | --- | --- |
| Original Library direct link to standalone guide | **Missing** | Authenticated GitHub main source inspection |
| Original Study Desk direct link to standalone guide | **Missing** | Authenticated GitHub main source inspection |
| Library source and generated paragraph | **Exactly matching** | Authenticated branch source/output comparison |
| Study source and generated paragraph | **Exactly matching** | Authenticated branch source/output comparison |
| Existing Library filtered cards | **75 unchanged** | Committed generated HTML count; manual 10 BB guide not represented as a fake card |
| Existing featured long-read cards | **Four unchanged** | HTML section structure |
| Existing tournament-study ordered steps | **Four unchanged** | Source and output HTML |
| Both target links | **Real** | Source Playbook has `id="six-checks"`; worksheet Markdown and Playbook download exist |
| New unit tests | **Nine authored and registered, not executed** | Full checkout is unavailable in current local runtime |
| Deterministic builder, HTML5, browser, all local tests | **Not executed** | Local shell cannot resolve github.com to clone entire current repository |
| Raw production status and exact response bytes | **Not checked for these two pages** | GitHub branch parity is not public deployment evidence |
| Search Console/Bing impressions or AI-answer citations | **Unavailable** | No new first-party metrics; no ranking or conversion claim |

## Release commands from a complete matching checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn84_standalone_poker_discovery.py -v
py -3 -m unittest discover -s _tests -p test_poker_library.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/library/ --only /poker/study/ --only /poker/10bb/ --only /downloads/ten-bb-tournament-checklist.md --attempts 8 --interval 15 --workers 1
```

Use `--scope all` in that selected-route command because the Library and Study Desk are **not** in the narrower priority target list. A successful selected-route report verifies only those four targets; run the whole release suite for a release-wide pass. On mobile, verify the native links are readable at 320px, keyboard focus and Enter work without JavaScript, and navigation lands at the intended Playbook section. A search engine result or content extractor cannot replace the exact-byte audit.

## Sprint status

**Advanced:** the site's main poker reading and study resources now directly surface an already published educational resource, while clearly distinguishing it from the 75 manifest-owned filtered guide cards. The site remains at 230 distinct canonical sitemap URLs. This is a practical internal discoverability improvement with genuine reader utility, not a demonstrated search ranking gain.

**Still open:** complete executable release suite and mobile reader checks, verified exact production bytes, authenticated Google/Bing query/page performance, assistant citations, measured performance and book edition validation.

**Next priority:** confirm source-to-live parity after deployment; then use actual observed search demand and reader behavior to prioritize a substantive content improvement rather than adding speculative pages.
