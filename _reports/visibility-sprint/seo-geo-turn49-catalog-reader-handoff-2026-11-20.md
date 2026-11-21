# SEO/GEO Turn 49 follow-up: Books catalog comparison and practice handoff

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Website:** https://nolankido.com/  
**Starting main:** `4a77761a2e8ed5d52f4547c74baeee0adf1dd8d3`, a concurrently merged Turn 49 topic-to-book release  
**Scope:** Incremental reader-path cleanup, not another independent sprint turn or indexable article

## Why this follow-up was needed

The first part of Turn 49, already merged into GitHub main by a separate workstream, connected the AI workflow pilot, the full Hold'em guide and the poker books comparison **directly to the books' original free site exercises**, and added reciprocal routes from the book pages back to focused free-guide sections. That is a worthwhile improvement and must not be overwritten. It is documented in [the first Turn 49 report](seo-geo-turn49-topic-book-paths-2026-11-20.md).

My initial parallel Turn 49 branch proposed overlapping edits to those exact article sources, creating a dirty PR. I inspected the newly merged commit, closed **conflicted PR #422 without merging it**, and created a fresh branch directly from current main. The final replacement change includes only the additional, still-useful Home and Books catalog improvements, plus tests and documentation. Nothing from the prior branch rewrites the already merged topical article or book page content.

## Actual reader problem and correction

The Books catalog previously used its two subject-comparison cards to promote the free worksheets, then used its distinct **Free exercises** section to explain the teaching examples **without** linking their corresponding worksheets. Readers had to cross between two roles to compare a book and perform the exercises. Home also offered a link to the dedicated Books catalog **and** a separate link to Creative Work's equivalent books overview.

The improvement concentrates each action in its proper place:

| Page context | Reader goal | Updated path |
| --- | --- | --- |
| [Books comparison cards](https://nolankido.com/books/#books-catalog-comparison) | Choose the right book subject | One exact canonical title link to each book, one relevant free subject guide, and a jump to `#books-catalog-free-learning`; no worksheet download here |
| [Books Free exercises](https://nolankido.com/books/#books-catalog-free-learning) | Try an actual, original teaching problem | Direct link to each `#ai-book-first-exercise` or `#poker-book-first-exercise` on the appropriate book page, immediately paired with its matching free original Markdown worksheet |
| [Home's Books section](https://nolankido.com/#books) | Choose a book or compare the two | One Books catalog link and one title link per work; removed the extra Creative Work books-overview link |
| [Three free topical guides](https://nolankido.com/technology/ai-workflow-pilot/) | Go straight to a relevant original example | **Preserved from concurrently merged Turn 49:** each guide's single canonical author-book link, single deep-linked original practice example and single matching free worksheet |
| About, Bio and Creative Work | Identify the author, inspect book work descriptions and see the distinct creative context | Deliberately unchanged; Bio includes book links in both its reader introduction and public evidence sections, which serve different purposes |

The free resources and numeric examples are **site-original teaching material**. The AI examples do not prove measured business time saved, and the poker examples are not recorded hands or solver verdicts. None is asserted to be a verified excerpt from a final retail book edition.

## Changes integrated with the already completed Turn 49 release

- `_source/books/index.html` and `books/index.html`: four paragraph changes, two comparison-card source-guide routes, two practice/example/worksheet handoffs, still exactly one canonical title link per work and one total worksheet download per work. Standalone source and published page are byte-identical.
- `_source/home.html` and `index.html`: removed only the duplicate link to Creative Work's books overview and retained an honest disclaimer about original site exercises and unverified retail chapters. Preserved the three existing unique root destinations for the Books catalog and two book pages.
- `_tests/test_turn49_book_catalog_handoff.py`: nine offline regressions, including negative controls for missing/duplicate links, exact section placement, sample and worksheet files, preserved previously merged topic-guide direct links and reciprocal fragments, unchanged About/Bio/Creative purpose-specific links, the existing author Book entity IDs and unverified retail edition ledger, sitemap dates, and no GitHub Actions.
- `_scripts/local_release_checks.py`: registered the new tests *in addition* to the previously merged `test_turn49_topic_book_paths.py`.
- `README.md` and `AGENTS.md`: documented this minimal decision-level refinement and the retained earlier Turn 49 content.

This is **no additional canonical page**, publisher data, KDP link, shopping button, new script, stylesheet, tracker, or external API. The 2026-11-20 book-page modification dates and all existing sitemap entries remain as they were.

## Verification and limitations

Before the parallel-branch conflict was detected, a current public retrieval confirmed that the Turn 48 original exercises and responsive CSS had reached the live website. Source and output of each new catalog/Home edit were subsequently compared; the catalog's comparison cards retain one canonical book link each and no worksheet downloads, while its Free exercises section has one link each to the sample and worksheet. Home retains one of each book/catalog link and no redundant Creative Work overview. The revised public source and already merged topical article paths were also inspected to ensure their existing direct sample and worksheet links remained.

**The new tests and complete site build were not executed** in this model container, which cannot resolve github.com to clone the repository. The source-level inspections and new regression definitions are not a passed Python test suite or proof that the changes are published. Independent post-merge live retrieval should check the Books catalog Free exercises section and the Home books block and distinguish cached content from a true HTTP failure.

### Complete-checkout checks

```powershell
py -3 _scripts/build_books.py --check
py -3 -m unittest discover -s _tests -p test_turn49_topic_book_paths.py -v
py -3 -m unittest discover -s _tests -p test_turn49_book_catalog_handoff.py -v
py -3 -m unittest discover -s _tests -p test_turn48_book_reader_journeys.py -v
py -3 -m unittest discover -s _tests -p test_book_pages.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only / --only /books/ --attempts 3 --interval 5
```

## Next turn

**Turn 50:** Assess whether first-screen Home and About readers can correctly identify the author's primary practical-AI expertise, verified published work, first-person poker experience and limits in a brief, evidence-supported view. Change only an actual comprehension problem, not assumed keyword demand. Search Console, Bing and valid AI-answer citations remain unavailable; do not treat an internal-link edit as measured ranking or engagement growth.

No GitHub Actions, cron, new paid API, private publication information, unverified retailer sales or copyrighted chapter excerpt is involved.
