# Visibility sprint, Turn 14: Accurate sitemap freshness for substantive revisions

**Review date:** November 3, 2026  
**Site:** https://nolankido.com/  
**Objective:** Keep the site's last-modified signals truthful after significant source-verified updates to Nolan Kido's practical AI, technology and poker pages.

## Verified problem

The published XML sitemap still reported October dates for four canonical landing pages, although their main content, visible links or structured identity metadata were materially updated on November 3. Google Search Central says `lastmod` should reflect real significant updates and that Google may use dates that prove consistently accurate. [Official guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).

This is a crawl-hint accuracy correction, not a promise of better ranking or faster indexing.

| Page | Previous sitemap date | Corrected date | Evidence of a substantive change |
| --- | --- | --- | --- |
| [Home](https://nolankido.com/) | 2026-10-28 | 2026-11-03 | Updated public identity links and Person markup in [Turn 12](https://github.com/nolankido/nolankido.github.io/pull/168) |
| [About](https://nolankido.com/about/) | 2026-10-28 | 2026-11-03 | Updated visible public work links and identity context in Turn 12 |
| [Technology](https://nolankido.com/technology/) | 2026-10-28 | 2026-11-03 | Added a substantive practical-AI evidence and poker comparison in [Turn 13](https://github.com/nolankido/nolankido.github.io/pull/169) |
| [Poker](https://nolankido.com/poker/) | 2026-10-15 | 2026-11-03 | Added public-video discovery in [Turn 11](https://github.com/nolankido/nolankido.github.io/pull/167) and a substantive solver-judgment section in Turn 13 |

## Changes

- Updated exactly four `updated` fields in `_source/pages.json` to November 3, 2026, preserving all other page metadata.
- Updated exactly four corresponding `<lastmod>` values in the existing `sitemap.xml`. The 199 canonical URLs and all other 195 dates are unchanged.
- Aligned the Home, Technology and Poker `dateModified` JSON-LD values with the same date.
- Left the About ProfilePage's optional `dateModified` absent because the site deliberately refuses to invent a timestamp from a calendar day.
- Kept page titles, copy, publication dates, navigation, canonicals, content links, main scripts, HTML layouts, feed history and robots policy unchanged.
- Added `_tests/test_turn14_sitemap_freshness.py` and an exact, SHA-gated test-only predecessor `_tests/turn14_freshness_history.py`. Two previous historical tests and their adapter are connected to that predecessor, without hiding unknown edits.
- No GitHub Actions, cron, scheduled jobs, paid API changes, personal details or new runtime dependencies.

## Verification

- Parsed the 114-page source manifest; exactly four `updated` fields differ from the preceding commit.
- Compared all 199 previous/current sitemap URL and date pairs; exactly four dates differ and no canonical URL changed.
- Parsed the three affected JSON-LD scripts; each has one `dateModified` matching the corrected sitemap date.
- Verified the existing About ProfilePage keeps its intentional omission of a day-only `dateModified`.
- Python AST syntax parsing succeeded for all modified and added test-only Python files.
- Confirmed each of ten expected Git blobs on the review branch before merging.
- The full Python site builder, unittest suite, HTML validator and browser suites could not run in this read-only workspace. No such pass is claimed.
- No new Search Console performance claims are made because authenticated performance data was not available.

## Publication

- [Pull request #170](https://github.com/nolankido/nolankido.github.io/pull/170) was squash-merged into `main` on November 3, 2026 with commit `d9c9944e0c144bb2b4e4759c543fbf1834b71e6a`.
- The merged commit was checked on the GitHub main branch and contains the exact expected new sitemap blob.
- Public URL verification: the public [sitemap.xml](https://nolankido.com/sitemap.xml) was fetched after GitHub Pages propagation with element-scoped XML extraction. All 199 `<url>` elements were present, and Home, About, Technology and Poker each returned `<lastmod>2026-11-03</lastmod>`. The remaining rows retained their existing dates. Public HTML pages were reachable, but the extractor suppresses embedded JSON-LD scripts; structured dates were therefore verified in the merged Git blobs, not through that text extractor.

## Next turn

Resume actual query/page opportunity analysis only after the owner has accessible Search Console data without new paid charges. Until then, continue bounded public crawl and content-quality checks. Do not date-bump untouched pages automatically, since that would make `lastmod` less trustworthy.
