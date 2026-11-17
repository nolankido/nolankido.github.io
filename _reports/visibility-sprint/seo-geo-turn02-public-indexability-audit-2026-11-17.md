# SEO/GEO sprint Turn 02: Indexability and canonical eligibility audit

**Date:** November 17, 2026 (America/Phoenix)  
**Site:** https://nolankido.com/  
**Repository:** `nolankido/nolankido.github.io`  
**Starting main:** `56c2662949479de051ca2c63badc424a758955bd` (Turn 01, PR #373)  
**Method:** Read-only production GET requests, parsed live XML and HTML, and a full internal-link graph. No Google/Bing ranking or indexed-page counts are inferred.

## Outcome

The audit covered **224 index-intended sitemap URLs plus five intentionally excluded utility URLs**, a total of **229 pages**. The current live `sitemap.xml` contains 224 unique `loc` values, and live `robots.txt` allows the general crawler and identifies that sitemap.

- **229/229** direct page fetches returned HTTP 200 with no fetch failures. This includes `/404.html`, whose direct address is a legitimate file; a deliberately nonexistent URL separately returned a proper HTTP 404.
- **224/224** listed pages have their expected self-referencing HTTPS canonical, exactly one H1, no HTML/meta or HTTP-header `noindex`, and at least one incoming link from a *different* page in the crawl. All parsed JSON-LD blocks and date strings passed syntax checks. These checks concern public eligibility, not real search-engine indexing or the validity of every schema property.
- **5/5** intentionally excluded pages are absent from the sitemap and present `robots` content `noindex, follow`. Their own self-canonicals are appropriate; no change to their exclusion was made.
- The 25 representative URLs use the stable `Person` identifier `https://nolankido.com/about/#nolan-kido` in JSON-LD; no broken schema JSON was detected.
- Both `http://nolankido.com/` and `https://www.nolankido.com/` resolved to `https://nolankido.com/` with one redirect in spot checks. This is a hosting-level observation, not an exhaustive redirect-matrix audit.
- **No confirmed critical indexing eligibility defect was found.** No content, canonical, metadata, crawler directive, publication date or schema was changed merely to manufacture a fix.

## Representative URL disposition

Reading the table: `self / 200` means a live HTTP 200 and the expected full canonical `https://nolankido.com` plus the listed path. `open` means no `noindex` in inspected robots meta or `X-Robots-Tag`; it does **not** mean indexed by Google. Inbound is the number of distinct *other* crawled page URLs with an HTML anchor pointing to the page, including shared navigation. Self-links are excluded. `JSON-LD valid` refers to parseable JSON and date syntax, not Google rich-result eligibility.

| Canonical path | In sitemap | Public fetch and canonical | Robots intent | Inbound pages | Structured data | Disposition |
| --- | :---: | --- | --- | ---: | --- | --- |
| `/` | yes | self / 200 | open | 228 | JSON-LD valid | Pass |
| `/about/` | yes | self / 200 | open | 228 | JSON-LD valid; `ProfilePage` | Pass |
| `/technology/` | yes | self / 200 | open | 228 | JSON-LD valid | Pass |
| `/technology/check-ai-answers/` | yes | self / 200 | open | 14 | JSON-LD valid | Pass |
| `/technology/local-ai-review-replies/` | yes | self / 200 | open | 16 | JSON-LD valid | Pass |
| `/technology/local-ai-gaming-laptop/` | yes | self / 200 | open | 8 | JSON-LD valid | Pass |
| `/technology/review-reply-evidence-audit/` | yes | self / 200 | open | 10 | JSON-LD valid | Pass |
| `/technology/ai-book-continuity-checker/` | yes | self / 200 | open | 13 | JSON-LD valid | Pass |
| `/technology/rightsreceipt-ai-licensing/` | yes | self / 200 | open | 8 | JSON-LD valid | Pass |
| `/poker/` | yes | self / 200 | open | 228 | JSON-LD valid | Pass |
| `/poker/library/` | yes | self / 200 | open | 111 | JSON-LD valid | Pass |
| `/poker/resources/` | yes | self / 200 | open | 111 | JSON-LD valid | Pass |
| `/poker/start-here/` | yes | self / 200 | open | 23 | JSON-LD valid | Pass |
| `/poker/holdem-basics/` | yes | self / 200 | open | 15 | JSON-LD valid | Pass |
| `/poker/six-to-ten-bb-tournament-decisions/` | yes | self / 200 | open | 16 | JSON-LD valid | Pass |
| `/poker/satellite-bubble-seat-equity/` | yes | self / 200 | open | 15 | JSON-LD valid | Pass |
| `/poker/poker-math/` | yes | self / 200 | open | 14 | JSON-LD valid | Pass |
| `/poker/nolan-kido/` | yes | self / 200 | open | 10 | JSON-LD valid | Pass |
| `/poker/episodes/portland-meadows-ep1/` | yes | self / 200 | open | 11 | JSON-LD valid | Pass |
| `/poker/episodes/portland-meadows-standoff/` | yes | self / 200 | open | 6 | JSON-LD valid | Pass |
| `/poker/study/` | yes | self / 200 | open | 112 | JSON-LD valid | Pass |
| `/projects/` | yes | self / 200 | open | 11 | JSON-LD valid | Pass |
| `/living-well/` | yes | self / 200 | open | 228 | JSON-LD valid | Pass |
| `/living-well/tasks/learn-and-reflect/` | yes | self / 200 | open | 2 | JSON-LD valid | Pass; consider richer contextual links later |
| `/creative/` | yes | self / 200 | open | 228 | JSON-LD valid | Pass |
| `/find/` | no | self / 200 | `noindex, follow` | 228 | JSON-LD valid | Correct exclusion |
| `/poker/find/` | no | self / 200 | `noindex, follow` | 111 | JSON-LD valid | Correct exclusion |
| `/living-well/find/` | no | self / 200 | `noindex, follow` | 12 | JSON-LD valid | Correct exclusion |
| `/card/` | no | self / 200 | `noindex, follow` | 2 | JSON-LD valid | Correct exclusion |
| `/404.html` | no | self / 200 | `noindex, follow` | 0 | JSON-LD valid | Correct exclusion; unrelated nonexistent URL returned 404 |

## Historical Search Console warning check

An October message reportedly referenced invalid `ProfilePage` `dateModified`, index exclusions and redirect outcomes. Today's `/about/` publishes `ProfilePage` JSON-LD with a `Person` `mainEntity`, but **does not currently publish a `dateModified` property in that ProfilePage object**. It therefore has no live invalid `dateModified` value in that object. [Google's ProfilePage documentation](https://developers.google.com/search/docs/appearance/structured-data/profile-page) lists `dateModified` as recommended if applicable, not a required `ProfilePage` property. This public check cannot establish whether Search Console has cleared the historical warning, which property Google actually selected as canonical, or whether a given URL is indexed.

## Unavailable first-party verdicts

Calls to the connected GSC Wizard indexing tracker, sitemap list, URL-inspection quota and stored inspection history each returned `INVALID_ARGUMENT` on November 17. No inspection quota was spent and no new indexation submission was attempted. A browser fallback did not provide authenticated data. Therefore these remain **unknown, not zero**:

1. Google indexed and not-indexed totals; individual 25-page URL Inspection verdicts and Google-selected canonicals.
2. Current sitemap submission/read status inside Google Search Console.
3. Current Bing URL indexing status and selected canonicals.
4. Search impressions, clicks, queries, AI Overview citations and ChatGPT Search referrals.

When authenticated access becomes available, inspect the 25 exact URLs in this table, save first-party URL Inspection findings privately, compare Google-selected to declared canonicals, and use Search Console's Page Indexing report to separate intentional from unintended exclusions. Do not request indexing for intentionally excluded utilities. Do not renew a paid connector without owner authorization.

## Reproduction and limits

The manual, read-only script `_scripts/live_indexability_audit.py` fetches the live sitemap, 224 listed pages and five excluded utilities; it tests public response status, declared canonicals, noindex directives, internal links, JSON-LD JSON and simple date syntax. It prints the selected 30 URL table, all-page problems and a PASS/FAIL result. Run locally with `python3 _scripts/live_indexability_audit.py`. It requires no new packages, account access, scheduling service or CI workflow. Because it uses live networking, transient failures should be rerun and independently checked before changing the site.

This does not inspect rendered JavaScript, mobile usability, actual search-bot fetches, rich result semantic eligibility, duplicate content quality, link quality, Google canonical choices or observed assistant citations. A navigation link counts as an internal link, so inbound counts do not establish topical authority.

## Turn 02 acceptance decision

**Public technical checks: completed, with no confirmed critical defect.** The validated 30-row sample and repeatable all-sitemap audit script create a reusable check for later releases. **First-party Google indexing verification: blocked by authenticated integration access.** This is a recorded evidence gap, not a passed indexed-state test. Preserve the gap in all future visibility scorecards.

**Next: Turn 03.** Test Bing discovery, the currently published crawler policy and the IndexNow submission configuration without changing the owner's crawler/training preferences. Compare what can be measured directly to what remains missing from Google/Bing and ChatGPT Search.
