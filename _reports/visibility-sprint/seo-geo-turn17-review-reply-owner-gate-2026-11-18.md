# SEO/GEO/AEO Sprint Turn 17: practical AI review reply approval gate

- **Date:** November 18, 2026 (Hawaii)
- **Property:** https://nolankido.com/
- **Sprint position:** Turn 17 of 25
- **Base checkpoint:** `2fb8727da457c5236e9842835a04fe7aaa78c61f` (Turn 16, merged PR #388)
- **Canonical retained:** https://nolankido.com/technology/local-ai-review-replies/
- **Scope:** A direct response to the question of safe AI review replies, source-linked approval steps, an original owner checklist, and existing Technology/Resources routes. No duplicate canonical, new paid service, automation or GitHub Actions.

## Reader problem and editorial change

The existing Review Reply Writer case already described a fictional duplicate-billing customer review, archived Gemma outputs, saved-text approval and an independent offline checker with published blind spots. Its introduction described the app more than it directly answered the likely reader question: **Can a small business safely use AI to answer customer reviews?**

The new opening answers **only with a human approval step**. The new `#reply-owner-gate` section teaches four distinct checks:

1. **Customer source:** Keep the exact positive and negative details of the review, without treating an allegation as verified reality.
2. **Owner policy:** A customer request or model suggestion cannot authorize a refund, credit, guarantee or operational commitment.
3. **Saved draft review:** An automatic status does not evaluate every factual claim. Check each promise, omission and quotation in context.
4. **Human approval and manual posting:** Review the exact saved revision; edits require another check and approval. The application does not automatically post to a review platform.

This answer is backed by the existing public source-linked example and linked [owner-first workflow record](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/docs/OWNER_FIRST_WORKFLOW.md), which I independently retrieved at the pinned commit. That record describes Draft, Read & Edit, Approve and Copy, with serious reviews routed to manual handling. The [review-evidence record](https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/docs/REVIEW_EVIDENCE_PASS.md) confirms the fictional duplicate-charge example's three source details, no authorized refund, and stale-edit invalidation. These are implementation and fixture observations, not observed customer results.

The new [downloadable owner approval checklist](../../downloads/review-reply-owner-approval-checklist.md) includes the fictional double-charge example, a historical cold-coffee source comparison, a blank review/policy/approval record, and explicit limits. It makes no model call, stores no private input, and is registered as a public read-only GET target.

## Distinguish actual model output from synthetic probes

An archived actual Gemma draft for a fictional cold-coffee review retained the reported 25-minute wait but included an operational-improvement claim not established by the review. An independent offline screen raised no targeted flag, so an owner would need to verify or remove that claim.

The separately authored local probe script, `downloads/reply-audit-boundary-probes.py`, uses **constructed sentences** appended to that historical fictional response. Its verified self-test produced one expected match and three mismatches across four synthetic probes: reimbursement and gift-card promises escaped the narrow phrase screen, while a quoted warning about a refund was incorrectly flagged. These are known limitations of a selected lexical checker, not additional generated model outputs, a random sample, a current model benchmark, or a production safety rate. The new page and checklist make those boundaries visible.

## Local verification observed

| Check | Recorded result |
| --- | --- |
| `python _scripts/build.py` | 253 generated outputs, 8 changed outputs |
| `python _scripts/build.py --check` | 253 checked, zero drift |
| `python _scripts/check_search.py` | Pass, 225 sitemap URLs, zero metadata errors |
| `python _tests/check_html5.py` | Pass, 230 HTML pages, zero parser failures |
| `python _scripts/check_internal_links.py` | Pass, 232 HTML pages and 16,263 internal links, zero issues |
| `python downloads/reply-audit-boundary-probes.py --self-test` | Pass, four probes, three expected mismatches retained, zero new model calls |
| `python -m unittest discover -s _tests -p 'test_turn17_review_reply_owner_gate.py' -v` | Five passed, including canonical/dates, downloaded artifact registration, source limits and overclaim negative controls |

The full historical unit suite and browser tests were not claimed to have run. These release checks do not measure search ranking gains, assistant citations, real-world reply quality, owner adoption, user satisfaction or time saved. Live byte parity for this new revision is a separate post-merge publication check.

## Suggested Turn 18

Strengthen the measurable decision framework connecting AI workflow pilots to Review Reply Writer and related practical AI cases. A useful next question is when the total cost of reviewing and repairing an AI draft outweighs the drafting time saved, without claiming results from a real business that has not been tested.
