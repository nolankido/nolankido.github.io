# NolanPoker AI-assisted content production: public evidence ledger

**Case date:** November 20, 2026  
**Status:** A public video and written companion exist; a separate AI-assisted editorial exercise produced candidate scene claims. Current-cut overlay accuracy and end-to-end AI productivity remain unverified.  
**Author:** Nolan Kido  
**Portfolio:** https://nolankido.com/ai-in-real-life/#real-life-creator

This public case separates what was actually published from archived first-person recollections, derived arithmetic, editorial proposals, software checks, and unresolved audiovisual release approval. It is not a private editing log, a certification of the present video, or a claim that AI produced every part of the released episode.

## A. Published deliverables

| Item | Public artifact | What it establishes |
| --- | --- | --- |
| Portland Meadows Episode 1 | https://www.youtube.com/watch?v=qABaiIcvvpU | A publicly accessible NolanPoker video exists |
| Written companion | https://nolankido.com/poker/episodes/portland-meadows-ep1/ | A first-person written account with a November 2, 2026 publication date, revised November 16 |
| Source-bounded editorial exercise | https://nolankido.com/technology/ai-poker-video-evidence/ | Three candidate captions and narrowly stated evidence rules, not current-video transcription |
| Structured scene claims | https://nolankido.com/downloads/portland-meadows-ep1-scene-claims.json | A public JSON proposal whose unresolved facts and review status are explicit |
| Offline fact checker | https://nolankido.com/downloads/poker-vlog-fact-gate.py | An independent deterministic check of selected fields and constructed negative controls |
| Truth-to-screen worksheet | https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md | The human acceptance checklist, not proof that it was completed |

The existing video is a newer public cut than the archived version 7 narration used for the companion. This ledger neither republishes the private edit logs nor assigns the old chapter offsets to the current cut.

## B. Source to screen: five checkpoints

1. **Source:** Earlier first-person narration and the public companion establish the player's reported hand sequence and payout. They are not independent observation of all cards and frames.
2. **Proposal:** The AI-assisted editorial article creates three proposed labels for the 6-4 offsuit hand, four-handed pocket sevens, and deal payout. These are proposed claims, not screenshots or confirmed subtitles from YouTube.
3. **Arithmetic:** The sourced numbers allow the following independent checks: 148000 / 15000 = 9.866... BB (displayed as about 9.87), 585000 / 30000 = 19.5 BB, 75000 / 30000 = 2.5 BB. Advertised first prize $5100 differs from the player's reported post-deal gross payment $2900.
4. **Automated rule boundary:** The published article reports zero targeted flags on three structured proposed scenes and seven deliberately seeded conflicts across four constructed negative-control examples. Those negative controls are hypothetical mistakes, not actual editing errors or real model outputs. These historical checks were not rerun for this November 20 portfolio update.
5. **Human release gate:** Current-cut timecodes, exact voiceover, actual on-screen graphics and cards, assets and permissions, and a human signoff remain unverified in the public structured scene record. The published upload is not retroactively declared approved against this separate checklist.

Run the existing targeted checker on public, local copies of the Python script and JSON only:

```powershell
py -3 poker-vlog-fact-gate.py --self-test
py -3 poker-vlog-fact-gate.py --check portland-meadows-ep1-scene-claims.json
```

A passing command would certify only that the chosen structured rules found no targeted conflicts. It does not listen to the video, inspect frames, prove strategic correctness or authorize publication.

### Explicit unresolved flags in the public scene JSON

- `current_public_cut_timestamps_checked: false`
- `current_public_cut_graphics_checked: false`
- `confirmed_board_runouts: false`
- `event_calendar_date_independently_verified: false`
- `human_release_approval: false`

Do not silently change any of these to true without a new reviewed source and verification record.

## C. Second release: keeping public metadata aligned

On November 18, 2026, a separate [Reserve Day 1 companion](https://nolankido.com/poker/episodes/reserve-day-1/) used the reviewed public YouTube listing for https://www.youtube.com/watch?v=edNSD5BjIV8. The site release connected the video listing, archived-source written companion, and the [dated public source ledger](https://nolankido.com/downloads/reserve-day1-public-source-ledger.json).

The [merged source diff, PR #386](https://github.com/nolankido/nolankido.github.io/pull/386) and [website publication case](https://nolankido.com/technology/ai-website-visibility/#site-visibility-recent-release) report that locally checked files were served after deployment. That is publication evidence at a dated checkpoint, not proof of transcript accuracy, hand graphics, rankings, traffic or subscriptions. The source title and thumbnail can change later; recheck their current state before asserting they remain unchanged.

## D. Human and AI responsibilities

**Useful AI task:** summarize publicly supported facts into candidate graphics, highlight missing evidence, and prepare checkable draft wording.

**Independent check:** recompute stated chip and payout figures; reject unsupported board runouts, suits, current-cut timestamps, solver verdicts and misleading payout or net-profit statements.

**Person responsible:** the creator/editor reviews the latest audiovisual export, visual layout and rights and approves the actual released version. The JSON proposal does not contain evidence of that approval.

**Outcome measurement still absent:** saved production labor, comparative editing quality, current-cut QA results, YouTube retention or new subscribers attributable to this workflow. Missing measurements are unknown, not zero.

## E. Reusable decision receipt

For another episode, capture these five fields **privately**, once per consequential scene: original source and version; current-cut audio/video timecode; proposed caption with evidence label; independent checks and unresolved unknowns; human HOLD, REVISE or ACCEPT decision with date. Use the existing [truth-to-screen worksheet](https://nolankido.com/downloads/poker-vlog-truth-to-screen-qa.md) rather than inventing a second approval policy.

The completed published video, archived source companion and unapproved candidate-caption exercise are different artifacts. The strength of this case is the distinction, not a claim that every part of the video was produced or verified by AI.

## F. November 20 read-only transcript checkpoint (new evidence, incomplete video QA)

During a read-only visit to the current public [YouTube upload](https://www.youtube.com/watch?v=qABaiIcvvpU), the viewer-facing transcript panel displayed entries at **4:20** (6-4 offsuit shove and A-K suited call), **6:27** (pocket sevens decision), **7:12** (sevens held), **8:08** (reported deal share $2,900) and **8:52** (same payout repeated). This is a *current public transcript observation*, unlike the older version 7 narration. The phrases align narrowly with the source-bounded companion's narrated topics, not with independently verified footage or profit records.

The browser could not play the video because YouTube required sign-in to confirm the viewer was not a bot. No current frames, audio, cards, graphic overlays, complete runtime or final-media release gate were actually inspected. The transcript appears auto-generated and no authenticated manual caption track was confirmed. A search did not find the advertised $5,100 first prize in the inspected transcript and description; no conclusion about the full video's visual content follows.

Download the separate [five-entry, machine-readable transcript checkpoint](https://nolankido.com/downloads/portland-meadows-public-transcript-audit-2026-11-20.json). The earlier structured scene-proposal flags remain false for current-cut timing, graphics and human approval. A human still needs to review the actual audio and image frames, including the distinction between $5,100 advertised and $2,900 reported gross payout, before calling the released video fully verified.

## G. Offline current-cut audiovisual QA workstation (no published current-cut verdict)

The new [NolanPoker local video QA workstation](https://nolankido.com/downloads/nolanpoker-local-video-qa.html) is a self-contained HTML file. It accepts the video from the reviewer's device into a local browser video element without uploading the media, sending source text to an AI model, or retaining reviewer notes in website storage.

It provides seek anchors at transcript observations 4:20, 6:27, 7:12, 8:08 and 8:52. These are **only suggested starting times** until the exact current cut has been identified and checked. For each segment, a person reviews audio and frames, records the actual local playback position and a specific observation, and selects HOLD, REVISE or PASS. The tool can export a current-frame PNG and private JSON/Markdown reports. Its final gate requires full-cut listening and viewing, substantive graphics checks, privacy and rights approval, payout wording, an actual clickable YouTube Studio end-screen check, reviewer identity, and a justified claim that the loaded file matches the public release.

**Implementation QA only:** A locally generated synthetic video was used to exercise browser metadata loading, seeks, an incomplete-review refusal, exported JSON/Markdown, frame PNG capture, reset, and 320-pixel reflow in a headless Chromium test. That synthetic media was not the NolanPoker episode and was not published in this repository.

**Current public video status:** Actual audio, card graphics, suits, board runouts, runtime, end screens and human signoff of the released video remain unverified here. The November 20 public transcript audit and the prior structured scene-claim file retain their explicit false and unknown flags. A filled human report is still an attestation rather than independent proof of video equivalence or strategy correctness.

## H. Local media fingerprint and continuous evidence gate (November 20)

The [standalone local video QA workstation](https://nolankido.com/downloads/nolanpoker-local-video-qa.html) now hashes the selected local video with chunked SHA-256, entirely inside the browser. The report includes the digest, file size and observed media metadata so a later reviewer can identify which local file was examined. The reviewer can compare that digest with another separately obtained reference file, for example by running `Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\\path\\to\\video.mp4'` in PowerShell. Matching hashes between two files establish their byte equivalence; **no trustworthy public-release hash was obtained here**, so a local checksum does **not** certify equivalence to the YouTube upload.

The review gate was strengthened after a specific defect was identified. The earlier tool validated a note when PASS was first selected, but did not recheck note length if it was subsequently erased. The new version rechecks all five notes, checked audio and frames, captured positions, video duration covering the last transcript anchor, and the computed checksum at every status update. Removing required evidence revokes the complete status. A human can still enter inaccurate observations, so every completed report remains explicitly a **reviewer-reported checklist**, not an independent audiovisual certification.

**QA scope:** A synthetic local MP4 was used for real browser loading, seeking, frame capture and export tests. Its SHA-256 was compared with an independently calculated checksum; separate known-vector tests used Node's cryptographic implementation. No actual released NolanPoker MP4 was inspected, and the older scene JSON and November 20 transcript audit retain all their audiovisual and release-approval unknowns.

## I. Checksum-bound review resumption (November 20)

The self-contained [NolanPoker audiovisual review workstation](https://nolankido.com/downloads/nolanpoker-local-video-qa.html) now supports reopening a saved QA report from a prior session. The user selects the **same locally stored video**, computes its SHA-256 digest, and then selects an exported v2 or v3 JSON QA report from the device. The form rejects a report with a different local digest, file size, decoded duration, public video ID, transcript source, invalid scene definition, invalid data types or excessive note lengths. Report import is local; no upload, server storage, network call or AI inference is performed.

**What carries forward:** Working scene notes, previous playback-position hints, reviewer identifier, identity-method text and global notes. An invalid import leaves existing work unchanged. **What is deliberately cleared:** Every scene decision including prior PASS, every audio and video checkbox, current captured scene positions, the same-cut attestation, all whole-video release gates and the prior review date. Notes cannot silently become current approval. An exported v3 report labels its prior schema and states that prior approvals were cleared. Even an imported matching checksum does **not** independently establish equivalence to the YouTube video or that any human review was accurate.

The change was tested with a **synthetic local MP4** in Chromium: exported incomplete notes, reloaded the same file, rehashed, imported the saved JSON, confirmed all prior approvals reset, rejected mismatched-checksum and unsupported-schema files without erasing current notes, and checked 320-pixel reflow. A separate Node regression checks malformed scene IDs, oversized notes, incorrect file hashes, wrong video identifiers and v2/v3 compatibility. The existing SHA-256 test still passes against an independent cryptographic implementation.

**Current published-video verification remains open.** No matching current released Portland Meadows MP4 was obtained for this improvement. The earlier public transcript and scene-claim records still mark audiovisual review and human release approval as unverified. Do not publish any synthetic QA review as an actual release finding.

## J. Source-linked public YouTube viewing path (November 20)

The actual [Portland Meadows public video](https://www.youtube.com/watch?v=qABaiIcvvpU) is available from the NolanPoker channel. It does **not** require possession of a local MP4 to perform a manual viewer check. The [public YouTube review worksheet](https://nolankido.com/downloads/nolanpoker-public-youtube-review.html) provides six direct timestamped watch links, explicit audio and frame checkboxes, evidence notes, current player-position fields, and local JSON/Markdown exports.

Five positions (4:20, 6:27, 7:12, 8:08, 8:52) come from the November 20 **current public transcript**. The 0:31 suggested prize-board position comes from **archived v12 edit metadata** and must be checked rather than presumed present in the current video. A link opens the known public video ID; it is not itself an audiovisual observation. The worksheet does not embed, record, transcribe, crawl, automatically analyze or fetch video data.

A Pass requires a reviewer to report listening, actual visual inspection, a manually observed player time, and a specific note. A six-scene checklist additionally requires explicit whole-video, payout, rights, end-screen and named-reviewer gates. The resulting report always identifies itself as **reviewer-reported, not independently verified by the tool**. Note import is constrained to this specific public video, restores notes and time hints only, and resets past Pass decisions and checkboxes. The page uses no storage or outgoing API calls.

**Current QA conclusion:** The previously checked public transcript remains narrow evidence. A separate attempted automated viewing session did not yield a complete trustworthy audiovisual review. No specific public frames, card suits, runouts, published payouts, audio quality or clickable end screens are now certified. The original unverified flags remain unchanged. The MP4-based SHA-256 tool continues to exist as an optional higher-provenance local alternative.

## K. Independent results-source coverage for Portland Meadows (November 20)

Following the organizer-schedule documentation, a second targeted
public-source check examined the venue's [Tournament Results link](https://portlandmeadows.com/schedule),
[Card Player's August 2026 festival listing](https://www.cardplayer.com/poker-tournaments/1732464-2026-wild-west-poker-tour),
and the [indexed 2026 Portland Meadows tournament archive](https://pokerdb.thehendonmob.com/festival.php?a=r&n=67809).

The venue points readers to a third-party result database but did not
display a High Noon winner or payout on its schedule page. The inspected
Card Player listing named the August 20 $200 Deep Stack, but did not
supply a finish or payout in its event row. The indexed 2026 Portland
Meadows archive displayed six events through April, not this August
event. Direct database access was restricted and the result could
exist elsewhere. This is a bounded *failure to confirm the event-specific
result*, not independent disproof of the player's account.

The narrator's claimed first-place trophy, 88 entries, $17,600 prize
pool, $5,100 advertised top prize and $2,900 gross post-deal share
remain self-reported. A venue-issued final-results record or separate
deal confirmation can strengthen those distinct claims. General
tournament databases warn that reported winnings may not reflect chops
and cannot be treated as net profit.

[Read the dated results-source audit](https://nolankido.com/downloads/portland-meadows-result-source-audit-2026-11-20.json)
and [the source-bounded public companion](https://nolankido.com/poker/episodes/portland-meadows-ep1/#episode-result-source-status).
The earlier audiovisual and human-approval flags remain false.
