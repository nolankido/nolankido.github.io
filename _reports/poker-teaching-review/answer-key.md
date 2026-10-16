# Current feedback and mechanical cross-check

Material commit: `8505785a02c2565e3dd97215f8ce7dc63aa6db43`.
Packet fingerprint: `0ab8f0afd7bb03e99c1c09f6900f1625a74aa8cff15e4da3779a1f0969501495`.
Prepared 2026-10-16 UTC. **Human review: pending.**

This key reproduces the current teaching feedback for inspection. It is not an independent human approval. Check the current prose against the recomputed card and ledger evidence below.

## L1-W

Your best five are Q-Q-J-8-3: a pair of queens. Calling adds 4 - 0 = 4 counters. You can fold, call 4 or make a legal raise; checking is unavailable. Having a pair does not choose an action for you.

## L1-A

Your best five are Q-Q-J-9-5, a pair of queens. A call adds 7 - 0 = 7. The 6 was paid preflop and does not pay for a flop bet. Facing this wager, you may fold, call 7 or make a legal raise; you cannot check.

Look for both parts in your explanation: five actual cards, and a payment counted on the current round. If you subtracted the earlier 6, reset the round's contribution to zero before counting again.

Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

## L2-W

You face an unraised big blind. A call would add 2 because you have paid zero. Both blinds still have decisions after your initial action; either may raise. Being on the button does not finish preflop. This description does not prescribe a call or a raise.

## L2-A

A call adds 6 - 1 = 5. The big blind still has an initial decision, and a raise could return action to you or the earlier players. The pot has already been raised and called, and you are in the small blind rather than on the button.

Your two cards did not change, but the earlier action, price and position did. If you reach a flop, the small blind acts before the other remaining seats in this six-player hand. The price alone does not settle whether to continue.

Snapshot repair: [starting-hand-decisions #position](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/starting-hand-decisions.html#L17); [readable exhibit](reference-text.md#ref-starting-hand-decisions-position). Live navigation: https://nolankido.com/poker/starting-hand-decisions/#position

## L3-W

Your best five are T-T-A-7-2: a pair of tens with an ace kicker. There are four hearts, so you also have a heart-flush draw. You may check or bet because nothing is owed. The opponent's check does not tell you which private cards they hold.

## L3-A

Your best five are K-K-Q-8-3, a pair of kings with a queen kicker. Four spades give you a spade-flush draw. You may fold, call 5 or make a legal raise; you cannot check past the bet.

Another spade would complete a flush, but it would not guarantee a win. A stronger flush or another stronger hand can be possible, depending on the later board and opposing cards. Keep 'improves my hand' separate from 'wins the pot.'

Snapshot repair: [first-flop-decisions #made-and-drawing](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/first-flop-decisions.html#L5); [readable exhibit](reference-text.md#ref-first-flop-decisions-made-and-drawing). Live navigation: https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

## L4-W

Your best five are J-J-T-8-5. The heart draw missed; you still have a pair of jacks. The bet makes the current pot 36. Calling adds 12 and makes 48, so 12 / 48 = 25% is the break-even share. It is not a measured chance that your hand wins.

## L4-A

Your best five are Q-Q-J-9-6. Four spades leave a missed flush draw and a pair of queens. The current pot is 48; your additional 12 makes 60. The break-even share is 12 / 60 = 20%.

The same bet of 12 has a different price because the earlier pot changed. You still need a justified model of the opponent's possible hands and their frequencies to estimate your pot share, including ties. The arithmetic alone does not show that calling is best.

Snapshot repair: [turn-and-river-decisions #catching-a-bluff](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/turn-and-river-decisions.html#L28); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-catching-a-bluff). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

## L5-W

A is impossible: it reuses your ace of hearts. B is physically possible, but its frequency is unknown. C is also possible and makes three tens, which beat your pair. Checking therefore does not prove the opponent holds a weaker hand. None of these observations supplies probabilities.

## L5-A

A is impossible because you hold the king of spades. B and C reuse none of the known cards. B makes a pair of kings and beats your queens; C does not. A check is compatible with either legal holding.

Neither physical possibility nor one reveal establishes a frequency. Different models can allow the same observed hand. Say which cards and actions are known, then label any frequency as an assumption needing evidence.

Snapshot repair: [ranges-for-beginners #known-and-possible](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/ranges-for-beginners.html#L5); [readable exhibit](reference-text.md#ref-ranges-for-beginners-known-and-possible). Live navigation: https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

## L6-W

Your pair of tens beats the nines and loses to three eights. Under these supplied responses, neither candidate supports the proposed value-bet argument: the worse hand does not call, and the better hand does. The better hand does not fold to support a bluff either. Checking already wins against the nines without a new wager. This conclusion is about this restricted model.

## L6-A

Your best five are 9-9-J-8-7. The eights are worse and, under the supplied response, call the bet. They are a candidate source of value. The jacks are better and also call, so they cost you when present. Unlike the worked example, at least one worse hand now calls.

That is useful evidence within the example, not a complete verdict. You still need the frequencies of opposing hands, other possible holdings and their responses, including raises. Compare the resulting expectation with checking. Winning one pot would not fill those gaps or prove the bet was best.

Snapshot repair: [betting-with-a-purpose #value](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/betting-with-a-purpose.html#L12); [readable exhibit](reference-text.md#ref-betting-with-a-purpose-value). Live navigation: https://nolankido.com/poker/betting-with-a-purpose/#value

## A-preflop

Calling adds 2 - 0 = 2. Raising to 6 adds 6 because you have paid nothing this round. The small blind and big blind still have initial decisions; either could raise and return the action to you. Being on the button does not put you last preflop.

If you said 4 for the raise, you counted the increase over the big blind rather than your own total contribution. If you said the round was over, you skipped two players.

## A-flop

Your best five are T-T-A-7-2: a pair of tens. Your two hearts plus two board hearts give a heart-flush draw, not a made flush. Checking is available because no one has bet on this round.

A value bet needs calls from worse hands. You would need assumptions about which worse and better hands call, how often, and what can happen later to compare betting with checking. A pair plus a draw alone does not establish that a particular bet is best. Confusing four hearts with five overstates your current hand; naming only a worse hand without its response does not explain value.

## A-turn

Your best five are now T-T-A-7-4. You still have four hearts among your available cards, so the flush has not arrived. The new card replaces the two as a kicker; it does not change the pair into a different category.

The check establishes that this opponent declined to bet at this turn. It does not identify their cards or measure how often they hold a strong hand. If you check, both players have checked and the round ends. The big blind, the first remaining seat clockwise from the button, acts first on the river.

## A-river

You have T-T-A-9-7, still one pair. The heart draw missed. Candidate A is impossible because you hold the ace of hearts. B is legal and weaker: its queen-high hand loses to your pair. C is legal and stronger: three nines beat your pair. These are alternatives to compare, not a complete range or a probability estimate.

Calling adds 7 - 0 = 7. The pot is 21 + 7 = 28 before your call and 35 after it. The break-even equity is 7 / 35 = 20% when this heads-up cash-style call ends the betting, with no fees or prize effects. That is a price, not your measured chance of winning. You still need an appropriate opponent range and frequencies, including any ties. Checking is unavailable while facing the bet; fold, call or a legal raise are the relevant actions.

If you subtracted your earlier 10 from this call, you mixed betting rounds. If you divided by 28, you omitted your own additional 7 from the final pot. One possible missed draw does not show that you meet the price.

## A-showdown

Opponent: 9c, 9d.

Scripted ending: you call 7. The big blind shows nine of clubs and nine of diamonds, making three nines, and wins the 35-chip pot. You contributed 17 across the hand and finish with 83. The big blind finishes with 118; the folded small blind has 99. The other three players still have 100 each, preserving all 600 counters.

This reveal settles this showdown. It does not establish the opponent's earlier frequencies or prove that calling was a mistake. Compare your explanation written before the reveal with the stated facts, not just the loss.

## B-preflop

Calling adds 6 - 1 = 5. Your posted 1 counts toward this preflop wager. The big blind still has an initial decision and could raise; your call does not complete their turn.

With only you and the cutoff remaining, you act first after the flop. You are now out of position rather than on the button. The same two-card category would not erase this change in prior action and order. If you said 6, you omitted the blind already paid; if you said the cutoff acts first, you carried preflop order into the next round.

## B-flop

Your best five are Q-Q-K-8-3, a pair of queens, with four hearts among your available cards: a heart-flush draw. Calling adds 7 - 0 = 7. The preflop 6 is already in the pot from a different betting round.

Checking is unavailable now because the cutoff's bet created a new decision for you. Your earlier check did not finish the round or pay the bet. If you counted only 1 more chip, you incorrectly reused preflop chips. If you called this a flush, you counted four hearts as five.

## B-turn

You have a king-high flush: K-Q-8-5-3, all hearts. Unlike Hand A, the turn completed your draw. Jack-ten of hearts makes a weaker jack-high flush; ace-jack of hearts makes a stronger ace-high flush. These candidate holdings are separate alternatives, not cards held at the same time.

A worse caller is relevant to value, but naming one does not establish that betting is best. You need the relative frequencies of worse and better callers, other responses, the amount bet and possible river action. Checking remains available. If your reason was simply 'a flush must bet,' it skipped the comparison and missing assumptions.

## B-river

Your best five remain the king-high heart flush, K-Q-8-5-3. Candidate A conflicts with your queen of hearts. B is legal and its ace-high flush beats yours. C is legal and its jack-high flush loses to yours. The checked turn does not physically rule out B or supply a frequency for it.

Calling adds 14 - 0 = 14. The pot is 28 + 14 = 42 before calling and 56 afterward. The break-even equity is 14 / 56 = 25% under the same heads-up, final-call, no-fee cash-style assumptions as Hand A. A made flush does not by itself establish equity against an unspecified betting range.

The changed bet is half the earlier pot, rather than Hand A's one-third pot. Reusing 20% would ignore that change. One later reveal tells you the holding in this scripted hand, not the frequencies of all possible hands that might take this line.

## B-showdown

Opponent: Jh, Th.

Scripted ending: you call 14. The cutoff shows jack of hearts and ten of hearts. Your king-high flush beats the jack-high flush, and you receive the 56-chip pot. You contributed 27, so your net gain is 56 - 27 = 29 and you finish with 129. The cutoff has 73 and the folded big blind 98. The other three stacks remain 100, preserving 600 counters.

Winning this ending does not prove that the call was best against the opponent's unknown range. Review your explanation before seeing the result. Name one way this hand differed from Hand A and one question you would still need to answer.

## G-position

Current selected answer: B.
The small blind and big blind still act. Before the flop, the initial action begins to the left of the big blind and proceeds clockwise. A raise can give earlier players another decision. The button is last in the initial order after the flop, not before it.

- **A:** Three folds do not finish the round. Both blinds still have decisions.
- **B:** Yes. The two seats after the button still have their initial decisions.
- **C:** The small blind still acts before the big blind. Its forced post was not its initial decision.

Snapshot repair: [starting-hand-decisions #position](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/starting-hand-decisions.html#L17); [readable exhibit](reference-text.md#ref-starting-hand-decisions-position). Live navigation: https://nolankido.com/poker/starting-hand-decisions/#position

## G-call

Current selected answer: C.
The call adds 6 - 2 = 4. The big blind's total contribution becomes 6. The pot then contains 6 + 1 + 6 = 13, and both remaining players have 94 behind. The folded small blind's counter stays in the pot. This explains the accounting, not whether either action is a good strategy.

- **A:** Six is the total wager. The big blind has already paid 2 of that total on this round.
- **B:** Adding the posted 2 to the total 6 counts those forced chips twice.
- **C:** Yes. Subtract the big blind's 2 already paid from the total wager of 6.

Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

## G-flop

Current selected answer: A.
Your current best five are J-J-A-7-2. You have a pair of jacks with an ace kicker, plus four hearts among your available cards. Another heart could complete a flush, but a possible improvement is not a completed hand or a guaranteed win. After the check you can check or bet; you do not call when nothing is owed.

- **A:** Yes. The two jacks make a pair; your two hearts plus two on the board make four hearts.
- **B:** A flush needs five hearts. Only four hearts are available to you now.
- **C:** The board's jack and your private jack already make a pair, even though you also have a draw.

Snapshot repair: [first-flop-decisions #made-and-drawing](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/first-flop-decisions.html#L5); [readable exhibit](reference-text.md#ref-first-flop-decisions-made-and-drawing). Live navigation: https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

## G-raise

Current selected answer: B.
The call adds 12 - 4 = 8, making the pot 37. Each remaining player has put in 6 preflop and 12 on the flop, leaving 82 from the original 100. You may instead fold or make a legal raise; checking is unavailable against the unmatched wager. The accounting does not establish which choice is best.

- **A:** Twelve is the opponent's total flop wager. Your 4 on this round already pays part of it.
- **B:** Yes. Match 12 total after accounting for your 4 already paid on the flop.
- **C:** The raise is to 12 total, not by another 12 on top of your bet of 4.

Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

## G-river

Current selected answer: C.
Your best five are J-J-A-9-7. The flush did not arrive, but your pair remains. A call adds 10 and makes a final pot of 57; a fold or legal raise is also available. There is no universally correct action supplied here because the opponent's hidden hands and their frequencies have not been established.

- **A:** There are still only four hearts available, and an unmatched river bet prevents checking.
- **B:** The river is the fifth and final shared card. No later card will complete this missed draw.
- **C:** Yes. The missed flush leaves your pair, and no earlier-round payment covers this new bet.

Optional after stage 4: if a call ends this heads-up cash-game hand, 10 / 57 is about 17.54%. With no fees or side pots this prices a call in chips; it does not measure your hand's equity or prove that calling is correct.

Snapshot repair: [turn-and-river-decisions #river-reset](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/turn-and-river-decisions.html#L11); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-river-reset). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#river-reset

## G-showdown

Current selected answer: A.
Your J-J-A-9-7 beats the opponent's J-J-Q-9-7 because the ace kicker outranks the queen. You paid 6 + 12 + 10 = 28 and receive 57, for a net gain of 29. Your stack finishes at 129; the big blind has 72 and the folded small blind has 99. The three earlier folders still have 100 each. All six stacks sum to the original 600 counters.

- **A:** Yes. Your ace kicker wins, and receiving the pot includes getting back your own contributions.
- **B:** You receive 57, but 28 of it is your own earlier contribution. The net gain is 29.
- **C:** One ending does not compare your choices against the alternatives or validate an assumed range.

Snapshot repair: [ranges-for-beginners #one-reveal](https://github.com/nolankido/nolankido.github.io/blob/8505785a02c2565e3dd97215f8ce7dc63aa6db43/_source/poker/ranges-for-beginners.html#L37); [readable exhibit](reference-text.md#ref-ranges-for-beginners-one-reveal). Live navigation: https://nolankido.com/poker/ranges-for-beginners/#one-reveal

## Independent recomputation from structured fields

Rank tuples are category followed by category-relevant ranks or kickers. Categories run 0 high card through 8 straight flush. Numeric ranks run 2 through 14 (ace). Preflop cards have no five-card rank.

| Task | Recomputed facts |
| --- | --- |
| L1-W | {"best_rank": [1, 12, 11, 8, 3], "category": "one pair"} |
| L1-A | {"best_rank": [1, 12, 11, 9, 5], "category": "one pair"} |
| L2-W | {"best_rank": null, "category": "preflop: no five-card hand"} |
| L2-A | {"best_rank": null, "category": "preflop: no five-card hand"} |
| L3-W | {"best_rank": [1, 10, 14, 7, 2], "category": "one pair"} |
| L3-A | {"best_rank": [1, 13, 12, 8, 3], "category": "one pair"} |
| L4-W | {"best_rank": [1, 11, 10, 8, 5], "category": "one pair"} |
| L4-A | {"best_rank": [1, 12, 11, 9, 6], "category": "one pair"} |
| L5-W | {"best_rank": [1, 10, 14, 8, 5], "category": "one pair", "candidate_comparisons": ["impossible", "weaker", "stronger"]} |
| L5-A | {"best_rank": [1, 12, 13, 9, 6], "category": "one pair", "candidate_comparisons": ["impossible", "stronger", "weaker"]} |
| L6-W | {"best_rank": [1, 10, 11, 8, 5], "category": "one pair", "candidate_comparisons": ["weaker", "stronger"]} |
| L6-A | {"best_rank": [1, 9, 11, 8, 7], "category": "one pair", "candidate_comparisons": ["weaker", "stronger"]} |
| A-preflop | {"pot": 3, "additional_call": 2, "hero_behind": 100, "best_rank": null, "category": "preflop: no five-card hand"} |
| A-flop | {"pot": 13, "additional_call": 0, "hero_behind": 94, "best_rank": [1, 10, 14, 7, 2], "category": "one pair"} |
| A-turn | {"pot": 21, "additional_call": 0, "hero_behind": 90, "best_rank": [1, 10, 14, 7, 4], "category": "one pair"} |
| A-river | {"pot": 28, "additional_call": 7, "hero_behind": 90, "best_rank": [1, 10, 14, 9, 7], "category": "one pair", "candidate_comparisons": ["impossible", "weaker", "stronger"], "pot_after_call": 35, "break_even_share": "1/5"} |
| A-showdown | {"pot_awarded": 35, "hero_rank": [1, 10, 14, 9, 7], "opponent_rank": [3, 9, 10, 7], "winner_seat": 5, "ending_stacks": [100, 100, 100, 83, 99, 118], "hero_net": -17} |
| B-preflop | {"pot": 9, "additional_call": 5, "hero_behind": 99, "best_rank": null, "category": "preflop: no five-card hand"} |
| B-flop | {"pot": 21, "additional_call": 7, "hero_behind": 94, "best_rank": [1, 12, 13, 8, 3], "category": "one pair"} |
| B-turn | {"pot": 28, "additional_call": 0, "hero_behind": 87, "best_rank": [5, 13, 12, 8, 5, 3], "category": "flush", "candidate_comparisons": ["weaker", "stronger"]} |
| B-river | {"pot": 42, "additional_call": 14, "hero_behind": 87, "best_rank": [5, 13, 12, 8, 5, 3], "category": "flush", "candidate_comparisons": ["impossible", "stronger", "weaker"], "pot_after_call": 56, "break_even_share": "1/4"} |
| B-showdown | {"pot_awarded": 56, "hero_rank": [5, 13, 12, 8, 5, 3], "opponent_rank": [5, 11, 10, 8, 5, 3], "winner_seat": 4, "ending_stacks": [100, 100, 73, 100, 129, 98], "hero_net": 29} |
| G-position | {"pot": 3, "best_rank": null, "category": "preflop: no five-card hand"} |
| G-call | {"pot": 9, "best_rank": null, "category": "preflop: no five-card hand"} |
| G-flop | {"pot": 13, "best_rank": [1, 11, 14, 7, 2], "category": "one pair"} |
| G-raise | {"pot": 29, "best_rank": [1, 11, 14, 7, 2], "category": "one pair"} |
| G-river | {"pot": 47, "best_rank": [1, 11, 14, 9, 7], "category": "one pair"} |
| G-showdown | {"pot": 57, "best_rank": [1, 11, 14, 9, 7], "category": "one pair", "opponent_rank": [1, 11, 12, 9, 7], "ending_stacks": [100, 100, 100, 129, 99, 72], "hero_net": 29} |

M1: Let P be the pot including the opposing bet and C the additional final call. With no fees, side pots, future betting or prize effects, a modeled expected pot share e has incremental call expectation e(P+C)-C versus folding. Setting this to zero gives e=C/(P+C). This identity supplies a price; it does not estimate e or compare raising.

M2: A physically legal candidate identifies a possible holding. Probability needs a model or evidence about frequencies. One compatible reveal cannot uniquely identify those frequencies. These are editorial reasoning checks, not measured player tendencies.

Prose numbers, legal-action wording and pedagogy require reviewer inspection.
Candidate comparisons treat holdings as separate alternatives, without frequencies.
No equity model, solver result, learner outcome or optimal-action grade is computed.
