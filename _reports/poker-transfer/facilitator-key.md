# Facilitator-only reasoning key and misconception map

**Draft, not reviewed or calibrated.** All scenarios and holdings are fictional. This key is public source code, so ask each participant whether they saw it before a session. Do not present it until after an independent explanation. These points are proposed qualitative observation criteria, not an automatic mastery grade or advice on how to wager.

### S1-A: Flop wager after a preflop payment

1. Your five cards form one pair of kings, with nine, seven and three as kickers.

2. You cannot check while facing an unmatched bet; folding, calling or a legal raise are the available action families.

3. The call costs 7 on this street. The five paid preflop is already in the pot, not credit for the flop.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,9,7,3]`.

Call: 7 minus 0 already paid = 7 more.

**Likely misconception:** Treating earlier-street chips as credit on this street.

**Exact repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S1-B: Big blind facing a raise

1. The big blind's 3 already counts on this preflop round, so calling adds 8 and reaches 11 total.

2. Checking is not an option against a raise that exceeds your current contribution.

3. The hand cards do not determine the price. The current wager and what you paid on this round do.

Call: 11 minus 3 already paid = 8 more.

**Likely misconception:** Adding the full raise total twice or checking against an unmatched wager.

**Exact repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S2-A: Action after a button call

1. The big blind still has an initial decision; posting a blind was forced, not a choice to call the raise.

2. If the big blind raises, the earlier players still in the hand may face a new decision.

3. If next, cutoff, button and big blind remain, the big blind acts first after the flop, clockwise left of the button.

**Likely misconception:** Assuming the button completes preflop action by calling.

**Exact repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S2-B: A two-player flop after a button raise

1. Posting the small blind does not itself use the player's preflop decision; their later call does.

2. With only small blind and button active on the flop, the small blind acts first and the button acts second.

3. Facing a check, the button may check or make a legal bet; there is no unmatched wager to call.

**Likely misconception:** Assuming the button is first on the flop or that a check requires a call.

**Exact repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S3-A: Private and shared cards on the flop

1. You currently have a pair of queens with jack, eight and two kickers.

2. Two clubs in your hand and two on the board make four clubs, not a completed five-card flush.

3. Checking is unavailable against a live bet; calling, folding and a legal raise are possible action families.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,12,11,8,2]`.

**Likely misconception:** Calling four cards a flush or checking through a bet.

**Exact repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S3-B: Two suited private cards on the flop

1. Your best five are king, ten, nine, seven and two high: no pair.

2. You can use four hearts now, two private and two shared. Another heart could make a flush, but not guarantee winning.

3. No wager is outstanding, so you may check or make a legal bet; calling is not the current action.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,13,10,9,7,2]`.

**Likely misconception:** Confusing a promising draw with a made hand or calling a check.

**Exact repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S4-A: River bet with ace and ten

1. You finish with one pair of aces, ten, nine and seven kickers. There are only four spades, not a flush.

2. A call adds 6; 18 + 6 + 6 = 30 total, making the call one fifth, or 20%, of that final pot.

3. That is the required pot share under the model, not your estimated equity or a recommendation. Opponent holdings and frequencies remain unknown.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,10,9,7]`.

River: 18 before, 6 bet, 6 call, 30 after; fraction 1/5.

**Likely misconception:** Using the pot price as if it were measured winning probability.

**Exact repair:** https://nolankido.com/poker/turn-and-river-decisions/#river-reset

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S4-B: River bet holding pocket sevens

1. Your best hand is a pair of sevens, with king, queen and nine kickers.

2. Calling costs 20 and makes a final 70-counter pot; 20/70 = 2/7, about 28.57%.

3. Pair strength alone does not determine the action. The call price must be compared with a reasoned range-based estimate, which is not supplied.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,7,13,12,9]`.

River: 30 before, 20 bet, 20 call, 70 after; fraction 2/7.

**Likely misconception:** Using hand category rather than a conditional price and range comparison.

**Exact repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S5-A: Three candidate river holdings

1. Ah-Qs is impossible because you hold Ah; Qc-Qd is a weaker pair of queens; Kh-2d makes two pair, kings and twos, beating your one pair of kings.

2. A check alone does not reveal or exclude the stronger holding.

3. No candidate frequency was supplied, so this list cannot be treated as a probability distribution.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,14,9,6]`.

Candidate status in order: impossible, weaker, stronger.

**Likely misconception:** Allowing known cards in an opposing holding or treating a check as proof of weakness.

**Exact repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S5-B: A checked river and one later reveal

1. 9d-As is blocked by your own 9d; Ks-Kc makes a pair of kings stronger than your jacks; Ad-7c makes only ace-high and is weaker.

2. A check can be consistent with more than one holding, including a stronger one.

3. One revealed hand is one observation, not an established distribution for later opponents or decisions.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,11,9,8,6]`.

Candidate status in order: impossible, stronger, weaker.

**Likely misconception:** Generalizing a single showdown or ignoring physical card removal.

**Exact repair:** https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S6-A: A checked river and two possible callers

1. Jd-Jh is a worse pair of jacks and is assumed to call, so it is a possible value target.

2. Ks-6d makes a pair of kings, ahead of your queens, and is also assumed to call.

3. Without frequencies and other possible responses, the comparison of betting with checking is underdetermined; no profitable-bet claim follows.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,12,13,9,5]`.

Candidate status in order: weaker, stronger.

**Likely misconception:** Concluding that one worse caller guarantees a good value bet.

**Exact repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.

### S6-B: A river bet with two possible responses

1. Kh-Kd makes one pair of kings, weaker than your pair of aces. 9c-9s makes three nines, stronger than your aces.

2. Folding the worse holding is not evidence of forcing a better hand to fold, and gives up that holding's possible call value.

3. Compare the outcomes of betting and checking across possible holdings and responses, with frequencies; one fold does not establish the better action.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,9,8,6]`.

Candidate status in order: weaker, stronger.

**Likely misconception:** Confusing a fold of a worse hand with profitable bluffing.

**Exact repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Observation labels:** unassisted / hinted / shown; explanation supported / error / not demonstrated; familiar / previously exposed / unknown exposure; returned after stated interval / not returned.
