# SEO, GEO, and AEO Turn 31: Two source-backed book landing pages

Date: November 20, 2026. Change base: `505a4552afbb5acaf6d8115d2c13e396aea0b67d`.

## Why this change
The author's two book descriptions previously existed only as fragments of
`/creative/`. Separate canonical URLs better distinguish each work's topic,
intended reader, author identity and free companion materials. This is a
discoverability improvement, not proof of rankings or AI citations.

## Published routes
- `/books/one-workflow-at-a-time/`: bounded AI workflow pilots, full time costs and verification
- `/books/how-to-play-no-limit-texas-holdem/`: no-limit Hold'em beginner learning and free exercises

Both are ordinary indexable HTML pages and carry `WebPage.mainEntity.Book`
with a shared Nolan Kido Person `@id`. Both have unique title/description,
canonical URL, breadcrumb, H1 and source-verified page content. The Creative
ItemList's Book identities now point to these persistent canonical pages.

## Distribution and release
Direct links from Home, About, Creative, Technology and Poker.
The routes are registered once in the main XML sitemap and once in Find cards,
with a Books filter and section-heading search. Sources are full HTML in
`_source/books/`, built to `books/` using the independent copy-and-check
builder. Existing page titles and article dates were left unchanged.

## Trust boundary
The owner describes the books as newly published, but an exact public Amazon
detail page or ASIN/ISBN was not confirmed. The pages do not include invented
purchase links, release dates, formats, prices, book reviews or sales claims.
Structured data identifies the works, not an independently verified retail edition.
Do not infer Google's indexing, ranking or ChatGPT citation performance from this release.

## Verification
Source-output equality, JSON-LD syntax/identity, exact internal links, sitemap
presence, Find filter and canonical path checks were reviewed at code level.
A local Python regression test is included at `_tests/test_book_pages.py`.
Full main-generator, HTML5, unittest and browser test suites could not be
executed in the connector session. Run:
```bash
python _scripts/build_books.py --check
python _scripts/build.py --check
python -m unittest _tests/test_book_pages.py
python _scripts/local_release_checks.py
```
No GitHub Actions or paid automated monitoring was added.
