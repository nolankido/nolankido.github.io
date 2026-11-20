# Six-case paired review-reply productivity pilot

**Status: protocol and blank observation sheet only. This pilot has NOT been run.** Published November 19, 2026 as a practical supplement to https://nolankido.com/ai-in-real-life/#real-life-business-pilot.

This exercise uses fictional reviews and a fictional owner approval policy. It makes no claim about actual customer interactions, live client value, a controlled productivity study, or measured time saved.

## A real machine result already exists, but it is not a productivity result

The historical October 13, 2026 Hawaii-time Review Reply Writer smoke run used `gemma3:4b` through Ollama on a GitHub-hosted Ubuntu CPU runner with two logical CPUs. The archived `case_elapsed_ms` values are:

| Historical case | Recorded application elapsed time | Human work observed |
| --- | ---: | --- |
| cafe-praise | 19.536 seconds | None |
| cafe-complaint | 18.157 seconds | None |
| stay-mixed | 19.325 seconds | None |

The mean of those three *selected* cases is **19.006 seconds**. These were developer-written fictional inputs. Each was one model attempt that passed the then-current automated checks. No owner reviewed the results; no manual drafting baseline, review minutes, correction time, setup/upkeep, or business outcomes were recorded. This run is not a benchmark of Nolan's Windows laptop or of current code.

Pinned raw data: https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-quality-smoke-2026-10-13.json

Source-grounded summary: https://nolankido.com/technology/local-ai-test-record/

**Do not copy those historical timings into the new observation sheet.** The six-case trial below requires fresh, matched observations.

## Task and fictional policy

For each case, draft a professional, specific public review reply of 50 to 100 words. Use only the review and this **fictional** owner policy: you may thank the customer, acknowledge reported positives and negatives, apologize for their experience where appropriate, and invite private contact through the ordinary business channel. No refund, credit, gift, investigation, operational change, promised time, or other specific business commitment has been authorized. Do not treat an allegation as a verified account fact. Do not request personal or payment details publicly. Human approval of the exact saved text is required before a real post.

The same task, policy and quality threshold apply to both a human-only draft and an AI-assisted draft. A real business must replace this teaching policy with its own approved rules in an appropriately authorized, private evaluation.

## Six frozen fictional review inputs

These cases are for *new* observations. RP01 to RP03 reuse topics from archived tests, so they are not an independent holdout set; RP04 to RP06 are newly constructed examples with no claimed model run.

| ID | Business | Rating | Review text | Suggested first method |
| --- | --- | --- | --- | --- |
| RP01 | Demo Cafe | 5 | The oat milk latte was perfect and the service was quick. | Manual |
| RP02 | Demo Cafe | 2 | Cold coffee and a 25 minute wait. The barista ignored my question. Disappointing. | AI |
| RP03 | Demo Stay | 3 | Beautiful room and ocean view, but check-in took forever and the shower was weak. | Manual |
| RP04 | Demo Cafe | 1 | My receipt shows two charges for one iced tea. I asked at the counter but nobody could explain it. | AI |
| RP05 | Demo Cafe | 2 | I asked whether the soup contained dairy. The server was not sure and the ingredient list was unclear. | Manual |
| RP06 | Demo Stay | 2 | My room was not ready at check-in. I want to know when I will receive a refund. | AI |

The suggested order alternates, but is not randomized. If the same person completes both methods, keep the first draft hidden while writing the second where feasible, and document any learning or carryover. Independent drafters and a reviewer blinded to method would reduce contamination, though this small trial still cannot establish a general effect.

## Acceptance criteria, fixed before testing

For **both** drafts in each pair, a human reviewer checks:

1. Material praise and complaints are represented accurately, including specific times, items, and circumstances.
2. Reported billing, ingredients and service conditions are not silently promoted to verified facts.
3. No unsupported business promise, compensation, action, or time commitment appears.
4. No private or payment information is requested in the public reply.
5. Tone and length meet the agreed standard, and the exact final wording is approved.

Write down why any draft is rejected or corrected. In the log mark `accepted` only if **both** methods reach the same quality standard. Mark `rejected` if either remains unacceptable after logged attempts, and `unreviewed` until a person completes that judgment. Never label an automatic pass as approval.

## Record complete time, not just inference time

Download the [pre-labeled blank CSV](https://nolankido.com/downloads/review-reply-paired-pilot-blank.csv). Every time cell is empty on purpose. Missing is **not** zero.

- `manual_minutes`: human work to produce and check the usual-method final draft at the same acceptance standard, including failed attempts.
- `ai_preparation_minutes`: human preparation, prompting and any generation waiting that blocks productive work. If the model runs unattended, record latency in separate private notes, not as active labor. Never count the same seconds twice.
- `ai_review_minutes`: actual human reading, source checks, approval checks, and evaluation.
- `ai_repair_minutes`: correction, retries, additional prompt work and repeat review, including failed attempts.
- `quality_status`: a human-entered status for whether the matched pair reaches the defined standard.

Use a stopwatch. Convert seconds to decimal minutes with at most two digits after the decimal point and document rounding. Record the model digest, system, settings, exact prompt, date, operator, independent reviewer, order effects, setup minutes, upkeep minutes, and wall-clock completion separately in private notes. Keep rejected attempts and their time. Never publish private customer records, private policy, personal information or credentials.

## Audit completed records offline

Use the existing [AI workflow pilot auditor](https://nolankido.com/downloads/ai-workflow-pilot-audit.py), which expects exactly the six CSV headers already provided. Download the script beside the completed CSV and inspect it first.

Test its built-in synthetic controls:

```powershell
py -3 ai-workflow-pilot-audit.py --self-test
```

When, and only when, all six rows have freshly measured numbers and human labels, run:

```powershell
py -3 ai-workflow-pilot-audit.py --input review-reply-paired-pilot-blank.csv --setup-minutes 0 --upkeep-minutes 0
```

The two command-line zeros are placeholders. Replace each with a measured value, using zero only if truly observed. The existing auditor refuses missing numeric cells, duplicate IDs and invalid statuses. It totals the *recorded* amounts and checks reviewer labels; it cannot establish that the numbers, assessments or study design are sound.

## Publication boundary

Only publish a measured productivity result after finishing paired trials with comparable acceptable quality, reviewer decisions, setup/upkeep, limitations and disclosed order effects. Six synthetic cases are a narrow exploratory sample, not a representative business benchmark. If an AI version remains unsafe, the appropriate result is *not adopted*, regardless of speed. Keep the historical machine test separate from any fresh paired-run data.

**Current status: no paired observations were collected for RP01 to RP06.** The historical CPU execution times are observed model-stage data only. No measured net savings, current model quality or real business outcome is established.
