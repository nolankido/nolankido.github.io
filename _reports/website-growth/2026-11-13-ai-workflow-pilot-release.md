# Public release: reproducible AI workflow pilot

Prepared November 13, 2026. This is a public release note and verification record, not a private strategy plan.

## What changed

- New `/technology/ai-workflow-pilot/` worked guide explains how to test one bounded task, compare two methods at the same acceptance standard, and count setup, preparation, review, correction and upkeep.
- A fictional six-case paired log, an empty CSV template, and an offline standard-library Python audit reproduce 139 manual minutes, 112 assisted task minutes, 172 total assisted minutes after overhead, a 33-minute loss, and one rejected quality label.
- Source-backed context links public Review Reply Writer receipts and the limits of what they measure. The page explicitly does not assert observed business time savings, customer adoption, actual pilot participation, or any statistical effect.
- Technology hub, calculator and public Projects index now link to the guide. Generated article metadata, sitemap, local search and feeds derive from one manifest entry with the actual publication date.
- New focused regression checks are added to the existing manual local release checklist. No GitHub Actions or automated recurring jobs.

## Evidence boundaries

- The six timing rows and their human quality labels are synthetic. They are not a productivity study, benchmark, or model run.
- The checker verifies the supplied numbers and field status labels, not the facts, policy compliance, review process, causal effect or real-world quality of a workflow.
- The NIST AI RMF Measure guidance is cited for general methodological principles, not as an endorsement or validation of this particular pilot design.
- Actual search indexing, AI citations, referral traffic and visitor usage require separate measurement.

## Local verification

Run:

```text
python downloads/ai-workflow-pilot-audit.py --self-test
python downloads/ai-workflow-pilot-audit.py --input downloads/ai-workflow-pilot-example.csv --setup-minutes 45 --upkeep-minutes 15
python _scripts/build.py --check
python _scripts/check_search.py
python _tests/check_html5.py
python _scripts/local_release_checks.py
```

The commands' observed results should be recorded separately from this prospective checklist and from public search outcomes.
