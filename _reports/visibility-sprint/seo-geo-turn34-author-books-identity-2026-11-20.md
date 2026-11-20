# Turn 34: Nolan Kido book-author identity and verification links

Date: November 20, 2026. Goal: increase discoverable, source-bounded connections
between an author's public biography, two book works, and their canonical pages.

## Implementation
- Added a dedicated Books subsection to the existing /bio/ public work.
  It links the two book pages, explains the scope of each book and points
  readers to the original free exercises.
- Added an explicit entry to the bio source-verification list separating
  author descriptions from independently verified publisher and retailer
  records. No KDP release or ISBN assertion was inferred.
- Updated the bio's search description, local Find result, JSON-LD
  dateModified and sitemap lastmod to November 20, 2026.
- Expanded the separately hosted identity graph with two Book work nodes,
  using the exact existing Book @ids, author Person @id, descriptions and
  canonical pages. No edition, ISBN, offers, datePublished or publisher
  record was invented.
- Added regression assertions for source-output graph parity, canonical
  author/book links, identity IDs and evidence boundaries.

## Boundary
Google Search Central's Book actions are a separate feed/onboarding system
for eligible large book providers. Having valid Book schema on a personal
author site does not guarantee book action rich results, AI citations,
indexing, rankings or traffic. No Amazon product URL was verified during
this work. Existing author and independent accounting research references
remain unchanged. The rich standalone identity graph is still not linked
into public pages, per the repository's historical privacy design.

## Local checks
Validate JSON and exact canonical references. Run:
  python _scripts/build.py --check
  python _scripts/check_search.py
  python -m unittest _tests.test_book_pages
  python _scripts/local_release_checks.py

Full local build and browser suites were not run through the GitHub connector.
No GitHub Actions, scheduled jobs, paid APIs or outside messages were added.
