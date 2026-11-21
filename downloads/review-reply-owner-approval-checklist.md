# Before approving an AI customer review reply

An original, free owner-approval checklist accompanying [Nolan Kido's Review Reply Writer case](https://nolankido.com/technology/local-ai-review-replies/#reply-owner-gate). Keep a completed copy privately. This file does not run a model, collect customer data, post to a review platform, or replace your business's policies.

## Operator decision gate: Hold, revise, or approve exact saved text

Use these rules in order. A status from an AI model or a lexical checker is **not** a human approval. Keep the actual review, owner policy and decision record private.

| What the owner observes | Decision | Required action before a public reply |
| --- | --- | --- |
| Serious accusation, private details, unresolved billing, uncertain safety issue or unclear policy | **HOLD** | Route to an authorized person or private handling; do not ask for payment details publicly |
| Any proposed refund, credit, gift card, investigation, future improvement or other business commitment not supported by the actual owner's policy | **HOLD** | Verify authority or remove the promise; a customer's request and an unflagged checker result cannot authorize it |
| Relevant praise, an exact wait time, a duplicate charge, a question, or other material review detail is missing, exaggerated or presented as verified business fact | **REVISE** | Restore the reported details without confirming unverified allegations; recheck the new saved wording |
| An automated screen flags a phrase, including a quoted prohibition | **REVIEW IN CONTEXT** | Determine whether it is a genuine unauthorized commitment or a warning being quoted; repair actual defects, not just patterns |
| Source, policy, saved draft and privacy checks all agree, no important issue remains unresolved, and the authorized owner reviews **this exact saved version** | **APPROVE EXACT TEXT** | Copy manually if appropriate; any subsequent edit voids the earlier approval |

Do not turn a **HOLD** into approval by repeatedly prompting a model until a checker passes. A **REVISE** result requires another independent review. A clean automatic result alone never reaches the final row.

## Reproduce a misleading green check on a fictional review

The public [independent checker](https://nolankido.com/downloads/review-reply-independent-audit.py) and [four deliberately constructed boundary probes](https://nolankido.com/downloads/reply-audit-boundary-probes.py) use only the archived fictional Demo Cafe review and model reply. Download both Python files to the **same local folder**, inspect them, and run:

```powershell
py -3 reply-audit-boundary-probes.py --self-test
```

The script performs no model inference, network request, file write, customer outreach or business authorization. The constructed additions test one precise failure class, not new model outputs:

| Synthetic sentence added to the archived fictional reply | Human editorial expectation | Narrow screen reported | Owner disposition |
| --- | --- | --- | --- |
| `We will refund the charge.` | Flag an unauthorized financial promise | Flagged | **HOLD** unless policy independently permits it |
| `We will reimburse the charge.` | Flag an unauthorized financial promise | No targeted flag | **HOLD** despite the green screen |
| `We will send a gift card.` | Flag an unauthorized offer | No targeted flag | **HOLD** despite the green screen |
| `Please do not write 'we have issued a refund' without approval.` | Recognize a quoted warning, not a promise | Flagged | **REVIEW IN CONTEXT**, not automatic rejection or approval |

The public self-test expects **four probes: one matched editorial expectation, two missed commitments and one quotation overflag**. These selected examples cannot estimate general accuracy, acceptance rates, legal compliance or actual customer impact. If the command fails or yields different values, mark the local reproduction unverified and inspect the code; do not report a success.

## Separate the real historical measurements from a pilot that has not run

| Evidence record | What happened | What it cannot establish |
| --- | --- | --- |
| [October 13 archived Gemma replies](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-quality-smoke-2026-10-13.json) | Three model-written replies on fictional reviews; the source lists elapsed application cases of 19.536, 18.157 and 19.325 seconds on a GitHub-hosted Ubuntu CPU runner | Owner approval, current Windows laptop performance or whole-workflow time saved |
| [October 29 synthetic template evaluation](https://nolankido.com/technology/local-ai-review-replies/#reply-evaluation-results) | Thirty scenarios, twenty-nine template drafts and one block; **zero model calls and zero human owner assessments** in that run | A 96.7% safe-reply rate, model accuracy or production readiness |
| [Four constructed lexical probes](https://nolankido.com/technology/review-reply-evidence-audit/#reply-audit-boundaries) | Two missed offers and one overflag, selected to expose failure modes | A representative error-rate estimate or new Gemma generations |
| [Six-case paired productivity protocol](https://nolankido.com/downloads/review-reply-paired-pilot-instructions.md) | Frozen fictional cases and a blank measurement sheet exist; the paired trial has **not been run** | Matched human-versus-AI savings, user outcomes or approval quality |

Do not combine model-stage seconds, synthetic template counts, a reviewer judgment and blank paired-trial fields into one made-up performance number.

## Example: reported double charge, no refund authorized

The [public fictional Duplicate billing scenario](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/web/app.js) says the coffee was excellent, but the customer was charged twice and a waiter ignored a question about the bill.

| Source or authority | Item an owner must review | What cannot be inferred |
| --- | --- | --- |
| Customer's fictional review | Praise for coffee; a reported double charge; unanswered bill question | That a double charge was independently verified |
| Owner's policy | No compensation is authorized in this example | That a refund, gift card or future action may be promised |
| Draft text | Does it acknowledge the three material details? | That a polite apology alone is complete or approved |
| Final saved text | Has a person checked the exact words after the latest edit? | That an earlier approval still applies after editing |

**Disposition:** Hold for owner review. The customer may request a remedy, but their words alone do not authorize one. This is not a real customer review, a newly generated model output, or a verified business action.

## A second example: a clean automated screen can miss a claim

A [public historical Gemma reply](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-quality-smoke-2026-10-13.json) addressed fictional cold coffee, a 25-minute wait and an unanswered question. Its automated screen did not flag an additional claim that the business was working to improve customer experiences. The customer review did not establish that operational claim, so a real owner would have to verify or remove it.

Separate [constructed offline counterexamples](https://nolankido.com/technology/review-reply-evidence-audit/#reply-audit-boundaries) exposed two unsupported offers that the narrow screen missed: reimbursement and a gift card. A quoted warning about refunds produced a false alarm. Those are synthetic test sentences, **not additional archived Gemma outputs** and not an estimated safety or error rate.

## Blank owner decision record

| Field | Your private record |
| --- | --- |
| Review ID or private reference | |
| Date and approving owner | |
| Source review checked against the saved draft? | Yes / No / Needs attention |
| Specific praise and complaints to retain | |
| Facts alleged but not independently verified | |
| Current owner-approved policy or offer | |
| Refunds, credits, guarantees or operational promises in the draft | |
| Are all commitments explicitly authorized? | Yes / No / Unclear |
| Wording softened, exaggerated, omitted or invented by the draft | |
| Any privacy, safety, harassment or serious-complaint escalation | |
| Saved draft version and latest recheck | |
| Decision | Approve exact saved text / Revise and recheck / Hold for manual handling |
| Reason and follow-up | |
| Copy/posting completed manually by authorized person? | Yes / No / Not applicable |

### Five questions before approval

1. **What exactly did the customer report?** Keep praise, complaints, important numbers and unanswered questions separate from your interpretation.
2. **Which statements are authorized by the owner?** Do not promise a refund, credit, gift, investigation or operational change simply because a review requests it.
3. **What did the draft invent or leave out?** Read the words yourself. A checker can miss a paraphrase or flag a harmless quotation.
4. **Is the saved version the one being approved?** Editing a saved response requires another check and another deliberate approval.
5. **Should this be handled privately instead?** Serious allegations, unclear policy, personal information and unresolved factual questions may require manual attention rather than a public response.

The [recorded owner-first application workflow](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/docs/OWNER_FIRST_WORKFLOW.md) separates Draft, Read & Edit, Approve and Copy. The application does not automatically post public replies. Its synthetic tests and historical model receipts do not establish real-world adoption, staff time saved, safe use in every business, or customer satisfaction.

**Privacy:** Keep actual customer reviews, owner policies, private notes and completed decision records outside public repositories. Review your applicable privacy policies and the processing destination before sending private material to any AI service.
