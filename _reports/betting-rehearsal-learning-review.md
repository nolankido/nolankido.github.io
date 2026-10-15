# Beginner learning-path review: from recognition to procedure

Reviewed October 15, 2026. Starting release:
`aa81b7f310c3d5fd23f70e7eae10066dffb604de`.

This is a task, content and interface audit. No beginners were observed and no
learning gains, retention rates or conversion effects were measured. The earlier
card-foundation implementation was complete and published before this review.

## How a beginner currently learns

The existing path teaches card names and the goal, demonstrates a five-card
selection, lets readers construct hands, follows a scripted hand, then provides
six connected lessons. First-pass reading limits, exact repair links, eighteen
changed questions and a separate checkpoint already support a more manageable
sequence than reading the entire archive. Readers can work without wagering,
accounts or external purchases. The long essay remains an optional overview.

| Beginner task | Evidence in the starting release | Learning implication | Priority and response |
| --- | --- | --- | --- |
| Find one useful starting task | Quick links plus a second card-first introduction precede several different activities | Returning readers must distinguish card construction, a scripted hand, reference lessons and practice | Replace the duplicate introduction with three concrete entry choices; explicitly choose one task per visit |
| Recognize and construct a hand | Card basics, one worked example and ten constructive hands cover the best five using zero, one or two private cards | This foundation is already directly practiced | Preserve it and its optional pacing |
| Understand a call or a check | Stage 1, the guided hand and the practice bank explain these distinctions | Readers can recognize the right number or description while relying on supplied choices | Add an amount input and a changing payment ledger |
| Track a whole betting round | Guided-hand actions are supplied by its script; individual questions test one situation at a time | The existing interface does not let a reader produce a legal line, observe how it changes later decisions, or compare legal alternatives | Add a branching, three-seat betting rehearsal with three starting states |
| Know when action is complete | The first lesson explains the big blind's option and action returning after a raise | Equal contributions or having acted once can look sufficient without a procedural demonstration | Keep pending turns distinct from payments; preserve the big blind's turn and return action after bets and raises |
| Judge strategy separately from rules | Existing lessons distinguish prices, equity, ranges and assumptions | A rule simulator could accidentally imply every accepted move is good poker | Accept alternate legal lines, never rank strategic choices, and state the omitted assumptions |
| Repair a specific error | Existing banks supply exact lesson links | A later successful retry can mask an earlier misunderstanding | Keep rule-specific study notes after retries and restarts, without a score or completion certificate |

These implications are design judgments from the observed tasks and interfaces,
not findings about a sampled learner population. The goal of this release is a
missing kind of practice, not another compulsory bank of questions.

## What changes

The existing course now contains a betting rehearsal. It starts with a three-seat
preflop round, a fresh flop, or a flop raise already made. Readers take the current
seat's turn and enter extra counters for calls, bets and raises. The table shows
payments on this round, the total wager, the earlier pot and the next player.
Checks, bets, full raises, calls and folds produce different legal lines. Errors
leave the ledger unchanged and explain a specific rule. Readers may see a worked
line, restart or switch starting points. Exact lesson arrivals and correction
messages receive visible focus below the site header after font layout settles.
Pending arrival focus is cancelled when a learner starts using the controls, so
a later font response does not take focus away from their action. Each line stays available in the current
document until restarted or reloaded.

The preflop start retains the big blind's option even when every payment matches.
Bets and raises give eligible earlier players another decision. The raise example
uses 4 followed by a raise to 10, so the next minimum total is 16, not 20.
When folding ends a hand, the rehearsal reports the returned uncalled amount and
the remaining awarded pot separately. It supplies no private cards, hand-strength
advice or strategy score.

This is a deliberately bounded procedure model: imaginary ample counters, whole
amounts, a disclosed practice ceiling of 1,000 per player per round, and no stack
limits, short all-ins, side pots, antes or fees. It checks proposed moves before
applying them. It does not reproduce a venue's binding declarations or penalties.
A ceiling error is identified as an exercise restriction, not a poker rule.

Native starting tables and worked lines survive disabled JavaScript, a blocked
script or invalid embedded data. Print includes all three starting tables and
worked lines. Answer state is held only in the document; the rehearsal performs
no network, storage, cookie or answer-bearing URL writes. Search links to the
actual starting state without indexing the worked-line explanations. Stages 1,
2 and 3 link directly to the relevant start. The blank study card adds a ledger
and a question about who still needs a decision.

## Basis and limits

The [IES practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/1) recommends
alternating worked solutions with attempts and connecting concrete and abstract
representations, each with moderate evidence in its educational review. Its
recommendations support this design direction but do not validate a poker course
or establish a learning gain here. Rules were checked against
[PokerStars' hold'em rules](https://www.pokerstars.com/poker/games/texas-holdem/)
and [Poker TDA 2026 rules, Version 1.1](https://www.pokertda.com/view-poker-tda-rules/),
including minimum raise increments, uncalled returns and non-standard folds.
These are primary rule references, not endorsements of their commercial services.

## Release verification contract

- Preserve the exact prior 193 public pages, 221 generated outputs and 472 product
  source files through a SHA-gated adapter for this reviewed change. Do not change
  old baseline snapshots or article/feed identities.
- Independently check the three worked ledgers, blind-option ordering, repeated
  action after a bet and raise, full raise increments, additional call costs,
  fold settlements, invalid moves and malformed starting data.
- Explore seeded alternative branches for conservation of counters, pending-turn
  eligibility and completion invariants, using checks separate from the rule engine.
- Exercise alternate lines, error recovery, persistent correction notes, help,
  explicit restart, direct lesson arrivals, reload, private operation and print in
  the browser. Check 320, 390, 768 and 1440 pixel widths, keyboard operation,
  horizontal overflow, script fallbacks and accessibility.
- Run the complete existing release checks and verify the actual deployed bytes.
  Final executed results and the exact deployed commit belong in the release PR.

Remaining uncertainty: how first-time learners describe each action without help,
how long one task takes, whether errors recur on another day, and whether learners
find the next stage unaided. A future observed task review should ask learners to
complete an unraised blind round, explain a returned turn and rebuild a changed
ledger without the worked line. Page visits and accepted moves alone would not
answer those questions.
