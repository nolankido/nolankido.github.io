# SEO/GEO Turn 85: include the independently published 10 BB Playbook in native Poker Find

**Date:** November 22, 2026 (Pacific/Honolulu)
**Starting main:** `ab5a02eb93e5de972cca16f26c3338910327dfdc` (Turn 84, merged PR #458).
**Reader route:** `/poker/find/` (existing noindex private, browser-local search).
**Source route:** `/poker/10bb/` (existing original written guide, already indexed in the site-wide `/find/`).

## Verified gap

The native Poker Finder's authored `_scripts/poker_finder.py` indexed only manifest-backed Poker pages, 146 reviewed external resources and 48 glossary definitions. Its committed generated results contained **300 records: 106 on-site pages, 146 external resources, 48 glossary entries**. The separately published 10 BB Tournament Playbook had been source-validated for the general site Find in Turn 65 and linked from Library/Study in Turn 84, but was **absent** from Poker Finder's 300 search cards. A Poker visitor searching the native finder for the Playbook could not receive that page as a result or filter it with Tournaments and Strategy. This is verified from actual source and generated records, not an inferred search-ranking problem.

## Implementation

1. `_scripts/poker_finder.py` now reuses `player_find.tenbb_entry(root)` to validate the published manual Playbook's canonical URL, public title, Article metadata, worksheet and fixed-input ICM checker before introducing a single result. A missing or partially published resource fails closed. A duplicate with a manifest page also raises rather than making two search cards.
2. The new record's ID is `standalone-tenbb`; it uses the real title, description and search title. It is a free, on-site, independently published written tournament guide with an honest note that its example is fictional, not a real-hand solver verdict or live-play tool.
3. The native Poker Finder includes only the Playbook's **eight visible H2 section headings**, dynamically read through the existing `search_sections.headings()` function. It does **not** ingest hidden Q1-Q6 answer paragraphs, create fabricated transcript segments or claim that the entire manually authored body is searchable. The result's own disclosure and the full Finder scope statement explain this heading-only exception.
4. `_scripts/poker_topics.py` grants the standalone page membership in the existing Tournaments and Strategy & math filters. No generic rule changes or fabricated filters. The pre-existing 75-card Poker Library is still a separate manifest-owned inventory.
5. The committed `poker/find/index.html` now contains the new native search card and 301-entry count. The exact new card was independently reconstructed from the real Playbook metadata, section IDs and the Python renderer's escaping and markup contract, then matched character-for-character with the checked-in result.
6. `_tests/test_poker_finder.py` now expects one approved standalone guide in addition to the manifest routes. Eleven additional source, real-target, code-versus-output, count, duplicate, negative-control, topic and noindex tests are in `_tests/test_turn85_poker_finder_manual.py`. The existing `_tests/finder_browser.py` adds an Enter-submitted `10 BB Playbook` search and topic/source-type filtering checks. The manual release runner and AGENTS.md were updated.

## Source-level verification completed

| Evidence | Before | After / observed |
| --- | --- | --- |
| On-site native Poker Finder entries | 106 | 107, including exactly one manually validated `/poker/10bb/` result |
| External resources | 146 | 146, unchanged |
| Glossary definitions | 48 | 48, unchanged |
| Total native Poker Finder cards | 300 | 301 |
| Standalone section destinations | 0 | 8 validated visible H2 headings |
| Manual Playbook topic membership | None | Tournaments; Strategy & math |
| Original generated page outside the change | Original 1,281,689-character HTML | Confirmed character-for-character identical after removing the single new card and reversing the two changed count/scope strings |
| New card and source renderer shape | None | Exact character match with independently reconstructed escaping, fields, eight passages and disclosure |
| Poker Library filtered cards | 75 | 75, unchanged |
| Sitemap canonical routes | 230 | 230, unchanged |
| New test methods | None | 11 authored; also updated existing Finder tests and browser flow |

The generated Finder is about 1.28 MB because it embeds the entire public index. The authenticated GitHub standard `fetch_file` wrapper returned empty content for that unusually large file, so the 1.28 MB file was read through the GitHub Contents fetch and updated with its exact original blob SHA. The reconstructed new card and the original-byte preservation comparison establish controlled source changes. **They are not a substitute for running the project's Python generator**.

## Unexecuted validation

The complete current repository checkout cannot be cloned in the container because `github.com` DNS is unavailable. Therefore the full site deterministic builder, the new eleven-method unittest module, the existing Finder tests, HTML5 and internal link checks, the Chromium Enter/filter tests at 320/390/768/1280 CSS pixels, and the status-bearing exact source-to-live byte verification have **not been executed** here. The browser source was extended but is not represented as passing. No current Google/Bing impressions, ranking, clicks, indexing or AI assistant citations were measured. No paid subscription was created.

## Local acceptance in a complete matching checkout

```powershell
py -3 -m unittest discover -s _tests -p test_turn85_poker_finder_manual.py -v
py -3 -m unittest discover -s _tests -p test_poker_finder.py -v
py -3 _tests/finder_browser.py
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _tests/diagnose_live_crawl.py --scope all --only /poker/find/ --only /poker/10bb/ --attempts 8 --interval 15 --workers 1
```

`/poker/find/` is a noindex search utility and is not in the narrower priority list. Use `--scope all` for its selected-route audit, then run the full registered release inventory separately. After deployment, a fresh read of the public Finder card can establish **content publication**, but only a matching checked-out-source raw GET from the verifier can establish byte parity.

## Sprint assessment

**Advanced:** real poker education is now discoverable through the exact native search tool that previously omitted the separately published resource. The guide can be filtered by tournament or math/strategy intent without falsely increasing the existing 75-guide Library catalog. The new record reuses source-verified identity rather than inventing separate SEO metadata.

**Still open:** full current-source test pass, exact live release receipts, mobile keyboard behavior and performance, settled owner Search Console/Bing query/page data, independent assistant citation observations and verifiable book retail editions.

**Next priority:** verify the newly generated index in a complete Python checkout and on the public site; correct any build parity or real user interaction defects before additional pages or internal links.
