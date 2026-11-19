# SEO/GEO/AEO Sprint Turn 18: Review Reply Writer time break-even

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 18 of 25
- **Base checkpoint:** `edf8fd928d9ad04d06147457c747dc3a7901a222` (Turn 17, merged PR #389)
- **Canonical retained:** https://nolankido.com/technology/ai-time-savings/
- **Reader question:** Does AI save time when replying to customer reviews?
- **Scope:** Existing calculator and case pages, a downloadable source-versus-hypothesis worksheet, a local regression test and native hub links. No duplicate canonical page, paid service, background run or GitHub Actions.

## Why this change matters

The time calculator already counted production, review, repair, setup and upkeep, with general fictional examples. The Review Reply Writer case already documented a human owner gate and honest evaluation limits. A search reader could nevertheless see the reported fast Gemma responses and infer that the project had saved a business time. The gap was a single source-bounded answer connecting the actual timing record to the full-task decision.

The new `#reply-time-break-even` section opens with the short answer: a fast model response does **not** establish staff time saved. Its historical evidence comes from the [pinned October 13, 2026 Gemma 3 4B smoke result](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-quality-smoke-2026-10-13.json), independently reviewed at that exact commit for this turn. The fixture's three fictional cases have recorded elapsed times:

| Archived fictional case | `elapsed_ms` | Converted time |
| --- | ---: | ---: |
| Cafe praise | 19,536 | 19.536 seconds |
| Cafe complaint | 18,157 | 18.157 seconds |
| Mixed hotel review | 19,325 | 19.325 seconds |

These are historical Linux CPU case receipts, not a new run, current laptop speed, human baseline, employee trial, review or owner approval time. The separate [independent review evidence](https://nolankido.com/technology/review-reply-evidence-audit/#reply-audit-reading-checks) also illustrates why a passing lexical check is weaker than a human policy and evidence decision. Nothing in these three machine timings can quantify total business time saved.

## The deliberately fictional calculation

To answer a practical break-even question without fabricating measurements, the page and the [downloadable worksheet](../../downloads/review-reply-time-break-even.md) introduce a clearly **invented cafe scenario**, entirely separate from the three archived timings.

| Variable | Fictional assumption |
| --- | ---: |
| Usual acceptable reply, M | 6 minutes per reply |
| Assisted preparation and production, A | 2 minutes per reply |
| Human review and repair, R | 3 minutes per reply |
| Initial setup, S | 20 minutes |
| Upkeep across the comparison, K | 5 minutes |
| Number of comparable replies, N | 10 |

Usual effort is `N * M = 60 minutes`. Assisted effort is `S + K + N * (A + R) = 75 minutes`. At this sample size the assisted method adds 15 minutes. Its 1-minute per-reply advantage before overhead requires 25 replies to break even and 26 to have any positive net saving under unchanged assumptions. Raising review effort to 4 minutes makes its per-task advantage zero, so the fixed overhead cannot be recovered by repeating that unchanged workflow.

The values were verified independently against the site's existing `assets/workflow-time.js` integer-minute calculation, which returned the expected 60-minute usual total, 75-minute assisted total, negative 15-minute saving, 25-reply break-even and first positive saving at 26. A positive arithmetic result would still require an acceptable, owner-approved reply to count as a substitutable completed task.

The worksheet preserves missing measurements explicitly and offers a blank locally kept observation record. The Review Reply Writer case, Technology hub and Resources link to the existing calculator section. The calculator links back to the owner's approval gate and a paired-trial methodology in `/technology/ai-workflow-pilot/`. The manifest's meaningful update is November 18; both original October 27 article publication dates are preserved.

## Local verification observed

| Check | Recorded result |
| --- | --- |
| `python _scripts/build.py` | 253 generated outputs, 6 changed outputs |
| `python _scripts/build.py --check` | 253 checked, zero drift |
| `python _scripts/check_search.py` | Pass, 225 sitemap URLs, zero metadata errors |
| `python _tests/check_html5.py` | Pass, 230 HTML pages, zero parser failures |
| `python _scripts/check_internal_links.py` | Pass, 232 HTML pages and 16,276 internal links, zero issues |
| `python -m unittest discover -s _tests -p 'test_turn18_reply_time_break_even.py' -q` | Five tests passed, including source boundaries, calculation, canonical/dates and negative mutation controls |
| Direct `node` calculation with `assets/workflow-time.js` | Verified the independent 60/75/-15/25/26 worked example |

The full historical unit suite and browser tests were not claimed to have run. No real employee time, customer-service quality, conversions, search impressions, rankings or AI-assistant citations were measured. Read-only deployed-byte parity, if verified after merge, belongs to a separate public release receipt.

## Suggested Turn 19

Review the Search Console and AI-answer citation measurement pathway for a specific priority question or page. If authenticated query data is unavailable, tighten one evidence-backed answer and design a falsifiable measurement log instead of claiming ranking or generative-answer uplift.
