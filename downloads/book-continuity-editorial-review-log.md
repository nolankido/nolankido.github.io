# Book continuity: source-first editorial review log

An original, reusable worksheet from [Nolan Kido's Preflight case](https://nolankido.com/technology/ai-book-continuity-checker/). It helps an author examine a possible continuity error without treating an AI finding as a command to revise. Save a private copy for each disputed fact.

This document contains no private manuscript text and makes no model calls. Keep your completed copy on a system you control. Do not paste unpublished chapters into a public demo without checking how that service handles submissions.

## Worked example A: a real question worth reviewing

**Candidate:** Dr. John Watson's war wound changes location across the Sherlock Holmes stories.

| Evidence | Source to inspect | Claimed detail |
| --- | --- | --- |
| Earlier occurrence | *A Study in Scarlet*, Watson's account of his military service | A bullet strikes the shoulder; a later reference mentions an injured arm. |
| Later occurrence | *The Sign of the Four*, Watson's description | He nurses a wounded leg. |

The [archived Preflight report](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/src/canonkeeper/preflight/samples/sherlock-holmes-report.html) contains source passages for comparison. The reported difference is worth reviewing, but a suggested replacement is still an editorial decision. Record the intended chronology and whether the author could plausibly mean two injuries before changing published text.

## Worked example B: a plausible but wrong flag

The same [recorded Holmes audit](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/README.md#what-it-found-in-sherlock-holmes) incorrectly treated an eye description of Holmes while disguised as a contradiction. It also confused a married surname with a maiden name. Context can explain a different description without any correction. A confident alert can therefore be wrong even when it quotes real passages.

**Possible decision:** Explained by context. Preserve the original text and write down the explanation. Do not mark it as a confirmed contradiction.

## Blank editorial decision record

Copy these fields for each finding:

| Field | Your record |
| --- | --- |
| Finding ID and date reviewed | |
| Character, object, place, or rule | |
| Exact first quote, book, chapter, edition | |
| Exact second quote, book, chapter, edition | |
| Are both quotes traceable to the original text? | Yes / No / Needs research |
| Do both claims concern the same person or object? | Yes / No / Unknown |
| Is the time or point of view the same? | Yes / No / Unknown |
| Could disguise, renaming, development, or narrator error explain it? | |
| Is any source detail missing or misattributed? | |
| Decision | Supported error / Explained change / Unresolved / Unsupported flag |
| Editorial action and reason | |
| Revised passage and recheck result, if applicable | |
| Reviewed by / follow-up date | |

### Four questions before approving a fix

1. **Where exactly is each claim written?** An AI-generated paraphrase is not the source passage.
2. **What context could make both statements true?** Consider chronology, disguises, different people, aliases, changed circumstances, and narrator reliability.
3. **What did the checker fail to extract?** Read nearby material and dialogue independently. An absent flag does not prove consistency.
4. **What changed after the edit?** Check the revised sentence against every other relevant appearance, not just the two passages that caused the alert.

## How to interpret a recorded benchmark

In the [October 27, 2026 seeded Holmes test](https://github.com/nolankido/canonKeeper/blob/947e9c3d7dbc9bfa719579ca1e697d4479567684/evals/results/holmes-seed0-2026-10-27/README.md), the same saved output was rescored, without another model run. Of 20 planted changes, 8 were counted as found and 12 as missed; there were 2 false positives, plus 1 finding classified separately. Eight misses occurred during extraction and four during judgment. Some planted cases were ambiguous or depended on a mistaken source fact. These numbers describe one imperfect experiment, not the accuracy or reliability of Preflight on your own books.

**Use this log for a human editorial decision.** It does not replace reading the manuscript, establish model accuracy, authorize uploading private content, or make a claim about time saved.
