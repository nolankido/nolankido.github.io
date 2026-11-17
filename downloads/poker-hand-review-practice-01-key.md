# Checking key: fictional hand-review practice 01

**Open this only after completing the [outcome-blind practice case](https://nolankido.com/downloads/poker-hand-review-practice-01.md).** This is an arithmetic and evidence-quality key, not an answer to "what is the best poker play?" The case is invented, and no actual opponent hand, showdown, future board, tournament payout or solved strategy is supplied.

## 1. Situation: classify each claim

| Claim | Correct label | Reason |
| --- | --- | --- |
| Hero begins with 80,000 before forced posts | **Given fictional fact** | It is stipulated in the question, not verified from an actual hand |
| Hero's chips behind after the forced posts | **Derived arithmetic** | Subtract the stipulated 4,000 live blind and 4,000 dead big-blind ante |
| Cutoff's true opening or calling range | **Unknown** | Two observed raises do not establish a range |
| Cutoff folds to a reraise to 24,000 | **Hypothetical branch assumption** | The question asks for bookkeeping under that assumption, not a prediction |
| ICM value of folding, calling or reraising | **Unknown** | The exact payouts and remaining player stacks are absent |

The distinction is between a **given fact within this invented case** and a real-world observed poker frequency. There are no independently verified opponent statistics.

## 2. Action: correct live and dead chip bookkeeping

The question stipulates six-handed play, a 2,000 small blind, 4,000 big blind, 4,000 **separate big-blind ante**, no other antes, no rake, no side pots and no prior voluntary bets.

| Check | Calculation | Answer |
| --- | --- | --- |
| Hero's stack behind **after posts** | 80,000 - 4,000 live BB - 4,000 dead BB ante | **72,000** |
| Current pot **before response** | 2,000 folded SB + 4,000 live BB + 4,000 BB ante + 10,000 cutoff open | **20,000** |
| Extra amount to **call** | 10,000 total open - 4,000 posted live BB | **6,000** |
| Pot **after call** | 20,000 + 6,000 | **26,000** |
| Chips behind **after call** | 72,000 - 6,000 | **66,000** |
| Extra amount to **reraise to 24,000** | 24,000 total live hero contribution - 4,000 posted live BB | **20,000** |
| Chips behind immediately **after reraise** | 72,000 - 20,000 | **52,000** |
| **Uncalled portion returned** if cutoff folds | Hero's live 24,000 minus cutoff's live 10,000 | **14,000** |
| **Awarded pot after refund** | 10,000 matched hero + 10,000 cutoff + 2,000 SB + 4,000 BB ante | **26,000** |

An alternative check of the final row is 20,000 in the pot before hero's move + 20,000 additional reraise - 14,000 unmatched refund = **26,000**.

**Optional final stack check:** Under the *assumed* immediate cutoff fold, hero receives 14,000 back as an uncalled bet and is awarded the 26,000 pot. The final stack is 52,000 behind + 14,000 refund + 26,000 pot = **92,000**, a **12,000 net chip gain** over the 80,000 starting stack. The 26,000 awarded pot includes hero's own matched contribution and dead ante; it is not a 26,000 profit.

**Common errors:** Calling for 10,000 instead of 6,000, treating the 4,000 big-blind ante as part of the live blind, ignoring the small blind's dead 2,000, or counting the entire 24,000 live reraise as permanently contested after the cutoff folds.

## 3. Decision: actions versus conclusions

The big blind can fold, call another 6,000, or reraise. The proposed 24,000 total is one legal reraise size in this case. Calling leads to later streets; raising introduces the cutoff's response branches. The case does **not** give enough evidence to rank actions.

The cutoff's **opening range** describes which hands initiate a raise to 10,000. Its **calling range against a reraise** is the possibly narrower or otherwise different subset that continues against increased pressure. Do not substitute one for the other. Neither range follows from the stipulated two raises in six observed hands.

## 4. What was known versus inferred

An acceptable **observation**: "The cutoff raised twice during the preceding six hands." This describes a very small sample and does not even specify the full positional opportunities.

An acceptable **hypothesis**: "The cutoff might open widely" or "the cutoff might fold frequently to reraises." These are **assumptions to test**, not measured frequencies. A numerical claim like "cutoff opens 33% and calls 15%" would be unjustified.

## 5. Missing inputs and why the call price is not a verdict

A useful chip-EV comparison would need credible cutoff opening and response ranges, equity or an appropriate future-play model, actual continuation policies, and legal action sizing under the scenario. A prize-value comparison would additionally need relevant other player stacks, all payout amounts, any bounties or deals, and a specified tournament-value model.

The call contributes **6,000 into a final preflop pot of 26,000**, giving a purely arithmetic immediate price fraction of **6,000 / 26,000 ≈ 23.1%**. That number **does not by itself establish** the best action, or a sufficient equity threshold for a multistreet call with future betting. Calling with Q♠ J♠ has not been evaluated in a validated strategy model.

## 6. Result: not supplied

There is **no actual showdown, board, winner or opponent holding** in this fictional case. The question's "cutoff folds" condition was created only for the bookkeeping branch. It does not tell us how frequently a real cutoff would fold, and it cannot justify a strategy verdict.

The correct answer to "did the chosen action win?" is **not provided**, not an invented result.

## 7. One next study step

For example, specify **two contrasting cutoff call-versus-reraise ranges** as explicit hypothetical inputs, record their source and limitations, and examine how different responses change an explicitly chosen objective. Without defensible ranges and tournament payouts, stop without an ICM claim.

### Self-check checklist

A successful attempt should be able to answer yes to these five questions:

- [ ] Did I distinguish fictional givens, calculated amounts, assumptions and unknowns?
- [ ] Did I reconstruct the 20,000 starting pot, 6,000 call and 26,000 pot after calling without counting the ante as a live wager?
- [ ] Did I distinguish the 20,000 reraise addition from the 14,000 uncalled refund and the 26,000 awarded pot?
- [ ] Did I keep the opening and continuation ranges separate and identify missing payout and stack data?
- [ ] Did I leave the actual result unknown and avoid declaring a best poker action?

A missed check suggests a **specific review skill to practice**, not poor poker judgment. Neither five checked boxes nor any synthetic case establishes profitability at a real table.

*Prepared with AI assistance, November 17, 2026. This is a solution key for the invented accounting and evidence exercise, not a solver result, personalized gambling advice or validation of a tournament decision. No answers are transmitted or stored by the website.*
