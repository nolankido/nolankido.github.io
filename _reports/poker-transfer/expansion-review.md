# Review of the 72-case draft expansion

Prepared October 17, 2026 UTC. Baseline: `8fc1d78b76e313be721d9bded0cb16d98501b81f` (PR #107).

## Scope and result

The draft expands from two to twelve cases for each of six Poker Foundations skills: 72 total, with 60 additions. Each case has three proposed reasoning points and exact repair links. The original A/B case dictionaries, including their prompts, explanations and repairs, remain identical to the baseline and have a fixed source fingerprint. This reaches the authored inventory milestone. It does not complete qualified teaching review, calibration, learner observations or a learning-effectiveness study.

The new cases vary the underlying reasoning as well as cards and counters. Examples include separating an ante from a live blind, the big blind's check/raise option, a full minimum reraise, relative position after the button folds, a wheel, one-card versus two-card draw completion, private pairs displaced by the board, shared-board ties, one private card improving a flush, exact-card blockers, counter scaling, and response assumptions that change a bet's purpose.

Six smaller self-study files give each skill its own entry. The full self-study copy, isolated questions and facilitator key are generated from the same source. Coverage notes are marked for instructor use because they may cue an answer. The original observation allocation remains separate from the expanded bank. No real session records or reviewer acceptance are included.

## Content review and corrections

Three AI authoring passes were followed by separate AI reviews of the other authored cases. This is engineering and editorial review, not the qualified human teaching review required by the protocol. The review checked each scene, prompt, explanation, candidate comparison and repair destination.

Corrections made before the release gate:

- S2-C now states that earlier folds do not establish later players' cards or responses. S2-D asks for the full postflop order that its key describes.
- S3-F and S3-L no longer identify the target hand category before asking for it. S3-L uses a different card construction from the previously published flop scene.
- Flush comparisons in S3-C, S3-L, S4-G and S4-J use the relevant hand-ranking explanation. S4-J compares all five flush ranks and identifies the first differing rank; S4-E uses conditional wording about a possible tie.
- S5-D correctly describes the opposing three of a kind and its ace kicker. S5-J no longer supplies the number of invalid candidates in the question. S5-F has a neutral title.
- S6-G evaluates the current bet's response model, matching its prompt. S6-H asks about a value-bet purpose without implying that the setup already stated one.
- The private session template explicitly requires a separate record for each participant and case attempt. Unspecified response actions are represented by an omitted field, not an explicit null.

## Mechanical and release verification

The packet verifier checks all 72 cases, all generated views and every repair anchor. The focused suite contains 21 tests, including corrupted-source cases that are regenerated before validation, so incorrect mechanics cannot pass merely because every view agrees with the same bad source. All legal learner and candidate holdings are also checked against the site's separately implemented JavaScript evaluator.

The focused checks passed locally. The unchanged public build checked all 221 generated outputs; HTML validation and search metadata checks covered 193 pages. The complete repository unit and browser gates run on the final PR commit. Their actual result and the subsequent merge/deployment evidence belong in the PR record; this report does not predeclare those remote results.

## Remaining evidence boundary

Every case remains marked unreviewed on the blank qualified-review form. Before supervised observations or inclusion in main course navigation, obtain the existing protocol's required review of the exact selected cases and teaching revision. Form letters are identifiers, not interchangeable tests. New card patterns do not prove unfamiliarity. Keep actual exposure, assistance, elapsed intervals and point-level observations separate, and report only sessions that occur.
