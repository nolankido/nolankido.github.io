# NolanPoker: Source to publication, with a human review boundary

**A documented AI-assisted content-production receipt**  
Nolan Kido | November 20, 2026  
Related public study: https://nolankido.com/technology/ai-poker-video-evidence/

This is a record of **what was published**, **what was checked**, and **what was not approved**. It is not a reconstructed transcript of the current video, a solver result, a viewer-retention study, or evidence that AI reduced the time needed to make the episode. The release itself and the three proposed captions have different statuses.

## The two deliverables

| Deliverable | Status supported by current public evidence | Important limit |
| --- | --- | --- |
| [Portland Meadows Episode 1 written companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/) | Published November 2, 2026; subsequently revised with clearly attributed event evidence | Based in part on earlier first-person narration, not a full independent check of the current video cut |
| [AI-assisted poker caption and verification case](https://nolankido.com/technology/ai-poker-video-evidence/) | Published November 4, 2026; contains three **proposed** captions, a worked source-to-claim audit and explicit editorial limits | It does **not** establish that any proposed caption appeared in a public video |
| [Current Episode 1 YouTube upload linked by the companion](https://www.youtube.com/watch?v=qABaiIcvvpU) | Public link provided in the source-backed companion | The present audio, exact chapter timing, displayed graphics and final video overlays were **not** independently reviewed for this receipt |

**Publication distinction:** The *written case about making and checking captions* is a released article. The *proposed captions in the current audiovisual edit* have **not** been cleared or verified by this record. A published YouTube link is not a certificate of caption accuracy.

## 1. Preserve the original material before drafting

**Input:** the [first-person episode companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/), specifically the [6-4 offsuit hand](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-64o-record), [pocket-sevens hand](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-77-record), and [event and payment numbers](https://nolankido.com/poker/episodes/portland-meadows-ep1/#event-numbers).

The companion itself distinguishes narration from externally checked schedule details. It attributes the result and actual deal payment to the player's account where independently audited, event-specific results are unavailable. Organizer schedule records do not establish the finish or $2,900 personal payout. The source includes archival version 7 narration and does not claim its timecodes are verified for the newest video cut.

**Source decision:** Carry forward what the account reports, identify assumptions and unknowns, and do not manufacture individual card suits, unrecorded streets, a complete board, effective stacks or opponent ranges.

## 2. Assign AI a bounded writing task

**Deliverable:** three proposed captions for a poker-video scene, not a model-produced replacement for the hand record.

The published [editorial study's brief and proposed captions](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-draft) instruct AI to use only the public companion and recomputable arithmetic. The article supplies proposals for the 6-4 shove, the pocket-sevens reshove, and the first-prize versus deal-payment explanation. These are **new writing produced for the public article**, not verified overlays or recovered speech from the posted YouTube video.

An original public article snapshot exists in the [November 4 website release source](https://github.com/nolankido/nolankido.github.io/blob/da8de1e4022490c851a618778c564cedaf70f03c/_source/technology/ai-poker-video-evidence.html). Its presence documents a real published editorial exercise; it does not reveal all private prompting conversations or human approvals.

**Draft decision:** A candidate is a question for editing, not permission to publish it as a factual on-screen graphic.

## 3. Check the facts with a separately inspectable method

**Inputs for a narrow check:**
- [Proposed scene claims JSON](https://nolankido.com/downloads/portland-meadows-ep1-scene-claims.json)
- [Standard-library Python fact gate](https://nolankido.com/downloads/poker-vlog-fact-gate.py)
- [Step-by-step explanation of the check](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-check)

The reported numbers can be recomputed without any AI service:

| Question | Calculation or distinction | Scope |
| --- | --- | --- |
| 6-4 stack | 148,000 ÷ 15,000 = 9.8666… BB, displayed approximately as 9.87 BB | Assumes the first-person stack was measured at the relevant pre-posting point |
| Pocket sevens | 585,000 ÷ 30,000 = 19.5 BB | Conditional on the reported stack-timing convention |
| Button open | 75,000 ÷ 30,000 = 2.5 BB | Raise-to size, not the incremental raise amount |
| Event money | $5,100 advertised first versus $2,900 reportedly received after a four-way deal | The reported $2,900 is gross, not net profit, and lacks an independent payout confirmation |

The article records that its structured scene checker returned **zero targeted flags for three proposed scenes**, and its synthetic negative controls triggered **seven seeded conflicts** before correction. Those are bounded, archived checking observations, **not a fresh current-video scan or a guarantee that other defects do not exist**. The checker does not parse prose captions, MP4 frames, current audio, rights, or solver output.

**Check decision:** The public structured proposals can be discussed with these qualifications. Do not treat a passing structured-file check as an approval of video graphics.

## 4. Separate editorial verification from human authorization

The public [human-review section](https://nolankido.com/technology/ai-poker-video-evidence/#poker-ai-approval) holds unsupported statements about a solver-approved shove, an exact full board, and winning the advertised $5,100. Each requires either evidence or narrower wording.

The JSON record explicitly states:

- `current_public_cut_timestamps_checked: false`
- `current_public_cut_graphics_checked: false`
- `confirmed_board_runouts: false`
- `human_release_approval: false`

These are **missing approval and verification states for the proposed audiovisual scenes**, not proof that the public video was never reviewed by anyone. Nothing in the open record authenticates the current-cut scene timing, narration or displayed hole-card suits.

**Human decision boundary:** A person must inspect the current export, verify statements against sound and video, check media rights and participant privacy, and accept or revise each consequential scene before claiming it is approved. The evidence here does **not** record that release decision.

## 5. Publish only the deliverable that met its evidentiary scope

The actual completed *written-content* pipeline is inspectable: an existing participant account was used as a source; an AI-assisted article proposed concise captions; limited facts and arithmetic were checked; the finished article disclosed what was unapproved; and the written article was published with source links and verification instructions.

**Published outputs:**
- [Episode 1 written companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/)
- [AI/poker editorial article](https://nolankido.com/technology/ai-poker-video-evidence/)
- [Original public structured candidate record](https://nolankido.com/downloads/portland-meadows-ep1-scene-claims.json)
- [Offline fact-gate script](https://nolankido.com/downloads/poker-vlog-fact-gate.py)
- [Truth-to-screen review worksheet](https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md)

**Not verified as published:** The three candidate captions as actual overlays in the current video, a newly recorded voiceover, any current-cut chapter offsets, a final human caption-approval log, or an independent $2,900 payment record.

The article was originally published November 4 and has a later documented source revision. The written companion was originally published November 2 and has subsequent updates. Neither publication date should be reset to the date of this receipt.

## Reuse this method on a different source

Before releasing a piece of AI-assisted content, keep one evidence record for each stage:

1. **Source:** exact original text, recording, observation and known gaps.
2. **Draft:** AI's permitted role, candidate text and prohibited inventions.
3. **Check:** independent source comparisons, calculations, negative controls and what was not tested.
4. **Human decision:** separate `ACCEPT`, `REVISE` and `HOLD` judgments for the current deliverable.
5. **Publication:** the actual shipped URL/file and its version. A draft released *as a labeled example* is not the same as that draft appearing in a final video.

For a scene-by-scene recording form and media rights checklist, use the existing [Truth-to-screen QA worksheet](https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md) rather than inventing a new video signoff record.

## What the case does not measure

There is no matched manual-versus-AI production time study, verified traffic uplift, Google indexing or ranking comparison, valid assistant citation rate, YouTube retention change attributed to AI, direct observation of all current video frames, or solver verdict. The source-backed article demonstrates an inspectable content-review *process* and clearly bounded published outputs, not a universal performance claim.

**Preparation notes:** Written as a public evidence synthesis on November 20, 2026 from the already published article, companion, scene-claims JSON, checker and historic revision snapshot. No new model inference, video-edit revision, tournament result certification or direct human approval of current-video graphics was performed for this receipt. Do not copy private video footage, unpublished hand histories or contact information into public acceptance logs.
