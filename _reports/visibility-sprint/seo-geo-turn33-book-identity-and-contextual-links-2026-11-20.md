# SEO, GEO and AEO Turn 33: Book identity graph and contextual guide links

Date: November 20, 2026 (Hawaii).

## Why this change
Two indexable first-party book pages exist, but three highly relevant
explanatory guides were missing direct links back to them. The book pages
also inherited a generic Creative Work social graphic and described
the *author* as WebPage.about, even though the pages describe books.

## Source-backed implementation
- `/technology/ai-workflow-pilot/`: links to `/books/one-workflow-at-a-time/`
  and the original free AI pilot worksheet. Clarifies that it is an
  author reference, not measured client outcomes.
- `/poker/poker-books-and-courses/`: links to the author's own beginner
  poker book and explicitly distinguishes an author description from an
  independent review or verified retail edition.
- `/poker/no-limit-holdem-guide/`: connects the free complete guide to
  the related book and fictional river-call worksheet.
- Each original guide's Article publication date is preserved.
  Their actual content revision, XML sitemap lastmod and Article
  dateModified are recorded as November 20, 2026.
- Both book pages replace the generic Creative share graphic with existing
  subject-specific 1200-by-630 topic graphics. The alt text states
  clearly that neither is an official book cover.
- Both book pages' WebPage.about points to their Book mainEntity, and
  Book.mainEntityOfPage points back to the same canonical WebPage.
  Book.author continues to use the approved Nolan Kido Person @id.

## Evidence limits
No verified Amazon detail URL, ASIN, ISBN, actual cover file,
publisher edition, price or publication date was found for either
book. Do not infer an edition or ranking improvement from this update.
Existing page canonical URLs, on-site search, published article dates,
book worksheet URLs and the original book author identity remain stable.

## Verification
Source and generated page copies were updated with identical in-body
links and metadata. The three guides retain their earlier reading time
estimates. Book source/output page parity, JSON-LD graph relations,
preexisting image asset paths, and sitemap dates received targeted
checks. Regression cases were added to `_tests/test_book_pages.py`.
The full local Python builder, HTML5, browser suite and Search Console
reports were not run in this connector-only edit. Do not restore
GitHub Actions or introduce paid API checks.
