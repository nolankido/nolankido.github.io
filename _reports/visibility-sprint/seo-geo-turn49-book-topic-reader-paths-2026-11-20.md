# SEO/GEO Turn 49: Clean topic-to-book paths without redundant retail promotions

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Website:** https://nolankido.com/  
**Starting GitHub main:** `ca4d53d682d58fe184e9d3cc8cdf220128cd7a81`  
**Sprint position:** Turn 49 of the 37 to 61 website visibility program

## Editorial decision

The next useful improvement is not another book landing page, another purchase button, or a generic additional internal link. The site already has the right public author-work canonical pages, standalone no-cost teaching exercises, a separate Books catalog, and explicit unresolved Kindle/paperback/hardcover retail evidence.

The audit found a weaker reader path: the Books catalog's title-comparison cards promoted free worksheet downloads while the separate **Free exercises** section promoted the sample problems but did not provide their matching worksheets. The Home book section also sent readers to both the dedicated Books catalog and Creative Work's near-duplicate book overview. Three context guides linked to the correct book and worksheet but failed to distinguish their **separate original site-only practice** from retail-book chapter excerpts. The goal is to make each link accomplish a different job, not to increase link volume.

## Source-level discovery audit

The audited entrypoints and their appropriate functions:

| Source page | Reader intent | Correct destination decision |
| --- | --- | --- |
| [Home](https://nolankido.com/#books) | Discover either subject | One catalog link plus one canonical title link per work; no duplicate Creative overview link |
| [About](https://nolankido.com/about/) | Understand the author's identity and topic areas | Retain each book description and the compact catalog, no new promotional CTA |
| [Bio](https://nolankido.com/bio/#profile-books) | Find a public introduction or evidence of authorship | Retain the two author-work links in both its reading and provenance sections, which have different roles |
| [Creative Work](https://nolankido.com/creative/#books-by-nolan-kido) | Explore books alongside other creative work | Retain one subject-linked title, one sample and one free worksheet for each work |
| [Books catalog](https://nolankido.com/books/) | Choose a book versus actually try it | Keep book choice in comparison cards; keep exercises and worksheets together in Free exercises |
| [AI workflow pilot](https://nolankido.com/technology/ai-workflow-pilot/) | Learn a small-business AI pilot process | One author-book link and one free worksheet; describe the original ten-repetition website practice separately |
| [Poker books/courses](https://nolankido.com/poker/poker-books-and-courses/) | Evaluate educational books by fair criteria | One author-book link and one free worksheet; explicitly apply those same criteria to the author's book |
| [Long-form Hold'em guide](https://nolankido.com/poker/no-limit-holdem-guide/) | Study the game without a book purchase | Keep the free guide distinct from its related author page and website-only river decision exercise |

The destination pages were inspected at their source and generated HTML in the repository. The original free worksheet files and the Turn 48 `#ai-book-first-exercise`, `#poker-book-first-exercise` and native answer-reveal anchors were all already present. The original book material, edition statuses and published social art were not changed.

Before editing, an independent live-site read confirmed that both Turn 48 practice exercises and `assets/book-reader-journey.css` had reached the public site. This is **content-level publication evidence**, not a viewport screenshot, completed keyboard test, or measured user behavior.

## Changes made

1. **Books catalog, selection step:** Moved each matching worksheet link out of the book comparison cards. Each card now has one topical free guide and one simple in-page link to the existing Free exercises section. The exact canonical book title link remains once in each card.
2. **Books catalog, action step:** Each Free exercises paragraph now pairs a direct link to the original website example on its relevant book page with one direct downloadable worksheet. This is where readers decide whether to try the material, without requiring a purchase or interpreting it as an excerpt.
3. **Home:** Replaced the second book overview CTA via Creative Work with a short explanation that book pages contain original, free teaching material, not independently verified book chapters or retailer offers. The separate catalog link and two unique canonical title links remain.
4. **AI workflow pilot referral:** Kept its one exact book-page and one worksheet link, but explained that the author's book page includes a distinct original site-only ten-use practice exercise. No client ROI, Amazon availability or actual draft performance is implied.
5. **Poker reading comparison:** Kept the single exact author-book and free worksheet links, distinguishing a fictional 25% pot-price exercise and invented 20% showdown estimate from any verified retail chapter or solver verdict.
6. **Full Hold'em guide:** Kept its free teaching guide independent of the author book, describing the optional original on-page exercise and free worksheet without suggesting that this is copied from the book or based on a real opponent range.
7. **Version discipline:** Applied exactly the same revised paragraphs to editable `_source/` and their corresponding generated HTML. No extra page, canonical, FAQ schema, new metadata claim, new retailer link or publication-date reset.
8. **Offline regressions:** Added nine tests in `_tests/test_turn49_book_topic_reader_paths.py`, wired into `_scripts/local_release_checks.py`, covering unique book links, worksheet placement, real sample targets, source-to-generated paragraph parity, no duplicate Home overview, existing About/Bio/Creative purpose-specific routes, Book schema/evidence ledger, sitemap freshness and no GitHub Actions. Included negative controls for wrong sample/worksheet destinations and a falsely described retail chapter.
9. **Maintainability:** Documented the intentional link topology, duplicate removal and constraints in `AGENTS.md` and `README.md`.

## Link contract after changes

| Page or section | AI book link | Poker book link | Free practice path |
| --- | --- | --- | --- |
| Home book section | 1 direct canonical | 1 direct canonical | Book pages provide exercises; 1 Books catalog link |
| Books catalog comparison | 1 direct canonical | 1 direct canonical | The shared Free exercises section, no worksheet download in the comparison cards |
| Books catalog Free exercises | 1 deep-link to teaching example | 1 deep-link to teaching example | Exactly 1 distinct downloadable worksheet per book |
| AI workflow pilot | 1 direct canonical | Not applicable | 1 matching free AI worksheet |
| Poker book comparison | Not applicable | 1 direct canonical | 1 matching poker study worksheet |
| Long Hold'em guide | Not applicable | 1 direct canonical | 1 matching poker study worksheet |
| About and Creative | 1 direct canonical | 1 direct canonical | Free resources remain contextual and subject-specific |
| Bio | 2 purposeful references | 2 purposeful references | Separate biography and public-evidence roles |

These are **link-count and source-path checks**, not visitor click paths measured through analytics or search engine crawling.

## Reader trust and limitations

The author has described two book works on first-party pages. The six format slots in the public `nolan-kido-book-edition-evidence.json` ledger remain `not_verified`, which does not mean `not_published`. No exact Amazon ASIN, print ISBN, retail availability, price, official book-cover file, Kindle Unlimited status or independent review is established by this improvement. The new site-only 10-run AI costing and 20%-versus-25% poker examples are fictional. Free original site worksheets are not final retail excerpts.

The existing author Person ID, Book Work JSON-LD nodes, canonical routes and November 20 modification dates stay unchanged. Only contextual reader-navigation copy changed, with no substantive revision of book source chapters or previously published models.

## Verification and next checks

**Statically checked via GitHub:** one direct canonical book link per relevant context guide; one corresponding free worksheet destination; the two original site exercise anchors; unique links in the Books catalog after moving downloads; the Home duplicate removal; untouched About/Bio/Creative links; original book schema and edition unknowns; and paired editable/generated content.

**Not run in this tool environment:** a full local `build.py --check`, `build_books.py --check`, all Python unittest discovery, HTML5 parsers, internal-link auditor, mobile/keyboard browser acceptance, and exact post-merge HTTP response-byte comparison. Shell access cannot reliably clone the repository because of DNS restrictions. GitHub diff/source checks should not be mistaken for successfully executed offline tests.

From a complete checkout:

```powershell
py -3 _scripts/build_books.py --check
py -3 -m unittest discover -s _tests -p test_turn49_book_topic_reader_paths.py -v
py -3 -m unittest discover -s _tests -p test_turn48_book_reader_journeys.py -v
py -3 -m unittest discover -s _tests -p test_book_pages.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /books/ --only /technology/ai-workflow-pilot/ --only /poker/poker-books-and-courses/ --only /poker/no-limit-holdem-guide/ --attempts 3 --interval 5
```

## Recommended next sprint turn

**Turn 50:** Verify page-level author and book source consistency across Home, About, Bio, Creative, public JSON-LD and topical resources, then compare book-intent discovery opportunities against *actual* first-party Search Console or Bing evidence if authorized and accessible. Without measured query data, do not claim higher search impressions or AI citation rates. Prioritize one source-backed correction over another SEO-only landing page.

No GitHub Actions, paid services, additional tracking, invented search traffic, private KDP records or unsourced product availability was introduced.
