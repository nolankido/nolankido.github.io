# Before approving an AI customer review reply

An original, free owner-approval checklist accompanying [Nolan Kido's Review Reply Writer case](https://nolankido.com/technology/local-ai-review-replies/#reply-owner-gate). Keep a completed copy privately. This file does not run a model, collect customer data, post to a review platform, or replace your business's policies.

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
