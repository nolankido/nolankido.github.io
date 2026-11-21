# SEO/GEO Turn 49: topic-to-book learning paths

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Base main:** `ca4d53d682d58fe184e9d3cc8cdf220128cd7a81`  
**Roadmap:** Turn 49 of 37 to 61

## Problem and audit
Home, About, Bio, Creative, Books catalog, AI workflow pilot, long-form Hold'em guide, poker-books comparison, and both book author pages were inspected against current GitHub main. Home, About, Bio, Creative, and the Books catalog already link both owned works and appropriate free learning resources. They were left unchanged to avoid repetitive promotional links.

The three topical guides had appropriate author book links and original free worksheets but no direct jump to the book pages' original site-only teaching examples. The book pages' free guide links returned to a generic top rather than a useful learning section.

## Change and reader map
| Topical entry | Book-page exercise | Free offline practice | Return from book to free topic |
| --- | --- | --- | --- |
| `/technology/ai-workflow-pilot/` | `/books/one-workflow-at-a-time/#ai-book-first-exercise` | `/downloads/one-workflow-ai-pilot-worksheet.md` | `/technology/ai-workflow-pilot/#pilot-protocol` |
| `/poker/no-limit-holdem-guide/` | `/books/how-to-play-no-limit-texas-holdem/#poker-book-first-exercise` | `/downloads/holdem-river-call-check-worksheet.md` | `/poker/no-limit-holdem-guide/#choose-your-route` |
| `/poker/poker-books-and-courses/` | Same site-original poker example | Same free study sheet | Same full free beginner guide |

The comparison guide explicitly identifies the author's own book and does not treat it as an independent review. The fictional numerical examples are original to the site, not verified book excerpts, solver output, measured productivity, or real poker outcomes.

Updated the three topical sources and generated HTML plus the two source-verified book pages and identical public copies. Added `_tests/test_turn49_topic_book_paths.py` and registered it in `_scripts/local_release_checks.py`; documented constraints in `README.md` and `AGENTS.md`. Existing canonical URLs, Person/Book IDs, Book JSON-LD, retailer-unknown statuses, dates, sitemap and worksheets were preserved. No paid services, automated workflows, new tracking, offers, ISBNs or fake review claims were introduced.

## Verification scope and limitations
GitHub connector static preflight checked **all five unique snippet substitutions in both source and output**, exact source/HTML parity for each standalone book, one unfragmented title link plus one sample link in each topic guide, the four unique anchor destinations, reciprocal guide links, and unchanged Book author JSON-LD/unsupported retail field absence. This is a static preflight, not a real browser session.

The working container could not resolve github.com for cloning. Therefore **Python tests, complete build, HTML5 parser, local link checker, Playwright at 320px and production exact-byte GET were not run in this environment**. The included test requires a complete checkout. A previous web fetch's error on `/books/` did not establish an HTTP 404. Owner Search Console/Bing/Umami/AI citations and reader conversion remain unobserved; internal-link changes do not establish visibility gains.

### Required local acceptance
```powershell
py -3 _scripts/build_books.py --check
py -3 -m unittest discover -s _tests -p test_turn49_topic_book_paths.py -v
py -3 -m unittest discover -s _tests -p test_book_pages.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
```

## Next
Turn 50: five-second first-screen identity evaluation for Home and About. Preserve practical AI as the primary specialty, with first-party books, historical accounting research and tournament poker distinguished from directly verified AI evidence. Make edits only for a demonstrable comprehension problem.
