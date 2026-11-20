# SEO, GEO and AEO Turn 36: Dedicated Books by Nolan Kido catalog

Date: November 20, 2026. Base commit: df4880fe61280a50cdf2293f369d0f1d806c7718.

## Why
The two existing book pages were discoverable through Home and Creative Work,
but no dedicated `/books/` address answered the natural navigational query
"Books by Nolan Kido" or allowed readers to compare both books in one place.

## Implemented
- Created an indexable, static, source-backed `/books/` CollectionPage
  with a unique canonical, title, meta description, visible H1 and
  BreadcrumbList, author-linked ItemList of the same two Book work IDs.
- Introduced four focused answer-first sections covering the topics,
  differences, related free exercises and what publication records
  remain unverified.
- Linked the catalog from Home, Creative Work, About, Bio, and each
  individual book page. Existing Creative Work section anchors remain.
- Extended the standalone book builder and registry to validate source
  parity, matching Book IDs, visible inbound links, metadata, and
  original publisher-evidence boundaries.
- Registered the catalog once in the sitemap, local Find cards and
  section-heading index, and in the SEO, HTML5 and live-byte inventories.
- Expanded regression tests, including negative controls for missing
  source and altered canonical.

## Source inventory
The repo sitemap now lists 229 unique canonical URLs. The manifest
still owns 225 pages, including five intentionally non-indexed
utilities; 9 other indexable pages are source-owned separately.
The audit records 2 standalone Book pages and 1 Books catalog.
Neither this report nor the sitemap establishes Google indexing,
AI citation visibility or search ranking.

## Verification and limits
The changed source/output HTML pairs, canonical JSON-LD, visible
internal links, Find and sitemap membership were reviewed before merge.
The complete Python site build and browser suite cannot run in this
connector environment. The full local suite should be run from a
complete checkout using `python _scripts/local_release_checks.py`.
An exact matching Amazon detail URL, ISBN, ASIN, book edition, offer,
official cover, publication date or independent sales evidence still
was not confirmed and is not asserted by the catalog.

No GitHub Actions or background jobs were added.
