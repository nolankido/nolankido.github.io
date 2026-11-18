# SEO/GEO Sprint Turn 08: honest local/hosted comparison readiness

**Date:** November 18, 2026
**Base commit:** `fcd1f0e9ebd1b731d866217a7293a2dd21f171cf` (Turn 07)
**Status:** comparison protocol released; matched experimental result **not performed**

## Outcome

The Turn 08 question was whether Nolan's publicly documented local AI workflow could support a genuine, matched local-vs-hosted task comparison now. Source inspection found **no** verified laptop run of the synthetic fixture and **no** comparable hosted-service run. Publishing a performance comparison would misrepresent the existing evidence.

Instead, this turn supplies an independently repeatable public test and the evidence-capture framework needed to make a later comparison defensible:

1. [Public local-vs-hosted task protocol](../../downloads/local-hosted-ai-comparison-protocol.md), with a frozen synthetic prompt, five binary human-quality gates, fair timing boundaries, cold/warm distinction, privacy constraints and explicit no-claim gates.
2. [Blank trial worksheet](../../downloads/local-hosted-ai-comparison-blank.csv), which deliberately contains headers only. Unknown and unmeasured values are not zeros.
3. [Enhanced loopback checker](../../downloads/local-ai-loopback-check.py), with an opt-in `--show-output` flag for a reviewer to see the fixed synthetic fixture's actual reply. By default the checker still exposes only its hash and measurements, never output text.
4. A short, context-specific download link from the [public gaming-laptop article](https://nolankido.com/technology/local-ai-gaming-laptop/) to the protocol and worksheet, so readers do not mistake historical CPU-hosted timings for personal-laptop benchmarks.

## Evidence trace

| Evidence | What it proves | What it cannot prove |
| --- | --- | --- |
| [Prior test record](../../downloads/local-ai-test-record.json) | Three fictional review replies were measured on a GitHub-hosted Ubuntu CPU runner in October 2026, not on Nolan's laptop. | MSI laptop throughput, a matched hosted AI comparison, human-quality ratings, end-to-end time savings. |
| [Local loopback fixture](../../downloads/local-ai-loopback-check.py) | A fixed synthetic note, bounded Ollama loopback request, `temperature=0`, `num_predict=96`, dry-run shape and output fingerprint. | A real model ran on any specific machine unless an execution record says so; model output meets the rubric. |
| [Public case study](https://nolankido.com/technology/local-ai-gaming-laptop/) | Existing caveat that model performance and whole-task savings on the personal laptop remain unmeasured. | Any 2026 laptop or hosted model benchmark. |
| New Turn 08 worksheet | A machine-readable contract for recording comparable, real attempts after review. | Experimental data. There are **zero trial rows at publication**. |

## Methods and guardrails

- Both test arms use the exact same public synthetic note. The protocol defines five review gates: three-label format, task identification, checking each action against source notes, obtaining approval before sending, and no invented facts.
- Model IDs, settings, wall-clock boundaries, errors and cold/warm state must be recorded for every attempt. The runner's historical customer-review tasks are ineligible as the local arm.
- Hosted tests require separate legitimate access and a deliberate user action; this turn does not submit prompts or retrieve tokens from an account.
- The opt-in output flag is for a human to assess a **real** reply; it does not automatically mark quality approved. Default behavior and loopback-only endpoint restrictions remain unchanged.
- No private documents, customer data, credentials or user files were introduced into the public synthetic fixture.
- No GitHub Actions, automation, paid API, external hosted inference or CI workflow was created.

## Validation, limits and open checks

- **Completed by repository inspection:** exact source/production paragraph match for the download insertion; existing script option signatures, bounds and documented output schema; empty CSV contract and no filled trial records.
- **Available in connector-side JavaScript:** static text and worksheet consistency checks; exact one-point insertion checks; character checks for prohibited em dashes.
- **Not performed:** local Python execution, real Ollama request, test suite, HTML build, 320px browser preview, hosted AI test or laptop benchmark. The task's execution environment was unavailable on November 18. These require a future available execution environment and, for model inference, the actual target model setup.
- **Not claimed:** measured ranking, indexing, click-through rate, traffic, AI citation, model quality, local privacy or task-time savings.

## Publication and next turn

The public web page now offers the blank evidence route for readers. The former case-study statement that timing was unmeasured remains true. **Turn 08 is complete as a preparation-and-honesty fallback**, not as a completed comparison.

**Turn 09 proposal:** audit click-path and link equity to the new local-AI protocol and existing AI workflow cases, then carry out a read-only site crawl and prioritization of broken/weak contextual links. Do not treat this as a task to force a benchmark run without both environments and a documented human quality review.
