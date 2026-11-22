# SEO/GEO Turn 69: make the recorded source-check case reachable from related AI guides

**Date:** November 21, 2026 (Pacific/Honolulu)  
**Starting `main`:** `08e23da5332b3c1eecfa8a7774f6e54d5de2a1f6`, merged Turn 68, PR #442  
**Focus:** Improve internal discovery of existing practical-AI evidence without creating a keyword-targeted page or fabricating a client result.

## Live verification of the preceding turn

A fresh public read-only retrieval on November 21 confirmed that the Turn 68 internal link to `/technology/ai-workflow-pilot/#pilot-protocol` is present on **both** live `/` and `/start-here/`. The pilot's original self-canonical and free worksheet are available. This establishes **content-level publication** of those two links, not a status-bearing exact-byte verification, browser task-completion result or search-traffic improvement.

A separate DNS check in the local execution container again failed for `github.com`, `raw.githubusercontent.com` and `nolankido.com`. The actual full site checkout and local Python/Playwright suites therefore remain unavailable in this environment.

## Confirmed practical-AI discovery gap

The site's primary AI source-check guides and the actual AI-assisted weekly-reset editing case describe complementary decisions:

- `/technology/check-ai-summary/`: how to compare a **fictional** summary against its source, identify unsupported claims, and repair them.
- `/technology/organize-public-notes/`: how a retained source-to-output record from **eight public-work preparation notes** was checked for invented owners, omissions and unjustified certainty.
- `/technology/ai-weekly-reset/`: how **three public guidance documents** were edited into a shorter weekly-reset note with an explicit source ledger and five checking questions, without pretending to verify anyone's private commitments or actual time savings.

The third case already linked to neighboring source-check methods. A review of the committed HTML found **no reciprocal link** from either of the first two guides to the recorded case. Across seven sampled primary site hubs, the weekly-reset editing case had a direct link from only the Technology hub. This was a genuine internal discovery limitation for a reader who already wants to inspect a real source-to-draft comparison.

## Implemented change

1. Add one contextual paragraph in the existing "A review sequence for your own summary" section of both `_source/technology/check-ai-summary.html` and its public output. It points to `/technology/ai-weekly-reset/#notes-case-sources` and invites the reader to inspect published source notes and the checked rewrite. It expressly distinguishes the public editing material from a real private calendar or a measured household trial.
2. Add one contextual paragraph in the existing source-review conclusion of `_source/technology/organize-public-notes.html` and its public output. Its link points to `/technology/ai-weekly-reset/#notes-case-checks`, where the separate case's source checks are available. It excludes any claim of completed obligations or productivity benefit.
3. The target's **two exact section IDs** were checked against the existing public repository HTML and occurred once each. We did not edit or duplicate the target case.
4. Keep both existing articles' canonical URLs, original dates, titles, descriptions, free tools, source examples, verification tables and written results. Set accurate November 21 modified dates in the manifest, Article metadata, and **two sitemap lastmod entries**. Sitemap inventory remains **230** URLs, not 232. The Find utility remains noindex and its underlying heading index is unchanged, because neither article gained a new H2.
5. The summary review's additional explanatory text raises its estimated reading length from about eight to about nine minutes. The generated public reading estimate was adjusted accordingly. The notes case remains about seven minutes.
6. Add `_tests/test_turn69_ai_source_case_links.py` with seven source-only/negative-control/generated-parity cases. Update the prior Turn 29 notes case test's **current release** modified-date assertions without altering its archived historical baseline. Register the new module in the existing **manual** release checklist; record source ownership and accurate evidence boundaries in `AGENTS.md`.

## Observed source-level invariants

| Item | Before | Source-reviewed branch state |
| --- | --- | --- |
| Direct summary-review link to recorded case | 0 | 1 to `#notes-case-sources` |
| Direct public-notes case link to recorded case | 0 | 1 to `#notes-case-checks` |
| Link from Technology hub | Present | Unchanged |
| Target section identifiers | Two existing anchors | Both exist exactly once |
| Source and committed public explanatory paragraphs | N/A | Exact paired markup in each article |
| Original published dates | Oct 12 and Oct 27, 2026 | Unchanged |
| Actual modified dates | None and Nov 4 | Both Nov 21, 2026 |
| Public canonical URLs | Two existing | Unchanged |
| Sitemap URL count | 230 | 230, only two date records changed |
| New scripts, trackers or paid search API | None | None |
| Measured Google clicks, AI citations, conversions | Unavailable | Still unavailable, not measured zeros |

This work is intentionally about **the usefulness and visibility of existing source-backed content within the website**. It does not establish a ranking increase, an AI-assistant citation, an observed client workflow or a successful personal weekly reset. A source-checked editing proposal should never be confused with the accuracy of a personal calendar.

## Verification scope and remaining gates

**Performed:** authenticated read-only inspection of original GitHub manifest, source and public files; exact destination IDs in the existing target; source/public paragraph comparisons; two changed Article modification-date records; sitemap count and lastmod checks; static checks that each link occurs only once and the paragraph names the relevant evidence limitations.

**Not run:** the full Python deterministic builder, `unittest` regression suite, strict HTML5 parser, Playwright keyboard/mobile task completion, comprehensive site link audit or raw HTTP status-and-byte match. The isolated container still cannot obtain a full GitHub checkout. Static review, a passing PR merge, or a text extractor cannot be described as those tests passing.

From a full checkout of the eventual merged commit, run:

```powershell
py -3 -m unittest discover -s _tests -p test_turn69_ai_source_case_links.py -v
py -3 -m unittest discover -s _tests -p test_turn29_source_notes_audit.py -v
py -3 -m unittest discover -s _tests -p test_summary_review.py -v
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py --full --browser
py -3 _scripts/check_live.py --only /technology/check-ai-summary/ --only /technology/organize-public-notes/ --only /sitemap.xml --attempts 3 --interval 5
```

If the builder changes the summary's reading estimate or other generated text differently, reconcile actual generation and committed output; do not treat a guessed estimate as verified. Recheck both public links after deployment before claiming this specific Turn 69 improvement is live.

## Next priority

Complete the release gate from an executable checkout and compare actual first-party Search Console query and landing-page exports once legitimately available. For a visitor-focused next pass, verify an end-to-end 320px and desktop path from Home or Start Here to a source check, a practical decision, and a free downloadable artifact. Do not add paid subscriptions, GitHub Actions or speculative new content just to create another change.

**Relevant files:** `_source/technology/check-ai-summary.html`, `_source/technology/organize-public-notes.html`, `technology/ai-weekly-reset/index.html`, `_source/pages.json`, `sitemap.xml`, `_tests/test_turn69_ai_source_case_links.py`.
