# When should AI-assisted work proceed, be revised, or stop?

**Four source-backed examples and one private decision worksheet**  
Nolan Kido | November 20, 2026  
Canonical explanation: https://nolankido.com/technology/check-ai-answers/#review-stop-rules

This field guide connects four different publicly documented uses of AI to the specific checks and authority each requires. It is a **decision method**, not a claim of overall model reliability, a universal safety certification, or an automated authorization system. The historical website and model checks, fictional review probes, and unverified video captions are different evidence types. Do not pool their counts or present them as one error rate.

## The four decisions

- **PROCEED IN SCOPE:** Independent evidence supports the exact claims needed for the proposed use, relevant tests actually ran on the intended version, any necessary person or external authority has accepted it, and the full review cost is acceptable. This does not certify the entire system.
- **REVISE AND RECHECK:** The issue is concrete and fixable, such as a missing duration, invalid HTML or an unsupported sentence. Correct the source or draft, then check the new version. Earlier approval is no longer valid after changing the output.
- **HOLD:** An essential fact, permission, test, payment status, or current-version check remains unknown. Missing information is not proof of failure, but the consequential action must not proceed.
- **STOP USING AI FOR THIS TASK:** The necessary facts cannot be safely obtained or checked, permission cannot be established, the workflow repeatedly fails its acceptance conditions, or the full burden of preparation and review makes the manual alternative preferable. This is a reasoned task decision, not a general declaration that AI never works.

## Four cases, four non-interchangeable gates

| Public case and evidence | What was actually observed | Distinguishing check | Decision boundary |
| --- | --- | --- | --- |
| [AI-assisted website repair](https://nolankido.com/technology/checking-ai-website-changes/#case-source-diff) | The historical October 11 change passed a build, search check and 347 unit/content tests; a separate HTML5 parser reported `end-tag-too-early` on an extra `div` closing tag. The source before/after is pinned. | Run an HTML5 parser capable of rejecting a deliberately malformed fixture, rebuild, and check the actual deployed release. [Reduced offline reproduction](https://nolankido.com/downloads/website-check-reproduction.py) tests the same failure class, not the full old site. | **REVISE AND RECHECK** while markup is malformed. **HOLD** release until the relevant gates pass. The archived repaired release passed its reported checks. This does not prove accessibility, security, traffic or rankings. |
| [Review Reply Writer owner gate](https://nolankido.com/technology/local-ai-review-replies/#reply-operator-decision) | An archived actual Gemma reply to a **fictional** review lost a precise 25-minute wait in an accepted retry. Separate **constructed** lexical probes detected an explicit refund, missed reimbursement and gift-card offers, and incorrectly flagged a quoted warning. | Compare the draft with the source review and owner's real policy; use [the four-probe demonstration](https://nolankido.com/downloads/reply-audit-boundary-probes.py) to prove the checker can disagree with editorial judgment. [Owner approval checklist](https://nolankido.com/downloads/review-reply-owner-approval-checklist.md) records a human decision. | **REVISE** omitted detail; **HOLD** unauthorized promises even with a green lexical screen. **REVIEW IN CONTEXT** a quotation. **PROCEED** only when a person approves the exact final saved text for manual posting. No real customer pilot or approved business result is established. |
| [RightsReceipt licensing prototype](https://nolankido.com/technology/rightsreceipt-ai-licensing/#rightsreceipt-software-proof) | Source-backed localhost handlers rehearse three fictional journeys with **injected payment-like responses**. Separately, a real locally executed classifier on synthetic requests incorrectly suggests the US and Canada where a request says Germany only. These are historical reported tests, not rerun for this worksheet. | Inspect the [pinned model proof and handler smoke](https://nolankido.com/downloads/rightsreceipt-local-software-acceptance.md); require actual creator and buyer authorization, a verified owner, and authenticated PayPal provider evidence before claiming payment or permission. | **HOLD** the territory and real licensing/payment action. The synthetic code test may be discussed or rerun, but its `simulated_only` result is not an authorized license, legal judgment, or proof of a paid invoice. |
| [NolanPoker caption proposals](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-approval) | The public article proposes three captions and reports zero targeted structured-file flags; seven deliberately seeded conflicts were caught by its separate test. Its [structured evidence](https://nolankido.com/downloads/portland-meadows-ep1-scene-claims.json) still marks current video cut timing, graphics and human caption approval **false**. | Compare every proposed word, card, suit, amount and timing with the *current* export and narration, check venue/media rights, and use the [scene acceptance worksheet](https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md). | **HOLD** a caption as a claim about the released video until those current-version checks are done. The written study itself is published **as a proposal**. Omit a detail if the footage cannot verify it. The reported $2,900 is gross after a four-way deal, not the advertised $5,100 first prize or net profit. |

The "proceed" labels here refer only to the corresponding **scope and evidence version**, never an unqualified guarantee. A historical source can prove what a checker did in October without verifying today's output. A real local inference result can coexist with simulated payments and unresolved legal authority. An accurate calculation can coexist with a false assumption.

## A six-gate release method

**Gate 1: Permission and data.** Is it authorized to use this input, run the tool, and publish the proposed output? Keep private customer reviews, policies, keys, media and participant information out of public evidence reports. If permission is unknown or unsafe, **HOLD**.

**Gate 2: Exact source truth.** List the decisive claims, their primary evidence, the original input, relevant dates and the unknowns. Separate a participant's recollection, a constructed test, actual model text and an independent third-party record. If a central fact is missing, **HOLD** that claim. If a detail is wrong but fixable, **REVISE**.

**Gate 3: An independent negative control.** Choose a checker that could fail if the asserted fact or behavior were wrong. For a website, parse malformed markup. For a reply, try an unauthorized commitment phrase the screen does not understand. For a licensing proposal, test contradictory territory. For a caption, compare against actual audio and frames. No single green check covers all these risks.

**Gate 4: Rightful human or external authority.** An AI model cannot authorize a refund, grant a license, verify a payment, decide what a third party agreed to, or certify footage it has not examined. Identify the owner, buyer, payment provider or editor whose real decision is required. A proposal without that approval is **HOLD**, not acceptance.

**Gate 5: Full task cost.** Compare *the same quality threshold* with a manual alternative. Count setup, human briefing, model and waiting time without double-counting active labor, fact-checking, review, retries, fixes, rights and privacy checks, upkeep, and unresolved work. Use the [full-workflow calculator](https://nolankido.com/technology/ai-time-savings/) or [paired pilot method](https://nolankido.com/downloads/review-reply-paired-pilot-instructions.md). The paired six-case review-reply study is **not completed**, so no measured AI time saving follows from it. If checking costs more than the work is worth, or cannot reach the required quality, choose **STOP USING AI FOR THIS TASK**.

**Gate 6: Exact deliverable and release.** Check the *version you will actually send or publish*. A source-code test is not proof of live deployment; a structured caption JSON is not a video-frame review; an accepted draft is not permission to auto-post. Record the URL/version and scope. Changes to approved wording require rechecking.

## Worked stop-rule decisions

**Scenario A: A customer-review checker reports no problem, yet the draft promises a gift card.** This phrase is a deliberately constructed probe, not a newly generated customer reply. The owner policy supplied by the user does not authorize such compensation. Mark the promise **unsupported**, decide **HOLD**, remove or obtain proper authorization, then recheck the saved draft and obtain explicit owner approval before any manual post.

**Scenario B: An HTML page is readable and 347 prior tests passed, but HTML5 parsing finds a mismatched closing tag.** The narrower statement "the build was consistent" can remain supported, but the broader statement "the HTML is structurally valid" is contradicted. Decide **REVISE AND RECHECK**. Do not claim a complete release until the parser and relevant deployment checks succeed.

**Scenario C: A synthetic licensing request says Germany only and a model proposes a different territory.** That is a detected conflict, not evidence of permission. Decide **HOLD**. A creator must resolve scope and a buyer must accept the final version. A successful simulated invoice response cannot verify payment.

**Scenario D: The poker-video structured claims pass their limited checker but the current cut has not been reviewed.** A proposed caption may remain available in the published written case as a **labeled example**. Decide **HOLD** for showing it as verified current-video footage. Cut or mark any unsupported card/board detail. Do not announce viewer-retention gains or an optimal poker decision without additional evidence.

## Private decision receipt

Duplicate these fields for each consequential claim or deliverable. Keep filled records and any private source material outside a public code repository.

- **Task and intended real-world action:** 
- **Input version and permission to use it:** 
- **Exact claim or generated text:** 
- **Primary source and date checked:** 
- **Evidence type:** observed / archival / participant-reported / synthetic / unknown
- **Narrow independent check and negative control:** 
- **Actual result on this version:** 
- **Claim status:** supported / contradicted / unresolved
- **Owner or provider whose approval is necessary:** 
- **Explicit approval for this exact saved version:** yes / no / not obtained
- **Privacy, rights, media, safety or payment unknowns:** 
- **Manual method and accepted-quality comparator:** 
- **AI preparation / generation / review / repair / setup / upkeep:** 
- **Total-workflow advantage:** measured with a matched quality baseline / unknown / unfavorable
- **Decision:** PROCEED IN SCOPE / REVISE AND RECHECK / HOLD / STOP USING AI FOR THIS TASK
- **Reason and what would change the decision:** 
- **Final release URL or file, or why it remains unpublished:** 
- **Responsible human and date:** 

A blank field is **not zero** and no completed source check automatically supplies human approval. If review, authority, safety or costs cannot be established, the answer may be to do the task manually or not do it.

## Provenance and limits

This worksheet is a **November 20, 2026 synthesis** of four already public, case-specific source and demonstration records. The author reviewed those pages and the associated pinned source/evidence files; no new model inference, payment, current-video review, actual cafe use, paired time study, Google ranking check or user satisfaction survey was performed for this field guide.

- [Website repair source before and after](https://nolankido.com/technology/checking-ai-website-changes/#case-source-diff)
- [Review Reply Writer owner decision and synthetic probes](https://nolankido.com/technology/local-ai-review-replies/#reply-operator-decision)
- [RightsReceipt runnable code and authority boundary](https://nolankido.com/technology/rightsreceipt-ai-licensing/#rightsreceipt-software-proof)
- [AI-assisted NolanPoker caption study and unapproved current-cut status](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-approval)

The cases concern different tasks, evidence types and historical moments. They do not supply a combined "AI failure rate," a compliance guarantee, a licensed professional judgment or permission to publish consequential content without the responsible person's approval.
