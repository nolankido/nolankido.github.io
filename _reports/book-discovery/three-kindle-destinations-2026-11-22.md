# Three Kindle destinations: site integration and evidence

**Review date:** November 22, 2026  
**Repository:** `nolankido/nolankido.github.io`  
**Scope:** Author-provided Amazon.com Kindle links, first-party book discovery and retail provenance.

## User-provided URLs

| Work | Exact author-provided Kindle URL | ASIN |
| --- | --- | --- |
| How to Play No-Limit Texas Hold'em | https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324 | `B0HSB98324` |
| One Workflow at a Time | https://www.amazon.com/One-Workflow-Time-Nolan-Kido-ebook/dp/B0HRQNCP7Y | `B0HRQNCP7Y` |
| AI Works, Human Decides | https://www.amazon.com/Works-Human-Decides-Nolan-Kido-ebook/dp/B0HSF8K76R | `B0HSF8K76R` |

These are **author-supplied exact URLs**, not inferred search results. No affiliate or attribution parameters were appended.

## Amazon reachability limit

A public fetch of the two newly provided URLs returned the same Amazon final URL but an Amazon **Continue shopping** interstitial instead of the product-detail document. The web search pathway also did not yield independently inspectable listing data. Accordingly, author/title match as displayed by Amazon, exact format selection, live status, cover, edition dates, Kindle Unlimited, current price, ratings and reviews **are not independently verified**. A shopping interstitial is not proof of a broken URL or a confirmed live listing.

## Website changes

1. `/books/one-workflow-at-a-time/`: One early Kindle link in the title area, with exact ASIN, explicit author-provided context, and existing free learning materials retained. The canonical author's Book JSON-LD still has no unsupported `offers`, `isbn`, `datePublished` or `aggregateRating`.
2. `/books/`: Three visible work choices. The original two canonical first-party book cards remain; the additional *AI Works, Human Decides* card includes the exact author-provided Amazon link and a free related reading route. This third book is recorded as a schema `mentions` Book tied to the existing author identity, without unsupported retailer offers. The two-work main `ItemList` intentionally stays limited to works with dedicated first-party pages.
3. `assets/book-reader-journey.css`: Accessible native CTA for One Workflow, with a 44px minimum target, keyboard focus outline, mobile wrap, high-contrast fallback and print handling. No additional JS or service is required for the anchor to work.
4. First-party click labels (not independently observed analytics events):
   - Poker: `poker-book-kindle-amazon-click`
   - One Workflow: `one-workflow-kindle-amazon-click`
   - AI Works, Human Decides: `ai-works-human-decides-kindle-amazon-click`
5. `downloads/nolan-kido-book-edition-evidence.json`: The existing two full format matrices remain under `works`. The One Workflow Kindle entry now contains author-supplied URL/ASIN metadata; *AI Works, Human Decides* is a separately recorded supplementary title. The three formats for each original work remain `not_verified` independently, with unknown retailer fields null.
6. `downloads/nolan-kido-book-edition-verification.md`: Now records all three author-supplied Kindle URLs and the independent verification boundary.
7. `_scripts/book_pages.py` and `sitemap.xml`: Reflect the revised One Workflow page with a truthful 2026-11-22 modification date, preserving canonical routes. The book catalog and poker page are already dated 2026-11-22.
8. Existing Turn 47, 48 and 49 book regression tests were adjusted to preserve link identities, source-output parity, original free exercises, unknown retail status and modification dates.
9. `README.md` and `AGENTS.md`: Document the link identities, third-title distinction and migration boundary. No GitHub Actions, new paid service, redirects or invented product claims.

## Live-site retrieval

Public content fetching on November 22, 2026 confirmed:
- `https://nolankido.com/books/` served the three-title page and exposed **all three exact Amazon URLs** as anchor destinations.
- `https://nolankido.com/books/one-workflow-at-a-time/` served the newly written Kindle CTA with its author-supplied ASIN.

This is confirmation of public links and served website content, **not** a retailer product-content verification or an observed Amazon sale.

## Quality gates

- Source files and generated public HTML copies must remain byte-identical for both touched standalone book pages.
- Main `Book` structured data must retain Nolan Kido Person identity and not fabricate offers, publication dates, cover art, pricing, ISBNs or ratings.
- No print listing may be inferred from a Kindle URL.
- The additional third title does not yet have its own canonical first-party page or full three-format evidence matrix. Adding that route is a separate build, sitemap, Find, structured-data, biography and tests migration.
- A full checked-out repository Python build and browser QA should be performed. Static checks and public retrieval do not establish full test-suite success.
- Outbound click events must be observed in Umami before any analytics claim about click totals can be made.

## Next recommended improvement

Create a dedicated, well-evidenced first-party author page for *AI Works, Human Decides* and integrate it through the normal book registry, site map, local Find and identity projection in a separate controlled turn. For the poker-book growth sprint, continue with the search and click-through baseline while preserving all three Kindle destinations.
