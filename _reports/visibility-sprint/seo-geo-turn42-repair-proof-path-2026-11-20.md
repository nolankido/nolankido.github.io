# SEO/GEO improvement Turn 42: Put the source-backed website repair evidence first

**Date:** November 20, 2026 (Pacific/Honolulu)  
**Site:** https://nolankido.com/  
**Page:** https://nolankido.com/technology/checking-ai-website-changes/  
**Starting `main`:** `5a39bd83e239603691bb9c43f0df218c4c33559e`  
**Roadmap:** Turn 42 of the planned 37–61 SEO/GEO sprint.

## Decision

The original AI-assisted HTML5 repair is a distinctive documented case on this website. The page already contains an accurate chronological explanation, a reduced offline parser demonstration, a pinned source-before-and-after comparison, a historical test receipt, and strong caveats. The problem was **discovery inside the article**, not an absence of facts: the exact source comparison appeared below the longer explanation, so a reader had to scroll before reaching direct independent proof.

Rather than add another keyword page or repeat a large case narrative, Turn 42 adds a concise **four-link proof path** directly after the first case summary, before the rest of the article. It connects the historical code defect to actual source changes and the reproducible teaching check. This reduces the distance between the opening claim and independently inspectable evidence.

## Evidence checked in this turn

The GitHub connector retrieved the two pinned historical source files themselves:

- **Before**: `_source/technology/task-brief.html` at commit `2bf8908339e06f604cea00f0254494e17171ecf4`, with the closing sequence `</div></div></section>`.
- **After**: the same file at commit `73782caa4697204690c679626b36427c28201234`, ending with `</div></section>`.

These directly inspectable source endings support the **one-extra-closing-tag** claim. They do not independently establish every other effect of the historical release.

The existing `downloads/website-check-evidence.json` reports a historical `end-tag-too-early` HTML5 parser error for the `div` on `/technology/task-brief/`, after 347 unit/content tests in the prior test suite. It also records the repaired candidate, the archived 21-browser-suite result and 235 public GET targets on October 11. Those historical counts remain **reported release records**, not newly rerun results in Turn 42.

The existing `downloads/website-check-reproduction.py` is a **reduced negative-control fixture** for the same HTML5 failure class. It is not the full historical source tree or a replay of the earlier test run.

## Changes implemented

1. Added one short paragraph in `_source/technology/checking-ai-website-changes.html`, positioned before the existing in-page navigation. It directly links, in evidentiary sequence, the pinned broken source, pinned repaired source, historical JSON test record and illustrative Python parser demonstration.
2. Added a fifth link to the page's existing `#case-source-diff` explanation for readers who want the exact source-diff context and limitations.
3. Applied **the exact same inserted paragraph** to the committed generated `technology/checking-ai-website-changes/index.html`. No other article prose, headings, source code, canonicals, titles, social metadata, JSON-LD identities or tracking were modified.
4. Added seven focused tests in `_tests/test_turn42_repair_proof_path.py`. They check early and identical source/output placement; exact source IDs; the recorded error class and reported counts; missing or incorrect proof links via negative controls; unchanged historical release labels; existing fixed GET download registration; and original deterministic builder output parity when run from a complete checkout.
5. Registered the regression tests with the existing `_scripts/local_release_checks.py` and updated `README.md` with the reader and maintainer handoff.

The proof paragraph adds about thirty visible words, without another H2 or anchor. The estimated reading length remains **six minutes** under the existing 225-words-per-minute rule. The six original reader-outline sections and existing anchors are unchanged. No new public page or sitemap entry is needed.

## Important date and evidence restrictions

The original article's `datePublished` remains **2026-10-11** and its `dateModified` remains **2026-11-18**, when its substantive source audit and offline runbook were updated. This turn changes the *navigation to existing proof*, not the historical event, its claims, or the original substantive record. Do not fabricate a new published article date or reclassify the 2026 tests as current.

The first-party repair case supports practical software checking, not a measured benefit from AI, a general model reliability rate, an SEO ranking increase or external endorsement. Do not present an HTML5 parse as full accessibility/security certification.

## What was checked and what remains outstanding

- GitHub's original pinned source endings were read directly and compared.
- Original source and generated article were confirmed to contain one identical new proof paragraph near the top.
- The original canonical, six existing section IDs, author identity links and article dates were preserved.
- The seven new unit test definitions were written and made part of the manual local release checklist. Source and committed output were inspected for exact paragraph equality, but the **full repository Python tests were not executed** in this connector environment.
- A complete checkout was not obtainable from this execution environment because GitHub DNS failed. The full `build.py --check`, HTML5, internal-link and browser suites remain **unverified**.
- An independent custom-domain retrieval before this edit confirmed that the case page and its existing evidence links were accessible. No claim is made about post-merge production byte parity until observed.

### Acceptance commands from a complete local checkout

```powershell
py -3 _scripts/build.py --check
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 -m unittest discover -s _tests -p test_turn42_repair_proof_path.py -v
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/check_live.py --only /technology/checking-ai-website-changes/ --attempts 3 --interval 5
```

Only an HTTP status and byte-matching response from the last command establish exact live-publication parity. A browser-extracted page or a GitHub merge does not independently establish live status, Google indexing, user engagement or search visibility.

## Next turn

**Turn 43:** Document a complete, original AI-assisted content-production workflow, from source truth and drafting to human checks, final publication and remaining unknowns. Prefer an already completed public case with inspected evidence rather than a fictitious automation success story.

No GitHub Actions, cron, paid API, new analytics, private research records, source-version rewrites or background work were introduced.
