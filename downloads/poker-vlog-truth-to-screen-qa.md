# Truth-to-screen QA for an AI-assisted poker vlog

**Public worksheet | Nolan Kido | November 3, 2026**

This is a reusable editing and release checklist, not a transcript or certification of any published video. Its worked examples come from the public [Portland Meadows Episode 1 hand record](https://nolankido.com/poker/episodes/portland-meadows-ep1/). The method can be used with a local editor or on paper. No account, API call, new upload, or paid service is required.

## One rule before using AI

A fluent reconstruction is not a verified hand history. Lock the known facts and the unknowns before drafting graphics or commentary. AI may suggest cuts and text, but the human editor decides what can responsibly be shown. Do not manufacture missing card suits or streets and present them as witnessed.

## Evidence labels

| Label | Means | Permitted display |
| --- | --- | --- |
| `SOURCE-BACKED` | Supported by a linked public primary account, recording, or checked note | Present as a fact, with sensible precision |
| `RECOLLECTED` | A participant describes it later, without independent timestamped verification | Attribute as a recollection |
| `RETROSPECTIVE` | Strategy or calculation prepared after the hand | Label as later analysis, not table-time thinking |
| `UNKNOWN` | Source does not establish the detail | Omit or mark unknown |
| `ILLUSTRATIVE` | A demonstrative visual intentionally not representing exact observed details | Mark as illustrative on-screen and in the edit record; never let it conflict with known facts |

`SOURCE-BACKED` means the cited account supports the statement. It does **not** imply independent verification of every fact reported by the person who played the hand.

## Worked, public examples

| Segment | Facts safe to carry into graphics | Explicit stop condition |
| --- | --- | --- |
| [6-4 offsuit, 13 left and 10 paid](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-64o-record) | Small blind, 8k/15k/15k blinds and ante, reported stack about 148k. 148,000 / 15,000 = 9.87 BB, conditional on stack timing. Nolan shoves; big blind calls with A-K suited; a four arrives and 6-4 wins. | Do not choose individual suits, show a complete runout as fact, fix an exact effective stack, or claim a verified solver/ICM judgment. This is a retrospective player account. |
| [Pocket sevens, four-handed](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-77-record) | Big blind, 15k/30k/30k, reported stack about 585k = 19.5 BB. Button makes it 75k total, 2.5 BB. Nolan reshoves 77, is called by A-T offsuit, and holds. | Do not show an invented full board as historical footage, substitute an effective stack, or describe hindsight as table-time calculation. |
| [Advertised prize and actual payment](https://nolankido.com/poker/episodes/portland-meadows-ep1/#event-numbers) | Advertised first-place prize: $5,100. Nolan's reported payment after a four-way deal: $2,900. | Do not call the advertised figure the cash received. Do not call either number net profit without complete costs. |
| [Current video versus archived edit](https://nolankido.com/poker/episodes/portland-meadows-ep1/) | The companion uses archived version 7 narration as its historical source. | Do not import version 7 timestamps into the currently published cut without rechecking them there. |

## Blank scene acceptance record

Duplicate this block for **every** hand scene, result graphic, and consequential claim.

- **Episode / current release cut identifier:** `[fill locally]`
- **Scene ID:** `[fill locally]`
- **Current-cut in / out timecodes, watched and confirmed:** `[not checked]`
- **Primary fact source / internal reference:** `[link or private local reference]`
- **Evidence labels applied:** `[SOURCE-BACKED / RECOLLECTED / RETROSPECTIVE / UNKNOWN / ILLUSTRATIVE]`
- **What the voiceover actually says (exactly or paraphrased):** `[fill locally]`
- **What the on-screen text says:** `[fill locally]`
- **Shown positions, hole cards, suits, street and board:** `[fill locally]`
- **Shown blinds / ante / stack / raise-to / pot, with unit:** `[fill locally]`
- **Arithmetic checked (include assumptions and pre/post-posting timing):** `[fill locally]`
- **Unsupported or incomplete details:** `[fill locally]`
- **Required changes, or reason the scene passes:** `[fill locally]`
- **Local reviewer / date:** `[fill locally]`
- **Status:** `[HOLD / REVISE / ACCEPT]`

**HOLD** if an unknown is shown as a fact, a card or board contradicts the narration, a bet size is inconsistent, the payout is misstated, or rights/privacy review is incomplete. **REVISE** when there is a clear local correction. **ACCEPT** only after reviewing the actual current cut with sound.

## Release gate

- [ ] Every card and suit visible on a hand graphic is accounted for by the source, or unmistakably labeled illustrative.
- [ ] The flop, turn and river graphics appear in the correct spoken order. Unknown streets are not depicted as known.
- [ ] Player positions and actions align with the voiceover and source record.
- [ ] Stack and bet labels distinguish chips from BB, raise-to from raise-by, and conditional counts from exact counts.
- [ ] Pot and BB arithmetic is checked, including any ante and whether the stack was counted before posting.
- [ ] Opponent holdings, result, and number of paid places match the supported account.
- [ ] Hindsight ranges, equity talk, and solver-style discussion are identified as retrospective unless a real analysis record is cited.
- [ ] Advertised prize, deal payment, gross proceeds and net profit are not conflated.
- [ ] Audio and images are checked together in the **latest** export, including title, chapter offsets, captions and end card.
- [ ] Venue footage permissions, third-party music/assets and participant privacy are checked separately. Do not publish a private hand record with the public worksheet.
- [ ] All `HOLD` scenes are resolved or cut. A named human accepts the final release.

## Suggested local handoff between ChatGPT, Claude and an editor

1. Save a source record with known facts, unknowns and provenance. Do not grant the editor creative authority over missing facts.
2. Have an AI propose a scene map and a list of potential narration/graphics mismatches. Treat them as questions, not verdicts.
3. Check the current audiovisual export yourself. Fill one acceptance record per scene.
4. Request a revised edit for each `REVISE` or `HOLD` item, with the exact correction and evidence.
5. Run the release gate again after the final export, when timecodes and graphics can be confirmed.

## Optional offline check for structured scene claims

A companion [Python fact-gate script](https://nolankido.com/downloads/poker-vlog-fact-gate.py) offers a narrow, **deterministic** check for this *one public episode*. It does not parse an MP4, hear the voiceover, read artwork, verify permission to film, or judge poker strategy.

The script recognizes only three public source records: `hand_64o`, `hand_77`, and `event_payout`. Its four deliberately constructed before/after scenes demonstrate **seven targeted flags before revision and zero after**. These are scripted editorial examples, not real production defects, AI model outputs, a general accuracy rate, or evidence that an earlier video was repaired.

Run it from the directory where the Python file is saved. Only Python's standard library is required:

```powershell
py -3 poker-vlog-fact-gate.py --self-test
py -3 poker-vlog-fact-gate.py --example > scenes.json
py -3 poker-vlog-fact-gate.py --check scenes.json
```

On macOS or Linux replace `py -3` with `python3`. The script reads only the JSON you explicitly name. Exit code `0` means no targeted flags, `2` means findings, and `1` means an input or self-test error. For actual edits, manually compare the current audio, the screen and stronger private sources, then return to the human release gate above. **No targeted flags never means approved.**

### Scope and limitations

The linked companion contains a player account and its public source boundaries. This worksheet does not prove the strategic quality of either hand, validate a solver result, independently audit a private recording, certify filming rights, or establish better viewer retention. Keep footage, people, business information, and other nonpublic records in your own private production environment.

**Related:** [The poker creator workbench](https://nolankido.com/poker/hand-to-vlog/) describes a proposed workflow using a fictional example. It should not be mistaken for a completed episode.
