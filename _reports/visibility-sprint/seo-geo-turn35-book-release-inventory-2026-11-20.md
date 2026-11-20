# SEO, GEO and AEO Turn 35: Bring standalone books into release audits

Date: November 20, 2026. Base main commit: `9408f983a9793e521390e7f346127ce545807047`.

## Problem observed
The site had gained two standalone book pages and their companion downloads,
but the release audit still treated them as unapproved extra sitemap URLs.
The HTML5 publication inventory omitted them, the exact-byte live checker
did not include them or their free worksheets, and the standard local release
checklist did not execute the book-specific builder or tests.

A second observation: `_reports/search-audit.json` still recorded 200 URLs
from an older snapshot, whereas the committed sitemap now contains 228
distinct canonical URL records.

## Fixes
- Register source-validated book canonical URLs in `check_search.audit`
  before comparing the sitemap to approved indexable pages.
- Add both standalone HTML pages to the HTML5 inventory.
- Add both book pages, two original companion Markdown worksheets and two
  existing topic-image files to `check_live.targets`, which verifies exact
  deployed response bytes when used on a network-capable checkout.
- Make `build_books.py --check` and `test_book_pages.py` mandatory in
  `local_release_checks.py`.
- Update existing player and release-integrity regressions from six to
  eight separately owned indexable pages, and test book route coverage
  against sitemap and exact-byte live targets.

## Checked-in source inventory
- 228 distinct sitemap URL entries.
- 225 manifest-backed pages, including 5 intentionally non-indexed utilities.
- 8 separately published pages: Nolan Poker player profile, 3 video
  companions, one local laptop case, one reply audit and 2 books.
- 133 article pages in the generated manifest, comprising 97 article-flagged
  original manifest entries and 36 Living Well essay/guide/experiment
  entries. Both books are `WebPage` documents with `Book` main entities,
  not articles.
- All 225 manifest page paths were inspected through the source repository.
  The oversized Poker finder required the raw-file endpoint.
  Canonical and schema URLs matched and each had one H1 and main landmark.
  This is a source-level inspection, not the execution of the complete
  Python site audit.

## Limitations
A full local Python release suite and browser parser were not run in
this connector-only session. The refreshed `_reports/search-audit.json`
is a source-reconciled snapshot. The next actual local release should run
`python _scripts/check_search.py --json _reports/search-audit.json`
and `python _scripts/local_release_checks.py`, then investigate any
difference. Do not present sitemap discovery as confirmed indexing,
AI citations or measured traffic.

No GitHub Actions, cron, paid APIs, outside emails, or unverified book
storefront information was added.
