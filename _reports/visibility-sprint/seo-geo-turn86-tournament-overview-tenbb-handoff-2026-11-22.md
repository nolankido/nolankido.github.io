# SEO/GEO Turn 86: direct tournament-overview readers to published 10 BB study

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Base:** `485c4919154d1cc6b0b31bd80bb9de37a38b9ad4`  
**Existing canonical entry:** `https://nolankido.com/poker/tournaments/`  
**Existing teaching destination:** `https://nolankido.com/poker/10bb/`  
**Status:** authored, source/public markup paired; local full-checkout tests and post-release exact-byte GET pending.

## Evidence from prior turn

Turn 85, merged in PR #459, added a separately published written 10 BB Playbook to the native, privacy-preserving Poker Finder. The original manifest-owned Poker Library stayed at 75 guides, and native Poker Find reached 301 entries: 107 on-site, 146 external, 48 glossary.

On November 22, a fresh read-only retrieval of the public `/poker/find/` page found the exact `data-id="standalone-tenbb"` guide record with the published canonical URL, eight visible heading passages, and `tournaments strategy` topics. A fresh read-only public fetch found `/poker/10bb/` available with its own Article metadata. These facts establish presence of those elements at the time of retrieval, not full Python generator parity or search ranking.

A separate public desktop browser interaction check reported:
- Search `10 BB Playbook`: one correct visible result out of 301.
- Eight headings inside that result card: present.
- Tournaments and Strategy & math filters: kept the Playbook result visible.
- Reset: cleared the query and filters.
- Search words: were not seen in the browser URL during that test.
- External resources filter: the agent reported the Playbook remained visible even though the record is a guide. The current `assets/poker-finder.js` code explicitly excludes cards when `kind.value` differs from `data-kind`, so the reason is uncertain; it may reflect the agent's dropdown interaction or a real event-handling defect. Treat as unconfirmed until a controlled Playwright test verifies the actual selected value, count, and card visibility. No speculative source-code fix.
- Mobile 390px width: not exercised.

The connected GSC Wizard account refused first-party Search Console reads because there is no active subscription. No page-level clicks, Google rankings, Bing impressions, or assistant citations can be claimed from this turn.

## Current gap and bounded solution

The separately published written guide was linked from the Poker Home, Library, Study Desk, and the newly updated Finder. However, the existing high-relevance tournament primer `/poker/tournaments/` still explained changing blinds, antes, bubble and chip-versus-cash value without offering a direct path to the six-check written companion or its worksheet.

In `_source/poker/tournaments.html`, extend the existing *Continue learning* navigation with:
1. `/poker/10bb/#six-checks-title`, labeled **After-play study: written 10 BB Playbook**.
2. `/downloads/ten-bb-tournament-checklist.md`, labeled **Download blank 10 BB worksheet**, retaining the HTML `download` attribute.

The original math guide, viewer library, general viewer reference and correction navigation stay intact. The same 179-character insertion is applied to generated `poker/tournaments/index.html` at exactly the matching navigation prefix. There are no new canonical URLs, edited tournament calculations, published testimonials, guessed solver results, source dates, social claims or tracking.

Because `poker_finder.GuideText` excludes `<nav>` content, the new link text should not alter searchable guide prose, existing Playbook search headings, or the 301-result native Finder. The site-wide canonical sitemap remains at 230 URLs. No new article is added to the manifest.

## Offline regression coverage introduced

`_tests/test_turn86_tournament_overview_handoff.py` adds six tests for:
1. Source fragment and generated public navigation equality.
2. Existing approved Playbook H2 anchor and downloadable worksheet target.
3. Preservation of original navigation, canonical, publication/modified dates and sitemap route.
4. Unchanged content exposed to Poker Find's spoiler-excluding article parser.
5. Exact deterministic `build.build_outputs()` equality for the generated tournament HTML.
6. No repository GitHub Actions workflows.

Register the new module in the existing local-only `_scripts/local_release_checks.py`. Owner rules stay in `AGENTS.md`.

## Full-checkout validation instructions

```powershell
py -3 -m unittest discover -s _tests -p test_turn86_tournament_overview_handoff.py -v
py -3 -m unittest discover -s _tests -p test_turn85_poker_finder_manual.py -v
py -3 _tests/finder_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/tournaments/ --only /poker/find/ --only /poker/10bb/ --only /downloads/ten-bb-tournament-checklist.md --attempts 8 --interval 15 --workers 1
```

## Evidence limitations and acceptance

GitHub source readback and patch comparison can establish the intended bounded edits, but no complete checkout and full local Python/HTML5/Playwright suite have run in this restricted runtime. A browser successfully reading the public card does not prove exact deployed bytes match the checked-out Git commit. The source-type filter anomaly needs a separate controlled, repeatable browser test before it justifies a production code modification.

After merging, require a read-only observation of the tournament page's two new navigation links. Later run the local deterministic build, link audit and public exact-byte GET from a complete matching checkout before declaring the release fully verified. Do not add GitHub Actions, cron, paid monitoring or invented search-improvement metrics.

**Next priority:** complete the local release tests and reproduce or dismiss the unconfirmed external-resource filter issue before another new page or search-index expansion.
