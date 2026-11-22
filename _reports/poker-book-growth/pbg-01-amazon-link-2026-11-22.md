# PBG-01: Amazon Kindle destination incorporated

**Date:** November 22, 2026  
**Work:** How to Play No-Limit Texas Hold'em  
**Author:** Nolan Kido  
**Outcome:** Author-provided Amazon Kindle URL incorporated into first-party pages; independent retail details still await inspection.

## Author-provided destination

- Exact URL: https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324
- ASIN parsed from that URL: `B0HSB98324`
- Source: direct author message in this sprint on November 22, 2026
- Book manuscript metadata, separately supported by the author's production archive: subtitle *A Beginner's Guide for Live Tournaments and Cash Games* and *2027 Edition*
- Direct Amazon product-page content could not be inspected through the available public retrieval path, so the retailer title, author byline, Kindle format selection, live availability, price, publication date, ISBN, cover, ratings and reviews are not represented as independently verified.

## Implemented changes

1. `_source/books/how-to-play-no-limit-texas-holdem.html` and generated `books/how-to-play-no-limit-texas-holdem/index.html`: a prominent native, keyboard-accessible CTA near the book title, displaying "View the Kindle eBook on Amazon" with the exact author-provided URL and a clear source/availability caveat. The original free instruction and companion links remain present.
2. `_source/books/index.html` and generated `books/index.html`: one contextual Amazon link in the poker book entry. The other author's book is not assigned this ASIN.
3. `assets/book-reader-journey.css`: scoped CTA styling with a 44-pixel minimum click target, visible keyboard focus, mobile wrapping, high-contrast fallback and print rules. The book page stylesheet query changed to `v=20261122`.
4. Click instrumentation on both external CTAs: `data-umami-event="poker-book-kindle-amazon-click"`, with distinct `data-umami-event-source` values `book-page-hero` and `books-catalog`. This is HTML instrumentation only; no event has been observed in the analytics backend during this turn.
5. `downloads/nolan-kido-book-edition-evidence.json`: added `author_supplied_product_url`, `author_supplied_asin`, `source_type`, and `supplied_on` for the poker Kindle row. The separately defined `retailer_product_url`, `retailer_asin`, print ISBN and other independently verified retail fields remain `null`. All six formats retain `not_verified` statuses until a public listing can be matched.
6. `downloads/nolan-kido-book-edition-verification.md`: clarified the author-provided link and revised the publisher-first verification instructions to distinguish links from independent claims.
7. `_scripts/book_pages.py` and `sitemap.xml`: the Books catalog revision is dated November 22, matching the updated Book catalog JSON-LD. The poker book revision remains dated November 22; the unrelated AI book remains dated November 20.
8. Adapted existing regression expectations in `_tests/test_turn47_book_edition_evidence.py`, `_tests/test_turn48_book_reader_journeys.py` and `_tests/test_turn49_book_catalog_handoff.py` for the specific authorized URL, provenance, unique CTA, and honest modification dates.
9. `README.md`, `AGENTS.md`, and the earlier PBG-01 retail audit now point to the superseding author-provided Kindle destination rather than treating the previous no-link state as current.

## Safety and quality gates

- No unsupported Amazon prices, ISBNs, claims of stock, ratings, retailer publication dates, or retailer cover images added.
- No paperback or hardcover URLs inferred from the eBook URL.
- The existing Book JSON-LD author identity and WebPage schema remain present; no unverified `offers` schema was fabricated.
- No GitHub Actions workflows or paid analytics services added.
- Source and public HTML are intended to remain byte-identical; verify after repository write.
- Existing local tests must be run from a full checkout because connected file writes do not execute repository Python or browser suites.
- Source commits do not prove that Cloudflare served the exact same bytes or that Google indexed the new copy. Perform a separate live GET / local smoke as available.

## Recommended acceptance commands, full local checkout

```bash
python _scripts/build_books.py --check
python _scripts/build.py --check
python -m unittest discover -s _tests -p 'test_*.py' -v
python _scripts/check_search.py --verify-snapshot _reports/search-audit.json
python _tests/check_html5.py
python _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2
```

The last live diagnostic needs network access after deployment. A deployment receipt is not the same as a search visibility observation.

## Remaining retail check

Inspect the public Amazon detail page, preferably via the author's KDP `View on Amazon`, to compare the displayed work, chosen format and byline with the author's title/subtitle. Once matched, promote the format's evidence state with the required regression updates. Until then the author-provided URL is safe to label as such but is not independently authenticated retail metadata.

## Next growth turn

**PBG-02: establish a dated Google/Bing/AI search and Amazon-click baseline.** Treat unavailable GSC metrics as unknown, not zero. Compare the two CTA source values after actual Umami events arrive and avoid conflating click counts with orders.
