# PBG-03: Reader-first poker book landing page

**Sprint:** POKER-BOOK-GROWTH, Turn 03 of 25  
**Date:** November 22, 2026, Pacific/Honolulu  
**Canonical page:** https://nolankido.com/books/how-to-play-no-limit-texas-holdem/  
**Amazon Kindle destination:** https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324  
**Status:** Source and public HTML updated in GitHub; live deployment check inconclusive. Source review passes, executable local suite and browser QA remain pending.

## Objective

Make a reader arriving from Google or an AI answer understand the book's relevance to beginner no-limit Hold'em before deciding whether to click through to Amazon. Offer a useful no-wager teaching example as a genuine alternative, not an interruptive purchase wall. Preserve evidence and author provenance boundaries.

## Before

The page's hero contained a title, manuscript-derived subtitle and edition label, and one author-supplied Amazon button. A reader had to continue to later explanatory sections to learn the scope of the material or find a practice opportunity. The introduction to the intended reader was broad and the free learning resources were present but lacked an explicit beginner study sequence. An existing historical reader regression also expected a prior CSS cache key and exact page-hero class, despite newer committed book-page assets.

## Implementation

1. **First-screen reader promise:** The hero now explains in plain language how to follow a hand, see the effect of position and betting, and evaluate the price of a call. This is a description of the author's educational intent, not a verified table of contents or sales guarantee.
2. **Two paths to act:** The exact Amazon Kindle link remains the primary labeled action and retains `poker-book-kindle-amazon-click` with `data-umami-event-source="book-page-hero"`. A new native `#poker-book-first-exercise` link offers a site-original free hand review before purchase. Its landing target already exists.
3. **Three compact learning goals:** Hand sequence, reasoning from position/ranges/pot odds, and cash-versus-tournament context. No claims of solver certainty, a number-one book ranking, or winning outcomes.
4. **Reader-fit clarification:** Specifically identifies adult new players, returning players and readers looking for reasoning rather than chart memorization; discloses the role of stacks, opponents, rake, payouts and rules.
5. **New substantive study route:** Added a separate three-step section with real free destinations: `/poker/free-poker-learning-path/`, `/poker/poker-math-reference/`, and `/poker/no-limit-holdem-guide/#choose-your-route`. This is an independently written site study path, not an excerpt or copied retail TOC.
6. **Improved navigation labels:** The existing four keyboard-native on-page links retain their actual fragment destinations, now labeled for reader tasks.
7. **Mobile and accessible styles:** The modified page gets `book-reader-journey.css?v=20261122-pbg03`. The scoped CSS turns the two actions and three outcome columns into single-column layouts below 760px, keeps 44px controls, strong focus outlines, 480px support, forced-color affordances, and print fallback. It does not change CSS ownership on the One Workflow page.
8. **Catalog accuracy:** The book's existing bottom link now mentions the site's three author-supplied titles rather than claiming there are two.

## Preserved contracts

- The page keeps one canonical URL, one H1, the same Book and Person identifiers, and unchanged within-day `2026-11-22` WebPage `dateModified`.
- The author-provided Amazon href is unchanged: `B0HSB98324`, exactly once as an outbound anchor; no duplicate event or extra tracking provider.
- The 20-counter pot / 10-counter bet / 10-counter call yields 40 counters, with `10 / 40 = 25%` preserved. The separate hypothetical 20% equity answer remains labeled fictional.
- The original study-sheet download and all four original reader navigation destinations remain available.
- Retailer price, live status, reviews, official cover, print editions, ISBN, rating, publication metadata and Kindle Unlimited enrollment are not invented.
- The two other Amazon book ASINs `B0HRQNCP7Y` and `B0HSF8K76R` are unchanged in the catalog.
- No JavaScript purchase intercepts, automatically opening windows, forced redirects, external scripts or GitHub Actions were added.

## Committed repository changes

- `_source/books/how-to-play-no-limit-texas-holdem.html`
- `books/how-to-play-no-limit-texas-holdem/index.html`
- `assets/book-reader-journey.css`
- `_tests/test_turn48_book_reader_journeys.py`
- `_tests/test_pbg03_poker_book_landing.py` (new, ten focused offline test methods)
- `_scripts/local_release_checks.py`

The new tests include source/output parity, hero ordering, one exact Amazon CTA/event, free exercise landing and mathematical continuity, three linked study routes, structured-data limits, scoped responsive/focus/forced-color CSS, other-book regression, mutation probes, and mandatory local test inclusion.

## Verification actually performed

The changes were read back from GitHub and passed **33 source-consistency checks**, including exact source/public equality, one H1, Amazon URL and event preservation, native free-example destination, three outcomes and study steps, known destination URLs, unmodified fictional exercise, evidence boundaries, scoped CSS, other-book and catalog preservation, registered tests, and matching date metadata.

The referenced `#choose-your-route` anchor was inspected in the existing Hold'em guide source. All three study-route HTML destinations were found in the repository. These checks establish navigational wiring, not browser layout or an actual click.

**Not executed:** complete local Python unit suites, deterministic `build.py --check`, HTML5 parsing of the full site, automated real browser reflow at 320px and desktop, and independent exact-byte public deployment verification. Live content retrieval through the available public tools failed on this turn. Do not call the public deployment verified from the code commit alone.

## Local acceptance commands

From a complete current checkout:

```powershell
py -3 _scripts/build_books.py --check
py -3 -m unittest discover -s _tests -p test_pbg03_poker_book_landing.py -v
py -3 -m unittest discover -s _tests -p test_turn48_book_reader_journeys.py -v
py -3 -m unittest discover -s _tests -p test_book_pages.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _tests/diagnose_live_crawl.py --scope priority --attempts 2 --interval 2
```

At both **320px** and desktop, verify no horizontal scrolling, clear title/subtitle and action hierarchy, readable action labels, keyboard focus/Enter behavior, action landing at the free example, correct `details` open/close behavior, and return navigation to the Kindle CTA. Browser and production verification should not be inferred from static media queries alone.

## Outcome metrics and next turn

The prior PBG-02 source baseline is **3 of 11** selected poker educational pages linking directly to the book. This turn changes the book landing page, so that source acquisition denominator remains **3 of 11**. Actual Umami clicks, pageviews, Google results, generative-AI citations, Amazon orders and conversion change are still unknown, not zero.

**Next improvement: PBG-04.** Add carefully chosen contextual links from high-fit free poker learning pages to the book page, without duplicating or withholding useful lessons. Prefer the learner route, basic rules, decision/practice and math pages identified in the frozen baseline. Compare direct-link coverage against the frozen 11-page cohort, then use actual search/Umami measures only when source access and dates are confirmed.
