# SEO/GEO Turn 51: canonical topic ownership without duplicate-page deletion

**Review date:** November 20, 2026 (Pacific/Honolulu)  
**Base main:** `f5f38bbc678c3a2740f4a3937a68e5c27d92cf3e` (Turn 50)  
**Scope:** practical AI guidance and measurement, with existing canonicals and URLs preserved.

## Reader-intent map

| Reader question or intent | Primary page (owns the answer) | Distinct supporting pages | Reason not to merge |
| --- | --- | --- | --- |
| Should this task use AI? | `/technology/should-i-use-ai/` | `/technology/task-brief/` | A decision screen precedes writing a brief. |
| How do I specify the task? | `/technology/task-brief/` | `/technology/organize-public-notes/` | Interactive brief builder versus an actual recorded notes case. |
| How do I check an AI answer? | `/technology/check-ai-answers/` | `/technology/check-ai-summary/`, `/technology/checking-ai-website-changes/` | General six-method reference versus a fictional summary exercise and a documented software defect. |
| How do I calculate AI workflow time? | `/technology/ai-time-savings/` | `/technology/ai-workflow-pilot/` | The calculator performs arithmetic from reader-supplied numbers, not data collection. |
| How do I design a valid AI workflow pilot? | `/technology/ai-workflow-pilot/` | `/technology/ai-time-savings/`, `/technology/local-ai-test-record/` | Trial design and quality gates require comparable observed tasks; model inference timings are insufficient. |
| How can a business evaluate AI-written review replies? | `/technology/local-ai-review-replies/` | `/technology/review-reply-evidence-audit/` | Application workflow and owner gate versus independent retrospective audit with synthetic negative controls. |
| Did this website gain search or AI visibility? | `/technology/ai-website-visibility/` | `/technology/checking-ai-website-changes/` | Publication receipts do not measure traffic, rankings, or assistant citations. |
| Where are the documented practical AI projects? | `/ai-in-real-life/` | `/projects/`, `/technology/` | Evidence-focused AI portfolio versus cross-topic project index and practical instruction hub. |
| Who is the person behind the work and books? | `/about/` | `/bio/`, `/books/`, `/creative/` | Identity/proof, reusable biography, book catalog, and creative overview serve different tasks. |

The review covered the Technology task menu, the AI answer-checking guide, specialist summary and website-check examples, the AI decision and brief utilities, the paired time calculator and pilot, a recorded local-model test, independent review-reply audit, and Home/author-book handoffs from Turns 49 and 50.

## Actual overlap and bounded repair

The Technology task menu previously grouped the time calculator, a customer-reply example, a controlled pilot and a search-visibility panel under a single **Measuring** row. The calculator introduction described whole-task cost; the pilot introduction also asked how to test whether AI saves time. These related headlines could cause visitors to take a calculation as evidence of a completed comparative trial.

The page bodies have genuinely different purposes, so removing one page or pointing both canonical tags at the same URL would discard useful material. Instead:

1. `_source/technology/home.html` and `technology/index.html` separate **calculate** from **test**, with direct routes to both, and retain the specialized search-visibility panel.
2. `_source/technology/ai-time-savings.html` and its committed output say the calculator owns arithmetic and point to the controlled pilot when observations are missing.
3. `_source/technology/ai-workflow-pilot.html` and its committed output say the pilot owns comparison design and quality gating, and point back to the calculator for arithmetic.
4. Add `_tests/test_turn51_topic_ownership.py` and include it in the manual local release checklist.

## Evidence boundary and release checks

**No redirects** are warranted: this audit did not establish that two pages deliver the same substantive content. **No new canonical** tag, schema, sitemap URL, tracking mechanism, retailer link, model call, article publication date, or automated workflow was introduced. Existing URLs and in-page fragment IDs remain. The worked six-case pilot is fictional and **not verified as a real-world saving**. Estimated calculator input is not observed productivity.

Pre-commit review from connected GitHub source inspected the six current source/public files and the read-only test runner; replacement uniqueness and paired source/public snippets were verified statically in this change. This verifies the proposed text edit, not the execution of the complete generator.

On a complete local checkout run:

```powershell
py -3 _scripts/build.py --check
py -3 -m unittest discover -s _tests -p test_turn51_topic_ownership.py -v
py -3 _scripts/check_search.py --verify-snapshot _reports/search-audit.json
py -3 _tests/check_html5.py
py -3 _scripts/check_internal_links.py
py -3 _scripts/local_release_checks.py
py -3 _scripts/check_live.py --only /technology/ --only /technology/ai-time-savings/ --only /technology/ai-workflow-pilot/ --attempts 3 --interval 5
```

The full build, local Python suite, HTML5 parser, Playwright desktop/mobile sessions and post-merge live-byte parity have **not** been run in the writing environment, which cannot resolve GitHub for a full checkout. Successful merge is not proof of deployed serving. Search Console impressions, clicks, conversion data and assistant citations also remain unmeasured.

## Exit criteria and next step

Each major practical AI question has an identified owner above, the substantive overlaps remain distinct, and the one ambiguous measurement handoff now explains the choice before asking a user to rely on a calculated number. No old page was deleted or relabeled as a duplicate without evidence. Next, inspect the revised live pages and target a genuinely weak answer or content gap, rather than publishing more near-duplicate pages for keyword volume.
