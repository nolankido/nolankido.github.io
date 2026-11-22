# PBG-06: Beginner poker search intent and canonical page ownership

**Date:** November 22, 2026 (Pacific/Honolulu)  
**Sprint:** Poker Book Growth, Turn 06 of 25  
**Status:** Source-backed editorial routing and a reader-facing navigation improvement committed; independently observed GSC demand, rank and AI citations remain unknown.  
**Main book:** https://nolankido.com/books/how-to-play-no-limit-texas-holdem/

## Editorial decision

Do **not** build a new article for each keyword variation or try to make the author-book page outrank every free poker rules lesson. Give each distinguishable learner question one best existing answer page, preserve the educational resources, and reserve the author-book landing page for readers looking for the specific book or its free sample. This is an editorial quality and internal navigation improvement, not measured query demand.

The [frozen 18-intent machine-readable map](pbg-06-intent-to-canonical-map-2026-11-22.json) records two natural-language hypothetical questions for every intent, one primary canonical owner, one supporting resource, the reader's task and an editorial priority. The map contains **36 candidate questions** but they are not Search Console query exports, a keyword volume dataset, a citation-rate observation or a guarantee of rankings.

## Evidence and research boundary

1. **First-party source:** Read `_source/pages.json`, `sitemap.xml`, and the published canonical pages. All 18 primary destinations have exactly one matching canonical link, one H1, and an indexable page record in committed GitHub HTML. Each also appeared in the current sitemap. Across the 18 primary owners and supporting destinations there are 19 distinct published routes, because the broad live tournament field guide remains a secondary resource alongside the focused first-event guide. This is a source-level technical check, not proof that Google indexed all 18.
2. **Site comparison:** The current book-comparison article is a distinct choice task rather than the canonical author product page, while `/poker/free-poker-learning-path/` is the guided beginner curriculum and `/poker/no-limit-holdem-guide/` is a longer integrated reference. Specific rules, starting hands and mathematics questions already have more focused guides.
3. **Qualitative outside sample:** Public search returned examples of sites organizing poker learning by rules, hand rankings, position and pot odds, and others organizing books by level and use case: [PokerLeap learning guides](https://pokerleap.app/learn), [Poker School guides](https://pokerschool.org/guides), and [PokerSkill beginner book reading order](https://www.pokerskill.com/blog/best-poker-books-for-beginners/). These illustrate user tasks and editorial patterns only. They are **not** a representative SERP dataset, an audited competitor comparison, conversion data, keyword difficulty or observed search volume.
4. **Authenticated owner data:** No authenticated Google Search Console Web query/page export, Bing Webmaster performance dataset, private Umami report, or sampled AI assistant citation result was available in this turn. All such values remain `null` and `status=not_collected`, rather than numeric zeros.

## Frozen query-to-page ownership

| Reader intent / example task | One primary page | Distinction from adjacent material |
| --- | --- | --- |
| Learn the game as a sequenced course | `/poker/free-poker-learning-path/` | Six free beginner lessons |
| Follow one Hold'em hand | `/poker/holdem-basics/` | Deal to showdown rather than full game strategy |
| Identify a winning five-card hand | `/poker/hand-rankings/` | Kicker, tie and board rules |
| Understand call, check, raise and side pots | `/poker/betting-and-pots/` | Mechanical betting rules rather than pot-price math |
| Compare starting hands and position | `/poker/starting-hand-decisions/` | Eight contextual preflop exercises |
| Explain seat order and effective stacks | `/poker/position-and-stacks/` | Positional action order and depth |
| Calculate pot odds | `/poker/poker-math-reference/` | Exact fractions and distinct thresholds |
| Practice decisions without wagering | `/poker/beginner-practice/` | Worked examples, varied exercises |
| Prepare for a first session | `/poker/getting-started/` | Format, full costs and boundaries |
| Prepare for first tournament logistics | `/poker/first-live-tournament/` | Registration and procedure; the broad live guide remains supporting material |
| Review a hand after play | `/poker/reviewing-a-hand/` | Uncertainty labels and review worksheet |
| Study 10 to 20 big blind decisions | `/poker/short-stack-decisions/` | Tournament depth and action options |
| Understand ICM and payout equity | `/poker/tournament-equity/` | Checkable prize-equity models |
| Evaluate which book or course to use | `/poker/poker-books-and-courses/` | Compare level, exercises, formats and access |
| Find Nolan Kido's named Hold'em book | `/books/how-to-play-no-limit-texas-holdem/` | First-party author work, free example, supplied Kindle link |
| Read a complete integrated Hold'em reference | `/poker/no-limit-holdem-guide/` | Long-form rules and strategic context |
| Find official rule authorities and tool restrictions | `/poker/poker-rules-and-fair-play/` | Operator/floor authority, not guessing local rules |
| Prepare for live table etiquette | `/poker/table-etiquette/` | Table conduct, declarations and floor calls |

The list is **not** a ranking of search-volume opportunities. A page can serve multiple long-tail questions but the map deliberately avoids assigning indistinguishable primary ownership to several pages. The original 11-page PBG-02/PBG-04 direct book-link acquisition cohort is a different dataset; its latest coverage remains **9 of 11**, not 18 of 18.

## Actual on-site improvement

In the existing `/poker/poker-books-and-courses/` article's `#choose-the-job` section, replaced one general paragraph with a focused **Use the exact free answer first** paragraph. It links five existing primary-learning destinations, in this order:

1. `/poker/holdem-basics/`: hand flow and rules.
2. `/poker/starting-hand-decisions/`: starting hands and position.
3. `/poker/poker-math-reference/`: pot odds.
4. `/poker/free-poker-learning-path/`: six-lesson beginner course.
5. `/poker/first-live-tournament/`: first-event registration and procedure.

The message invites comparison shopping only when free resources do not answer the reader's question. It does not send a student straight to Amazon, add a tracking event, promise poker success or imply independent evaluation of the author's book.

This paragraph is exactly matching in `_source/poker/poker-books-and-courses.html` and `poker/poker-books-and-courses/index.html`. The existing unfragmented author-book link remains once, its original free example deep link remains once, and the free worksheet, author disclosure and other substantial content remain unchanged. No additional H1, new canonical route, false `datePublished`, or marketing schema was added. The change is navigational, so the existing page modification date was not artificially advanced.

**Precision refinement:** The first live tournament question has a more focused published answer at `/poker/first-live-tournament/`; the broader `/poker/live-tournament-guide/` remains a supporting hub. The reader chooser now points to the focused first-event guide.

**Reading-time check:** The original source had approximately **807** text words; the revised source approximately **813**, a net six. Both are within the 4-minute bucket at the existing 225-words/minute editorial estimate. The published page still says about four minutes, so the changed paragraph does not require a known reading-time update.

## New quality gate

Created `_scripts/poker_beginner_intent_map.py`, a read-only, zero-network, standard-library-only validator. It checks the map version and 18 unique intent owners, question uniqueness and source explanations, null-only unobserved performance data, exact canonical URLs and manifest/sitemap registration, the five reader choice routes, and preservation of the original author-book/sample links. The output is JSON.

```powershell
py -3 _scripts/poker_beginner_intent_map.py
```

Created `_tests/test_pbg06_beginner_intent_map.py` with **12** offline test methods, including negative controls against duplicated owners, wrong book ownership, repeated or malformed questions, fake impressions or clicks, and loss of the native book-comparison routing. The script and test module are registered in `_scripts/local_release_checks.py`.

These new Python tests were authored and registered. They were **not executed** in a complete checkout, because the container runtime cannot resolve `github.com` to download the whole repository. Do not present a static source inspection as executed unit tests.

## Verification completed

- Fetched the frozen map, source manifest, sitemap, new validator, 12 tests, release runner and both changed article files from authenticated GitHub. The source-level map audit passed **18** recorded consistency assertions.
- Inspected the canonical metadata for each of the **18** mapped primary public HTML files, in two repository fetch batches. Each had one canonical matching its intended URL, one H1 and no noindex meta.
- Confirmed the book-selection article's new paragraph contains precisely **five** intended free guide links; its original book and original free-example deep links were retained separately.
- Read-only public website retrieval confirmed the current `/poker/poker-books-and-courses/` page **already exposes the five free learning URLs and original author-book URL**. This confirms live navigational availability, not exact source-byte deployment parity.
- Existing source-backed author book Kindle ASIN `B0HSB98324` and its Umami event were not modified.
- No new paid tools, GitHub Actions, new tracking scripts, redirects or site-promotion banners were created.

**Still open:** full deterministic site build, HTML5 and internal-link checks, the registered Python tests, actual browser-width and keyboard accessibility checks, live-byte comparison, and all authenticated GSC/Bing/Umami/KDP performance measurements.

## Local acceptance steps

Run in a complete current repository checkout:

```powershell
py -3 _scripts/poker_beginner_intent_map.py
py -3 -m unittest discover -s _tests -p test_pbg06_beginner_intent_map.py -v
py -3 -m unittest discover -s _tests -p test_turn49_topic_book_paths.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
```

A future exact-byte live check should compare matching deployed HTML, not merely check that the visible hyperlink exists.

## Next growth turn: PBG-07

Improve the existing `/poker/no-limit-holdem-guide/` as a genuinely useful comprehensive answer, but avoid duplicating the focused hand rules, starting hands, pot odds or first-session content. Begin with a structural and factual editorial audit of its highest-impact examples and internal navigation. Correct actual issues and add bounded evidence or exercises, not cosmetic keyword repetition. Preserve the buyer-versus-learner distinction, all existing ASIN links, original calculations and no-cost study routes.

Subsequent PBG-08 through PBG-10 should use the specific route owners frozen here. Once genuine Search Console query/page rows become available, revise editorial priorities only with the same property, date range and filter provenance.
