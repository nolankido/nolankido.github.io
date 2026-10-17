# Facilitator-only reasoning key and misconception map

**Draft, not reviewed or calibrated.** All scenarios and holdings are fictional. This public key contains answers. Ask about prior exposure and show it only after an independent explanation. The three proposed reasoning points are qualitative review criteria, not a mastery grade.

<a id="s1-a"></a>

### S1-A: Flop wager after a preflop payment

1. Your five cards form one pair of kings, with nine, seven and three as kickers.

2. You cannot check while facing an unmatched bet; folding, calling or a legal raise are the available action families.

3. The call costs 7 on this street. The five paid preflop is already in the pot, not credit for the flop.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,9,7,3]`.

Call: 7 minus 0 already paid = 7 more.

**Likely misconception:** Treating earlier-street chips as credit on this street.

**Starting repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#best-five)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#chips-owed)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s1-b"></a>

### S1-B: Big blind facing a raise

1. The big blind's 3 already counts on this preflop round, so calling adds 8 and reaches 11 total.

2. Checking is not an option against a raise that exceeds your current contribution.

3. The hand cards do not determine the price. The current wager and what you paid on this round do.

Call: 11 minus 3 already paid = 8 more.

**Likely misconception:** Adding the full raise total twice or checking against an unmatched wager.

**Starting repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#chips-owed)

<a id="s1-c"></a>

### S1-C: An ante and a raised pot

1. Calling adds 7 counters: the current wager of 9 minus your small blind of 2.

2. The separate ante is already in the pot but does not count toward the preflop wager; it cannot reduce the call to 6.

3. You face an unmatched wager, so checking is unavailable; you may fold, call or make a legal raise.

Call: 9 minus 2 already paid = 7 more.

**Author's design note, for review:** This case requires separating two payments made before the cards, rather than distinguishing a previous street from the current one.

**Likely misconception:** Subtracting an ante from the additional call as though it were part of the live blind.

**Starting repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#turn-order)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#legal-actions)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#chips-owed).

<a id="s1-d"></a>

### S1-D: A preflop turn in the big blind

1. You owe zero extra counters because your posted 3 already matches the live preflop wager.

2. You may check or make a legal raise; increasing the live big-blind wager is a raise, even though nobody raised earlier.

3. Posting the forced blind did not use up your opportunity to act, so the dealer must wait for your decision.

Call: 3 minus 3 already paid = 0 more.

**Author's design note, for review:** This tests the big blind option when nothing extra is owed, including why an increase is still a raise rather than a first postflop bet.

**Likely misconception:** Treating a matched blind as a completed voluntary turn, or calling its increase a bet.

**Starting repair:** https://nolankido.com/poker/first-decisions/#turn-order

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#turn-order)

<a id="s1-e"></a>

### S1-E: A response to your flop bet

1. Calling adds 11 counters, bringing your total contribution on this flop from 5 to 16.

2. Your original 5 counts because it was paid on this same betting round; the announced 16 is a total, not 16 more.

3. The raise creates a new unmatched wager for you, so you may fold, call or legally reraise, but cannot check.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,7,14,9,2]`.

Call: 16 minus 5 already paid = 11 more.

**Author's design note, for review:** The learner starts as the bettor and must credit that same-street bet when the opponent raises.

**Likely misconception:** Adding the entire raise total again or assuming that an earlier bet removes the need for another decision.

**Starting repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#round-complete)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#legal-actions).

<a id="s1-f"></a>

### S1-F: The action returns on the flop

1. Facing the bet, your response families are fold, call or legal raise; another check cannot match it.

2. An earlier check keeps the hand live and does not surrender the right to make a legal raise when a later bet returns the action.

3. Calling adds 9 counters because you contributed zero on this flop; a check was not a payment.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,12,6,2]`.

Call: 9 minus 0 already paid = 9 more.

**Author's design note, for review:** This changes the prior action from a payment to a check and asks whether that action constrains the later legal response.

**Likely misconception:** Treating a check as either a contribution or a promise never to raise on that street.

**Starting repair:** https://nolankido.com/poker/first-decisions/#round-complete

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#round-complete)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#chips-owed)

<a id="s1-g"></a>

### S1-G: A river with a paired board

1. Your best five are two aces, two kings and the nine: two pair, aces and kings, with a nine kicker.

2. Only your private ace is used; the shared nine is a better fifth card than your four, and hold'em does not require both private cards.

3. You owe zero counters and may check or make a legal bet; keeping your hand live does not require betting.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[2,14,13,9]`.

Call: 0 minus 0 already paid = 0 more.

**Author's design note, for review:** This requires discarding an unused private card from the best five while separately recognizing a zero-price river option.

**Likely misconception:** Forcing both private cards into the hand or believing a player must bet to keep a checked-to hand live.

**Starting repair:** https://nolankido.com/poker/first-decisions/#best-five

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#best-five)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#best-five)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#legal-actions)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#chips-owed).

<a id="s1-h"></a>

### S1-H: Three players on the flop

1. You have paid 12 on the flop and face a total of 30, so a call adds 18 counters.

2. The later full raise returned action to you; having already called once did not finish the betting round.

3. You may fold, call or make a legal reraise, but cannot check while 18 remains unmatched.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,11,8,3]`.

Call: 30 minus 12 already paid = 18 more.

**Author's design note, for review:** This asks the learner to retain the latest same-street contribution through two separate increases of the wager.

**Likely misconception:** Paying only the first call or overlooking a new decision created by a later full raise.

**Starting repair:** https://nolankido.com/poker/first-decisions/#round-complete

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#round-complete)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#legal-actions)

<a id="s1-i"></a>

### S1-I: A preflop raise to 10

1. Calling costs 10 new counters because you have paid nothing on this preflop round.

2. Facing the raise, you may fold, call or make a legal reraise; checking cannot match the wager.

3. The raise from 3 to 10 increased the wager by 7, so a full reraise must reach at least 17 total, not merely add another big blind.

Call: 10 minus 0 already paid = 10 more.

**Author's design note, for review:** This separates a matching call from the minimum legal increase, using the last full raise increment rather than the blind size.

**Likely misconception:** Using the big blind as the minimum reraise increment after a larger full raise.

**Starting repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#check-min-raise)

<a id="s1-j"></a>

### S1-J: Five shared cards and a river bet

1. Your best five are the shared jack, ten, nine, eight and seven, a jack-high straight using zero private cards.

2. An unused private card cannot break a tie between identical best-five hands; there is no sixth-card tiebreaker.

3. Playing the board does not remove the wager: calling adds 8, and the response families are fold, call or legal raise, not check.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[4,11]`.

Call: 8 minus 0 already paid = 8 more.

**Author's design note, for review:** This tests zero private cards and the absence of a sixth-card tiebreaker without confusing hand construction with permission to check.

**Likely misconception:** Adding a private-card tiebreaker or treating a shared straight as an exemption from responding to a bet.

**Starting repair:** https://nolankido.com/poker/first-decisions/#best-five

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#best-five)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#ties)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#legal-actions)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#chips-owed).

<a id="s1-k"></a>

### S1-K: Two players at the river

1. You owe zero counters because no river wager has been made.

2. You may check or make a legal bet; a call or raise would require an existing wager.

3. If you check, both players have checked the final street and the hand proceeds to showdown; checking did not fold your cards.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,9,13,12,7]`.

Call: 0 minus 0 already paid = 0 more.

**Author's design note, for review:** This moves the no-wager decision to the final street and asks the learner to distinguish showdown from folding or dealing another card.

**Likely misconception:** Confusing a river check with surrendering the hand or expecting another shared card after the river.

**Starting repair:** https://nolankido.com/poker/first-decisions/#round-complete

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#checking-behind)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#legal-actions).

<a id="s1-l"></a>

### S1-L: A flop bet and a caller

1. Calling adds 6 counters, not 12; each player matches the current wager rather than the sum of other players' contributions.

2. Your response families are fold, call or legal raise; checking cannot match the bet.

3. A call here completes the flop round, but later streets can create new wagers and new costs before showdown.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,9,12,6,4]`.

Call: 6 minus 0 already paid = 6 more.

**Author's design note, for review:** This distinguishes the price of one multiway call, completion of the current round, and possible costs on later streets.

**Likely misconception:** Adding every opponent payment to the call price or treating a completed flop call as a ticket to every remaining card.

**Starting repair:** https://nolankido.com/poker/first-decisions/#chips-owed

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#chips-owed)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#legal-actions)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#round-complete)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/starting-hand-decisions/#price-and-action).

<a id="s2-a"></a>

### S2-A: Action after a button call

1. The big blind still has an initial decision; posting a blind was forced, not a choice to call the raise.

2. If the big blind raises, the earlier players still in the hand may face a new decision.

3. If next, cutoff, button and big blind remain, the big blind acts first after the flop, clockwise left of the button.

**Likely misconception:** Assuming the button completes preflop action by calling.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/starting-hand-decisions/#position)

<a id="s2-b"></a>

### S2-B: A two-player flop after a button raise

1. Posting the small blind does not itself use the player's preflop decision; their later call does.

2. With only small blind and button active on the flop, the small blind acts first and the button acts second.

3. Facing a check, the button may check or make a legal bet; there is no unmatched wager to call.

**Likely misconception:** Assuming the button is first on the flop or that a check requires a call.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#legal-actions)

<a id="s2-c"></a>

### S2-C: Two folds before the cutoff

1. The cutoff acts next, after the folds from under the gun and the hijack.

2. The button, small blind and big blind still have their initial decisions, in that order.

3. Those folds do not establish the private cards or future responses of the three players still behind you.

**Author's design note, for review:** This identifies the remaining initial decisions at the cutoff and separates observed folds from unknown actions still behind.

**Likely misconception:** Treating earlier folds as though the whole table had already yielded the pot or revealed the remaining hands.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/starting-hand-decisions/#position)

<a id="s2-d"></a>

### S2-D: A raiser and caller before the small blind

1. The small blind acts next, with the big blind still to take its initial decision.

2. Your call does not necessarily finish preflop action because the big blind can make a legal raise and return action to earlier players.

3. If all four see the flop, the small blind acts first after the fixed dealer button, followed by the big blind, cutoff and button.

**Author's design note, for review:** This places the learner between completed voluntary entries and an unacted blind, then asks how the order changes on the flop.

**Likely misconception:** Assuming a small-blind call closes action because several other players already contributed.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#price-and-action)
3. [Point 3 repair](https://nolankido.com/poker/starting-hand-decisions/#position)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#round-complete).

<a id="s2-e"></a>

### S2-E: A raise reaches the big blind

1. The big blind has the next decision; the cutoff already raised and every other seat has folded.

2. A call matches the only opponent's wager and completes this preflop round, assuming no new raise.

3. On the flop the big blind acts before the cutoff; the last initial preflop decision does not make you last on the next street.

**Author's design note, for review:** This contrasts a genuinely closing big-blind call with the learner's earlier position on the following street.

**Likely misconception:** Carrying the big blind's last preflop turn into the postflop order.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#price-and-action)
3. [Point 3 repair](https://nolankido.com/poker/starting-hand-decisions/#position)

<a id="s2-f"></a>

### S2-F: Three seats reach the flop

1. The hijack acts first, skipping the folded small blind, big blind and under-the-gun seats clockwise after the button.

2. The cutoff follows the hijack, and the button has the last initial flop decision.

3. The new street starts with the first remaining player clockwise after the dealer button, not automatically with the last preflop actor.

**Author's design note, for review:** This removes both blinds and the earliest remaining seat, requiring the learner to find the postflop starting point from the fixed button.

**Likely misconception:** Starting a new street at a folded blind or at the last preflop actor.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#turn-order)

<a id="s2-g"></a>

### S2-G: Two remaining seats with the button folded

1. The hijack acts first and the cutoff acts second, following the original clockwise order while skipping folded seats.

2. The cutoff has the last initial flop decision among the survivors, but does not become the dealer button during this hand.

3. Acting later lets the cutoff observe your action before deciding; it does not reveal your private cards or prove which holding you have.

**Author's design note, for review:** This distinguishes being last among the remaining players from occupying the button, while limiting what acting later actually reveals.

**Likely misconception:** Moving the dealer button after folds or treating position as knowledge of an opponent's private cards.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#turn-order)
3. [Point 3 repair](https://nolankido.com/poker/starting-hand-decisions/#position)

<a id="s2-h"></a>

### S2-H: A small-blind check on the flop

1. The big blind acts next, immediately after the small blind's check in the remaining clockwise order.

2. The button still has its initial flop decision after yours.

3. Your check would not end the round because the button still has a turn and may bet, returning a decision to the earlier checkers.

**Author's design note, for review:** This begins after one postflop action and requires preserving the unacted player behind rather than declaring two checks complete.

**Likely misconception:** Skipping an unacted seat or ending a multiway round before the last player has had an opportunity.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#round-complete)

<a id="s2-i"></a>

### S2-I: A flop bet before the cutoff

1. The cutoff responds next, and the button follows; the big blind has already made the opening flop action.

2. Being the preflop raiser does not change seat order or require an earlier postflop player to check.

3. If you call, the button can still make a legal raise, which can return action to you after the big blind responds.

**Author's design note, for review:** This puts the prior raiser after an opponent's flop bet and before another unacted player, separating betting history from seat order.

**Likely misconception:** Assuming the prior raiser owns the first postflop action or that calling before the button closes the round.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#turn-order)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#round-complete)

<a id="s2-j"></a>

### S2-J: Six players before the first decision

1. Under the gun acts first preflop, as the first seat clockwise after the big blind.

2. The remaining initial order is hijack, cutoff, button, small blind and big blind.

3. Neither forced blind post is a voluntary decision; both blind seats still have their initial opportunity to act.

**Author's design note, for review:** This starts before any voluntary action and requires reconstructing the complete initial order, including the unacted blind seats.

**Likely misconception:** Starting preflop at the dealer button or skipping the blinds because they already placed counters.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-decisions/#turn-order)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#turn-order)

<a id="s2-k"></a>

### S2-K: The action reaches the two blinds

1. The small blind acts now, followed by the big blind in this initial preflop order.

2. If both continue, the small blind also acts first on the flop, with the big blind second.

3. The button remains at its original seat; a six-player hand reduced to two survivors does not acquire the special starting order of a table dealt heads-up.

**Author's design note, for review:** This contrasts two surviving blinds from a six-player hand with the special order of a hand originally dealt to a heads-up table.

**Likely misconception:** Applying the heads-up button exception midway through a six-player hand.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/first-decisions/#turn-order)
3. [Point 3 repair](https://nolankido.com/poker/first-decisions/#turn-order)

<a id="s2-l"></a>

### S2-L: A raise and call before the cutoff

1. The cutoff acts next, after the under-the-gun raise and hijack call.

2. The button, small blind and big blind still follow, and a legal raise by one of them can create another decision for earlier players.

3. This pot already has a voluntary raise and call; an unopened-cutoff reference omits that action and does not describe this decision.

**Author's design note, for review:** This keeps the cutoff seat but replaces folds with a raise and call, requiring a different action context rather than a position-only label.

**Likely misconception:** Using an unopened-pot reference simply because the current player occupies the cutoff.

**Starting repair:** https://nolankido.com/poker/starting-hand-decisions/#position

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
2. [Point 2 repair](https://nolankido.com/poker/starting-hand-decisions/#position)
3. [Point 3 repair](https://nolankido.com/poker/starting-hand-decisions/#earlier-action)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/first-decisions/#round-complete).

<a id="s3-a"></a>

### S3-A: Private and shared cards on the flop

1. You currently have a pair of queens with jack, eight and two kickers.

2. Two clubs in your hand and two on the board make four clubs, not a completed five-card flush.

3. Checking is unavailable against a live bet; calling, folding and a legal raise are possible action families.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,12,11,8,2]`.

**Likely misconception:** Calling four cards a flush or checking through a bet.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
3. [Point 3 repair](https://nolankido.com/poker/first-flop-decisions/#whose-turn)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-b"></a>

### S3-B: Two suited private cards on the flop

1. Your best five are king, ten, nine, seven and two high: no pair.

2. You can use four hearts now, two private and two shared. Another heart could make a flush, but not guarantee winning.

3. No wager is outstanding, so you may check or make a legal bet; calling is not the current action.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,13,10,9,7,2]`.

**Likely misconception:** Confusing a promising draw with a made hand or calling a check.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
3. [Point 3 repair](https://nolankido.com/poker/first-flop-decisions/#whose-turn)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-c"></a>

### S3-C: A flop after a check

1. Your best five are jack, nine, seven, four and two of hearts, a jack-high flush.

2. All five available cards are hearts. The flush is already complete; another heart is not needed to make the category.

3. A completed flush is not proof that you are ahead. An opponent can hold higher hearts that make a stronger flush on this same board.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[5,11,9,7,4,2]`.

**Author's design note, for review:** Unlike the four-suit-card draws in A and B, this case requires recognizing a completed flush while keeping completion separate from a guaranteed lead.

**Likely misconception:** Treating every suited hand as unfinished, or treating a completed flush as a guaranteed winner.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#ties)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-flop-decisions/#shared-improvement).

<a id="s3-d"></a>

### S3-D: Jack and ten on a new flop

1. Your made hand is jack-high: jack, ten, nine, eight and two. Four consecutive ranks do not yet make a five-card straight.

2. A seven or a queen completes a straight on the next card. None is known, so the four sevens and four queens give eight physical completion cards.

3. Completing a straight is an improvement, not a guaranteed win. Opposing cards and any later shared card still affect the showdown.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,11,10,9,8,2]`.

**Author's design note, for review:** This replaces suit counting with an explicit two-ended straight completion count and separates improvement from winning.

**Likely misconception:** Calling four consecutive ranks a straight or treating eight completion cards as eight guaranteed winning cards.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#straight-completions)
3. [Point 3 repair](https://nolankido.com/poker/first-flop-decisions/#straight-completions)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-e"></a>

### S3-E: King and queen on a new flop

1. Your current hand is king-high: king, queen, ten, nine and three, with no completed straight.

2. A jack fills the gap between ten and queen, making nine, ten, jack, queen and king. All four jacks are outside the known cards.

3. An eight leaves eight, nine, ten, queen and king with the jack still missing. It does not produce five consecutive ranks.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,13,12,10,9,3]`.

**Author's design note, for review:** This contrasts with the two-ended case by requiring a missing internal rank and rejecting a plausible but incomplete sequence.

**Likely misconception:** Counting an endpoint card that leaves an internal gap as a straight completion.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#straight-completions)
3. [Point 3 repair](https://nolankido.com/poker/first-flop-decisions/#straight-completions)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-f"></a>

### S3-F: Ace and two with three shared cards

1. Ace, two, three, four and five already make a straight; no further card is needed to complete it.

2. The ace works below the two in this sequence, so this is a five-high straight, also called a wheel.

3. A six-high straight wins the comparison. The ace does not act as a high kicker or raise the height of this five-high straight.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[4,5]`.

**Author's design note, for review:** This adds a completed straight whose ace must be read low, rather than another unfinished suit draw.

**Likely misconception:** Treating an ace-low straight as ace-high or adding a kicker to compare straights.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#compare)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-g"></a>

### S3-G: Ace and eight after the flop is checked

1. Your current hand is ace-high: ace, king, eight, seven and two, with no pair or flush.

2. Three hearts are available. Both the turn and river would have to be hearts to make five; one turn heart would leave only four.

3. Checking behind ends this flop betting round, but a turn bet can create another payment decision. It does not secure both later cards without any further bet.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,14,13,8,7,2]`.

**Author's design note, for review:** This tests the two-card requirement of a backdoor flush possibility and connects it to the possibility of a later payment.

**Likely misconception:** Treating three suited cards as a one-card flush draw or a flop check as payment for all future cards.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
3. [Point 3 repair](https://nolankido.com/poker/first-flop-decisions/#paying-again)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-flop-decisions/#whose-turn).

<a id="s3-h"></a>

### S3-H: Pocket sixes and a queen on the flop

1. Your two private sixes and the shared six make three of a kind, with queen and two as the other cards.

2. You have two hearts available, both shared. Even two more hearts would give only four, so these private cards cannot make a heart flush on this board.

3. Three sixes are not a guaranteed lead. An opponent with two queens can have three queens, which outrank your three sixes.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[3,6,12,2]`.

**Author's design note, for review:** This adds three of a kind and a suit-count impossibility, rather than assuming every visible pair of suited cards gives the learner a flush draw.

**Likely misconception:** Overlooking the third matching rank or assuming two hearts on the board let every holding complete a heart flush.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#compare)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-i"></a>

### S3-I: Ace and jack on the final board

1. Your best five are three eights, ace and king: three of a kind with ace and king kickers.

2. The shared king is higher than your private jack, so the jack is omitted. You use only the private ace alongside four shared cards.

3. Candidate 1 also has eights with ace and king and ties you. Candidate 2 has eights with king and queen and loses; shared three of a kind does not force equal kickers.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[3,8,14,13]`.

Candidate evidence, each opponent compared with the learner's best five: 1: tie; 2: weaker.

**Author's design note, for review:** This moves the made-hand check to shared three of a kind, where one private card is displaced and opposing side cards determine ties.

**Likely misconception:** Using both private cards automatically or declaring a tie before comparing the side cards.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#compare)

<a id="s3-j"></a>

### S3-J: Pocket kings with three shared cards

1. Your five cards are king, king, king, eight and eight: kings full of eights, a full house.

2. The two eights are the pair needed alongside the three kings to make a full house; they are not unused kickers.

3. Full houses compare the rank of the three matching cards first. Three kings outrank three eights, so kings full of eights beats eights full of kings.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[6,13,8]`.

**Author's design note, for review:** This adds a full house and its comparison rule, extending the made-hand identification beyond the pair and high-card examples.

**Likely misconception:** Describing a full house as only three of a kind or comparing its pair before its three matching cards.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#compare)

Additional point 1 repair: [Related lesson explanation](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing).

<a id="s3-k"></a>

### S3-K: Pocket sevens on the final board

1. Your best five are ace, ace, king, king and seven: aces and kings with a seven kicker.

2. The two higher shared pairs take four places. Your pair of sevens is not used as a pair, but one seven improves the final side card above the shared two.

3. Candidate 1 uses a queen kicker with the same aces and kings and beats you. Candidate 2 uses a six kicker with those pairs and loses to your seven.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[2,14,13,7]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker.

**Author's design note, for review:** This requires rebuilding the final five after two shared pairs displace a private pair, with that private rank surviving only as a kicker.

**Likely misconception:** Keeping a private pair in the best five when two higher shared pairs replace it.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#counterfeited)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#counterfeited)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#compare)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s3-l"></a>

### S3-L: Ten and five on the final board

1. Your best five are ace, queen, ten, seven and two of hearts, an ace-high flush. The private ten joins four shared hearts; the private five is unused.

2. Candidate 1 joins its queen to the two shared queens and its seven to the shared seven, making queens full of sevens. That full house beats your flush.

3. Candidate 2 makes a lower flush, ace, queen, nine, seven and two of hearts. Your flush wins at the first different rank, ten versus nine. The completed flush therefore does not establish the result against every possible holding.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[5,14,12,10,7,2]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker.

**Author's design note, for review:** This uses one private heart and four shared hearts, then compares the flush with a full house assembled from two different private ranks and with a lower flush.

**Likely misconception:** Treating the completion of a flush as the same event as winning against any opponent.

**Starting repair:** https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/first-flop-decisions/#shared-improvement)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#ties)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#rankings).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/first-flop-decisions/#shared-improvement).

<a id="s4-a"></a>

### S4-A: River bet with ace and ten

1. You finish with one pair of aces, ten, nine and seven kickers. There are only four spades, not a flush.

2. A call adds 6; 18 + 6 + 6 = 30 total, making the call one fifth, or 20%, of that final pot.

3. That is the required pot share under the model, not your estimated equity or a recommendation. Opponent holdings and frequencies remain unknown.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,10,9,7]`.

River arithmetic: 18 + 6 + 6 = 30; additional call / final pot = 1/5.

**Likely misconception:** Using the pot price as if it were measured winning probability.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#river-reset

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/turn-and-river-decisions/#river-reset)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s4-b"></a>

### S4-B: River bet holding pocket sevens

1. Your best hand is a pair of sevens, with king, queen and nine kickers.

2. Calling costs 20 and makes a final 70-counter pot; 20/70 = 2/7, about 28.57%.

3. Pair strength alone does not determine the action. The call price must be compared with a reasoned range-based estimate, which is not supplied.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,7,13,12,9]`.

River arithmetic: 30 + 20 + 20 = 70; additional call / final pot = 2/7.

**Likely misconception:** Using hand category rather than a conditional price and range comparison.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/turn-and-river-decisions/#river-reset)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s4-c"></a>

### S4-C: Two low private cards at the river

1. The shared board supplies ace, king, queen, jack and ten, an ace-high straight. Neither private card is used.

2. Calling adds 6 and makes 24 + 6 + 6 = 36 counters. The call is 6/36 = 1/6, about 16.67%, of the final pot.

3. Both candidates tie your straight, giving you half the pot rather than an outright win. The 1/6 price is a break-even share for the call model, not your chance of winning outright.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[4,14]`.

River arithmetic: 24 + 6 + 6 = 36; additional call / final pot = 1/6.

Candidate evidence, each opponent compared with the learner's best five: 1: tie; 2: tie.

**Author's design note, for review:** Unlike the original one-pair river cases, this uses no private cards and separates a guaranteed split in the shown comparisons from winning the pot outright.

**Likely misconception:** Treating zero outright wins as zero pot share or using private cards to break a shared straight tie.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#shared-pot)

Additional point 3 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s4-d"></a>

### S4-D: King and jack facing a river bet

1. Your best five are king, king, jack, nine and six. Candidate 1 has a lower kicker and loses, Candidate 2 ties, and Candidate 3 makes three nines and beats you.

2. A call costs 10 and makes 20 + 10 + 10 = 40. The price is 10/40 = 1/4, or 25%, of the final pot.

3. One win example, one tie example and one loss example do not define the bettor's range or its frequencies. Equal weighting was not established, so the examples do not measure your equity or justify a call.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,11,9,6]`.

River arithmetic: 20 + 10 + 10 = 40; additional call / final pot = 1/4.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: tie; 3: stronger.

**Author's design note, for review:** This adds a tied candidate and tests whether the learner keeps unweighted outcome examples separate from the equity needed for the price comparison.

**Likely misconception:** Treating a list with one win, one tie and one loss as three equally likely outcomes.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#equal-weights)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff).

<a id="s4-e"></a>

### S4-E: Ace and two facing a river bet

1. Your best hand is ace, two, three, four and five, a five-high straight. The ace is low in this sequence.

2. Calling costs 21 and makes 42 + 21 + 21 = 84. The call is 21/84 = 1/4, or 25%, of the final pot.

3. Candidate 1 makes a seven-high straight and wins. Candidate 2 ties your five-high straight, so you receive half of 84, or 42 counters, in that comparison. A tie contributes a half share, not a whole-pot win.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[4,5]`.

River arithmetic: 42 + 21 + 21 = 84; additional call / final pot = 1/4.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: tie.

**Author's design note, for review:** This integrates ace-low straight ranking with the distinction between a tied pot share and an outright win.

**Likely misconception:** Comparing an ace-low straight as though its ace were high, or crediting a tied hand with the whole pot.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#shared-pot)

Additional point 3 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s4-f"></a>

### S4-F: Pocket eights on the final board

1. Your best five are ace, ace, king, king and eight. The board's two higher pairs replace your private pair; one eight remains as the kicker.

2. A call adds 15 and makes 60 + 15 + 15 = 90. The price is 15/90 = 1/6, about 16.67%, of that pot.

3. Candidate 1 beats you with a queen kicker, Candidate 2 loses with a seven kicker, and Candidate 3 ties with an eight kicker. The shared label "two pair" does not determine the outcome or supply the frequencies needed to assess a call.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[2,14,13,8]`.

River arithmetic: 60 + 15 + 15 = 90; additional call / final pot = 1/6.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker; 3: tie.

**Author's design note, for review:** This applies the price calculation after rebuilding two pair and shows why even the same named category can win, lose or tie.

**Likely misconception:** Keeping the pocket pair as one of the final pairs or treating matching hand-category names as equal strength.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#counterfeited)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#compare)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff).

<a id="s4-g"></a>

### S4-G: Two hearts facing a river bet

1. Your best five are ace, ten, nine, six and four of hearts, an ace-high flush.

2. Calling costs 40 and makes 40 + 40 + 40 = 120. The call is 40/120 = 1/3, about 33.33%, of the final pot.

3. Candidate 1 makes nines full of fours and beats your flush. Candidate 2 has the lower flush ace, nine, eight, seven and four and loses. Your completed flush alone does not identify the actual bettor's hand or its frequencies, so it does not justify the call.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[5,14,10,9,6,4]`.

River arithmetic: 40 + 40 + 40 = 120; additional call / final pot = 1/3.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker.

**Author's design note, for review:** This connects a completed flush on a paired board with a large river price, including one stronger and one weaker possible holding.

**Likely misconception:** Letting the success of a draw replace the range comparison required by a river call.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/first-flop-decisions/#shared-improvement)

Additional point 3 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff).

<a id="s4-h"></a>

### S4-H: Ace and seven on the final board

1. Your best five are four nines with an ace kicker. Candidate 1 has the same ace kicker and ties; Candidate 2 has a king kicker and loses. Your seven cannot break the ace-kicker tie.

2. Calling adds 16 and makes 48 + 16 + 16 = 80. The call fraction is 16/80 = 1/5, or 20%.

3. The tie returns half of 80, or 40 counters. That includes your new 16-counter call, so the return exceeds this decision's new payment by 24; it is not 40 counters of new profit.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[7,9,14]`.

River arithmetic: 48 + 16 + 16 = 80; additional call / final pot = 1/5.

Candidate evidence, each opponent compared with the learner's best five: 1: tie; 2: weaker.

**Author's design note, for review:** This adds shared four of a kind and asks the learner to distinguish a split-pot return from the net effect of the current call.

**Likely misconception:** Using a sixth card to break a tie or treating the returned pot share as entirely new profit.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#shared-pot)

<a id="s4-i"></a>

### S4-I: Ace and queen after the river arrives

1. Your final hand is ace-high: ace, king, queen, nine and six. Only four clubs are available, and a river call cannot bring another shared card.

2. A call costs 8 and makes 32 + 8 + 8 = 48. Its fraction is 8/48 = 1/6, about 16.67%.

3. Candidate 1 has only king-high and loses to your ace-high. Candidate 2 makes a pair of sevens and beats you. The missed draw still has showdown value against some hands, without establishing its equity against the actual bettor.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,14,13,12,9,6]`.

River arithmetic: 32 + 8 + 8 = 48; additional call / final pot = 1/6.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger.

**Author's design note, for review:** This extends the original missed-draw case from a surviving pair to an unpaired high-card hand that can still beat a specified opponent.

**Likely misconception:** Equating an unpaired missed draw with no showdown value or buying a nonexistent sixth community card.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/turn-and-river-decisions/#river-reset)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#ace-high)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s4-j"></a>

### S4-J: Nine and two on the final board

1. Your best five are ace, king, queen, nine and eight of hearts. The private nine replaces the shared four; the private two is unused.

2. Calling costs 7 and makes 28 + 7 + 7 = 42. The call is 7/42 = 1/6, about 16.67%, of the final pot.

3. Candidate 1 makes A-K-Q-J-8 of hearts and beats your A-K-Q-9-8 at jack versus nine. Candidate 2 makes A-K-Q-8-7 of hearts and loses at the first different rank, your nine versus its eight. A five-heart board does not force a tie when a private heart improves the best five.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[5,14,13,12,9,8]`.

River arithmetic: 28 + 7 + 7 = 42; additional call / final pot = 1/6.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker.

**Author's design note, for review:** This contrasts with the shared-straight split by requiring a private card to replace a weaker shared flush card.

**Likely misconception:** Playing all five shared flush cards automatically when a private card improves the flush.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#ties)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/hand-rankings/#ties)

<a id="s4-k"></a>

### S4-K: Pocket queens and a counter conversion

1. Your best five are queen, queen, ace, nine and seven: one pair of queens with ace, nine and seven kickers.

2. The original call costs 25 and makes 50 + 25 + 25 = 100. The price is 25/100 = 1/4, or 25%.

3. Doubling gives a 50-counter call into a final 200, still 1/4. Scaling the counter amounts preserves the fraction; neither calculation provides the opponent's holdings or frequencies needed to estimate your equity.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,12,14,9,7]`.

River arithmetic: 50 + 25 + 25 = 100; additional call / final pot = 1/4.

**Author's design note, for review:** This adds a scale comparison so the learner must explain a constant proportion and distinguish it from an equity estimate.

**Likely misconception:** Confusing a larger absolute call with a different proportional price or treating that price as measured equity.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)

<a id="s4-l"></a>

### S4-L: King and ten facing a larger river bet

1. Your best five are king, king, ten, nine and eight. Candidate 1 has a pair of aces and beats you; Candidate 2 has only king-high and loses; Candidate 3 has kings with a lower kicker and also loses.

2. Calling adds 18 and makes 9 + 18 + 18 = 45. The price is 18/45 = 2/5, or 40%, of the final pot.

3. The 40% is a required average pot share in this call model, not an observed bluff frequency. The example cards supply neither their betting frequencies nor the opponent's purpose, so a weaker holding is not by itself proof of a bluff.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,10,9,8]`.

River arithmetic: 9 + 18 + 18 = 45; additional call / final pot = 2/5.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker; 3: weaker.

**Author's design note, for review:** This uses both a weaker made hand and an unpaired hand to separate a winning showdown comparison from a claim about the bettor's intent or frequency.

**Likely misconception:** Reading a break-even pot share as the opponent's bluff rate or inferring betting intent from one weaker possible hand.

**Starting repair:** https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)

<a id="s5-a"></a>

### S5-A: Three candidate river holdings

1. Ah-Qs is impossible because you hold Ah; Qc-Qd is a weaker pair of queens; Kh-2d makes two pair, kings and twos, beating your one pair of kings.

2. A check alone does not reveal or exclude the stronger holding.

3. No candidate frequency was supplied, so this list cannot be treated as a probability distribution.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,14,9,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: weaker; 3: stronger.

**Likely misconception:** Allowing known cards in an opposing holding or treating a check as proof of weakness.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#equal-weights)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s5-b"></a>

### S5-B: A checked river and one later reveal

1. 9d-As is blocked by your own 9d; Ks-Kc makes a pair of kings stronger than your jacks; Ad-7c makes only ace-high and is weaker.

2. A check can be consistent with more than one holding, including a stronger one.

3. One revealed hand is one observation, not an established distribution for later opponents or decisions.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,11,9,8,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: stronger; 3: weaker.

**Likely misconception:** Generalizing a single showdown or ignoring physical card removal.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#one-reveal)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s5-c"></a>

### S5-C: Four river alternatives with aces

1. Candidate 1 is impossible because it repeats your ace of clubs. The other aces are different cards, so Candidates 2 and 4 are physically possible.

2. Your best five are A-A-J-T-6. Candidate 2 has A-A-K-T-6 and wins on the king kicker. Candidate 3 has Q-Q-A-T-6 and loses. Candidate 4 also has A-A-J-T-6 and ties.

3. An exact ace removes holdings containing that card, not all ace holdings. The check does not identify which legal holding is present or prove the opponent has no ace.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,11,10,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: stronger; 3: weaker; 4: tie.

**Author's design note, for review:** This case requires distinguishing one blocked ace from legal aces with different suits, then separating a kicker win from a tie.

**Likely misconception:** Treating one known suit of a rank as if every card of that rank were unavailable.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible)

Additional point 1 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#four-holdings).

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards).

<a id="s5-d"></a>

### S5-D: A river with two shared eights

1. Candidate 1 is impossible because the eight of diamonds is already on the board. A shared card excludes an opposing holding just as a private card does.

2. Your best five are 8-8-8-Q-7. Candidate 2 has 8-8-8-A-Q and wins with the ace kicker. Candidate 3 has Q-Q-8-8-J, and Candidate 4 has K-K-8-8-Q; both two-pair hands lose to your three eights.

3. Three legal rows establish three listed possibilities, not equal probabilities or observed checking rates. Which holdings reach this decision and choose to check remains a separate question.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[3,8,12,7]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: stronger; 3: weaker; 4: weaker.

**Author's design note, for review:** This case moves the blocked card to the board and requires comparing three of a kind with a higher-kicker three-of-a-kind hand and two different two-pair hands.

**Likely misconception:** Ignoring shared-card blockers or turning a list of legal holdings into equal checking frequencies.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#equal-weights)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible).

<a id="s5-e"></a>

### S5-E: Four hearts among the shared cards

1. Candidate 1 is impossible because it includes your ace of hearts. The queen, ten, nine and eight of hearts used in the other candidates are not among the known cards.

2. Your A-K-J-7-4 heart flush beats all three legal examples. Candidate 2 makes a K-Q-J-T-7 heart flush; Candidate 3 makes K-K-K-J-7; Candidate 4 makes a K-J-9-8-7 heart flush.

3. Holding the ace of hearts removes that exact card, not the whole suit. Neither the suit blocker nor these three comparisons supplies the checking frequency of any candidate.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[5,14,13,11,7,4]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: weaker; 3: weaker; 4: weaker.

**Author's design note, for review:** This case distinguishes a blocked ace-high flush from several legal lower flushes and a three-of-a-kind hand.

**Likely misconception:** Treating an ace of one suit as if it removed every flush in that suit or measured how often a flush checks.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#equal-weights)

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible).

<a id="s5-f"></a>

### S5-F: Four alternatives after a river check

1. Candidate 1 is impossible because the ace of spades is already a shared card. The other three candidates do not repeat any known card.

2. Your best hand and every legal candidate's best hand are the board's ace-high straight flush. All three legal candidates tie you; neither a pocket pair nor lower private spades improves this board.

3. The reveal establishes the opposing cards in that one observed hand. It does not establish a checking distribution on a different board or a general rule that checked hands are weak.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[8,14]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: tie; 3: tie; 4: tie.

**Author's design note, for review:** This case makes every legal comparison a board-playing tie, so a revealed pocket pair cannot be interpreted as a distinct showdown strength.

**Likely misconception:** Adding a private-card tiebreaker to a shared royal flush or generalizing one reveal to later boards.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#ties)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#one-reveal)

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#rankings).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible).

<a id="s5-g"></a>

### S5-G: Several rows with ace and king

1. All four candidates are legal. Your A-A-K-9-6 ties Candidates 1, 2 and 3, each of which also makes A-A-K-9-6. Candidate 4 has Q-Q-A-9-6 and loses.

2. Candidates 1, 2 and 3 are three different exact combinations of ace-king, despite sharing a broad hand label and the same final rank. Their repeated cards across alternative rows are allowed because the rows are not simultaneous holdings.

3. One-quarter per row would be an additional model assumption. Counting distinct combinations alone does not establish how often each reaches this river and checks.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,13,9,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: tie; 2: tie; 3: tie; 4: weaker.

**Author's design note, for review:** This case uses overlapping legal alternatives under one hand label to separate physical combination identity, equal final rank and likelihood.

**Likely misconception:** Confusing a broad hand label with one exact combination or assuming equally likely rows after an action.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/ranges-for-beginners/#four-holdings)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#equal-weights)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible).

<a id="s5-h"></a>

### S5-H: A note about an unseen folded hand

1. All four candidates remain physically possible. An unconfirmed guess about a folded ace of hearts is not an additional known card and cannot physically exclude Candidate 1.

2. Your Q-Q-J-9-7 loses to Candidate 1's A-A-Q-9-7, Candidate 3's K-K-Q-9-7 and Candidate 4's Q-Q-9-9-7. It beats Candidate 2's K-Q-T-9-7.

3. The check is an observed action, not an exposed holding. It does not identify one candidate or rule out the candidates that beat you.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,12,11,9,7]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker; 3: stronger; 4: stronger.

**Author's design note, for review:** This case tests whether an unsupported read about a folded player is incorrectly treated as physical card removal.

**Likely misconception:** Promoting a guess about unseen folded cards to a certain blocker or treating a check as a hand reveal.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible)

<a id="s5-i"></a>

### S5-I: Four alternatives after a river bet

1. Candidate 1 is impossible because it repeats your ten of spades. Its exclusion is certain from the cards, independently of any view about the opponent's betting choices.

2. Your best five are K-T-9-8-6. Candidate 2 makes A-K-Q-8-6 and Candidate 3 makes K-J-9-8-6, so both beat you. Candidate 4 makes K-8-7-6-4 and loses.

3. Removing one holding is not automatically favorable to a call. A useful comparison needs the remaining possible holdings and how often they reach this bet; the number removed does not supply those weights or your winning share.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,13,10,9,8,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: stronger; 3: stronger; 4: weaker.

**Author's design note, for review:** This case changes the observed action to a bet and asks why physical removal alone cannot determine whether calling improved.

**Likely misconception:** Assuming that holding any blocker automatically makes a call more favorable.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible)

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff).

<a id="s5-j"></a>

### S5-J: Paired kings with six and five

1. Candidate 1 repeats the board's king of clubs. Candidate 2 repeats your six of spades. Both are impossible; Candidates 3 and 4 are legal.

2. Your best five are K-K-6-6-5, not three pairs. Candidate 3 has K-K-K-J-6 and wins with three kings. Candidate 4 has K-K-6-6-Q and wins on the queen kicker.

3. Two physical exclusions do not establish the relative likelihood of the surviving holdings. Their chances after checking need a model or evidence about how they reach and take that action.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[2,13,6,5]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: impossible; 3: stronger; 4: stronger.

**Author's design note, for review:** This case combines one private and one shared exclusion with a best-five comparison where a third pair cannot serve as an extra hand category.

**Likely misconception:** Keeping three pairs in a five-card comparison or converting two blockers into an unsupported probability ratio.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#ties)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#equal-weights)

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible).

<a id="s5-k"></a>

### S5-K: One later reveal from a river bet

1. Your T-T-J-8-4 loses to Candidate 1's J-J-9-8-4 and Candidate 2's 8-8-8-J-4. It beats Candidate 3's A-K-J-8-4. All three holdings are physically possible.

2. The reveal establishes that Candidate 3 occurred in that one hand. It does not establish that the three candidates were equally likely at the betting decision or validate the rest of the proposed range.

3. One favorable showdown does not establish that calling was justified from the information available earlier. That judgment needs the call price and a defensible model of the possible betting hands and their frequencies.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,10,11,8,4]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: stronger; 3: weaker.

**Author's design note, for review:** This case asks the learner to separate a known later result from both the earlier range weights and the justification for the earlier decision.

**Likely misconception:** Using a favorable single showdown to validate an entire betting model and the prior call.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/ranges-for-beginners/#one-reveal)
3. [Point 3 repair](https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff)

Additional point 1 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards).

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#one-reveal).

<a id="s5-l"></a>

### S5-L: An earlier note and the final shared card

1. Candidate 1 must be removed because the two of clubs is now a known shared card. A range note must be updated when a new known card makes one of its exact holdings impossible.

2. Your best five are Q-J-9-8-7. Candidate 2 makes Q-Q-J-T-7 and wins. Candidate 3 also makes Q-J-9-8-7 and ties. Candidate 4 makes A-A-Q-J-7 and wins.

3. A legal combination is only physically possible. Its survival does not prove it followed the earlier action history or establish how often it checks at this decision.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,12,11,9,8,7]`.

Candidate evidence, each opponent compared with the learner's best five: 1: impossible; 2: stronger; 3: tie; 4: stronger.

**Author's design note, for review:** This case requires revising a previously written candidate list after a newly exposed river card while preserving a legal tie.

**Likely misconception:** Keeping a newly blocked holding in an old range note or equating physical possibility with reaching the decision.

**Starting repair:** https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/ranges-for-beginners/#remove-known-cards)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible)

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#ties).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-a"></a>

### S6-A: A checked river and two possible callers

1. Jd-Jh is a worse pair of jacks and is assumed to call, so it is a possible value target.

2. Ks-6d makes a pair of kings, ahead of your queens, and is also assumed to call.

3. Without frequencies and other possible responses, the comparison of betting with checking is underdetermined; no profitable-bet claim follows.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,12,13,9,5]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger.

**Likely misconception:** Concluding that one worse caller guarantees a good value bet.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

<a id="s6-b"></a>

### S6-B: A river bet with two possible responses

1. Kh-Kd makes one pair of kings, weaker than your pair of aces. 9c-9s makes three nines, stronger than your aces.

2. Folding the worse holding is not evidence of forcing a better hand to fold, and gives up that holding's possible call value.

3. Compare the outcomes of betting and checking across possible holdings and responses, with frequencies; one fold does not establish the better action.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,9,8,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger.

**Likely misconception:** Confusing a fold of a worse hand with profitable bluffing.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

<a id="s6-c"></a>

### S6-C: Three responses to a bet of six

1. Your best five are 9-9-J-7-4. Candidate 2 has 8-8-J-7-4 and is assumed to call, supplying a possible value target.

2. Candidate 1 has T-T-J-7-4 and beats you, so its assumed fold supplies a bluff target. Candidate 3 has Q-Q-J-7-4 and also beats you; its assumed call loses your new six counters.

3. These targets describe useful responses in different alternatives. Their existence alone does not compare betting with checking: the possible holdings and their frequencies at this decision are still needed.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,9,11,7,4]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker; 3: stronger.

**Author's design note, for review:** This case lets one proposed bet obtain a weaker call in one alternative and a stronger fold in another, while also retaining a losing call.

**Likely misconception:** Assuming that naming both a value target and a bluff target proves a bet beats checking.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#bluff)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-d"></a>

### S6-D: Three callers on a double-paired board

1. Your Q-Q-Q-J-J ties Candidate 1's Q-Q-Q-J-J. Candidate 2 has J-J-J-J-Q and beats you. Candidate 3 has Q-Q-J-J-A and loses.

2. Candidate 3 supplies a weaker call and Candidate 2 a losing call. Candidate 1 ties, so its call is not value from a worse hand: with no fees, equal five-counter contributions are split back and your share of the existing pot is unchanged.

3. The number of listed callers does not give their frequencies. A complete comparison with checking needs the possible holdings and how often each response occurs, including any alternatives not represented here.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[6,12,11]`.

Candidate evidence, each opponent compared with the learner's best five: 1: tie; 2: stronger; 3: weaker.

**Author's design note, for review:** This case introduces a tied full-house caller beside a losing quads caller and a weaker caller, requiring separate treatment of all three outcomes.

**Likely misconception:** Counting an equal hand as a weaker value caller or breaking a full-house tie with an unused private card.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#ties)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#value)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#rankings).

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#purpose).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-e"></a>

### S6-E: Three alternatives on a shared straight

1. Your best five are the board's ten-high straight. Candidate 1 makes a queen-high straight and beats you. Candidates 2 and 3 both play the ten-high board straight and tie you.

2. Candidate 2's fold wins the existing pot instead of splitting it, but does not make a stronger hand fold. Candidate 3's tied call supplies no value from a worse hand; equal new contributions are split back under these no-fee assumptions.

3. Candidate 1's call loses the ten-counter bet. The comparison must weigh that cost against the benefit of tied hands folding and any other responses. These example rows do not establish the needed frequencies.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[4,10]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: tie; 3: tie.

**Author's design note, for review:** This case distinguishes a tied fold that gains an otherwise shared pot from a tied call and a losing call against an improved straight.

**Likely misconception:** Treating every fold as a stronger-hand fold or every call as value, even when the board creates ties.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#ties)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#value).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-f"></a>

### S6-F: Three holdings and a proposed bet

1. Your A-A-T-9-7 beats Candidate 1's A-A-T-8-7 and Candidate 3's A-Q-J-T-7. It loses to Candidate 2's T-T-T-A-7.

2. Candidates 1 and 3 could be value targets if they call the proposed amount. Being weaker does not supply that call assumption; their responses, including folds or raises where allowed, must be modeled or supported.

3. Beating two listed hands does not establish a better bet. Checking already wins against those hands, and the comparison needs their frequencies and their responses to this amount, as well as the cost of responses from hands that beat you.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,14,10,9,7]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger; 3: weaker.

**Author's design note, for review:** This case deliberately leaves every response unspecified so the learner must distinguish conditional value targets from assumed callers.

**Likely misconception:** Inferring that a physically weaker holding will call even though no response assumption was supplied.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#value)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#purpose).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-g"></a>

### S6-G: A revised river bet amount

1. Your K-K-J-8-6 beats Candidate 1's K-K-T-8-6 and Candidate 3's A-K-Q-8-6. Candidate 2 has 8-8-8-K-6 and beats you.

2. Candidate 1 now folds, so it contributes no new counters to the larger bet. Tripling a bet does not triple payment from a hand whose assumed response changes from calling to folding.

3. The current call from Candidate 2 loses twelve new counters, while checking would already win against Candidates 1 and 3. Comparing the current bet with checking requires the full set of possible holdings, their frequencies and their responses to the twelve-counter bet; these examples alone do not establish that it improves on checking.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,11,8,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger; 3: weaker.

**Author's design note, for review:** This case changes the stated response of one candidate when the amount increases, so the learner must not preserve a smaller-bet caller assumption.

**Likely misconception:** Scaling value with bet size while ignoring a changed caller response.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#size)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#value).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-h"></a>

### S6-H: A call followed by a reveal

1. Your K-K-T-9-6 beats Candidate 1's K-K-9-8-6 and Candidate 3's Q-Q-K-9-6. Both are assumed to call and are possible value targets.

2. Candidate 2 has 9-9-9-K-6 and beats you, so its call loses the new bet. That single result does not erase the possible weaker callers or by itself disprove a value-bet intention.

3. The earlier comparison with checking depends on the possible holdings, responses and frequencies at that decision. A losing result does not establish a bad bet, just as naming weaker callers does not establish a profitable one.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,13,10,9,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger; 3: weaker.

**Author's design note, for review:** This case reveals a losing caller after a proposed value bet and asks the learner to retain the distinction between intention, expected comparison and one result.

**Likely misconception:** Judging the validity of a value-bet explanation solely from one losing showdown.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
2. [Point 2 repair](https://nolankido.com/poker/hand-rankings/#compare)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#size).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#one-reveal).

<a id="s6-i"></a>

### S6-I: A pair of twos and three responses

1. Your 2-2-A-K-Q loses to Candidate 1's J-J-A-K-Q and Candidate 2's A-A-K-Q-9. It beats Candidate 3's A-K-Q-9-7.

2. Candidate 1's assumed fold supports a bluff explanation because its jacks beat your twos. A bet can aim to fold a better hand even when the betting hand is a made pair.

3. Candidate 3 folds a hand you would beat by checking, while Candidate 2 calls and costs your new eight counters. An overall comparison needs the frequencies of these and other possible holdings and responses; one fold or a made pair does not establish the preferred action.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[1,2,14,13,12]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: stronger; 3: weaker.

**Author's design note, for review:** This case uses a small made pair as a possible bluffing hand, with one stronger fold, one weaker fold and one losing call.

**Likely misconception:** Assuming that every bet with a made pair must be for value, or that every fold shows a successful stronger-hand bluff.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#bluff)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#purpose).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-j"></a>

### S6-J: Two private hearts on the final board

1. You have A-K-J-8-6, an ace-high hand, not a flush. There are only four hearts among your seven cards and no further community card after the river.

2. Candidate 1 has Q-Q-K-8-6 and beats you, so its assumed fold supports a bluff explanation. Candidate 2 has A-K-9-8-6 and loses to your jack kicker. Candidate 3 has 8-8-8-K-6 and beats you.

3. Checking would still win against Candidate 2; its fold is not a stronger-hand fold. Candidate 3's call loses the new seven counters. The full comparison needs the frequencies of the possible holdings and responses, including the showdown value retained by checking.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[0,14,13,11,8,6]`.

Candidate evidence, each opponent compared with the learner's best five: 1: stronger; 2: weaker; 3: stronger.

**Author's design note, for review:** This case requires recognizing a missed flush draw while preserving an ace-high kicker win that matters when comparing betting with checking.

**Likely misconception:** Treating a missed river draw as having no possible showdown value or as still having a card to come.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/first-flop-decisions/#made-and-drawing)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#bluff)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 1 repair: [Related lesson explanation](https://nolankido.com/poker/turn-and-river-decisions/#river-reset).

Additional point 2 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-k"></a>

### S6-K: Two private ranks on a paired river

1. Your best five are K-K-8-8-7. Candidate 1 has K-K-A-Q-8 and loses. Candidate 2 has K-K-K-8-7 and wins. Candidate 3 has K-K-8-8-A and wins on the ace kicker; your second private rank does not add a third pair to the best five.

2. Candidate 3's assumed fold is a fold by a better two-pair hand, so it can support a bluff explanation. Calling your own hand two pair does not determine the bet's purpose.

3. Candidate 1's fold adds no new opposing counters and checking would already beat it. Candidate 2's call loses nine new counters. Compare those possibilities and the stronger fold using a full response model and frequencies before claiming betting improves on checking.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[2,13,8,7]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger; 3: stronger.

**Author's design note, for review:** This case makes a same-two-pair kicker loss the bluff target while a different candidate loses to checking and a third wins when calling.

**Likely misconception:** Using the two-pair label to skip kicker comparisons or to label every bet as value.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#ties)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 1 repair: [Compare the best five cards](https://nolankido.com/poker/hand-rankings/#compare).

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#bluff).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).

<a id="s6-l"></a>

### S6-L: A call with two listed explanations

1. Your J-J-T-T-9 beats Candidate 1's J-J-9-9-T and Candidate 3's A-K-J-T-9. Candidate 2 makes a jack-high straight, J-T-9-8-7, and beats you.

2. Both Candidate 1 and Candidate 2 call under the stated assumptions, yet one loses to you and one wins. The call therefore does not identify an exact hand or settle whether you are ahead.

3. A testable value intention is to get Candidate 1's worse two pair to call six counters. Candidate 2's call would beat you and must also be counted, and Candidate 3 folds a hand checking would beat. Their frequencies and any other possible responses remain necessary for comparing the bet with checking.

Computed high-hand vector (category 0 to 8, ranks 2 to 14): `[2,11,10,9]`.

Candidate evidence, each opponent compared with the learner's best five: 1: weaker; 2: stronger; 3: weaker.

**Author's design note, for review:** This case gives the same observed calling action to holdings on opposite sides of the showdown comparison, requiring an explicit value target instead of an information-only reason.

**Likely misconception:** Betting for information as though one observed call reveals a unique hand or guarantees that the caller is weaker.

**Starting repair:** https://nolankido.com/poker/betting-with-a-purpose/#purpose

**Repair by reasoning point:**

1. [Point 1 repair](https://nolankido.com/poker/hand-rankings/#compare)
2. [Point 2 repair](https://nolankido.com/poker/betting-with-a-purpose/#purpose)
3. [Point 3 repair](https://nolankido.com/poker/betting-with-a-purpose/#takeaway)

Additional point 2 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#known-and-possible).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/betting-with-a-purpose/#value).

Additional point 3 repair: [Related lesson explanation](https://nolankido.com/poker/ranges-for-beginners/#equal-weights).
