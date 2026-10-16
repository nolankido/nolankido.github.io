# Poker Foundations: independent teaching review

Material commit: `74f438934beca0ab2563af0dfe279923d588f0f1`.
Packet fingerprint: `7449fd7a4632eace38d9e5c5b3d9d4e1554c0abf6febd97e61c5909aa5fe53fa`.
Prepared 2026-10-16 UTC. **Human review: pending.**

Read README.md for the review protocol. Work through the prompts before opening answer-key.md. Use reference-text.md to inspect the complete source-article text. This is a reviewer packet with fictional examples, not a beginner outcome study.

Card codes: T=ten, J=jack, Q=queen, K=king, A=ace; s=spades, h=hearts, d=diamonds, c=clubs. Candidates are separate alternatives.

## S1. Cards, legal actions and additional payment

Full source: https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-decisions.html
Live lesson: https://nolankido.com/poker/first-decisions/#course-first-pass-title

### Accuracy and misconception criteria

- **S1.1**: Construct exactly five available cards; distinguish private cards from the shared board.
  - Watch for: Uses six cards, requires both private cards, or names a card that is unavailable.
- **S1.2**: Count an additional call as the current wager minus this round's contribution.
  - Watch for: Subtracts an earlier round's payment or adds an already posted blind twice.
- **S1.3**: Explain when checking, betting, calling, folding or a legal raise is available under the stated assumptions.
  - Watch for: Checks past an unmatched bet or treats every contribution as a new raise.

Reviewer probe: If the learner says the right number but subtracts preflop chips from a flop call, would the feedback expose that reason?
Cross-check tasks: L1-A, A-preflop, A-river, B-preflop, B-flop, G-call, G-raise, G-river.
Reference IDs: R1, R2, R3.

### Current short explanation

Your two private cards belong to you. The board is shared by everyone still in the hand: three cards on the flop, a fourth on the turn and a fifth on the river. On the flop, those five available cards make your current hand. On the turn and river, choose the best five again. At showdown, when all five shared cards are out, you may use zero, one or two private cards.

A check keeps your hand without paying when you owe nothing. A call matches a wager; a raise increases it. Folding gives up your claim to the pot. On your turn facing a bet, with enough chips and raising permitted, you may fold, call or raise. You cannot check past the bet.

Count a call using this betting round only: the current total wager minus what you already paid on this round. Payments on an earlier round stay in the pot. The amount owed says what a call costs, not whether it is a good decision.

### L1-W: worked model

It is your turn on the flop. The opponent bets 4. You have paid nothing on this round and have ample counters. Both short-lesson examples exclude antes, fees and all-ins.

- Your private cards: Qh, Jc
- Shared flop: Qs, 8d, 3s

### L1-A: independent attempt

A different hand reaches this flop. You paid 6 preflop. The opponent now bets 7; you have paid nothing on this new round. It is your turn, with ample counters and raising permitted.

- Your private cards: Qh, Jc
- Shared flop: Qd, 9c, 5h

Name your best five. How many additional counters would a call add? Explain whether checking is available and whether the earlier 6 reduces the call.

Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.

## S2. Position and players still to act

Full source: https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/starting-hand-decisions.html
Live lesson: https://nolankido.com/poker/starting-hand-decisions/#course-first-pass-title

### Accuracy and misconception criteria

- **S2.1**: Follow the six-player initial preflop order through button, small blind and big blind.
  - Watch for: Says the button ends preflop or counts posting a blind as taking an initial turn.
- **S2.2**: Rebuild postflop order from remaining seats clockwise after the button.
  - Watch for: Carries preflop order into the flop or moves blinds after other players fold.
- **S2.3**: Explain how earlier action, price and relevant stacks change a situation with the same two cards.
  - Watch for: Uses a hand label or seat alone to prescribe an action without those facts.

Reviewer probe: Can the text distinguish two players remaining from a hand originally dealt heads-up? The examples remain six-player deals.
Cross-check tasks: L2-A, A-preflop, A-turn, B-preflop, G-position.
Reference IDs: R1, R3.

### Current short explanation

The button marks the dealer position. At a table of three or more players, preflop action starts after the big blind and proceeds clockwise. In a six-player game, the initial order is first seat, next seat, cutoff, button, small blind, big blind. The cutoff is the seat immediately before the button.

After the flop, the first remaining player clockwise after the button acts first. The button therefore acts after a blind on the flop, but the blinds still have initial turns after the button preflop. A later raise can give earlier players another decision.

Describe your seat, earlier action, price and relevant stacks before using a hand label or chart. Suited means your two cards share a suit; it does not establish that playing them is best. These examples use six players who began with 100 counters each, blinds 1/2 and no ante or fees.

### L2-W: worked model

The first seat, next seat and cutoff fold. You are on the button with queen-jack of spades. The small blind has posted 1 and the big blind 2. Neither blind has taken its initial turn.

- Your private cards: Qs, Js
- Six seats in order: first seat, next seat, cutoff, button, small blind, big blind.
- Hero seat index (zero-based): 3; paid this round: [0, 0, 0, 0, 1, 2]; folded: [0, 1, 2].

### L2-A: independent attempt

You now sit in the small blind with the same private cards. The first two seats fold, the cutoff raises to 6, and the button calls 6. Your posted small blind is 1. The big blind has not yet acted.

- Your private cards: Qs, Js
- Six seats in order: first seat, next seat, cutoff, button, small blind, big blind.
- Hero seat index (zero-based): 4; paid this round: [0, 0, 6, 6, 1, 2]; folded: [0, 1].

How much more would your call add? Who still has an initial decision after you? Explain two ways this situation differs from the worked example, despite the same private cards.

Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.

## S3. Made hand, draw and observed action

Full source: https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-flop-decisions.html
Live lesson: https://nolankido.com/poker/first-flop-decisions/#course-first-pass-title

### Accuracy and misconception criteria

- **S3.1**: Name the current best five and count the suit cards actually available.
  - Watch for: Calls four suited cards a completed flush or overlooks a made pair beside a draw.
- **S3.2**: Explain that improving and winning are different claims.
  - Watch for: Treats a completed draw as a guaranteed win regardless of later board or opposing cards.
- **S3.3**: Read a check or bet as an action and explain the resulting options.
  - Watch for: Treats a check as proof of weakness or allows checking again past a new bet.

Reviewer probe: Would a confident answer of 'a flush' be repaired by counting the exact hearts or spades rather than only revealing the category?
Cross-check tasks: L3-A, A-flop, B-flop, B-turn, G-flop.
Reference IDs: R1, R2.

### Current short explanation

A made hand describes what your cards make now. A draw describes cards that could improve it. You can have both. A pair needs two cards of one rank; a flush needs five of one suit. Four cards of one suit are not a completed flush.

Count distinct cards, including your private cards and the shared flop. Then describe the action separately. A check does not reveal a weak hand, and a possible improvement does not guarantee the winning hand. These scenes assume it is your turn, ample counters, no all-ins and raising permitted.

### L3-W: worked model

You are on the button. Only you and the big blind reached the flop. The big blind checks to you; nobody has bet on this round.

- Your private cards: Ah, Th
- Shared flop: Tc, 7h, 2h

### L3-A: independent attempt

In another heads-up flop, the opponent bets 5. You have paid nothing on this round.

- Your private cards: Ks, Qs
- Shared flop: Kd, 8s, 3s

Name your best five and your draw separately. Is checking available? Does another spade guarantee that you win?

Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.

## S4. Rebuild the hand and distinguish price from equity

Full source: https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/turn-and-river-decisions.html
Live lesson: https://nolankido.com/poker/turn-and-river-decisions/#course-first-pass-title

### Accuracy and misconception criteria

- **S4.1**: Rebuild the best five after the turn and river, including changed kickers and missed draws.
  - Watch for: Keeps an obsolete kicker, waits for a card after the river or awards the wrong showdown winner.
- **S4.2**: For the stated final heads-up call, divide the additional call by the pot after calling.
  - Watch for: Omits the caller's extra chips from the denominator or treats the bet size alone as the price.
- **S4.3**: State the no-fee, no-side-pot, no-prize-effect assumptions and distinguish required pot share, including ties, from estimated equity.
  - Watch for: Treats 20% or 25% as a measured winning probability or an automatic instruction to call.

Reviewer probe: Can the reviewer derive e(P+C)-C = 0 and explain why that prices this call without ranking every available action?
Cross-check tasks: L4-A, A-turn, A-river, B-turn, B-river, G-river, G-showdown.
Reference IDs: R1, R2, M1.

### Current short explanation

The turn is the fourth shared card; the river is the fifth and last. Rebuild your best five when a card arrives. A missed draw can leave a pair, but no later community card can complete a draw once the river is out.

For a heads-up river call that ends betting, the break-even pot share in chips is the additional call divided by the pot after your call. This is a price. Your expected share against possible opposing hands, including ties, is a different question.

Both scenes assume a fictional cash game, ample chips, no fees, no side pots and no tournament payout effects. A fold or legal raise may also be available; pricing a call does not compare every action.

### L4-W: worked model

The opponent bets 12 into a river pot of 24. You have paid nothing on this round.

- Your private cards: Jh, Th
- Shared river board: Jc, 8h, 3h, 2d, 5s

### L4-A: independent attempt

A different river pot contains 36 before the opponent bets 12. You have paid nothing on the river; a call ends betting under the same assumptions.

- Your private cards: Qs, Js
- Shared river board: Qh, 9s, 4s, 2c, 6d

List the best five. Did the spade draw arrive? Give the current pot, the pot after calling and the break-even share. What is still missing before recommending a call?

Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.

## S5. Known cards, possible holdings and frequencies

Full source: https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/ranges-for-beginners.html
Live lesson: https://nolankido.com/poker/ranges-for-beginners/#course-first-pass-title

### Accuracy and misconception criteria

- **S5.1**: Remove candidates that reuse a known exact card and compare each remaining candidate separately.
  - Watch for: Allows a duplicate card or combines mutually exclusive candidates into one physical deal.
- **S5.2**: Compare legal candidates with the hero's best five without assigning unsupported frequencies.
  - Watch for: Makes all listed candidates equally likely or calls a small candidate list a complete range.
- **S5.3**: Separate a check or one showdown reveal from an estimate of how often a holding takes that action.
  - Watch for: Uses one revealed hand or a checked turn to establish or eliminate an entire frequency model.

Reviewer probe: If two possible models allow the same observed hand, does the explanation keep both possible until more evidence is supplied?
Cross-check tasks: L5-A, A-turn, A-river, B-river, G-showdown.
Reference IDs: R1, R2, M2.

### Current short explanation

A range is a model of the hands an opponent could hold in a situation. First remove exact cards you already know. A card cannot be in your private hand, on the board and in an opponent's hand at the same time.

Then separate possibility from frequency. A legal holding may be possible without being common. A check is an observed action; the cards and frequencies behind it remain uncertain. Listing three candidates does not give each a one-third chance, and these candidate lists are not complete ranges.

### L5-W: worked model

The opponent checks to you on the river. Consider the three exact candidate holdings below.

- Your private cards: Ah, Td
- Shared river board: Ts, 8c, 5h, 3d, 2s
- Candidate A: Ah, Kh
- Candidate B: Ac, Kd
- Candidate C: Th, Tc

### L5-A: independent attempt

In another river hand, the opponent checks. Consider these different exact candidates.

- Your private cards: Ks, Qh
- Shared river board: Qs, 9d, 6c, 4s, 2h
- Candidate A: Ks, Jh
- Candidate B: Kh, Kc
- Candidate C: Jd, Td

Which candidate is impossible? Can a legal candidate beat your queens? Does a candidate being legal, or appearing once at showdown, establish how often it checks?

Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.

## S6. Bet purpose, alternatives and outcome bias

Full source: https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/betting-with-a-purpose.html
Live lesson: https://nolankido.com/poker/betting-with-a-purpose/#course-first-pass-title

### Accuracy and misconception criteria

- **S6.1**: Identify worse callers for a value argument and better folders for a bluff argument.
  - Watch for: Calls any winning bet value or any losing hand a profitable bluff.
- **S6.2**: Compare betting with checking using frequencies, amounts, other responses and future action where relevant.
  - Watch for: Treats naming one worse caller or holding a strong category as a complete betting verdict.
- **S6.3**: Keep the scripted result separate from the quality of the earlier decision.
  - Watch for: Uses a win or loss as proof of the best action or implies profitable-play readiness from this course.

Reviewer probe: Can the restricted response assumptions support the stated comparison without pretending to describe an actual player's measured range?
Cross-check tasks: L6-A, A-flop, B-turn, A-river, B-river, G-flop, G-showdown.
Reference IDs: M1, M2.

### Current short explanation

A value-bet explanation needs worse hands that will call. A bluff explanation needs better hands that will fold. A hand's label or one winning result is not a complete reason to bet. Different opposing hands may respond differently.

When the opponent checks to you last to act on the river, checking takes the hand to showdown without a new wager. Compare that option with betting. The frequency of each opposing hand and its response matter, including possible raises.

Both examples use fictional heads-up river hands, ample counters, no fees or side pots and the supplied response assumptions. They teach questions to ask; the site has not measured any player's actual responses.

### L6-W: worked model

The opponent checks to you. Suppose, for this restricted example, a worse pair of nines always folds to your proposed bet and a better hand of three eights always calls. These are two illustrative candidates, not an estimated range.

- Your private cards: Js, Td
- Shared river board: Th, 8c, 5d, 3s, 2c
- Worse: pair of nines: 9s, 9d
- Better: three eights: 8s, 8d

### L6-A: independent attempt

In a different hand, the opponent checks to you last to act. For a proposed bet of 4, suppose the worse eights call and the better jacks also call. No frequency or complete range has been supplied.

- Your private cards: 9h, 8h
- Shared river board: 9c, 7s, 4d, 2c, Js
- Candidate: pair of eights: 8c, 8d
- Candidate: pair of jacks: Jc, Td

Which candidate could pay a value bet, and which beats you? What changed from the worked example? What is still missing before saying betting is better than checking?

Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.

## Hand A: follow the hand from the button

Six players start with 100 counters each. Blinds 1/2; no antes, fees, all-ins, side pots or prize effects. Seats: first seat, next seat, cutoff, button, small blind, big blind.
Hero private cards: Ah, Th.

### A-preflop

You are on the button. The first seat, next seat and cutoff fold. The small blind posted 1 and the big blind posted 2. It is your turn; neither blind has taken a turn yet.
Board available now: none.
Cumulative paid by seat: [0, 0, 0, 0, 1, 2]. Current-round hero payment: 0; current wager: 2.


How much would calling add? If you instead raise to a total of 6, how much do you add, and who still has an initial decision? Explain why the button does not end this preflop round.

Count the additional chips. Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

Follow the players still to act. Snapshot repair: [starting-hand-decisions #position](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/starting-hand-decisions.html#L17); [readable exhibit](reference-text.md#ref-starting-hand-decisions-position). Live navigation: https://nolankido.com/poker/starting-hand-decisions/#position

### A-flop

Scripted continuation: you raise to 6, the small blind folds and the big blind calls by adding 4. The pot is 13. The flop is dealt, and the big blind checks to you.
Board available now: Tc, 7h, 2h.
Cumulative paid by seat: [0, 0, 0, 6, 1, 6]. Current-round hero payment: 0; current wager: 0.


Name your current best five and a possible improvement. Is checking available? If you bet for value, which response would help, and what would you need to compare the bet with checking?

Separate the made hand and draw. Snapshot repair: [first-flop-decisions #made-and-drawing](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-flop-decisions.html#L5); [readable exhibit](reference-text.md#ref-first-flop-decisions-made-and-drawing). Live navigation: https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

Explain the response a value bet needs. Snapshot repair: [betting-with-a-purpose #value](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/betting-with-a-purpose.html#L12); [readable exhibit](reference-text.md#ref-betting-with-a-purpose-value). Live navigation: https://nolankido.com/poker/betting-with-a-purpose/#value

### A-turn

Scripted continuation: you bet 4 on the flop and the big blind calls 4. The pot becomes 21. The turn is the four of clubs. The big blind checks to you again.
Board available now: Tc, 7h, 2h, 4c.
Cumulative paid by seat: [0, 0, 0, 10, 1, 10]. Current-round hero payment: 0; current wager: 0.


Rebuild your best five. Has the heart flush arrived? What does the opponent's check establish, and what does it leave unknown? If you both check, who acts first on the river?

Review what the new card changes. Snapshot repair: [turn-and-river-decisions #turn-reset](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/turn-and-river-decisions.html#L5); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-turn-reset). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#turn-reset

Separate observed action from assumptions. Snapshot repair: [ranges-for-beginners #known-and-possible](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/ranges-for-beginners.html#L5); [readable exhibit](reference-text.md#ref-ranges-for-beginners-known-and-possible). Live navigation: https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

### A-river

Scripted continuation: you check the turn. The river is the nine of spades. From the pot of 21, the big blind bets 7. The displayed pot now includes that bet. It is your turn.
Board available now: Tc, 7h, 2h, 4c, 9s.
Cumulative paid by seat: [0, 0, 0, 10, 1, 17]. Current-round hero payment: 0; current wager: 7.

- Candidate A: Ah, Kd
- Candidate B: Qh, Jh
- Candidate C: 9c, 9d

Name your best five and what happened to the draw. Which candidate conflicts with a known card? Which legal candidate is weaker and which is stronger? Count the call and final pot, calculate the break-even equity, and state what is still missing before judging a call. Is checking available?

Separate call price from equity. Snapshot repair: [turn-and-river-decisions #catching-a-bluff](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/turn-and-river-decisions.html#L28); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-catching-a-bluff). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

Check candidates before assigning frequencies. Snapshot repair: [ranges-for-beginners #known-and-possible](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/ranges-for-beginners.html#L5); [readable exhibit](reference-text.md#ref-ranges-for-beginners-known-and-possible). Live navigation: https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

## Hand B: return later from the small blind

Six players start with 100 counters each. Blinds 1/2; no antes, fees, all-ins, side pots or prize effects. Seats: first seat, next seat, cutoff, button, small blind, big blind.
Hero private cards: Kh, Qh.

### B-preflop

You are the small blind and posted 1. The big blind posted 2. The first two seats fold, the cutoff raises to 6 and the button folds. It is your turn. The big blind has not taken a turn.
Board available now: none.
Cumulative paid by seat: [0, 0, 6, 0, 1, 2]. Current-round hero payment: 1; current wager: 6.


How many additional chips would calling cost? Who still has an initial decision? If only you and the cutoff reach the flop, who acts first after the flop? Explain what changed from the button hand.

Count only the additional chips. Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

Rebuild the action order. Snapshot repair: [starting-hand-decisions #position](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/starting-hand-decisions.html#L17); [readable exhibit](reference-text.md#ref-starting-hand-decisions-position). Live navigation: https://nolankido.com/poker/starting-hand-decisions/#position

### B-flop

Scripted continuation: you call by adding 5 and the big blind folds. The pot is 14. On the flop you check, and the cutoff bets 7. The pot now includes the bet.
Board available now: Qd, 8h, 3h.
Cumulative paid by seat: [0, 0, 13, 0, 6, 2]. Current-round hero payment: 0; current wager: 7.


Name your best five and draw. How much would a call add? Can you check again? Explain why the chips you paid preflop do or do not reduce this call.

Name the current hand and draw. Snapshot repair: [first-flop-decisions #made-and-drawing](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-flop-decisions.html#L5); [readable exhibit](reference-text.md#ref-first-flop-decisions-made-and-drawing). Live navigation: https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

Reset the contribution for a new round. Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

### B-turn

Scripted continuation: you call 7. The pot is 28. The turn is the five of hearts, and you act first. No one has bet this round.
Board available now: Qd, 8h, 3h, 5h.
Cumulative paid by seat: [0, 0, 13, 0, 13, 2]. Current-round hero payment: 0; current wager: 0.

- A possible worse caller: Jh, Th
- A possible better caller: Ah, Jh

Name your best five now. Compare the two possible holdings with yours. If both would call a proposed bet, does naming the worse caller alone establish a good value bet? What else would you compare with checking?

Rebuild the hand when a draw arrives. Snapshot repair: [turn-and-river-decisions #turn-reset](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/turn-and-river-decisions.html#L5); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-turn-reset). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#turn-reset

Compare the responses with checking. Snapshot repair: [betting-with-a-purpose #value](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/betting-with-a-purpose.html#L12); [readable exhibit](reference-text.md#ref-betting-with-a-purpose-value). Live navigation: https://nolankido.com/poker/betting-with-a-purpose/#value

### B-river

Scripted continuation: you check the turn and the cutoff checks behind. The river is the two of spades. You check; the cutoff bets 14 into the pot of 28. It is your turn again.
Board available now: Qd, 8h, 3h, 5h, 2s.
Cumulative paid by seat: [0, 0, 27, 0, 13, 2]. Current-round hero payment: 0; current wager: 14.

- Candidate A: Qh, Jd
- Candidate B: Ah, Jh
- Candidate C: Jh, Th

Name your best five. Classify the candidates as impossible, legal and stronger, or legal and weaker. Did the checked turn rule out the stronger hand? Count the call and final pot, calculate the break-even equity and explain why the result will not measure the opponent's range.

Calculate the changed call price. Snapshot repair: [turn-and-river-decisions #catching-a-bluff](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/turn-and-river-decisions.html#L28); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-catching-a-bluff). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#catching-a-bluff

Keep possibility separate from frequency. Snapshot repair: [ranges-for-beginners #known-and-possible](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/ranges-for-beginners.html#L5); [readable exhibit](reference-text.md#ref-ranges-for-beginners-known-and-possible). Live navigation: https://nolankido.com/poker/ranges-for-beginners/#known-and-possible

## Guided hand: inspect the recognition choices and feedback

Hero: Ah, Jh. Read each scene before the key; later cards and the opponent are revealed only where the scene does so.

### G-position

Six players start with 100 counters each. The small blind posts 1 and the big blind posts 2. There is no ante, fee or side pot. Three players fold. You are on the button, the seat marked by the dealer marker. Both blinds still have their first decisions.
After your initial action on the button, who still has an initial decision?

- **A.** Nobody; the flop must come next.
- **B.** The small blind and the big blind.
- **C.** Only the big blind.

Snapshot repair: [starting-hand-decisions #position](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/starting-hand-decisions.html#L17); [readable exhibit](reference-text.md#ref-starting-hand-decisions-position). Live navigation: https://nolankido.com/poker/starting-hand-decisions/#position

### G-call

For this scripted practice hand, you raise to 6 total and the small blind folds. The big blind already posted 2 on this betting round and faces your total wager of 6. The current pot is your 6, the folded small blind's 1 and the big blind's 2: 9.
How many additional counters does the big blind need to call?

- **A.** 6 more.
- **B.** 8 more.
- **C.** 4 more.

Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

### G-flop

The big blind calls. The flop, the first three shared cards, is jack of spades, seven of hearts and two of hearts. The big blind checks, meaning it makes no bet. Your private cards remain ace of hearts and jack of hearts.
Which description fits your cards on this flop?

- **A.** A pair of jacks and a heart-flush draw.
- **B.** A completed heart flush.
- **C.** Only a draw, with no made hand.

Snapshot repair: [first-flop-decisions #made-and-drawing](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-flop-decisions.html#L5); [readable exhibit](reference-text.md#ref-first-flop-decisions-made-and-drawing). Live navigation: https://nolankido.com/poker/first-flop-decisions/#made-and-drawing

### G-raise

The scripted line continues: you bet 4 and the big blind raises to 12 total on the flop. The pot is now the previous 13 plus your 4 plus the opponent's 12: 29. Your preflop contribution belongs to an earlier round.
How many more counters would a flop call add?

- **A.** 12 more.
- **B.** 8 more.
- **C.** 16 more.

Snapshot repair: [first-decisions #chips-owed](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/first-decisions.html#L28); [readable exhibit](reference-text.md#ref-first-decisions-chips-owed). Live navigation: https://nolankido.com/poker/first-decisions/#chips-owed

### G-river

You call the extra 8. The turn is nine of clubs; both players check, so nobody pays more on that round. The river is four of diamonds, the last shared card. The big blind bets 10 into the pot of 37, making the current pot 47.
Which statement is justified before you decide?

- **A.** You have a heart flush and may check.
- **B.** Your draw can wait for one more community card.
- **C.** You have a pair of jacks; a call would add 10.

Snapshot repair: [turn-and-river-decisions #river-reset](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/turn-and-river-decisions.html#L11); [readable exhibit](reference-text.md#ref-turn-and-river-decisions-river-reset). Live navigation: https://nolankido.com/poker/turn-and-river-decisions/#river-reset

### G-showdown

For the final scripted action, you call 10. The big blind reveals queen of hearts and jack of diamonds. Compare each player's best five. This is one fictional ending, not evidence about how frequently an actual opponent bluffs or bets for value.
Which conclusion follows from this ending?

- **A.** You win the pot of 57 and gain 29 overall; that result alone does not grade the earlier call.
- **B.** You make a profit of 57.
- **C.** Winning proves every earlier bet and call was best.

Snapshot repair: [ranges-for-beginners #one-reveal](https://github.com/nolankido/nolankido.github.io/blob/74f438934beca0ab2563af0dfe279923d588f0f1/_source/poker/ranges-for-beginners.html#L37); [readable exhibit](reference-text.md#ref-ranges-for-beginners-one-reveal). Live navigation: https://nolankido.com/poker/ranges-for-beginners/#one-reveal
