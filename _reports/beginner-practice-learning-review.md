# Beginner learning and practice review

Reviewed October 15, 2026 against production commit
`fd9fa67f65c367adba5026c8cc2321e61a0f2f94`.

## What the current course already does well

The published path has six coherent stages, limited first-pass reading, a
continuous fictional hand, specific mistake explanations, twelve separate
checkpoint/retry situations and private worksheets. These are substantial
improvements over a reading list. The complete lessons explain their assumptions
and distinguish arithmetic, hidden information and a decision's result.

This review follows the tasks a new reader would attempt. It inspects content,
sequence, practice and interfaces. It does not observe actual learners and cannot
establish retention, completion rates, ease of use for all beginners or learning
gains. Likely effects below are design judgments.

## Remaining learning bottleneck

| Observation in the reviewed version | Implication for a beginner | Implemented response |
| --- | --- | --- |
| The first guided scene explicitly states that both blinds still have initial decisions, then asks who still has an initial decision. | Useful worked instruction can also cue the answer. A correct choice here provides little evidence of independent application. | Keep the introductory hand and add distinct practice prompts whose solutions are not supplied in the prompt. |
| The guided hand uses the same cards, amounts and answer positions on every replay. | Recognition can become easier without the reader applying the rule to another setting. | Eighteen fixed questions change amounts, streets, positions, cards and conclusions. The finite bank and repetitions are disclosed. |
| The separate checkpoint has fresh cases and retries, but a struggling reader returns to a full reference lesson. | The repair can still be a large step for someone missing one elementary idea. | Six short rules and worked examples sit beside three changed questions per idea. Every full lesson links to its matching skill. |
| Immediate feedback exists, but the guided hand ends with a general next-step suggestion. | The learner must remember which mistakes need another look. | A visit review retains uncertain and different answers, with exact repair links, even after a corrected retry. |
| The course opening offers several further-reading routes before the hand. | A first-time visitor has extra choices before the main learning activity. | Put the full overview and first-session alternatives in a native disclosure and provide a direct small-step practice entry. |

The review does not treat a matching multiple-choice response as mastery. The
learner is asked to give a reason before the options appear, but the site cannot
verify an explanation spoken or written on paper.

## How the revised learning loop works

1. Choose one elementary idea from the six-stage course.
2. Read a short rule and one fully worked example.
3. Explain a changed question before showing the choices.
4. Compare the answer and its specific mistake explanation. Readers can choose
   “I'm not sure” instead of guessing.
5. Try two more changed questions for the same idea.
6. At a later visit, attempt a mixed set without worked examples initially shown.
7. Use the visit review to choose one repair link and a question to explain later.

There are three mixed sets, each containing one question from each of the six
skills. Across the sets, every reviewed question appears once. Further sets
repeat. The interface does not claim unlimited generation, adaptive difficulty,
proficiency measurement, a qualification or profitable-play readiness.

Worked examples can be requested during mixed practice. The review distinguishes
an example being shown from a matched choice without an example shown. It retains
an uncertain or incorrect attempt after a later correction. These labels describe
interface events, not whether an example was read or an idea was learned.

## Content and technical scope

The new `/poker/beginner-practice/` is a study utility with WebPage metadata.
It does not add an essay or inflate the guide count. Original publication dates,
feed identities and authored article sources are preserved. The course, all six
lessons, library shortcut and Learn topic connect to it. Search reaches precise
exercise anchors while excluding the model and answer panels.

All examples use standard no-limit Texas Hold'em. Numeric calls assume enough
counters to call. Showdowns use best-five rules and distinct cards. The hand bank
includes a missed draw, a completed flush using one private card, a board straight
tie using zero private cards and a board that supersedes a pocket pair. Qualitative
range and betting questions distinguish observations and conditional purposes
from estimates of frequency or claims that an action is optimal. No solver
outputs, Nolan hands or personal results are invented.

The optional script keeps choices and review notes in the current document.
It has no network, storage or cookie API and writes no answer to a URL. Reloading
clears the visit. Native pages retain all six models and eighteen questions when
the script is blocked; print reveals their explanations. Existing private study
cards remain the durable note-taking option. Site pageview analytics is separate.

## Evidence and verification

The [IES practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/1) recommends
alternating worked solutions with independent attempts, explanatory questions,
retrieval and spaced study. Applying those general recommendations here is a
design inference. The guide does not validate poker questions or establish the
optimal timing of this course's review routine.

Mechanics were checked October 15, 2026 against [PokerStars' Hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/)
and [hand rankings](https://www.pokerstars.com/poker/games/rules/hand-rankings/).
The independently implemented test evaluator verifies the card categories,
draw counts, river best five and tie. Separate arithmetic and action-order checks
verify call amounts and seats; known-card removal is enumerated. Qualitative
explanations remain reasoned editorial content rather than solver-graded answers.

The focused browser suite exercises all eighteen changed questions at four
widths, all three mixed sets, uncertainty, corrected retries, prior visits,
focus, exact lesson and search arrivals, print, native fallbacks, accessibility,
text spacing and privacy. Desktop and phone screenshots are inspected visually.
Complete predecessor hashes and negative mutations protect previous releases.
The pull request and deployment logs record the actual full-suite and live-byte
verification results. No learner success percentage is inferred from test counts.
