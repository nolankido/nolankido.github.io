# SEO/GEO Turn 61: release and visibility evidence scorecard

**Audit date:** November 20, 2026 (Pacific/Honolulu)  
**Repository:** [nolankido/nolankido.github.io](https://github.com/nolankido/nolankido.github.io)  
**Starting `main`:** [`7140c2419c49bfa39b391ab7105afc4b25ce4b4c`](https://github.com/nolankido/nolankido.github.io/commit/7140c2419c49bfa39b391ab7105afc4b25ce4b4c) (Turn 60, merged PR #434)  
**Scope:** Read-only connected-source, public-retrieval and release-evidence audit. This report adds no new visitor-facing page, tracking, service, workflow or schema.

## Decision

**Qualified progress; sprint exit gate remains open.** The current website has a coherent canonical publishing inventory and the latest three corrections are observable in retrieved public page content. That does **not** establish a complete local release pass, exact source-to-production byte parity, Google/Bing indexing, rankings, AI citations or improved business outcomes. The originally planned performance, whole-journey and measured query-relevance work for Turns 58 to 60 was not completed by their numbered PRs: those turns instead repaired specific poker teaching errors. The repairs are useful, but the planned gates still need their own evidence.

## Evidence scorecard, November 20

| Signal | Observation | Status and limitation |
| --- | --- | --- |
| Current committed sitemap | Exactly **230 distinct canonical `<loc>` URLs** in `sitemap.xml`. | Repository fact, not indexing. |
| Current public sitemap | Read-only extraction returned **230 distinct URL links**, with the same URL set as the committed sitemap (230/230, zero differences). | **Content-level parity verified**. Extractor output is not a raw-byte XML receipt. |
| Search audit | Committed `_reports/search-audit.json` states `status: pass`, **225 manifest pages, 230 sitemap URLs, 133 articles, five noindex pages, zero errors**, and records two standalone book pages, one books hub and one 10 BB page. | **Previously generated committed snapshot**, not a new execution of `check_search.py` on this turn. The five noindex cases were not individually reaudited here. |
| Live critical HTML | Retrieved **15 distinct HTML pages** with their expected self-canonical: Home, About, Technology, AI in Real Life, Books catalog, two book pages, Poker hub, 10 BB, three recently corrected poker lessons, Contact, a Portland Meadows companion and the documented AI website repair. | **Content-level smoke pass** on these 15 only; not an HTTP status-bearing exhaustive crawl or browser/accessibility test. |
| Latest three source/output changes | Each source and committed public HTML contains exactly one copy of the new Turn 58, 59 and 60 anchors. The **six named anchor fragments** are identical in their source/output pairs. | **Committed content parity passed**, not raw live-byte equality. |
| Latest three publicly served articles | Each canonical article was retrieved with its November 20 modified-date metadata and its substantive correction text: cutoff shove role/break-even boundaries; $1,000 tenth-place example; card-filtered Bayes formula and worked check. | **Observed public content**, not a complete proof that every CSS, JavaScript or downloadable asset deployed. |
| `robots.txt` | Public retrieval shows `User-agent: *`, `Allow: /` and the main sitemap URL; committed file has the same intent. | Crawl guidance present; crawler behavior unmeasured. |
| Public downloadable Python evidence | The content extractor reported `target_unreachable` for `/downloads/poker-under-uncertainty-reproduce.py`. | **Inconclusive**, not an observed 404. No status-bearing GET or exact-byte receipt was obtained. |
| Local current-source release | The execution environment could not resolve `github.com` for a complete checkout. No current-source `build.py --check`, `build_books.py --check`, search snapshot regeneration/check, HTML5, internal-link, historical unittest, Playwright or `local_release_checks.py --full --browser` execution was completed. | **Not run**, not passed. Previous reports cannot be silently reused as this turn's run. |
| Live exact-byte verifier | `_scripts/check_live.py` and `_tests/diagnose_live_crawl.py` were not run from a complete checkout with status-bearing network access. | **Not run**. Public text retrieval is not an exact-byte receipt. |
| Google Search Web clicks, impressions, queries and pages | No authenticated period export retrieved. The connected GSC Wizard account refused access with `payment_required`. No paid subscription was enabled. | **Unavailable**, not zero. |
| Google AI Search and Discover visibility | Neither first-party Generative AI performance report was accessible. | **Unavailable**, not zero or the same as traditional Web clicks. |
| Bing Webmaster AI citations | No authenticated Bing AI Performance report retrieved. | **Unavailable**, not zero or proof of no citations. |
| Umami assistant referrals | No owner dashboard/referrer export retrieved, ingestion not independently checked. | **Unavailable**, not zero. |
| Frozen assistant citation panel | The November 17 panel still has 20 nonbranded and five branded frozen prompts. Turn 40's single Perplexity pilot had an unverified exact question and was excluded. No newly eligible exact-prompt runs were completed in this audit. | **Citation rate undefined**, not 0%. The earlier pilot cannot serve as an eligible denominator. |
| Retail author editions | Two author pages and free original exercises are public. KDP/Amazon identifiers, format-level listings, dates, official covers, prices and `Offer` claims remain unverified for the six possible book/format pairs in Turn 47's ledger. | **Unverified**, not unpublished or unavailable. |
| Off-site proof | Turn 54 verified six YouTube watch-page titles and three existing written companions. This turn did not re-check the latest media cuts, backlink profile, third-party citations or external distribution receipts. | Historical bounded evidence only; not new discovery impact. |

### Sampled pages

The 15 self-canonical pages in the live audit were:

`/`; `/about/`; `/technology/`; `/ai-in-real-life/`; `/books/`; `/books/one-workflow-at-a-time/`; `/books/how-to-play-no-limit-texas-holdem/`; `/poker/`; `/poker/10bb/`; `/poker/poker-under-uncertainty/`; `/poker/tournament-entry-prize-pool-ledger/`; `/poker/six-to-ten-bb-tournament-decisions/`; `/contact/`; `/poker/episodes/portland-meadows-ep1/`; and `/technology/ai-website-visibility/`.

Named committed source/output parity anchors:
- Turn 58: `#bridge-ev-break-even`, `#bridge-ev-two-prices`, `#bridge-ev-action-gate`.
- Turn 59: `#ledger-personal-cash-check`.
- Turn 60: `#bayes-range-update-formula`, `#bayes-range-update-check`.

These six content anchors were checked in source and generated repository HTML. Live content checks confirmed selected associated explanatory text and self-canonicals. The audit did not compare raw page bytes from production.

## Roadmap gate reconciliation

The original Turns 37 to 61 roadmap (November 20, 2026, planning artifact stored outside this public repository) was a planning artifact outside this repository. Relevant dated reports in this folder document actual work, which sometimes differs from the planned turn labels.

| Planned gate | Actual evidence | Disposition |
| --- | --- | --- |
| 37-38: complete release and live truth | Source-level release qualification plus bounded live smoke, with explicit no-checkout limits. The current audit repeats critical public content and sitemap checks. | **Partially achieved**. Full local suite and raw-byte production checks remain open. |
| 39-41: first-party baseline and assistant panel | Reproducible private intake and panel protocol; an excluded, non-eligible single-answer pilot; no authenticated owner performance counts. | **Protocol ready, numerical baseline missing**. |
| 42-46: differentiating practical-AI evidence | Website-repair proof path, human decision boundaries, RightsReceipt local tests and AI stop-rule matrix with explicit claims limits. | **Source-backed editorial work**, not measured search benefit. |
| 47-51: author and book routes | Two public book routes, reader exercises, topic ownership and first-screen evidence paths; possible retailer editions still unverified. | **Site journeys published; retail gate open**. |
| 52-55: poker/video crosslinks | ICM reproduction, video listing accuracy, documented revisions and free practice links. | **Bounded evidence-backed resources**, not current video-cut verification. |
| 56-60: experience and relevance | PRs #430-434 corrected TDA reopening, prize-pool ICM, cutoff shove, tournament receipt and Bayes teaching math. They **did not perform the roadmap's planned Turn 58 performance lab, Turn 59 three-journey completion audit or Turn 60 GSC query/page experiment**. Turn 50 did conduct a prior 375 px first-screen browser review. | **Accuracy improved; planned experience, performance and query gates remain open**. |
| 61: final scorecard | This dated, source-backed audit separates available publication evidence from missing measurements and tests. | **Scorecard delivered; full sprint success not certified**. |

No user-authored GitHub Actions, scheduled CI, paid API, new tracking or fabricated generative-AI schema was introduced in this turn.

## Prioritized next five improvements

1. **P0, release assurance:** Obtain a complete checkout of the latest `main` in a network-capable local environment, run the documented deterministic builders, snapshot search check, HTML5, internal links, full unit and browser suites, and status-bearing exact-byte live verifier. Fix actual failures, pin commit and record pass/fail. This is the largest current uncertainty, not a known website defect.
2. **P0, first-party measurement:** Use existing no-cost Google Search Console, Bing Webmaster and Umami owner interfaces and private exports. Record a complete previous month of Web clicks/impressions, top canonical query/page pairs, indexing outcomes, and available Google AI, Bing AI and assistant-referrer metrics. Keep raw exports private and all unavailable series marked as such. Do not subscribe to GSC Wizard merely to fill this report.
3. **P1, user completion:** Run and record 320 px keyboard and desktop journeys for an AI-case newcomer, an author-book reader and a NolanPoker viewer studying a hand. Correct only observed navigation, contrast, focus, download or misleading-label failures. Do not infer conversions from pageview counts.
4. **P1, performance diagnosis:** Obtain representative local Lighthouse or equivalent lab measurements for Home, the practical-AI hub, one book page and one long poker essay on documented desktop/mobile settings. Prioritize only proven image/font/CSS/JS bottlenecks; do not claim real-user Core Web Vitals from a lab run.
5. **P1, verified external identity and distribution:** Confirm actual KDP retailer edition URLs and identifiers from primary publisher records before adding purchase links or `Offer` schema. Connect selected distinctive source-linked site cases from relevant existing YouTube descriptions/companion references and Substack pieces only where the links help readers; record actual placements and avoid artificial backlinks or generic cross-posting.

## Measurement calendar and handoff

- November 2026 contains significant site edits, so a November comparison has mixed release exposure. **December 1-31, 2026 is the first complete potential post-release calendar month**, available to measure only after the month ends and source data settle. It is *future*, not a measured zero on November 20.
- The existing monthly Nolan GEO/SEO Scorecard automation and [measurement protocol](seo-geo-measurement-v1.md) may consume this report and later private exports. **Do not create a duplicate automation** or publish private source rows to GitHub.
- Do not declare the sprint's full release/impact exit complete until the above gates have actual, documented observations. Until then, the honest summary is: **the website has an increasingly verifiable body of published content; its search and assistant-discovery impact remains unmeasured.**

### Source ledger

- Current committed [search audit](../search-audit.json), [sitemap](../../sitemap.xml), and [robots.txt](../../robots.txt). Links are repository-relative only; the live versions are at `https://nolankido.com/sitemap.xml` and `https://nolankido.com/robots.txt`.
- [Turn 37 source qualification](seo-geo-turn37-release-parity-2026-11-20.md), [Turn 38 live smoke](seo-geo-turn38-live-verification-2026-11-20.md), [Turn 39 data access](seo-geo-turn39-first-party-baseline-2026-11-20.md), [Turn 40 prompt panel](seo-geo-turn40-answer-panel-protocol-2026-11-20.md).
- [Turn 47 edition verification](seo-geo-turn47-book-edition-verification-2026-11-20.md), [Turn 50 mobile-first-screen review](seo-geo-turn50-first-screen-identity-2026-11-20.md), [Turn 54 video links](seo-geo-turn54-nolanpoker-video-links-2026-11-20.md).
- [Turn 58](seo-geo-turn58-shortstack-action-tree-2026-11-20.md), [Turn 59](seo-geo-turn59-payout-example-consistency-2026-11-20.md), [Turn 60](seo-geo-turn60-bayesian-range-update-2026-11-20.md), merged as [PR #432](https://github.com/nolankido/nolankido.github.io/pull/432), [PR #433](https://github.com/nolankido/nolankido.github.io/pull/433) and [PR #434](https://github.com/nolankido/nolankido.github.io/pull/434).
- Google Search Central: [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) and [optimizing for generative AI](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). Google's documentation does not guarantee crawling, indexing or AI placements merely from technically accessible pages.
