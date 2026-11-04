# Visibility sprint, Turn 19: Evidence routes from the Nolan Kido biography

**Review date:** November 3, 2026 (America/New_York)  
**Site:** https://nolankido.com/  
**Reader route:** https://nolankido.com/bio/#profile-evidence-routes

## Opportunity and outcome

The public biography had useful general examples and reusable introduction text, but no direct, descriptive path to the source-backed poker creator introduction released in Turn 18. It also did not route AI-specific introductions directly to the website-change evidence and small-business pilot work.

Turn 19 adds a compact navigation section on the existing biography for two audiences:

1. **Practical AI:** [The source-linked website-change case](https://nolankido.com/technology/#site-visibility-evidence) and [small-business AI pilot guide](https://nolankido.com/technology/#small-business-ai-pilot).
2. **Tournament media and poker collaborators:** [The sourced poker creator introduction](https://nolankido.com/poker/nolan-kido/#creator-introduction), connected to selected independent results and publicly available videos.

The copy explicitly distinguishes these public examples from endorsements, professional credentials, audience growth, official creator status or poker profit. It does not claim that adding links has increased indexing, referrals or AI-assistant mentions.

## Implementation

- Added one heading and one contextual paragraph to `_source/bio.html` and the identically placed generated `bio/index.html`.
- Added `_tests/test_turn19_bio_evidence_routes.py` with source-generation parity, destination and anchor, unique-ID, biography/download, copy-control and fail-open history checks.
- Added SHA-gated test-only `_tests/turn19_bio_evidence_routes_history.py` for the two modified bio pages, with a narrow hook in `_tests/turn12_cross_platform_history.py` and `_tests/brand_positioning_history.py`. Production builders do not use these adapters.
- Left both public biography texts, their .txt downloads, canonical URL, Person identity, descriptions, scripts, copy controls, existing URLs, sitemap and metadata timestamps unchanged. This is a navigation improvement, not republication of the biography.
- No GitHub Actions, cron, new analytics, collection forms, paid services, credentials or confidential personal information.

## Verification

- Reviewed the six-file GitHub compare. Only the two intended site files and four related focused test/history files changed.
- SHA-verified both current public files and their exact previously released blobs.
- Reversed both new files through the test-only predecessor, checked idempotence and fail-open behavior on unexpected mutations.
- Confirmed byte-identical inserted text in source and generated HTML, unique ID, all three source URLs exactly once, preserved three copy controls, no em dashes, and balanced relevant HTML tags.
- Confirmed all three target anchors exist in currently committed published Technology or poker profile pages.
- Parsed all four new or amended Python test/history modules with the local Python AST parser.
- The complete deterministic static-site build, local unittest suite, HTML5 parser and browser suites were **not** run in the available read-only filesystem environment. No full-suite success is asserted.

## Publication

- [PR #175](https://github.com/nolankido/nolankido.github.io/pull/175) squash-merged to `main` as commit `291e00f9b6a7ab0102cbb946a3e26924a254e176`.
- GitHub main source, compiled bio and focused test were re-fetched and byte-matched against the approved release.
- Live canonical [biography](https://nolankido.com/bio/#profile-evidence-routes) was fetched after deployment propagation. Its newly published heading and all three contextual destination links were present in the rendered public HTML.

## Next improvement direction

Prioritize a distinctive, source-verified new piece of practical work rather than multiplying navigational pathways. A second poker episode companion is an attractive next step only after the final video cut and hand chronology are reviewed; a new AI case can instead be chosen if it offers stronger public evidence. Quantify search or AI-answer performance only from primary measurements when available and authorized.
