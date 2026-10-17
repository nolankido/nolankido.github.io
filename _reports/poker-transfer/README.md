# Poker Foundations: two-form transfer practice and diagnostic repair

**October 16, 2026. Draft content and mechanical QA only.** No qualified human teaching review, actual adult beginner session, study result or retention claim is implied. This extends the earlier observation kit without changing its evidence, its six original follow-up problems or any published Poker Foundations lesson.

## Why this is the next improvement

The six-stage course already offers a worked example, a changed first attempt, practice situations, a checkpoint and an optional private progress tracker. Repeatedly recognizing the same answer is not the same as explaining a new case. This package adds **two new situations for each of six skills**, an answer-free participant file and a separate reasoning key with misconception-specific repairs. The cases deliberately change card combinations, betting quantities, action sequences or hypothetical opponent responses relative to the earlier six probes; that engineering comparison alone cannot establish that any particular person finds them unfamiliar. Participants must be asked about previous exposure.

Use [participant-cards.md](participant-cards.md) for a supervised independent attempt, or [self-study.md](self-study.md) for private practice with answers in closed disclosures. [facilitator-key.md](facilitator-key.md) supplies proposed explanation points and exact live repair links. [review-form.md](review-form.md) is an unsigned qualification and teaching-clarity gate. Keep this draft outside the site's main navigation until a qualified reviewer accepts the new prompts and keys. Publication in this *public GitHub repository* is not reviewer approval, and it is not a secure place for learner records.

## Proposed research use (not performed)

After the original 18-criterion teaching packet and the new prompts are independently approved, use the already prepared [beginner observation protocol](../poker-beginner-baseline/protocol.md). Ask 6 to 8 consenting adult beginners to attempt a novel case in a realistic sequence. Present only the assigned case, record the first reason before hints, record any repair visited and time spent away, and label actual prior exposure. Where practical, reserve the paired form for a genuinely later reattempt, not a repeat immediately after feedback. Do not assume a delayed test is unfamiliar. Randomized assignment, comparable difficulty and validated scoring are **not established** by this draft.

A single response, short break or browser test does not prove learning gain, readiness to risk money, seven-day retention or the effectiveness of the course. With small samples, report raw observed difficulties, assistance and incomplete answers, not percentages framed as population effects. Adapt the site only to observed, independently reviewed patterns; do not fabricate participants, feedback, timestamps or reviewer signoff.

## Coverage

| Skill | Form A | Form B | Precise lesson repair |
| --- | --- | --- | --- |
| S1 Call and action | The flop resets the price | The blind is already in | [Lesson](https://nolankido.com/poker/first-decisions/#chips-owed) |
| S2 Position and turn order | The blind has not decided yet | The button does not lead the flop | [Lesson](https://nolankido.com/poker/starting-hand-decisions/#position) |
| S3 Made hand vs draw | A pair and a draw are different | A draw without a pair | [Lesson](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing) |
| S4 River price vs equity | A missed river draw at a new price | Same concept, different denominator | [Lesson](https://nolankido.com/poker/turn-and-river-decisions/#river-reset) |
| S5 Physical blockers vs inference | One blocked card, two possible rivals | A reveal is not a frequency table | [Lesson](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible) |
| S6 Bet purpose vs checking | Possible worse callers do not prove value | A fold is an outcome, not the full argument | [Lesson](https://nolankido.com/poker/betting-with-a-purpose/#purpose) |

Cases and expected mechanical fields live in [cases.json](cases.json). [verify.py](verify.py) uses only Python's standard library. It independently enumerates legal best-five selections for each 5- or 7-card holding, validates full card uniqueness, compares possible opponent holdings, checks current-round call increments and river pot fractions, checks the 6-by-2 skills/links, and checks document sections. It does not verify whether every prose instruction is pedagogically clear, prove a participant did not previously see a case, or validate strategic EV when frequencies are unknown.

```sh
python _reports/poker-transfer/verify.py
python -m unittest discover -s _tests -p test_poker_transfer.py -v
```

The independent review and observation gates from cycles 2 and 3 remain pending. No existing site data, pages, scripts, CSS, course answers or privacy settings are modified by this preparation commit. For mechanical rules, see [PokerStars Hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/) and [hand rankings](https://www.pokerstars.com/poker/games/rules/hand-rankings/). These are rules references, not learning-effectiveness evidence.
