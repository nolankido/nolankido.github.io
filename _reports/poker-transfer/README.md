# Poker Foundations: 72-case practice bank

**Expanded October 16, 2026, Hawaii time. Draft content and mechanical QA only.** The bank now contains **72 cases, twelve per skill**, including the original 12 A/B cases and 60 additional C–L cases. Qualified human teaching review and actual beginner observations remain pending. This completes the roadmap's authored case-count milestone, not a finding about learning or retention.

## Use the bank

For self-study, choose a small [skill-specific practice file](self-study.md). Each question has its own closed answer and precise lesson links. The complete self-study file also retains all cases in one copy. No monetary stakes, account or submission is needed.

For a supervised independent attempt, show only the assigned individual [learner card](cards/S1-A.md). The [combined question file](participant-cards.md) is a facilitator index. The [coverage index](coverage.md) contains instructor design notes that may cue answers, and the [facilitator key](facilitator-key.md) contains all reasoning. Keep both off the learner's screen until the first explanation is recorded.

| Skill | Cases | Self-study | First isolated card |
| --- | --- | --- | --- |
| Calls and available actions | S1-A through S1-L | [Twelve cases](study/S1.md) | [S1-A](cards/S1-A.md) |
| Position and turn order | S2-A through S2-L | [Twelve cases](study/S2.md) | [S2-A](cards/S2-A.md) |
| Made hands and draws | S3-A through S3-L | [Twelve cases](study/S3.md) | [S3-A](cards/S3-A.md) |
| River price and expected pot share | S4-A through S4-L | [Twelve cases](study/S4.md) | [S4-A](cards/S4-A.md) |
| Known cards and opposing ranges | S5-A through S5-L | [Twelve cases](study/S5.md) | [S5-A](cards/S5-A.md) |
| Betting purpose and checking | S6-A through S6-L | [Twelve cases](study/S6.md) | [S6-A](cards/S6-A.md) |

Every case has three proposed explanation points and a repair link for each point. Additional links support points spanning more than one concept. Card names are written in full alongside compact codes. The new cases vary action context, board structure, hand comparisons, draws or assumptions about responses. Their instructor-only focus tags describe intended coverage; they do not demonstrate equivalent difficulty or prove a learner has not seen a similar problem.

## What remains unchanged in the original observation plan

The original A/B question source, answers and repair mappings from [PR #107](https://github.com/nolankido/nolankido.github.io/pull/107) are retained exactly and checked by a source fingerprint. The earlier [T1–T6 observation kit](../poker-beginner-baseline/README.md) is separate. Neither has acquired learner results through this expansion.

The [separate A/B protocol](protocol.md) retains its original proposed allocation. Adding C–L cases does not silently assign them to those sessions. A qualified reviewer must approve the exact cases and a recorded selection plan before supervised use. The expanded [review form](review-form.md) starts with every case unreviewed. Review of a subset approves only that subset. Form letters are stable identifiers, not calibrated or interchangeable tests.

Use a private [session form](session-form.md) for each actual attempt and a private copy of the [aggregate form](summary-form.md) for the exact selected cases. Preserve independent and assisted attempts, all three reasoning points, exact-case/answer-key/similar-problem exposure, lesson revision and elapsed intervals separately. Any later attempt needs a new full record with its own case ID. Unused blank rows are not zero outcomes. No real learner records belong in this public repository.

Keep this draft outside the site's main navigation until a qualified reviewer accepts the new prompts and keys. This public GitHub pack is available for inspection; repository publication is not teaching approval. No reviewer signoff, learner feedback, study result, mastery, money-play readiness or retention claim has been generated.

## One source, separate views

[cases.json](cases.json), schema version 2, is the source for all 72 cases. [build_packet.py](build_packet.py) deterministically renders the individual cards, combined question file, separate key, complete self-study copy, six skill copies, coverage index and blank review/summary forms. Edit the source and regenerate rather than separately editing those outputs.

[verify.py](verify.py) independently checks unique legal cards, best-five ranks, possible opponent comparisons, current-round call increments, zero-owed action options, clockwise position records, one-card straight-completion ranks, suit counts and exact river fractions. It checks every repair against the actual lesson anchor and rejects drift in every generated view. The original A/B case source is protected by a fixed fingerprint tied to the preceding release.

Focused regression tests also cross-check every legal holding against the site's separately implemented JavaScript hand evaluator. Mutation checks verify rejection of incorrect calls, action order, hand comparisons, river fractions, missing observations, changed baseline cases and view drift. These checks do not establish that prose is unambiguous, scoreability is valid, possible hands have equal frequencies or an action is optimal.

```sh
python _reports/poker-transfer/build_packet.py
python _reports/poker-transfer/build_packet.py --check
python _reports/poker-transfer/verify.py
python -m unittest discover -s _tests -p test_poker_transfer.py -v
```

All scripts use Python's standard library; the independent evaluator cross-check uses the already required Node runtime. The full repository release gate also remains required.

No existing site data, pages, scripts, CSS, course answers or privacy settings are modified by this draft-bank expansion. Public HTML is checked through the ordinary committed-build and release checks. Mechanical rules references: [PokerStars Hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/) and [hand rankings](https://www.pokerstars.com/poker/games/rules/hand-rankings/), checked October 17, 2026 UTC. These support the game mechanics, not teaching-effectiveness claims.

## Next evidence step

Qualified review should first identify confusing prompts, unasked reasoning requirements and unsuitable prerequisites, then record changes against exact case IDs and commits. After acceptance, actual consenting adult beginners can supply observations under the separately approved plan. Keep observations attached to the cases actually used; a larger bank alone is not evidence of improved understanding.

## Offline qualified-review handoff

The [qualified review and observation handoff](review-workflow.md) and [local-only review-round tool](review_round.py) provide an 18-case first-pass triage, a separate full 72-case review packet, question/key separation and case-bound source fingerprints. Completed review records must stay private and cannot be treated as verified human signatures. A first-pass subset cannot approve unreviewed cases. The tool always reports that publication is not authorized; both the qualified six-lesson review and case-scoped human assessment remain pending.
