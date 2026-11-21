# SEO/GEO Turn 65: make the 10 BB Playbook discoverable in native site search

**Date:** November 21, 2026 (Pacific/Honolulu)  
**Base `main`:** `862117655e3640f75d145ae15cdb8f11d5df81af` (Turn 64, merged PR #438)  
**User journey:** [Search the site](https://nolankido.com/find/) to [10 BB Tournament Playbook](https://nolankido.com/poker/10bb/)  
**Type:** Real reader discovery and internal navigation correction. No new public canonical page, sitemap entry, metadata claim, off-site promise, provider API or analytics tracking.

## Confirmed defect

The separately published `/poker/10bb/` Playbook is already registered in the XML sitemap, the read-only exact-byte production inventory, the manual HTML5 inventory, and the site's poker links. But a search for its **exact canonical URL** in the committed `find/index.html` found **zero result-card links**. It was also missing from the compact searchable section-heading data.

The site search builds its cards through `site_find.render(player_find.add(root, site_find.entries(root, pages)))`. The public page manifest excludes this manual companion, and the `player_find.add` extension already adds other verified standalone articles, a player profile, and the independently maintained books. It had no branch for the 10 BB Playbook. Thus the link was not merely hard to find; the internal Find card genuinely was not generated.

This defect affects **on-site discovery and reader task completion**. A Find result is not itself proof of indexing in Google, a new backlink, an improvement to search ranking, an AI Overview citation or additional traffic.

## Bounded correction

1. `_scripts/player_find.py`: add `tenbb_entry(root)`, deriving title, search title, description, date and canonical from the **already published** HTML. Reuse the existing fail-closed `tenbb_companion.record(root)` Article/publication validator. Require the actual 10 BB page and verification script, matching public description and Article fields. Reject partial publication, a duplicate result, or unreviewed metadata. Do not invent an AKA, SEO keyword or solver result.
2. `find/index.html`: add one sorted Poker-group **Video companion** card to the native, no-JavaScript-readable Find result list. The Poker group rises from **112 to 113** visible cards. Its one link is `/poker/10bb/` and its original November 19 publication date is preserved.
3. Rebuild the embedded version-4 public section index content to include the eight named, visible H2 headings on the Playbook, while excluding H3 practice-question headings and hidden exercise content. Other pages, their canonical headings and the compressed index format are preserved. These are in-page navigation targets, not copied full text.
4. `_tests/test_turn65_tenbb_find.py`: add public metadata, one-result, generated parity, eight-section, local Node search-match, tampering, duplicate and noindex/sitemap boundary regressions. Register with the existing manual release runner.
5. `_tests/test_player_find.py`: reconcile an obsolete historical six-extra-only assumption with the independently registered three book/catalog records and the new Playbook. Keep the list of expected source-checked routes explicit and retain historical profile checks.
6. `_tests/test_search_sections.py`: compare current output with the **actual** manual-page-inclusive index and inspect source HTML for the manual routes. Its older manifest-only comparison and 60 KB payload ceiling were already out of date: the untouched pre-Turn-65 compressed section index was **84,485 characters**. The new limit is 100,000 bytes, but exact index-to-source comparisons, required anchors and negative controls still apply. This is an acknowledged changed scale, not claimed payload reduction.
7. `AGENTS.md` documents builder ownership, source limitations, local checks and the unchanged indexability rules.

## Independently checked source-level evidence

| Check | Before | After branch edit | What it proves |
| --- | --- | --- | --- |
| Find result link for `/poker/10bb/` | 0 | 1 | One native internal discovery route |
| Visible Poker Find cards | 112 | 113 | One new item, no duplicated Poker cards |
| Searchable Playbook named H2 sections | 0 | 8 | Direct results may lead to the original visible content |
| Embedded section JSON UTF-8 bytes | 84,543 | 85,110 | The increase is bounded; not a claimed performance gain |
| Complete generated Find HTML UTF-8 bytes | 222,979 | 224,202 | No new external runtime package or network search |
| Existing sitemap count | 230 URLs | 230 URLs unchanged | New navigation, not duplicate canonical publication |
| Playbook original Article publication | Nov 19, 2026 | Unchanged | No fabricated freshness or modification |
| Read-only local search privacy | No query transport | Unchanged | Search stays in browser memory |

The before-state section JSON was unpacked, re-pooled and serialized with the same source format, returning **identical bytes** to the existing 84,485-character string. The eight new headings were extracted from the original 10 BB public page, not guessed, and the updated decoded heading pairs matched the eight published named H2s. Source-level structural checks found exactly one new card, correct sorted Poker order, no duplicated target link, unchanged Find noindex setting and a valid complete version-4 JSON payload.

The correct scope of the HTML card change is **site search**, not a new indexable page. Search results still depend on the existing local JavaScript when filtering; the cards remain browsable without JavaScript. No external search service is called and no private queries are logged.

## Verification not completed in this environment

The isolated execution container cannot resolve `github.com` and therefore cannot obtain an executable full checkout. The actual Python builder, Node-based tests, Playwright/browser/mobile checks, strict HTML5 parser, complete historical suite and exact-byte production check **have not run in this turn**. The static source and JSON checks above are not substitutes. A GitHub merge alone is not confirmation that the public custom domain has deployed the new Find card.

Run the following on a full checkout at the merged commit, with local test dependencies installed:

```powershell
py -3 -m unittest discover -s _tests -p test_turn65_tenbb_find.py -v
py -3 -m unittest discover -s _tests -p test_player_find.py -v
py -3 -m unittest discover -s _tests -p test_search_sections.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /find/ --attempts 3 --interval 5
```

If any generated source/output discrepancy is found, fix it rather than marking the gate passed. The exact-byte check must use a status-bearing GET with a complete checkout. An inconclusive DNS failure is not a site HTTP 404.

## Next priority

Confirm the new Find result publicly after deployment, complete the full local suite when a full checkout is available, then prioritize **actual** first-party Google Search Console query/page observations and three reader-journey completions rather than inventing more pages or attributing traffic changes to this edit. The user's existing monthly visibility task remains the only recurring review; no duplicate automation or paid API was created.

**Related evidence:** [Turn 61 closeout](seo-geo-turn61-release-and-evidence-scorecard-2026-11-20.md), [Turn 64 measured-zero fix](seo-geo-turn64-google-ai-zero-evidence-2026-11-21.md), `_scripts/player_find.py`, `_scripts/search_sections.py`, `_scripts/tenbb_companion.py`, `_source/find.html`, and `poker/10bb/index.html`.
