# Poker player desk: product decisions and release scope

## What makes a resource genuinely useful

The goal is not to declare the site the best. It is to reduce the distance between a player's question and an understandable, appropriately sourced answer. A first-time viewer, live cash player, tournament player, mixed-game learner and research reader need different entrances.

| Opportunity | Decision for this release | Reason |
|---|---|---|
| Search across disconnected libraries | Implemented: one answer finder across public Poker pages, external resources and existing glossary definitions | Visitors should not need to understand the information architecture first. |
| Question-first navigation | Implemented: six player routes on the Poker home; finder and resources promoted into shared Poker navigation | The site can stand on its own before personal videos arrive. |
| Quick usable reference | Implemented: exact math table, worked call/bluff/raise examples and one generated Markdown download | A reference should answer the immediate question and explain where its formula stops applying. |
| Preflop chart literacy | Implemented: model inputs, combo weights, mixing and stack conventions | Avoid publishing unsupported ranges or teaching visitors to read colors without context. |
| Rules and integrity | Implemented: authority map, minimum-raise example, dated official policy references and private reporting guidance | Room rules and online permissions are not interchangeable. |
| Source depth instead of link inflation | Implemented: six focused additions; five public-page/catalogue reads and one explicitly index-only record | Preserve each source's original review scope, access label and caution. |
| Accessible browsing and privacy | Implemented: keyboard operation, native controls, no-query-transport search, complete no-JS and blocked-script index, print restoration | Finding an answer should not require an account or sacrifice a private query. |
| Independent maintenance | Finder and math exports are generated from the same source data; future approved pages enter the finder automatically | Avoid secondary catalogues, stale counts and duplicate glossary definitions. |
| Saved reading lists and shareable searches | Deferred | Persistent state or query URLs need a deliberate privacy decision. Native page bookmarks already work. |
| Full calculators or solved strategy charts | Deferred | Correct accounting is not a validated strategy engine. Do not market unverified outputs or build live assistance. |
| Original hands, videos and personal results | Await actual approved material | Never invent the author's experiences. |
| Multi-language and jurisdiction coverage | Further research required | Translation links do not establish equivalent versions or worldwide eligibility. |

## Inventory and boundaries

39 guide-library entries, 138 external resources and eight guided collections. The finder contains 234 entries: 48 on-site pages, 138 external resources and 48 existing glossary definitions. Hubs and definitions are not counted as additional guides. There are nine new native self-check panels.

New guides: poker-math-reference, reading-preflop-charts, poker-rules-and-fair-play. New utility route: /poker/find/. New download: /downloads/poker-math-reference.md.

Only the finder page loads the new local script and stylesheet. The original Technology-first homepage, non-Poker pages, shared visual assets, contact configuration, analytics and private solver boundary are preserved. The Poker sub-navigation prioritizes discovery while retaining direct guide, hand-review, study and glossary access. Existing Start Here and story URLs remain reachable from Poker home.

The source index searches titles, descriptions, topics and keywords, not full article bodies or video transcripts. Common abbreviations are expanded and results are ranked by text match, not by product quality or source endorsement. Search controls appear only after initialization. No query goes into an HTTP request, browser storage, cookie, URL or analytics event. The full server-rendered index remains visible without the script. Existing pageview analytics is unchanged.

## Source review

See resource-expansion-batch-005.json. Five public pages/catalogues were read. The TDA download page timed out twice, so its directory record explicitly says Search index only and states that the downloads and translations were not reviewed. Existing review dates are not reset. The GTO Wizard roadmap's September 2024 limitation was not used as a current capability claim.

## Verification

The local 173-test unit suite passes, including independent physical-deck enumeration for 169 classes and 1,326 combinations, exact arithmetic, source/export parity, source-scope preservation, safe HTML rendering and complete index coverage. The original browser policy blocks local HTTP navigation in this container, so no local HTTP browser pass is claimed. Run finder_browser.py in GitHub Actions along with the full existing suites. Inspect the exported mobile and desktop screenshots, then require successful PR checks, Pages deployment and exact live-byte verification before reporting publication.

## Next highest-value work

Use genuine reader questions and anonymous page-level traffic to identify missing topics without collecting raw search terms. Expand authored mixed-game explanations, captioned or transcribed creator resources and operator-specific access information only after reviewing the actual sources. Preserve old URLs and individual review histories. Measure successful discovery with task-based reader tests rather than raw link counts or an unsupported best-on-the-internet badge.
