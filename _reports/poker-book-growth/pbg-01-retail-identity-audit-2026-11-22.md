# PBG-01: No-limit Hold'em book retail identity audit

**Sprint:** POKER-BOOK-GROWTH
**Turn:** PBG-01
**Review date:** 2026-11-22
**Decision:** PARTIAL IMPLEMENTATION; HOLD ON BUY LINKS

## Objective

Confirm the work identity and edition-specific Amazon destinations before marketing or measuring Amazon book clicks. The owner describes the book as currently on Amazon, but an exact format, public retailer page and identifier are still required before using a specific retailer link on this website.

## Evidence observed

### Author-controlled production metadata, not retail verification

The owner's archived Kindle production instructions identify:

- Title: *How to Play No-Limit Texas Hold'em*
- Subtitle: *A Beginner's Guide for Live Tournaments and Cash Games*
- Author: Nolan Kido
- Edition label: 2027 Edition

An archived production file or reported submission is **not** a confirmed public Amazon listing, ASIN, publication date, or official retailer cover. The source was inspected via connected private author files; private document IDs, account details and screenshots are deliberately omitted from this public report.

### Independent retail check

- Targeted public searches for the exact author/title/subtitle did not yield an independently authenticated exact-format product page.
- Direct Amazon product content was not retrievable through the web search pathway used in this review.
- A missing result, robots restriction, or inaccessible listing does **not** prove the edition is unpublished or unavailable.
- Kindle, paperback and hardcover remain `not_verified` in the public edition ledger. No ASIN, ISBN, marketplace price, official retail cover, rating, offer, or stock claim was asserted.

## Work implemented

1. Added the author-controlled subtitle and 2027 Edition information to the canonical poker book page, with an explicit retail-evidence boundary.
2. Preserved byte-for-byte equality of `_source/books/how-to-play-no-limit-texas-holdem.html` and `books/how-to-play-no-limit-texas-holdem/index.html`.
3. Updated the poker book's `WebPage.dateModified` and the matching sitemap `lastmod` to 2026-11-22 without altering the separate Books catalog or unrelated AI book date.
4. Improved the standalone book registry to validate/generate dates per work, preserving the original catalog date.
5. Updated two historical book-journey regression tests to expect the actual revised poker book date while retaining the November 20 dates for unchanged book routes.
6. Added a separate `author_archive_metadata` record to the public JSON evidence ledger without changing any format-specific retail status.
7. Added a November 22 explanatory note to the existing retailer verification guidance.

## Verifications actually performed

- Read back all eight changed repository files after commits.
- Confirmed source/public HTML equality, one H1, Book-to-author identity, correct metadata/date, the exact subtitle and edition visible in the HTML, and no em dash in the book HTML.
- Parsed the page's JSON-LD and the public retail JSON evidence ledger.
- Confirmed no unsupported `Book.offers`, `isbn`, or `datePublished` and no invented Amazon links or ASINs.
- Checked the poker book sitemap `lastmod` is 2026-11-22 while the unrelated book remains 2026-11-20.
- Checked the registry and two regression-test assertion changes statically.

**Not performed:** complete repository build/test suite, 320px browser QA, or live deployed-byte comparison. Those require a full local checkout/build and deployment access; source-level checks must not be described as full test execution or live publication.

## Gate to finish PBG-01

For each retail format that actually exists:

1. In the owner's KDP Bookshelf, use the specific format's `View on Amazon` action and confirm its `Live` state.
2. On that exact public marketplace page, confirm the full title/subtitle, Nolan Kido byline, chosen format, ASIN and any applicable print ISBN.
3. Record the publicly observable cover, marketplace URL and observation date. Do not copy account-private details into GitHub.
4. Only then add the format-specific retailer link to the poker book page, update schema where genuinely supported, test a browser click-through, and update the edition ledger's corresponding status.

The gate is **blocked by missing authenticated format-specific retailer evidence**, not by a demonstrated publication failure.

## Next sprint turn

**PBG-02:** record a dated search and referral baseline with only accessible free first-party metrics. Google Search Console data via GSC Wizard was not available in this session due to an inactive paid connection, so use direct free Search Console/Bing exports if available; record unavailable metrics as `unknown`. PBG-01 retail validation remains an open dependency before an Amazon buy button or attributable outbound-click experiment.
