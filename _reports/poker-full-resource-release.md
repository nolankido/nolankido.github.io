# Poker resource completion pass

## Product decisions

A useful resource site must answer a real question, expose relevant sources, help readers practice and remain maintainable. This release follows through on those priorities without inventing personal material or claiming universal coverage.

| Reader need | Implemented |
|---|---|
| Find an explanation without guessing its title | Full original guide prose is searched alongside catalogue metadata. Matching passages link directly to existing section anchors. Exercise answers and hidden navigation are excluded. External articles and media transcripts are not copied into the index. |
| Keep a useful selection | A 12-item study list lives only in page memory and exports selected public links, metadata and source cautions as Markdown. Queries and matching excerpts are not exported. Reloading clears the list. |
| Check basic arithmetic | Three study-only calculators distinguish call thresholds, zero-equity bluff fold thresholds and pot-limit wager accounting. Visible worked examples remain available without JavaScript. |
| Learn beyond hold'em | New Omaha hi-lo and stud/lowball workshops provide original examples, source links and self-checks. |
| Understand multiway decisions | A new workshop separates closing action, multiple ranges, eligible pots and conditional folding probabilities. |
| Put a video or podcast to use | A new media-study guide distinguishes transcripts, show notes and actual viewing, with reviewed source-page links. |
| Check player protections | A new guide links authoritative register, support and account-security sources, with explicit jurisdiction and review limits. It is not an individual eligibility determination. |
| Judge source freshness honestly | A generated resource-review page shows methods, individual dates and index-only limitations without equating a successful HTTP request with a new editorial review. |
| Avoid another wall of links | Homepage shortcuts lead to the new utilities; the full collection list is available in a native disclosure. Existing URLs and reader paths remain. |

## Inventory

44 guide-library entries, 145 external resources, 13 resource collections and 48 glossary definitions. The finder indexes 248 entries: 55 public Poker destinations, 145 external entries and 48 glossary definitions. Utility pages, hubs and definitions are not counted as additional guides.

New guides: omaha-hi-lo-workshop, stud-and-lowball-workshop, multiway-pot-workshop, poker-media-study and poker-access-and-protection. They contain 15 native self-check panels. New utilities: study-calculators and resource-quality.

Six new source pages or catalogue descriptions were read; the New Jersey regulator entry is explicitly search-index-only because its current official page returned 403. The old address returned 404. Video pages and podcast notes are not described as complete media reviews. All 138 existing resource records and review dates are preserved. See resource-expansion-batch-006.json.

## Calculation and content boundaries

The call calculator takes the CURRENT pot including the bet and the EXTRA amount to call. The bluff calculator takes the pot BEFORE betting and the new risk. Both require no further action and the stated no-rake, eligible-pot assumptions. The pot-limit calculator separates chips newly added from the total street wager; it does not establish stack availability, minimum raises or whether action is reopened. None estimates opponent ranges or recommends a live action.

The Omaha counterfeiting examples are independently enumerated from physical cards. The Badugi example checks distinct ranks and suits. Split-pot examples distinguish pot share, incremental decision value and whole-hand net results. Multiway calculations never replace a joint event with a product of marginal probabilities unless independence is explicitly assumed.

The published player-protection guide does not assert that an operator is available or authorized for a particular visitor. Great Britain and New Jersey are examples of official-source routes, not a worldwide legal map. Translation links do not establish equivalent rule versions.

## Privacy and preservation

Search terms, calculator values and study selections remain in the open page. No network requests, URL rewriting, cookies, browser storage, analytics events or new message endpoints are used for these interactions. Only explicitly selected public resource information is exported by the download action. Existing pageview analytics is unchanged. All new script and style loading is scoped to its relevant utility page.

The Technology-first root homepage, non-Poker pages, shared identity/design assets, contact setup, private solver boundary and real-publication catalogue are unchanged. No personal experiences, hands, results, videos or reviews are fabricated. Old routes and source review history remain intact.

## Verification

The local deterministic build checks 79 generated files with zero differences. All 181 unit tests pass, including source/export parity, full-text section extraction, query boundaries, catalogue coverage and independently recomputed calculator results against exact fractions. JavaScript syntax checks pass.

Local HTTP browser navigation was blocked by the container administrator. No local browser pass is claimed. The new full_resource_browser suite is designed to test eight routes at four widths with expanded text spacing, full-text section retrieval, bounded study selections, query-free downloads, calculator validation, keyboard self-checks, no-JavaScript access and automated accessibility. It must run in GitHub Actions with the existing suites before merge. The ordinary CI receives the new suite and calculator syntax check.

Expected production coverage is 115 public targets, including new pages and calculator assets. Do not infer publication from a build or archive alone. Require successful PR checks, Pages deployment and the exact public-byte verifier. Final run identifiers and actual outcomes belong in the pull request release receipt.

## Further development boundaries

Human usability research, an exhaustive worldwide jurisdiction map, independently tested paid products, full media reviews, original author hands and validated solved strategy ranges require their own evidence. This release does not claim those have happened. Expand based on actual reader tasks and reviewed sources rather than arbitrary page or link targets.

## Integration with the concurrent topic architecture

Main changed to ba25df088914971f0ed6b50c49feccc8bd0b6806 (PR #22) while
this release was being prepared. The combined release retains the topic index,
ten focused topic pages, topic breadcrumbs, simplified homepage and whitelisted
filter-fragment navigation. Full-text passage matching and the portable study
list now work alongside topic filtering. Every new guide has a primary topic;
new utilities and media resources have explicit topic placements. Existing
resource records and review dates are preserved. The resulting finder contains
259 entries, including 66 on-site pages. Guide and external counts remain
44 and 145. Search text and selections are not serialized; only the previously
approved topic/type/free filters appear in fragments.

The entire combined build and browser suites, including topics_browser, must
pass before merging. Expected public-response coverage is 127 targets.
