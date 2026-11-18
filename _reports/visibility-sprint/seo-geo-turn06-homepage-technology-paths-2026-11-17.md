# SEO and GEO sprint: Turn 06, evidence-first reader paths

**Audit date:** November 17, 2026

**Site:** https://nolankido.com/
**Status:** Source change and local checks complete. Public deployment and post-merge visual check must be recorded separately.

## Goal and editorial boundary

Make it easier for someone who encounters Nolan Kido through search or an AI-generated answer to understand, within the first few interactions, what the site actually offers and what its evidence can support. Favor useful tasks and source records over slogans, unsupported authority claims, or added marketing copy.

The unchanged site position remains **AI Works, Human Decides**. Technology, Living Well, Poker, and Creative Work remain available in the global navigation. There is no new schema, keyword-stuffing, artificial freshness date, redirect, personal disclosure, paid service, or scheduled workflow.

This turn follows the Turn 04 twelve-question map and Turn 05 thirty-page audit. Turn 05 identified many sound pages but opportunities to deepen or expose relevant entry points. It did not identify a critical technical indexability defect. Therefore, a short route correction is a higher-confidence improvement than rewriting existing evidence-rich content.

## Before and after

| Visitor action | Before | After | Why the change matters |
| --- | --- | --- | --- |
| Click homepage **Practical AI in real life** | Landed at `/technology/#ai-works-human-decides`, below the hub introduction and first three choices | Lands at `/technology/` and starts with the introduction and the three visible choices | The general action label now matches its general destination. The philosophy section retains its own link within Technology. |
| Scan the Technology first three choices | Public projects, task brief, identity claim correction | Public projects, **check an AI answer**, **measure whole-workflow time** | Two widely useful nonbranded tasks and their explanatory pages are discoverable without searching the long hub. |
| Find the displaced task brief and claim correction | Both were top-level cards | Both remain in a plainly visible **Other first steps** line directly below the cards | Preserve prior useful paths and their evidence without introducing another card row. |
| Find the Start Here task picker | Already included the answer-checking page and task brief | Unchanged | Avoid redundant edits to an already clear entry route. |

## What is actually on the destinations

1. [Public technology projects](https://nolankido.com/technology/#technology-projects) link to Review Reply Writer, Preflight, and Dinner on Time, with project-specific examples and limits. Their presence demonstrates publicly described artifacts, not business adoption or measured client outcomes.
2. [Check an AI answer](https://nolankido.com/technology/check-ai-answers/) teaches checking individual claims, original citations, arithmetic, code, and unconfirmed commitments. It includes three previously recorded examples and distinguishes supported, contradicted, and unresolved claims. The examples are not new benchmark runs.
3. [Full-workflow time calculator](https://nolankido.com/technology/ai-time-savings/) accepts the reader's own numbers for manual work, assisted production, review, setup and upkeep. It performs arithmetic locally, makes no AI call, and does not observe actual work. The worked examples are hypothetical and are labeled as such.
4. [AI task brief](https://nolankido.com/technology/task-brief/) is still offered at the top of Technology in a secondary but visible sentence. It helps specify constraints and acceptance checks, not run an AI model.
5. The [identity claim correction](https://nolankido.com/technology/#identity-claim-audit) remains linked in the same sentence, so visitors can inspect the original claim, public sources and corrected record.

No additional expertise claims, success metrics or testimonials were introduced.

## Files affected

- `_source/home.html`: Change one primary navigation target from a deep philosophy fragment to `/technology/`.
- `_source/technology/home.html`: Replace two opening choice cards with specific question-led tasks; retain their previous destinations in visible secondary text; align the introduction with the chosen tasks.
- `_tests/test_turn26_technology_first_screen.py`: Update the existing first-screen contract to verify current choices, their real routes, the two preserved secondary links, the homepage CTA target and canonical metadata without requiring an obsolete exact update date.
- `index.html` and `technology/index.html`: Rebuilt public outputs.
- `poker/find/index.html` and `poker/study/index.html`: The deterministic build also reconciled two previously stale generated files to their already-authored poker source. These are **not newly written poker lessons** and are separately disclosed because they are outside the main navigation change.
- This report and the visibility-sprint README.

## Technical and mobile checks

| Check | Result | Evidence boundary |
| --- | --- | --- |
| `python3 _scripts/build.py` | Pass, 253 generated files, four output changes | Derived files are reproducible from checked-in source. |
| `python3 _scripts/build.py --check` | Pass, zero remaining changes | No unbuilt generated output remains locally. |
| `python3 _scripts/check_search.py` | Pass, 224 public pages, 224 sitemap URLs, unique titles/descriptions | Static metadata integrity, not a search rank or indexation result. |
| `python3 _tests/check_html5.py` | Pass, 229 HTML pages plus parser self-test | HTML5 structure, not every visual breakpoint. |
| `python3 -m unittest _tests.test_turn26_technology_first_screen` | Pass, eight tests | First-screen routes, source-output match, canonical and link preservation. |
| `git diff --check` | Pass | No whitespace errors. |
| Site CSS relevant to 320px | Reviewed `.identity-readings` three-column grid with a single-column breakpoint below 900px, and heading links with `overflow-wrap:anywhere` | Static CSS evidence only; a 320px browser layout check is still required after deployment. |
| Full release script | Attempted, then stopped after unrelated legacy failures | Shallow checkout lacked historical commits required by archived rewind tests. At least one older poker count assertion also expected a historical page total. The focused live-link, build, HTML5, search and changed-path tests above are the verification basis for this turn. |

### Post-publication verification

- [ ] Homepage's first primary AI action resolves to `https://nolankido.com/technology/` and shows the Technology introduction, not a deep anchor.
- [ ] Technology intro has exactly three first-choice cards in the order projects, answer checking, full-workflow time measurement.
- [ ] Task brief and identity-correction links both remain accessible above the deeper content sections.
- [ ] At a 320px viewport, there is no page-level horizontal overflow, inaccessible card link or clipped CTA.
- [ ] Document deployed commit and merge request.

## Interpretation and measurement

This change improves the clarity and prominence of existing human-useful answers. It does **not** prove a change in Google/Bing indexing, impressions, click-through rate, traffic, AI mentions, citations, or conversion. Maintain the existing 25-question assistant answer panel and query measurement rules. After enough time has passed, compare the same property, device, country and date windows, and distinguish missing data from zero.

## Turn 07 handoff

Use the Turn 04 question map and Turn 05 evidence audit to select **one** high-priority nonbranded question with a meaningful missing explanation. Create or deepen one source-supported, answer-first article with a direct summary, concrete worked example, provenance and uncertainty, links to related pages, and a clear author identity. Avoid publishing a near-duplicate or padding the site simply to increase article count. Run the same build, link, metadata and HTML5 checks and update the frozen measurement ledger without claiming ranks or AI citations.
