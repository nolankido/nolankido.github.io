# Visibility sprint, Turn 15: Direct links to inspectable AI and poker work

**Review date:** November 3, 2026  
**Site:** https://nolankido.com/  
**Objective:** Make Nolan Kido's documented practical AI investigations and independently sourced tournament-poker profile easier to discover from the site's two strongest identity entry points.

## Verified internal-link gap

Before this turn, the homepage had no direct visible `href` link to any of three existing, published, canonical pages:

1. [Running local AI on a gaming laptop](https://nolankido.com/technology/local-ai-gaming-laptop/)
2. [Independent review-reply evidence audit](https://nolankido.com/technology/review-reply-evidence-audit/)
3. [Nolan Kido tournament-poker player profile](https://nolankido.com/poker/nolan-kido/)

About linked the player profile but neither of the two new evidence-oriented AI pages. All three destinations existed before this change and were verified independently from the repository, with their own canonical URLs. This was an internal discovery gap, not a missing page or a search-engine indexing failure.

[Google's link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) recommend ordinary crawlable `<a href>` links and relevant, descriptive anchor wording.

## Published changes

- [Home](https://nolankido.com/) now follows the existing three featured AI project cards with two deeper investigations: a gaming-laptop local-AI guide with benchmark limits, and an independent audit of archived fictional review replies with no implied production error rate.
- Home's personal-introduction section now links directly to the independent tournament-player record with a caveat distinguishing third-party finishes from first-person analysis.
- [About](https://nolankido.com/about/) now includes a concise paragraph linking the two AI investigations, their original artifacts and their limitations.
- Retained three featured project cards, four subject destinations, the established philosophy, Person identity, existing URLs and all existing links.
- Original templates and checked-in generated HTML each contain the same new authored paragraph markup.
- No new claim of model performance, laptop benchmark, business results, poker profitability, ranking improvement, external endorsement, or professional credential.

## Changed files and test-only verification

- Edited `_source/home.html` and `index.html`.
- Edited `_source/about.html` and `about/index.html`.
- Added `_tests/test_turn15_evidence_links.py` for duplicate-free links, targets, canonical paths, source/generated parity, preserved layout counts and claim boundaries.
- Added the test-only SHA-gated `_tests/turn15_evidence_links_history.py` predecessor to preserve exactly the prior approved blob set without hiding unrelated changes.
- Linked the prior Turn 14 test predecessor and its focused historical test to the new test-only adapter. This introduces no runtime dependency or build change.

## Verification scope

- Compared authored source and generated paragraph markup for equality.
- Verified exactly one direct Home link to each of the three canonical destinations and matching About links.
- Verified each target page exists with the expected canonical URL and explanatory article content.
- Confirmed three original AI project cards and four subject destinations remain.
- Confirmed the eight reviewed Git blobs exactly matched the review-branch files.
- No GitHub Actions, recurring jobs, paid API configuration, extra trackers or personal information were added.
- The local runtime failed to initialize, so Python syntax, deterministic build, full unit tests and browser suites were not executed. No test-suite pass is claimed.
- No Search Console performance data was available, so no click, impression, indexing, ranking or assistant-citation gain is asserted.

## Publication

- [Pull request #171](https://github.com/nolankido/nolankido.github.io/pull/171) was squash-merged to `main` with commit `9e074db9276a7c568cd1c5409bcfa1c6f513108d`.
- Live verification: After GitHub Pages propagation, the public Home `.visibility-projects` section contained the new evidence paragraph and direct links to the local-AI guide and review-reply audit. The Home `.home-connection` section contained the direct poker-player-profile link with the third-party-finish caveat. The public About `.editorial-grid` section contained the new methods paragraph and both AI links. These observations establish that the links are published, not that their destinations are indexed or that rankings changed.

## Next improvement candidate

Continue a measured inventory of high-value first-party cases and their most relevant incoming internal links. Avoid adding thin or repetitive navigation just to increase link counts; only promote genuinely distinct evidence to readers it would help. If private Search Console query/page data becomes available without an unapproved charge, use it to prioritize the next substantive revision.
