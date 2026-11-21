# SEO/GEO Turn 66: connect short-stack readers to the 10 BB Playbook

**Review date:** November 21, 2026, Pacific/Honolulu  
**Starting `main`:** `5adcc76e2eef74bbaa96bb93509f02f0943f714e` (merged Turn 65, PR #439)  
**Existing canonical destination:** https://nolankido.com/poker/10bb/  
**Focus:** Source-backed internal discovery and useful after-play learning journeys, without adding another article or unverified ranking claims.

## Verified public state

A new public, read-only retrieval on November 21 successfully found **The 10 Big Blind Tournament Playbook** and its direct URL in the deployed [Search the site](https://nolankido.com/find/) page. This independently resolves the previous Turn 65 content-retrieval uncertainty. The observed HTML extraction and navigation link are **not** an exact-byte release receipt or proof of search-engine indexing.

A separate inspection of **eleven** current GitHub HTML entry points showed that the established Poker hub, short-stack guides, Poker Library and ICM article did not yet have direct `href="/poker/10bb/"` or fragment links; only the updated `find/index.html` did. Inbound contextual learning paths were still absent from the most relevant reader journeys. The Playbook already existed, had a single canonical and separate ICM and practice headings. Adding a new keyword page would duplicate content instead of helping readers discover the original.

## Two bounded, intentional reader handoffs

| Where a reader is | Existing question | New single link | Why it helps |
| --- | --- | --- | --- |
| `/poker/`, the existing `poker-stack-route` reader choice | I have about ten blinds. Where can I review actual decisions after a tournament? | `/poker/10bb/#practice-title`, labeled as the Playbook's answered exercises | Takes the visitor to **six original fictional after-play questions** without changing the existing 3–5, 6–10 and 10–20 BB guide choices |
| `/poker/six-to-ten-bb-tournament-decisions/`, directly after the scope/bubble introduction | I want a second ICM example with clearly stated assumptions | `/poker/10bb/#icm-title`, described explicitly as a **different three-player ICM example** | Distinguishes the Playbook's three-player modeled prize decision from this guide's separate **four-player** bubble case, rather than implying a transferable solver verdict |

Both target section IDs exist **once each** in the original Playbook. The Playbook's modeled 58.88% threshold belongs to its own assumptions, not to the other page's prize ladder. The new copy does not imply this is a real hand, an approved in-tournament aid or a universal 10 BB shoving recommendation.

## Actual code changes

1. In `_source/poker/home.html` and its generated `poker/index.html`, insert one practice link within the established short-stack reader paragraph, after the existing four-player bubble link.
2. In `_source/poker/six-to-ten-bb-tournament-decisions.html` and generated `poker/six-to-ten-bb-tournament-decisions/index.html`, insert one distinct ICM learning link adjacent to the original explanation, without replacing its own example.
3. Add `_tests/test_turn66_tenbb_reader_paths.py` to check exact unique link counts, content-specific labels, source/rendered paragraph equality, valid Playbook section anchors, explicit model boundaries, unchanged original metadata and sitemap, a stable 24-minute reading estimate, and generated-output parity. Include negative tests for broken/missing/duplicated links. Register it in the existing manual local release runner.
4. Correct `_tests/test_turn152_short_stack_route.py`, which still checked an outdated **three-link-only** navigation pattern despite the preexisting bubble/solver links, an old disclaimer phrasing and November 16 metadata. The updated regression checks the exact complete six-link sequence, preserves the three essential stack-depth choices in their established order, and rejects broken practice links and unsafe claims. It does not silently remove the historical test.
5. Document the new source ownership and tests in `AGENTS.md`, preserving the owner restriction against GitHub Actions.

## Evidence and limitations

| Check | Before Turn 66 | Static branch result | Limitation |
| --- | --- | --- | --- |
| Link from Poker hub to 10 BB practice | 0 | Exactly 1 in source and 1 in public HTML | Content-level, not measured visitor clicks |
| Link from 6–10 BB guide to 10 BB ICM | 0 | Exactly 1 in source and 1 in public HTML | Distinct teaching fixture, not a solver result |
| Playbook target section anchors | Both already published | Each verified present once | Raw public response bytes not compared |
| Paired source/output link paragraphs | Same legacy content | **Byte-identical markup fragments** after the edit | Full deterministic build still must run |
| 6–10 BB guide reading time | 24-minute listed estimate | A bounded text-count preflight estimated **5,387 words**, within the existing 24-minute threshold of 5,400 words | Actual `poker_library.minutes()` and build checks are unrun |
| Sitemap and new indexable pages | 230 URLs | No sitemap or new canonical changed | Crawl/indexation is not measured |
| Publication dates | Poker hub and guide modified Nov 20; Playbook published Nov 19, revised Nov 20 | Unchanged | Navigation-only update does not falsify content freshness |
| Search and assistant traffic | Not available from authenticated sources | Not measured | No new rankings, GSC impressions, Bing citations or AI referrals claimed |

### Release checks to run from a complete checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn66_tenbb_reader_paths.py -v
py -3 -m unittest discover -s _tests -p test_turn152_short_stack_route.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /poker/ --only /poker/six-to-ten-bb-tournament-decisions/ --attempts 3 --interval 5
```

**Not run here:** The container again cannot resolve `github.com` or `nolankido.com` and lacks a full checkout. GitHub source retrieval and read-only public content extraction are available, but they are not a substitute for local Python, strict HTML5, Playwright or status-bearing exact-byte production checks. The added test suite and complete site build must not be reported passing until they execute successfully.

## Next improvement

Verify both links after public deployment and finish the full release gate. Then put most new efforts into *first-party* search query/page evidence, task completion, real reader accessibility and relevant third-party discovery, not arbitrary page count. When no authenticated GSC/Bing/Umami export is available, mark those metrics unavailable rather than zero.

**Source ledger:** [Turn 65 on-site Find correction](seo-geo-turn65-tenbb-local-find-2026-11-21.md), `_source/poker/home.html`, `_source/poker/six-to-ten-bb-tournament-decisions.html`, `poker/10bb/index.html`, `_tests/test_turn152_short_stack_route.py`, and the existing `_reports/visibility-sprint/seo-geo-measurement-v1.md`.
