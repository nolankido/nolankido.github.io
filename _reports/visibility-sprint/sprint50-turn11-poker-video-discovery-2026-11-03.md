# Visibility sprint, Turn 11: Public poker-video discovery

**Review date:** November 3, 2026  
**Site:** https://nolankido.com/  
**Scope:** Poker hub, sourced player profile, public Find listing, local verification boundaries

## Purpose

Make Nolan Kido's published tournament videos discoverable through the personal site while keeping three evidence categories distinct:

1. First-person edited poker videos hosted on YouTube.
2. Independently recorded tournament results, including the gross-versus-net distinction.
3. The separately reviewed, written Portland Meadows Episode 1 companion and its two decision records.

This improves navigational access to Nolan Kido's public poker work without inventing results, promising solver certainty or exposing unfinished material.

## Public viewing routes

- [Portland Meadows Deepstack, 6.5 big blinds and trophy](https://www.youtube.com/watch?v=qABaiIcvvpU): public video with [written source-checked companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/), including the [6-4 decision](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-64o-record) and [pocket-sevens decision](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-77-record).
- [Portland Meadows evening Stand Off, A-K with 10 big blinds](https://www.youtube.com/watch?v=I75GOBVXij4): public video only. No reviewed written companion is claimed.
- [WSOP Circuit Reserve Day 1, near the money](https://www.youtube.com/watch?v=edNSD5BjIV8): public video only. No reviewed written companion is claimed.

The video pages were reachable in direct public checks on November 3, 2026. YouTube availability may change.

## Changes in this turn

- A visible three-video list in [Poker with Nolan](https://nolankido.com/poker/#watch), with internal links to the verified [player record](https://nolankido.com/poker/nolan-kido/) and companion hand sections.
- Updated standalone player profile: existing public uploads instead of a future vlog promise, with video-versus-result qualifications.
- Updated player page title, description, structured-data modification date, on-site Find card and sitemap change date.
- Source and generated HTML kept in sync; the main Poker collection description now distinguishes the one source-checked companion from other public uploads.
- Added test assertions for the three identifiers and a test-only exact-Git-blob predecessor bridge so historical release checks can still inspect previously approved files. No production code depends on this bridge.

## Boundaries and verification

- Existing independent poker result citations and caveats were retained.
- No unverified YouTube chapter timestamps, additional tournament results, opponent identities, poker profits, paid APIs, GitHub Actions or scheduled jobs were introduced.
- Static consistency checks confirmed the same three video IDs in both source and generated pages, the complete profile body in its generated HTML, the new player metadata, Find title, sitemap route, and no em dashes in changed prose.
- Python syntax was checked for all changed or newly authored `.py` modules.
- The full local Python, HTML and browser test suites could not be executed in the current read-only workspace, so no full-suite pass is claimed.
- Live-site confirmation must be recorded separately after publishing and retrieving the updated HTML.
