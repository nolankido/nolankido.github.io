# SEO/GEO/AEO Sprint Turn 13: source-bounded Reserve Day 1 companion

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 13 of 25
- **Base repository checkpoint:** `5b85722`, Turn 12 on `main`
- **Canonical destination:** https://nolankido.com/poker/episodes/reserve-day-1/
- **Local status:** Implemented with an independently built, source-checked page. This report's checks describe the local checkout; the live site, actual search indexing, ranking changes and AI-answer uptake require separate verification.

## Opportunity and choice

Turn 11 identified a third public NolanPoker upload, the WSOP Circuit Reserve Poker Club Day 1 episode, without a dedicated canonical written hand companion. Compared with making another generic bubble strategy article, this public video provided a distinct first-person narrative with an already independently documented tournament result and memorable, answerable questions about the seven-big-blind money bubble and uncalled chips in a three-way A-K pot. Turn 12 already owns the separate hypothetical ten-blind bubble math lesson, so the companion links to it without presenting that model as an adjudication of the actual hand.

## Evidence separation

**Independent tournament listing.** The official [WSOP Event #1 page](https://www.wsop.com/tournaments/result/19248/) lists the $400 No-Limit Hold'em Double Stack Kick-Off, October 29 to 30, 2026, 527 entries, 80 paid places and a $173,910 prize pool. The [Global Poker Index](https://www.globalpokerindex.com/tournaments/2026/united-states/world-series-of-poker-circuit-wsopc-reserve-poker-club-no-limit-hold-em-double-stak-kick-off-ring-event-1-1629128/) and [The Hendon Mob](https://pokerdb.thehendonmob.com/event.php?a=r&n=1439413) each list Nolan Kido 63rd with a $800 **gross** cash. These records do not establish net profit, full reentry spend, table decisions or hole cards.

**Archived firsthand source.** The owner supplied a private November 3 v8 script, truth-and-continuity review, metadata and change log for the filmed narration. They establish the author's reported near-bubble 9-7 offsuit fold, the unresolved J-diamond/9-diamond small-blind question, a late A-club/K-heart reshove with Q-J offsuit and pocket nines joining, and a last 9-diamond/10-diamond big-blind call. The private files remain private. The current public YouTube cut **has not been independently checked** against that v8 script, footage, audio or editor's chapter timestamps. The written companion discloses this in the lead and source section; it makes no assertion about live cut timestamps or an exact five-card board.

**Checkable arithmetic, not solved strategy.** Schematic 28 BB and 18 BB competing stacks leave approximately 10 BB of Nolan's reshove unmatched and returned. A 7 BB third player creates approximately 7 BB per player in a three-way layer and an additional 11 BB from each larger stack in a two-way layer. Folded contributions, blinds, antes and exact posting conventions are not inferred, and the article labels the layer figures as rounded illustrations. No solver/ICM verdict, unconfirmed suits, board, exact reentry count or reconstructed comeback hands were added.

## Implemented pathways

1. New reader-first, approximately 2,100-word canonical HTML article with an answer at the top, direct public video link, event listing, action sequence, layered pot explanation, three expandable after-play study questions and open-evidence section.
2. A public-safe JSON source ledger in `/downloads/reserve-day1-public-source-ledger.json` explicitly classifies independently listed, narrated, arithmetic and unknown claims. It does **not** include the private source packet.
3. A standalone deterministic builder and fail-closed registry, retaining independent publication ownership and the stable author Person `@id` in a single Article JSON-LD block. The public video link is direct; no iframe, tracking expansion or second sitemap service was added.
4. Native contextual links from the Poker hub and player profile. Exactly one registration in the existing main sitemap, Poker Find, general Find section search, Poker RSS, combined writing RSS and read-only live-byte inventory.
5. Standalone source, metadata, feed, section-search, schema, negative-control, sitemap and HTML5 tests were updated. No GitHub Actions, cron, paid API or automated indexing submission was introduced.

## Local verification

Initial development checks:

| Check | Observed local result |
| --- | --- |
| Turn 13 Reserve companion tests | 7 passed |
| Manual Poker RSS, Poker Find, author archive, Portland and Stand Off companion regressions | Passed in targeted runs |
| Main generator | 253 outputs; deterministic `--check` found zero drift |
| Standalone Reserve and player builders | Deterministic `--check` passed |
| Search audit | 225 sitemap URLs; 3 manually published poker episodes; unique titles and descriptions |
| Internal link verifier | 232 HTML pages; 16,235 links; zero broken |
| HTML5 parser | 230 HTML pages; zero parser failures |
| Standalone search-section tests | 12 passed after adding the sixth manual route |
| Player sitemap tests | 5 passed after accounting for the sixth manual route |
| Historical release-integrity test | One unresolved historical `git show` error at an unavailable old commit in the shallow checkout; current functional assertions passed |

This is bounded verification, not an assertion that the entire historical test suite or visual browser suite passed. The broad checklist, historical fixtures and public-byte comparison must be reported separately if actually completed. An offline build cannot prove the current YouTube footage or live search visibility.

## What success would look like

The new page should be accessible under its canonical route, included exactly once in sitemap and feeds, and discoverable from both the existing creator profile and the topic hub. Search Console can later measure impressions and click-through for brand and “Reserve Day 1 A-K pot” query families. AI-answer citation and referral behavior would need separate, observed measurement. Neither a source-backed page nor an IndexNow receipt guarantees indexing, rankings or citations.

## Next turn

**Turn 14:** verify the exact public Reserve video cut and, if feasible, reconcile the article's archived narrative with the current speech and card overlays. If the current cut is blocked, use a different selected first-party query/page pair with measurable search opportunity, preserve the evidence boundary and prioritize a concrete canonical improvement over guessed analytics or invented chapter timestamps.
