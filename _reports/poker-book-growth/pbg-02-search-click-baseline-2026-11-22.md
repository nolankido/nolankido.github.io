# PBG-02: frozen poker-book search and Amazon-click baseline

**Date:** November 22, 2026, Pacific/Honolulu  
**Sprint:** POKER-BOOK-GROWTH, Turn 02 of 25  
**Book:** *How to Play No-Limit Texas Hold'em* by Nolan Kido  
**Canonical destination:** https://nolankido.com/books/how-to-play-no-limit-texas-holdem/  
**Author-supplied Kindle link:** https://www.amazon.com/Play-Limit-Texas-Holdem-Poker-ebook/dp/B0HSB98324  
**Status:** TECHNICAL AND CONTENT BASELINE FROZEN. Private reach, clicks and sales remain unknown.

## Decision and baseline integrity

A source audit can count hyperlinks and inspect accessible public pages. It **cannot** measure how often Google shows the page, how many readers click through to Amazon, book sales, or whether an assistant cites the URL. Actual Search Console, Bing, Umami owner dashboard, KDP and AI prompt observations were not accessible as authenticated baseline datasets on this turn. Therefore all outcome measures are **not collected**, not zero. Prior GSC Wizard access returned `payment_required`; this sprint is not asking to renew a paid subscription.

The [machine-readable frozen route baseline](pbg-02-acquisition-route-baseline.json) records 11 intentionally selected existing poker-learning URLs, with static exact-link counts from committed HTML. The current audited set is a denominator for future internal-routing work, not an estimate of Google search traffic or all site pages.

## Source-backed acquisition map

| Canonical URL | Direct link to poker book | Discovery judgment |
| --- | ---: | --- |
| `/poker/` | 1 | Existing entry point |
| `/poker/no-limit-holdem-guide/` | 1, plus deep link | Existing complete beginner guide |
| `/poker/poker-books-and-courses/` | 1, plus deep link | Existing book-shopper route |
| `/poker/free-poker-learning-path/` | 0 | High-fit course |
| `/poker/holdem-basics/` | 0 | High-fit rules introduction |
| `/poker/library/` | 0 | Searchable library |
| `/poker/study/` | 0 | Study-desk destination |
| `/poker/starting-hand-decisions/` | 0 | High-fit starting-hands guide |
| `/poker/poker-math-reference/` | 0 | Relevant supporting mathematics |
| `/poker/betting-and-pots/` | 0 | High-fit betting explanation |
| `/poker/beginner-practice/` | 0 | High-fit free practice |

**Observed baseline: 3 of 11 have direct links; 8 of 11 do not.** These are exact `href="/books/how-to-play-no-limit-texas-holdem/"` matches on the reviewed committed pages. Anchor-deep links on two source pages are tracked separately and not double-counted as another page. This is a selected sample, not a whole-site backlink count.

The optional acquisition path is **educational answer -> contextual book page -> author-supplied Amazon Kindle link**. The book page and Books catalog already each have a labeled Amazon link. The free lessons must remain free and fully useful without a purchase.

## Frozen measurement fields

| Source | Exact metric | November 22 baseline | State |
| --- | --- | --- | --- |
| Google Search Console, Web | Property clicks and impressions in a verified, fully settled 28-day range | Unknown | `not_collected` |
| Google Search Console, Web / Pages | Visible clicks and impressions for book page and relevant `/poker/` entry pages | Unknown | `not_collected` |
| Google Search Console, Web / Queries | Visible beginner and poker-book intent queries, keeping privacy-filtered queries unavailable | Unknown | `not_collected` |
| Google AI Search performance | AI Search impressions, if the relevant report is available | Unknown | `not_collected` |
| Bing Webmaster Tools | Search clicks, impressions and separately supported AI citations | Unknown | `not_collected` |
| Umami Cloud | Book-page and catalog pageviews, with exact same reporting period | Unknown | `ingestion_unverified` |
| Umami Cloud Events | `poker-book-kindle-amazon-click` by `book-page-hero` versus `books-catalog` | Unknown | `ingestion_unverified` |
| Owner KDP reporting | Orders and royalties | Unknown | `not_collected` |
| Fixed 25-question AI panel | Actual cited `nolankido.com` URLs and correctly linked book mentions | Unknown | `not_run` |
| Site source | 11-page internal-link sample | 3 linked / 8 not linked | `source_audited` |

Search impressions, Google AI impressions, Bing assistant citations, outbound clicks, and book sales are **separate units**. Never add them into a fictional SEO/GEO score. Google Web clicks are not book sales. A link event is not proof that Amazon loaded or that the visitor purchased the book. Site-canonical HTML and an accessible response are not proof of indexing.

## Book-specific analytics event contract

| Event | Link placement | Book ASIN |
| --- | --- | --- |
| `poker-book-kindle-amazon-click` | `book-page-hero` on dedicated book page | `B0HSB98324` |
| `poker-book-kindle-amazon-click` | `books-catalog` on catalog | `B0HSB98324` |
| `one-workflow-kindle-amazon-click` | Corresponding book page and catalog | `B0HRQNCP7Y` |
| `ai-works-human-decides-kindle-amazon-click` | Catalog only | `B0HSF8K76R` |

The attributes were added earlier. This turn **did not add a second tracker**. It corrected an older discrepancy in the public Privacy page and in `ANALYTICS.md`, which had described pageview-only tracking despite the existing fixed book-click events. The privacy notice now says those clicks can be sent when analytics is permitted, explains the fixed source values, and makes clear that a click is not an order. The main event test now explicitly allows the three named events only in the three known book routes and continues to prohibit contact form or reader-input tracking.

### Offline collection helper

`_scripts/poker_book_growth_scorecard.py` is a no-network, no-file-write, standard-library-only helper. Without private input it emits `null` for unknown counts:

```powershell
py -3 _scripts/poker_book_growth_scorecard.py --month 2026-11
```

When the owner's **Umami** dashboard is genuinely accessible, first confirm that the entire selected time period belongs to `nolankido.com`, then create an aggregate-only JSON input **outside the public repository** with exactly these top-level keys: `month`, `property`, `period_verified`, `pageviews` and `events`. `pageviews` may contain the three named public canonical paths; `events` may contain only the three named click events, each with its known `books-catalog` or `book-page-hero` source counts. Use integer zero only for a genuinely checked zero; omit an uncollected field rather than setting it to zero.

Example command with a real, privately prepared input, not a supplied real dataset:

```powershell
py -3 _scripts/poker_book_growth_scorecard.py --month 2026-11 --umami-json "$env:USERPROFILE\Documents\poker-book-umami-2026-11-private.json"
```

The script's rate is `book-page-hero click events / dedicated-book-page pageviews * 100` when both values are explicitly available and the pageview denominator is positive. Repeated clicks make this an **events-per-100-pageviews** metric, not a unique-visitor conversion probability. A separate Google Web export can be reviewed using the existing offline `downloads/gsc-monthly-local-audit.py` and `downloads/visibility-private-scorecard.py` tools without paying for GSC Wizard.

### Comparable time windows

- **First observed baseline:** the first available *settled* 28-day Search Console Web interval, with the exact dates and source property written in the owner's private record. Do not invent a settled end date.
- **Pre-sprint historical reference:** October 2026, but only if an actual compatible export exists.
- **Transition:** November 2026, with a partial-month flag until the month finishes.
- **First fully post-change calendar month:** December 2026, after data settle.
- Never compare a partial November with a full December without aligning windows or labelling the difference.

## Frozen AI discovery prompt panel

Use the **exact 25 question texts** below for each chosen search-enabled assistant or answer engine. Record the assistant, model/mode, date, locale, search-enabled status, prompt, whether a clickable `nolankido.com` URL was cited, exact cited URL, whether the correct book was named, and separate actual response evidence. Test clean conversations. Do not invent search results, responses, citations, or model versions.

### Twenty nonbranded questions

1. What is a good beginner book that teaches no-limit Texas Hold'em from the rules onward?
2. Which free resources teach the sequence of a Texas Hold'em hand step by step?
3. What do I need to learn before playing my first live no-limit Hold'em cash game?
4. How are preflop and postflop betting rounds organized in no-limit Hold'em?
5. How do I compare two five-card poker hands correctly?
6. What is a beginner-friendly explanation of position in Texas Hold'em?
7. What does it mean to act in position and why does it matter?
8. How does a beginner calculate pot odds on a river call?
9. Why can a mathematically correct pot-odds calculation still lead to a bad poker decision?
10. What is a beginner's first approach to starting-hand selection in no-limit Hold'em?
11. What do effective stacks mean in no-limit Hold'em?
12. How does tournament poker differ from cash games for a first-time player?
13. How do blinds and antes change the choices in a no-limit Hold'em tournament?
14. What are common first-time live poker table etiquette mistakes?
15. How should a novice review a poker hand without judging only the outcome?
16. Where can I find free no-wager Texas Hold'em practice exercises?
17. What should an introductory no-limit Hold'em book cover to be genuinely useful?
18. What is the difference between poker odds, outs, and equity for beginners?
19. How do I learn bet sizing and why is a minimum raise not always a fixed amount?
20. What structured study plan combines poker rules, math, decisions, cash games and tournaments?

### Five branded identity and book questions

21. Who is Nolan Kido and what no-limit Texas Hold'em learning materials has he published?
22. What is Nolan Kido's beginner no-limit Hold'em book about?
23. Where is the official Nolan Kido site page for How to Play No-Limit Texas Hold'em?
24. Where can I find the Kindle listing for Nolan Kido's How to Play No-Limit Texas Hold'em?
25. How does Nolan Kido's poker book relate to the free lessons on nolankido.com?

A nonbranded hit requires an actual relevant link or accurate title mention appearing **without** the name being supplied in the question. A branded answer is not evidence of nonbrand discovery. Exact citations, unlinked mentions and inaccurate substitutions must be recorded separately. At the time of this report, **no prompt trials have been completed for this frozen panel**; this is a test design, not a citation-performance claim.

## Release delta and tests

- Updated `_source/privacy.html`, generated `privacy/index.html`, the Privacy record in `_source/pages.json`, and the `privacy` entry in `sitemap.xml` to reflect November 22 and book-click disclosure.
- Corrected `ANALYTICS.md` to distinguish the October pageview-only installation from the November book-link events, without adding analytics suppliers.
- Updated `_tests/test_analytics.py` for exact allowed book-event names, reader privacy, standalone source-backed book tracker handling and the truthful updated privacy notice.
- Added a zero-network book scorecard script and ten focused offline unit tests in `_tests/test_pbg02_poker_book_growth_scorecard.py`, registered with the existing manual local release-check runner.
- Saved the 11-route JSON acquisition snapshot, preserving source counts and `null` outcome metrics.
- This is a **measurement and privacy-integrity turn**, not a new content campaign.

**QA not yet claimed:** the complete local Python build, HTML5, visual mobile or browser suite, and an independent exact-byte production parity check. Committed source checks and a public GET cannot substitute for those tests. No Google indexing/ranking improvements, Umami event counts, KDP orders or assistant referrals are asserted.

## Next action: PBG-03

Improve the existing first-screen poker-book landing page for adult beginners and returning players: clearer reader fit, truthful features and learning outcomes, official source-verified cover only if available, the existing exact Amazon link, accessible free exercise, and mobile keyboard/viewport QA. Do not promote speculative edition/price/quality claims or interrupt free learning.
