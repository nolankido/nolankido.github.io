# SEO/GEO improvement Turn 47: Two author works, six unverified retailer editions

**Review date:** November 20, 2026 (Pacific/Honolulu)  
**Site:** https://nolankido.com/  
**Canonical author catalog:** https://nolankido.com/books/  
**Starting GitHub main:** `3a23dd5aacb2d8f06f1b671de445e9b4e0e711c4`  
**Roadmap position:** Turn 47 of the planned 37 to 61 sprint, Phase C.

## Result

The two first-party book descriptions are real public author resources with their own existing canonical pages, free original exercises and Book schema linked to `https://nolankido.com/about/#nolan-kido`. However, the available source checks **did not establish an exact Amazon product page for either work**, much less each distinct eBook or print format.

The right outcome is a **six-format edition evidence ledger with explicit unknowns**, not a guessed retailer offer, official cover or missing-publication claim. A public title search can omit a newly released product and an author-written summary is not an independent retail record.

### First-party works versus retailer editions

| Public author work | Kindle eBook | Paperback | Hardcover |
| --- | --- | --- | --- |
| [One Workflow at a Time](https://nolankido.com/books/one-workflow-at-a-time/) | Not independently verified | Not independently verified | Not independently verified |
| [How to Play No-Limit Texas Hold’em](https://nolankido.com/books/how-to-play-no-limit-texas-holdem/) | Not independently verified | Not independently verified | Not independently verified |

**Important:** `not_verified` is not `not_published`, `unavailable`, `out_of_stock` or `not_for_sale`. No accessible authenticated KDP Bookshelf session or exact public `View on Amazon` listing for these six possible formats was established in this turn. Targeted public title, author and retailer web searches gave no reliable matching product identifiers, but those searches are incomplete and cannot rule out publication or recent indexing delay. The linked author site pages remain public and useful regardless of storefront status.

There is no independently verified public product ASIN, print ISBN, exact format listing, imprint, price, cover or retailer publication date to add. No Kindle Unlimited enrollment or live KDP status is inferred.

## Primary publisher sources checked

1. **Exact product detail URL:** [KDP, How to find your book on Amazon](https://kdp.amazon.com/en_US/help/topic/GPYDJ3SECAVVPNVG). The owner can find the precise live product page via the KDP Bookshelf's `View on Amazon` menu rather than interpreting a search snippet as an edition.
2. **Publication state:** [KDP, Book Status](https://kdp.amazon.com/en_US/help/topic/G200627450) distinguishes `Draft`, `In Review`, `Publishing`, `Live` and other statuses. A Bookshelf-only status is owner account information, not public retail evidence unless the actual product page can also be checked.
3. **ASIN and direct product link:** [KDP, Linking from Your Website](https://kdp.amazon.com/en_US/help/topic/G200652190) explains where to find the actual ASIN and how the exact `/dp/ASIN` destination is formed. Never fabricate an ASIN from a title.
4. **ISBN requirements:** [KDP, What is an ISBN and Imprint Name?](https://kdp.amazon.com/en_US/help/topic/G7DMSKCM9DVS65TC) says paperback and hardcover require ISBNs; a Kindle eBook does not require one. An Amazon ASIN and ISBN-13 have distinct roles, and different print formats have edition-specific identifiers.
5. **Edition linking:** [KDP, Why are my books not linked on Amazon?](https://kdp.amazon.com/en_US/help/topic/GTQGN866DSS6XBD2) lists metadata requirements such as exact title, subtitle, author, language and edition. A live Kindle version does not establish that every print format is orderable.
6. **Timing:** [KDP, Timelines](https://kdp.amazon.com/en_US/help/topic/G202173620) explains why product pages, covers, format linking and Amazon search discovery can appear at different times. A missing search hit is not a confirmed absence.

The six KDP Help pages are primary **instructions**, not primary evidence that these specific author editions are Live. No official Amazon listing was substituted with a third-party lookalike, and no personal KDP email, private account detail or manuscript was published.

## Concrete website changes

- **Books catalog:** Added the native `#books-retailer-evidence` section explaining the exact six-format statuses and connecting readers to original public primary-publisher instructions and the two new evidence downloads. The two existing book-page links remain unique, not duplicated in the new list.
- **Both individual book pages:** Added concise, clearly labeled edition-status explanations at `#ai-book-edition-evidence` and `#poker-book-edition-evidence`. Each retains its main title, original book description and free subject-related exercises, and now provides the format-specific checklist plus a link to the structured ledger.
- **Machine-readable evidence:** Added [`downloads/nolan-kido-book-edition-evidence.json`](../../downloads/nolan-kido-book-edition-evidence.json). It contains two distinct author works, three possible edition format slots per work, and `null` values for **54** unknown retailer-specific details. It does not confuse zero, missing or an empty Amazon search with an unavailable edition.
- **Verifiable reader process:** Added [`downloads/nolan-kido-book-edition-verification.md`](../../downloads/nolan-kido-book-edition-verification.md). It explains how to establish actual Bookshelf state, follow the exact public retailer link for each format, match title/byline/ASIN/print ISBN/cover, and record source, date and human go/no-go decision. Filled KDP or private records stay off this public site.
- **Distribution checks:** Registered both new public downloads in the existing read-only exact-byte inventory `_scripts/check_live.py`.
- **Release regression:** Added ten offline controls in `_tests/test_turn47_book_edition_evidence.py` for six unknown statuses, fail-closed invented ASIN/edition mutations, title and canonical consistency, exact KDP Help sources, public book-source parity, Book schema without unsupported retailer fields, sitemap and download integrity and the no-GitHub-Actions restriction. Added the test to `_scripts/local_release_checks.py`.
- **Maintainer guidance:** Updated `README.md` and `AGENTS.md` with evidence and future retailer-entry standards.

### Identity and date constraints

All **three** existing author pages, including `/books/`, are standalone full HTML with source in `_source/books/` and the exact same committed output under `books/`. No new indexable article was created and no existing canonical changed. The pages already have a meaningful **November 20, 2026** modification date, which remains appropriate to this same-day verification improvement.

The two `Book` identifiers still refer to the **author's works**, not verified products with retail offers. Their existing Person author link stays unchanged. `Book.isbn`, `Book.offers`, `Book.bookFormat`, retailer `datePublished` and `aggregateRating` remain absent. The 1200-by-630 book-topic sharing graphics still clearly state they are **not official covers**. No extra sitemap URLs, duplicate Work entities, invented imprint, book ranking or retailer keywords were added.

## Validation scope

**Performed:** Retrieved the live site and read its author book descriptions; inspected the exact source and generated HTML for all three canonical pages; compared each pair to identical Git blobs after the edit; verified all six ledger format slots and **54** null retailer fields; checked all six publisher URLs exist in the guide; checked original Book structured-data identity and absence of unsupported retailer properties; confirmed one unique catalog link per title, same-day date stamps, unchanged canonical URLs and addition of the two downloadable files to the release inventory. No repository-created GitHub Actions workflows were found.

**Not performed:** An authenticated KDP Bookshelf inspection, a successfully matched public retail listing, direct verified ISBN/ASIN/official-cover inspection, the new Python test suite, a complete local static-site rebuild/HTML5/browser sweep, or post-merge raw HTTP exact-byte verification. The model's local container cannot directly clone GitHub because its network/DNS access remains unavailable. A source consistency check is **not** a passed end-to-end test or confirmation that the new release has propagated to the custom domain.

### Full-checkout release commands

```powershell
py -3 _scripts/build_books.py --check
py -3 -m unittest discover -s _tests -p test_turn47_book_edition_evidence.py -v
py -3 -m unittest discover -s _tests -p test_book_pages.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /books/ --only /books/one-workflow-at-a-time/ --only /books/how-to-play-no-limit-texas-holdem/ --only /downloads/nolan-kido-book-edition-evidence.json --only /downloads/nolan-kido-book-edition-verification.md --attempts 3 --interval 5
```

External sources and the public edition audit should be revisited when an **exact** listing becomes accessible. A verified change must be tied to the corresponding format and actual public product page, not an unrelated title or the author saying the book has been submitted.

## Next roadmap turn: Turn 48

**Improve the book-page reading and acquisition journeys.** Each page should help visitors identify its intended reader, understand the subject, inspect a legitimate teaching sample, use a relevant free original worksheet and, only if independently verified, reach an exact retailer edition. Verify 320-pixel/mobile, keyboard and local navigation as far as actual test tooling permits. Do not publish manuscript excerpts not matched to the final owned edition. Keep retailer status unresolved until source evidence changes.

No GitHub Actions, paid service, new analytics tracker, private files, invented book sales, false search citations or fabricated availability claim was introduced.
