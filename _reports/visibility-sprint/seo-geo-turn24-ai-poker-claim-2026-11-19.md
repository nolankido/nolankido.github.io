# SEO/GEO/AEO visibility sprint, Turn 24 of 25

**Date:** November 19, 2026 (Honolulu)

**Scope:** A concrete, source-bounded nonbranded answer and native discovery pathway between practical AI verification, poker research and Nolan Kido's public authorship.

**Primary answer:** https://nolankido.com/technology/check-ai-answers/#review-poker-solver-claim

## Observed gap and selected change

The AI-answer checking guide already contained six general review methods and a dated Google AI Overviews claim audit. The poker solver-fit guide already contained an independently reproduced fictional 10 BB bubble comparison. A reader arriving through a generic AI-checking query did not have an example connecting numerical correctness to an inappropriate recommendation, and a poker reader had no direct route into the general AI claim-checking framework. No real Search Console query, click-through, AI assistant citation or traffic change is inferred from that site-content gap.

The original general guide now answers **“How do you check an AI answer that recommends a 10 BB bubble call?”** at a new fragment of the existing canonical. The new example explicitly invents its supposed AI claim, and checks each part against the preexisting public model. A descriptive early jump link and three inbound links from the Technology hub, poker solver-fit guide and poker research map provide native, crawlable context. Its answer also links to the already established author identity evidence. These are content and discovery improvements, not newly measured search results.

## Bounded claim-to-evidence check

| Element of the invented claim | Reproducible evidence | Correct use |
| --- | --- | --- |
| A call needs 45% showdown win probability | 9 BB additional call into a final 20 BB contested pot, after returning unmatched chips; direct no-tie chip price is 9 / 20 | Supported only as a chip-EV threshold for the specified closed-action fictional hand |
| That 45% is enough to justify a bubble call | Classic-ICM model with 40/30/20/10 BB pre-post stacks and $50/$30/$20/$0 prizes; modeled fold equity $12.286143 and call-win equity $21.785714 | Contradicted for that prize-equity objective; corresponding no-tie threshold is about 56.40% |
| The player should call | No actual hand, opponent range or observed showdown probability was supplied; the illustrative 50% probability is invented | Unresolved. Neither chip threshold nor classic-ICM model makes a real-hand recommendation |
| Nolan's Portland Meadows 6-4 decision is proven by the model | His separate first-person account has different blinds and antes, without the full field stacks, payout ladder and ranges | Not established; the article links that distinct account explicitly as unverified for solver analysis |

**Sources and boundaries:** `/poker/evaluating-poker-advice/#solver-fit-test` states the conditions, `/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble` records all three branches, and `/downloads/ten-bb-bubble-icm.py` enumerates exact ICM fractions offline. The new article links all three once. No new solver, chatbot, source document, strategy recommendation, actual hand evaluation or AI citation observation was invented. The content is for after-play study only.

## Files and publication structure

1. `_source/technology/check-ai-answers.html` adds the direct answer and early jump link, preserving its older Google claim audit, historical November 18 source check, six review methods, original Article date and existing fragments.
2. `_source/poker/evaluating-poker-advice.html` links from inside the bounded solver example to the AI audit without changing the underlying model; `_source/poker/poker-research-guide.html` points from source-reading advice to the same audit.
3. `_source/technology/home.html` adds a descriptive answer link alongside its existing Google guidance example.
4. `_source/pages.json` registers genuine November 19 updates to the four changed canonical pages, retaining the October 12 or October 8 original Article publication dates. The research guide now includes a short revision note.
5. `assets/answer-review.css` separates two adjacent source-audit sections, using the existing site style and native anchors with no JavaScript.
6. New `_tests/test_turn24_ai_poker_claim_bridge.py` reproduces the mathematics, checks inbound source and built-page links, validates canonical/Article/sitemap agreement, and rejects mutated unsupported conclusions. Existing date-sensitive Turn 7, Turn 21 and Turn 22 tests reflect subsequent real revisions, not a backdated publication.
7. README and AGENTS record the new public route and precise truth boundaries. The deterministic builder refreshes the public static HTML, existing feeds, Find outputs and sitemap. No new canonical article, Person identity, `FAQPage` schema or workflow was created.

## Local validation

- `python _scripts/build.py`: 253 generated files built; 15 initial output changes, followed by one regenerated stylesheet fingerprint reference after the CSS adjustment.
- `python _scripts/build.py --check`: 253 generated files checked, 0 drift after final source changes.
- `python _scripts/check_search.py`: 224 manifest pages, 225 sitemap URLs, 0 errors.
- `python _tests/check_html5.py`: 230 HTML pages parsed, 0 failures.
- `python _scripts/check_internal_links.py`: 232 HTML pages, 16,329 internal links, 0 issues.
- Turn 24 tests: 5 passed, including negative claim mutations and source-to-output parity.
- Turn 21 Google claim-audit tests: 4 passed; original source audit and anchor retained.
- Turn 22 solver-fit tests: 4 passed; original model and anchor retained.
- Turn 12 independent ten-blind ICM tests: 5 passed.
- Turn 7 answer-guide tests: 5 passed after replacing a stale exact modification-date assertion with a non-backdating and manifest parity check.
- Turn 126 Article method-link tests: 4 passed.
- `git diff --check`: no whitespace errors.

Several exploratory older tests still contain unrelated historical snapshot assumptions, including an older Technology introduction anchor in `test_turn26_technology_first_screen.py` and previous unrelated site file hashes in `test_study_interest.py`. Neither failure is counted as a successful check. The broad historical regression suite and browser-rendering suites are not claimed to pass.

## Release and measurement boundary

After merge, compare each changed public HTML, existing feed, sitemap and stylesheet byte-for-byte against the tested local output. A passing build and live-byte comparison establish technical publication, **not** Google indexing, rankings, answer-engine retrieval, assistant citations, impressions, click-through or conversions. The frozen 25-question branded/nonbranded panel remains unchanged and unobserved here. No paid SEO connector, private analytics, automation, live-play tool, GitHub Action or background task is introduced.

**Suggested final Turn 25:** Close the sprint with a precise measurement and maintenance handoff: reconcile the 25-turn shipped-change ledger, choose the highest-value Search Console and assistant-answer checks the owner can run, and distinguish confirmed visibility outcomes from unmeasured publication work.
