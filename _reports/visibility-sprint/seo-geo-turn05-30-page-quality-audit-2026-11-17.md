# SEO/GEO Turn 05: thirty-page evidence and discoverability audit

**Property:** https://nolankido.com/  
**Assessment date:** November 17, 2026 (Hawaii)  
**Sprint:** Turn 05 of 25  
**Outcome:** Audit completed; one confirmed low-severity content repetition and five evidence/reader-route improvement candidates. No confirmed critical or high-severity public-HTML blocker in the sampled pages.

## Executive judgment

The next meaningful step for the site is **better task routing and more original proof**, not an indiscriminate wave of new articles. This sample is unusually substantial: the 30 reviewed public pages use distinct titles and descriptions, readable HTML, named subject intent, self-referencing canonicals, and extensive internal links. The poker foundations include an auditable pot-odds example, the tournament articles distinguish chip calculations from payout- or range-sensitive decisions, and the AI cases repeatedly state what was actually run and what remains unmeasured.

This is **not** a claim that Google has indexed all 30 pages, that every external factual statement has been independently verified, that their mobile visual layout is flawless, or that assistants cite them. Those require separate evidence. The immediate editorial decision is to protect the finished work, correct a small repeat heading, and examine a few high-value reader paths before altering copy.

## Scope and provenance

- The sample contains **exactly 30 current public URLs**: all twelve destinations prioritized by Turn 04, supporting AI cases, poker foundations, manually built poker companions, the home/About/portfolio hubs, Creative Work, and two Living Well routes.
- A manually executed, **read-only HTTP GET and standard-library HTML parser** checked each URL's status, final destination, self-canonical, title and description, H1/H2, language, viewport, image-alt attribute presence, JSON-LD syntax, approximate main content words, main-content links and source domains. The live sitemap included all 30. Snapshot source: `turn05_live_audit_raw.json`, collected in the working scratch environment; the smaller accompanying CSV freezes the review matrix in the repository.
- Direct content spot checks covered the poker math calculation, first-live-tournament plan, AI-time-savings method, and six-to-ten-BB price examples. The exact live text was consulted, not reproduced in bulk.
- The existing repo's [read-only full-sitemap indexability audit](https://github.com/nolankido/nolankido.github.io/blob/main/_scripts/live_indexability_audit.py) and Turn 02 report already covered **224 sitemap pages and five intentional noindex utilities**. This Turn 05 sampling work does not reclassify the five utilities as failures.
- The connected on-page SEO and top-page performance tools were both attempted with `sc-domain:nolankido.com` and returned `INVALID_ARGUMENT`. The underlying configuration/authorization cause was not established. **Clicks, impressions, CTR, positions, indexed-state and AI assistant citations remain unavailable, not zero.** Nothing is ranked by invented traffic.
- A bounded public-source comparison was performed in Turn 04, including established poker instruction and original Google people-first guidance. This turn does not claim to reproduce a live full competitive SERP.

## Technical HTML results (30 of 30 pages fetched)

| Check | Result | Interpretation |
| --- | --- | --- |
| Public HTTP GET returns 200 | **30/30** | No sampled HTTP fetch failure. |
| Declared canonical exactly matches requested page | **30/30** | The sampled pages declare a consistent preferred URL; not a Google canonical-selection result. |
| One nonempty H1 | **30/30** | A structural heading exists; one page repeats it as the first H2. |
| Nonempty distinct HTML title and meta description | **30/30** for both; no exact duplicates in sample | No observed missing or same-copy meta blockers. Search snippets are not guaranteed to use the supplied description. |
| `lang` and mobile viewport | **30/30** for both | Basic document-language and viewport signals are present. Not an accessibility or mobile usability certification. |
| JSON-LD blocks parse as JSON and expose types | **30/30** | No JSON syntax error in the sample. Schema semantic correctness and rich-result eligibility were not independently tested. |
| `<img>` elements lacking an `alt` attribute | **0 across 30** | Basic alt-attribute check passes. Appropriateness of every alt phrase was not visually tested. |
| Sampled pages carrying an explicit `noindex` meta tag | **0/30** | Expected for index-intended pages. Does not establish indexing. |
| Pages with zero links from their main content | **0/30** | No observed isolated main-content destinations in this sample; full-site inbound links were assessed in Turn 02. |
| Approximate words extracted from `<main>` | **823 to 4,736**; median **1,539.5** | No page appears empty or mechanically thin by a crude word count. Word count alone does not establish quality. |

**Low-priority presentation checks:** Three HTML titles are longer than 65 characters and four meta descriptions longer than 160. These are *display-length observations*, not measured truncation, SEO penalties or a reason to rewrite them without query and snippet evidence. No title/description rewrite is a priority on these facts alone.

**One confirmed content repetition:** `/poker/six-to-ten-bb-tournament-decisions/` uses the exact H1 text again as its first H2. Both the main guide and its mathematics are otherwise substantial. A descriptive first H2 that introduces the reader's decision would make scanning cleaner without manufacturing a new page or claim.

## Five-score editorial rubric

Each entry receives five provisional **1-to-5 judgments**, displayed as `E/F/T/A/L` below:

1. **E, evidence-backed accuracy readiness:** source limitations, checkable references, examples, and relevant caveats in the public page. This is **not** a complete independent audit of every external fact or all poker math.
2. **F, firsthand and original value:** real case material, original calculation, documented experience, public artifact, or honest research method.
3. **T, reader-task completion:** can the user find an actionable answer, exercise, example, checklist, or next step?
4. **A, author and subject clarity:** is Nolan's relationship to the content, its purpose and limitations understandable?
5. **L, native internal discoverability:** visible useful routes into and out of the content. Counts do not alone determine this score.

**Score interpretation:** 5 = strong on inspected evidence, 4 = solid with a possible targeted test, 3 = adequate for a different or broader hub task, 2 = expected limited firsthand value in a generic teaching reference, 1 = serious uncovered concern. These are **editorial review scores**, not Google's ranking factors. In particular, a clear fictional beginner hand can earn a low *firsthand* score yet still be exactly the right, high-quality instructional page.

## Thirty-page disposition ledger

Use the full absolute URL `https://nolankido.com` followed by the path shown. There is **exactly one** primary disposition per page. Detailed numeric observations and scores are preserved in [`seo-geo-turn05-30-page-audit-matrix-2026-11-17.csv`](seo-geo-turn05-30-page-audit-matrix-2026-11-17.csv).

| URL path | E/F/T/A/L | Disposition | Specific evidence or next action |
| --- | --- | --- | --- |
| `/` | 4/4/4/5/5 | **Keep** | Three evidence-oriented entry points, clear Nolan identity, and 29 distinct main-content internal destinations. Test which path readers actually choose in Turn 06; do not add links indiscriminately. |
| `/about/` | 5/5/5/5/5 | **Keep** | Visible identity, professional context, project links and external public profiles. Existing `Person` and `ProfilePage` data are present. Avoid making unverifiable reputation claims. |
| `/start-here/` | 4/3/5/5/5 | **Keep** | Offers task- and interest-based routes and explains evidence types. No observed missing core entry path. |
| `/projects/` | 5/5/4/5/5 | **Keep** | Browser experiences and three inspectable application cases are separately labeled; public evidence and status sections already exist. Do not duplicate them on `/about/`. |
| `/technology/` | 4/5/4/5/5 | **Deepen** | Approximately 4,736 main-content words and 51 distinct internal targets. First test whether a new reader reaches an inspectable AI answer check, original project and calculator in one or two clear decisions. Simplify competing choices only if this test fails. |
| `/technology/check-ai-answers/` | 5/4/5/5/4 | **Keep** | About 3,617 words of source, arithmetic, writing and code checks with related examples and referenced standards. Maintain the answer-first worksheet path; no evidence of thinness. |
| `/technology/ai-time-savings/` | 5/4/5/5/4 | **Deepen** | Calculator includes setup, review, repair and upkeep, plus worked examples and negative savings. Add **actual comparable full-workflow observations** if collected; keep illustrative numbers labeled meanwhile. |
| `/technology/local-ai-gaming-laptop/` | 5/5/4/5/4 | **Deepen** | Original Windows/Ollama/LM Studio setup is documented and expressly says no measured laptop benchmark. The next unique-value layer is a reproducible *actual* local test record, not a guessed speed claim. |
| `/technology/local-ai-review-replies/` | 5/5/5/5/4 | **Keep** | Source-backed owner policy and archived draft/review examples are present. It links to the narrower independent audit rather than duplicating its task. |
| `/technology/review-reply-evidence-audit/` | 5/5/5/5/4 | **Keep** | Recorded six-case check, clear fictional customer scenarios and a checker failure case. Avoid converting the test into unsupported product-efficacy marketing. |
| `/technology/ai-book-continuity-checker/` | 5/5/4/5/4 | **Keep** | Source-linked sample and Watson wound example demonstrate the verification method; limitations are visible. Preserve the prototype-versus-proven-system boundary. |
| `/technology/organize-public-notes/` | 5/5/5/5/4 | **Keep** | Original input, outputs and source identifiers are presented. No external-domain citation is required just to substantiate Nolan's own recorded exercise. |
| `/technology/ai-weekly-reset/` | 4/4/4/5/4 | **Leave untouched** | Source-based editing task is distinct; no measured demand justifies rewriting this niche case now. |
| `/technology/local-ai-test-record/` | 5/5/5/5/4 | **Leave untouched** | Historical measurements and their limitations are clear. Do not date-refresh or transplant hosted timings into the laptop guide. |
| `/technology/dinner-on-time/` | 4/5/4/5/4 | **Leave untouched** | Video-supported cooking-planner prototype distinguishes demonstrated behavior and future ambition. Maintain its honest scope. |
| `/technology/rightsreceipt-ai-licensing/` | 5/5/5/5/4 | **Keep** | Separates a $425 test fixture from a sale, a local invoice rehearsal from payment and AI from permission. Original source links support the audit trail. |
| `/poker/` | 4/4/4/5/5 | **Deepen** | Broad poker library includes 78 main-content internal destinations and a named beginner route. Test novice ability to choose **rules**, **first live event**, or **short-stack decision** without scanning a long directory. Preserve the resource breadth. |
| `/poker/six-to-ten-bb-tournament-decisions/` | 5/4/5/5/4 | **Correct** | Its first H2 exactly repeats the H1. Replace that repeated subheading with a task-oriented label, preserving tables, stack assumptions, source caveats and real modification-date rules. |
| `/poker/satellite-bubble-seat-equity/` | 5/3/5/5/4 | **Keep** | Explicit closed model, seat-equity arithmetic and specialist references serve a distinct task. Do not treat illustrative numbers as a live solver output. |
| `/poker/poker-math/` | 5/3/5/5/4 | **Keep** | Spot-checked example: 20 in the pot, bet 10, call 10 gives a final pot of 40 and break-even 10/40 = **25%**; the no-tie 30% EV calculation is +2 chips. It links to the longer pot-odds workshop. |
| `/poker/first-live-tournament/` | 4/4/5/5/4 | **Deepen** | Useful registration, table etiquette and practical preparation plan. Its main-content links do **not** directly target `/poker/holdem-basics/` or `/poker/hand-rankings/`; test two compact, contextual prerequisite links, without creating a competing beginner article. |
| `/poker/holdem-basics/` | 4/2/5/5/4 | **Keep** | Fictional complete hand clearly teaches blinds, position and showdown. The fictional label is appropriate, not a lack of quality. |
| `/poker/hand-rankings/` | 4/2/5/5/4 | **Keep** | Ranked five-card combinations and four fictional showdowns solve the rules question. Avoid padding with redundant hand-ranking pages. |
| `/poker/study/` | 4/4/5/5/5 | **Keep** | Review worksheets, practice paths and 55 internal destinations are already organized. Recent Turn 167 and Turn 168 work added responsive, script-free practice readers and section-matched navigation. Do **not** reopen those fixes without a regression. |
| `/poker/nolan-kido/` | 5/5/5/5/4 | **Keep** | Independently linked player-result records and gross-versus-net caveats support identity and tournament claims. Do not infer a WSOP ring or unverified results. |
| `/poker/episodes/portland-meadows-ep1/` | 5/5/5/5/4 | **Keep** | Two bounded firsthand hand sections, an evidence ledger and result distinctions are visible. Do not restore unverified offsets or claim solver conclusions from incomplete inputs. |
| `/poker/episodes/portland-meadows-standoff/` | 5/5/4/5/4 | **Leave untouched** | Public source-limited companion clearly describes archived v9 evidence and the limits of current-video verification. Additional details need fresh checked footage before publication. |
| `/creative/` | 4/4/4/5/4 | **Leave untouched** | Original stories/illustration/creative exercise are discoverable; no observed demand supports priority over AI and Poker. |
| `/living-well/` | 4/3/4/5/4 | **Leave untouched** | Clear subject hub and 38 contextual destinations; no verified keyword/assistant opportunity justifies expanding this pillar now. |
| `/living-well/scattered-notes-to-next-step/` | 4/4/5/5/4 | **Keep** | A bounded everyday action exercise explicitly links to the deeper recorded Technology notes case. They serve different reader depths, not a confirmed duplicate-keyword problem. |

**Disposition totals:** 18 keep, five deepen, one correct, six leave untouched; **zero consolidations and zero redirects** are justified by this evidence. Similar vocabulary alone does not establish keyword cannibalization. No pages should be deleted merely to reduce the count.

## Priority backlog for the next substantive edits

These priorities are **expected reader benefit and feasibility**, not measured click potential.

| Order | Target and work | Reader benefit and completion test | Constraints |
| --- | --- | --- | --- |
| 1. Low-effort correction | `/poker/six-to-ten-bb-tournament-decisions/`: replace the first repeated H2 with a question or task label introducing the specific pricing comparison. | One unambiguous page title, a distinct and useful first section heading, unchanged verified arithmetic and source caveats. | Make this small correction within a reviewed poker content edit and rebuild the generated page. Never change dates without a real content revision. |
| 2. Turn 06 lead | Homepage and `/technology/`: test a cold reader's route to a concrete **answer-check**, one **original AI case**, and the **time-savings calculator**. | A user can identify and reach the most inspectable proof through one clear choice; avoid adding more navigation than needed. | Existing homepage has 29 main internal targets and the Technology hub has 51. Measure the journey locally before changing links. |
| 3. Poker reader choice | `/poker/`: test beginner, first-live, and six-to-ten-BB routes on desktop and narrow mobile. | Three distinct entry questions are easy to choose, while the 78-link resource directory remains available below. | Do not rebuild Turn 167/168 script-free reader and navigation work, already shipped. |
| 4. Direct prerequisites | `/poker/first-live-tournament/`: consider native in-sentence routes to `/poker/holdem-basics/` and `/poker/hand-rankings/`. | A first-time reader can resolve missing rules knowledge without backing out to a directory. | The page already links broader guides, so add no duplicate summary or intrusive navigation. |
| 5. Genuine workflow evidence | `/technology/ai-time-savings/`: append one *recorded* comparable before/after task when honest full-workflow timing inputs exist. | Users can reproduce a measured total time calculation, including checking and repairs, alongside the current illustrative calculator. | Never invent benchmark timings or treat a quicker draft as end-to-end savings. |
| 6. Genuine local performance evidence | `/technology/local-ai-gaming-laptop/`: add a versioned real-machine test with task, hardware, model, prompt, sample and measured timing only after collecting it. | Readers can make a bounded hardware/workflow decision from actual recorded performance. | Do not misattribute hosted CPU tests to the MSI Crosshair. Until data exists, preserve current candid no-benchmark language. |
| 7. Measurement access | Establish working first-party query/inspection views before re-ranking content opportunities. | Future priorities can be justified by actual page/query impressions, clicks, CTR and indexing/citation observations. | Current tools returned `INVALID_ARGUMENT`; do not infer an account-access diagnosis, fake zero traffic or initiate paid services. |

## Matters that do **not** need another fix this turn

- **Indexability fundamentals:** all sampled public pages delivered expected status, self-canonical, H1, metadata and basic JSON-LD syntax. Preserve the intentional five noindex utilities and the full sitemap check from Turn 02.
- **Search crawler separation:** Turn 03 already tested OAI-SearchBot and Bingbot separately from GPTBot training preferences. Do not silently change privacy rules.
- **Turn 167 and Turn 168 poker reader accessibility:** responsive, script-free practice reading and section-specific navigation were recently delivered. Reopen only for a real failing browser scenario, not for a fresh-looking sprint task. [Turn 168 repository commit](https://github.com/nolankido/nolankido.github.io/commit/ef0d4089892287152a49c96c395886c1cd33a8cd).
- **Gambling accuracy and privacy:** keep tournament cash figures separate from advertised prizes, payout versus profit, recorded action versus retrospective read, and chip-EV versus ICM. Never add opponents' identities or uncertain card suits for perceived authority.
- **Artificial publication freshness:** maintain the later actual revision date when content genuinely changes. A re-run of a build or an SEO report is not a content revision.

## Verification limits and next step

The read-only parser did not render pages in a graphical browser, validate all outbound links, compare current YouTube footage frame by frame, or obtain Google/Bing private performance metrics. Its approximate word count includes visible text within `<main>` and is not a meaningful ranking predictor. The quality scores summarize visible public evidence and limited spot checks, not an independent verification of every factual claim.

**Turn 05 acceptance:** exactly 30 URL decisions; five explicit quality dimensions; a complete measured technical sample; no invented search demand; recent shipped fixes respected; a prioritized action list with sources, risks and completion tests. **Met.**

**Turn 06 instruction:** Begin with the current homepage and Technology hub. Test three cold-reader click paths to the highest-quality evidence pages and one practical poker task on desktop and 320-pixel mobile. Only if a path is unclear, make the smallest source change that improves it, rebuild the owned pages locally, run the existing checks, and confirm the live response. Record actual differences and protect current canonical, author and privacy signals. Do not create new articles, reenable GitHub Actions or claim a ranking lift without measured data.
