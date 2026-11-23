# Main pot, side pot and tournament ICM: a three-way call

**Original after-play study worksheet | Nolan Kido | November 23, 2026**

Companion to [Chips, prizes and ICM](https://nolankido.com/poker/tournament-equity/) and the [three-way contribution example in the bounty guide](https://nolankido.com/poker/bounty-knockout-equity/#bounty-side).

[Download the fixed-case Python verifier](https://nolankido.com/downloads/poker-multiway-icm-verify.py). It uses only the standard library and checks the complete branch ledger with exact fractions. No account or solver is needed.

**Scope:** All stacks, prize amounts, action probabilities and rankings are invented. This is a model comparison for study after play, not a recommendation, solver result, actual tournament rule sheet, or estimate of any player's range. The ICM model assumes chip-proportional finishing probabilities among surviving players. There are no ties, bounties, fees, deals, rake or further betting.

## 1. Fix the decision before comparing the outcomes

Three players remain in a fictional no-limit hold'em tournament. The remaining ordinary prizes are $70 for first, $30 for second and $0 for third. Blinds are 0.5/1 BB with no ante. X is the button (4 BB), H is the small blind (14 BB), and Y is the big blind (9 BB). All three starting stacks are stated before posting.

X shoves 4 BB. H calls to 4 BB, adding 3.5 to the posted small blind. Y raises all-in to 9 BB, adding 8 to the posted big blind. The full raise increment is 5 BB, which exceeds the prior increment of 3 BB. H's remaining alternatives in this exercise are fold or call 5 BB more. No further player can act.

| At H's final decision | X | H | Y |
| --- | ---: | ---: | ---: |
| Before posting | 4 | 14 | 9 |
| Already contributed | 4 | 4 | 9 |
| Still behind | 0 | 10 | 0 |

If H folds, the 4 BB already contributed remains in the pot. Y receives the unmatched 5 BB back, and X and Y contest the 12 BB main pot. H keeps 10 BB. The fold does **not** freeze every other player's stack.

If H calls, all three contest a 12 BB main pot. H and Y alone contest a 10 BB side pot. H retains 5 BB uncommitted. Both opponents are all-in. The 27 BB total is always conserved, whether the hero folds or calls.

For the artificial event, if X and Y are both eliminated on this hand, the larger pre-hand stack Y (9 BB) is awarded second and X (4 BB) third. This is a stipulated rule of the example, not a claim about every tournament's simultaneous-elimination procedure.

## 2. Compare three shared showdown rankings

The following joint distribution is entirely hypothetical and is conditional on the prior action. It applies to the underlying card rankings whether H folds or calls. Folding excludes H from pot eligibility; it does not change which remaining hand beats which. The other three possible strict ranking orders have probability zero in this exercise. This is not a claim that any particular preflop hand or real range produces these frequencies.

| Ranking (best to worst) | Assumed probability | Folded stacks X/H/Y | Called stacks X/H/Y |
| --- | ---: | ---: | ---: |
| H > Y > X | 10% | 0 / 10 / 17 | 0 / 27 / 0 |
| X > H > Y | 30% | 12 / 10 / 5 | 12 / 15 / 0 |
| X > Y > H | 60% | 12 / 10 / 5 | 12 / 5 / 10 |

Why these outcomes?

- H > Y > X: if H folds, Y beats X for the 12 BB pot and retains the 5 BB refund. If H calls, H wins both pots, ends with all 27 BB, and wins the event.
- X > H > Y: if H folds, X wins the 12 BB main and Y retains 5 BB. If H calls, X wins the main, H wins the 10 BB side, and Y is eliminated. H ends with 5 + 10 = 15 BB.
- X > Y > H: if H folds, X still wins the 12 BB main and Y retains 5 BB. If H calls, X wins the main and Y wins the side, leaving H just 5 BB. All three survive.

Notice that H can lose the main pot and still receive a side-pot award. A single all-pot winning probability cannot price this call.

## 3. Audit chip EV with two distinct pots

H's assumed probability of winning the main pot is 10%. H's probability of winning the side pot is 10% + 30% = 40%. The main and side events are related, not independent. Main wins in this no-tie example imply side wins, but side wins do not imply main wins.

The incremental comparison against folding is:

**12 × 0.10 + 10 × 0.40 − 5 = +0.2 BB.**

Equivalently, H ends with 10 BB after folding, and calling produces an expected 0.10 × 27 + 0.30 × 15 + 0.60 × 5 = **10.2 BB**. The 4 BB already contributed is sunk at the final decision and is not charged a second time.

This formula accounts for both eligible pots. Using just 5/22 and comparing it to the chance of beating everyone would omit the partial side-pot wins. A pot-weighted expected share would work for the chip comparison, but it would not identify the different elimination outcomes for the prize calculation.

## 4. Apply classic ICM to each final state

When two players remain, each is assured $30 and has a modeled first-place chance equal to their share of the 27 BB. When all three remain, H's first-place probability is H/27. H's second-place probability is the sum of the two paths in which someone else finishes first, then H finishes second.

For the folded three-player state (12, 10, 5):

- First: 10/27.
- Second: (12/27 × 10/15) + (5/27 × 10/22).
- Prize value: $70 × P(first) + $30 × P(second) = **$11090/297 ≈ $37.34**.

For the called three-player state (12, 5, 10):

- First: 5/27.
- Second: (12/27 × 5/15) + (10/27 × 5/17).
- Prize value: **$9490/459 ≈ $20.68**.

The other values use the same model on two-player states or the completed event.

| Ranking | H fold modeled prize equity | H call modeled prize equity |
| --- | ---: | ---: |
| H > Y > X | $1210/27 ≈ $44.81 | $70.00 |
| X > H > Y | $11090/297 ≈ $37.34 | $470/9 ≈ $52.22 |
| X > Y > H | $11090/297 ≈ $37.34 | $9490/459 ≈ $20.68 |

Calculate the weighted sum of each column using 1/10, 3/10 and 3/5. Use the exact fractions rather than the rounded display dollars.

- Fold: **$11312/297 ≈ $38.09**.
- Call: **$5366/153 ≈ $35.07**.
- Call minus fold: **−$15226/5049 ≈ −$3.02**.

The call gains 1/5 BB in modeled chip expectation while losing modeled ordinary prize equity. The two objectives answer different questions. This is not a general recommendation to fold a profitable side pot; the result is conditional on the specific constructed prizes, joint probabilities and stacks.

## 5. Check the reasoning before reading the answers

1. Why is H's fold stack always 10 BB but the fold prize value not constant?
2. Who is eligible for each pot if H calls? How much of Y's raise is refunded if H folds?
3. If H wins the side and not the main, can H still increase its stack relative to folding?
4. Why does 40% side-pot win probability not mean 40% main-pot win probability?
5. Would the comparison remain the same if the entire $100 went to first place?
6. Which inputs must be known before treating this example as applicable to a real hand?

**Answer key:**

1. H contributes no additional chips on a fold, but an opponent may bust, changing the payout state.
2. Main 12 BB: X/H/Y. Side 10 BB: H/Y. Fold: Y gets 5 unmatched BB back, with X/Y alone contesting 12 BB.
3. Yes. In X > H > Y, H retains 5 and receives 10, finishing with 15 instead of 10 BB.
4. H can beat Y yet lose to X. The side-pot event includes both H > Y > X and X > H > Y here.
5. No. Winner-only ICM is chip-proportional: the 0.2 BB expected gain corresponds to $100 × (0.2/27) = $20/27 ≈ $0.74. The ordinary two-prize inversion disappears in that counterfactual.
6. Exact action/eligibility and all-in amounts, the payout and elimination rules, the full remaining field's relevant stacks, the action tree, and a defensible joint outcome distribution. Real play can have ties, bounties, and future betting, among other omitted inputs. Unknown probabilities must remain unknown.

## 6. Advanced comparison: the missing counterfactual fold

Suppose you know H's expected chip gain from calling and even the entire distribution of final stacks **if H calls**. Is that sufficient to decide whether the call improves modeled prize equity? Not necessarily. The other players' relative ranking can still matter when H folds, even in a branch where H would win everything by calling.

Keep the same 4/14/9 BB starting stacks, 12 BB main pot, 10 BB side pot, 5 BB additional call, $70/$30/$0 ordinary prizes and stipulated simultaneous-elimination rule from sections 1 to 4. Change only the invented strict-ranking probabilities. The following two alternative distributions are each conditioned on the prior action; neither is a measured distribution of poker hands. All unlisted orders have zero probability.

| Strict ranking | Distribution A | Distribution B | H's final stack if called |
| --- | ---: | ---: | ---: |
| H > X > Y | 20% | 0% | 27 BB |
| H > Y > X | 0% | 20% | 27 BB |
| X > H > Y | 25% | 25% | 15 BB |
| X > Y > H | 55% | 55% | 5 BB |

Both distributions give H a 20% main-pot win chance and a 45% side-pot win chance. The chip comparison is identical: 12 × 0.20 + 10 × 0.45 − 5 = **+1.9 BB**. H expects 11.9 BB from calling versus 10 BB from folding. The complete called-state distribution is also identical: 20% (0, 27, 0), 25% (12, 15, 0), and 55% (12, 5, 10), in X/H/Y order. As a result, every player's modeled ordinary prize equity from calling is the same in both distributions. For H, it is **$17638/459 ≈ $38.43**.

But the fold branch is different:

- **A:** X beats Y in every listed ranking after removing H from eligibility. X wins the main pot, Y receives the unmatched 5 BB, and all three survive with stacks (12, 10, 5). H's modeled fold value is **$11090/297 ≈ $37.34**.
- **B:** Y beats X in the 20% H > Y > X branch, so X busts when H folds. Y then holds 17 BB, and H retains 10 BB and is guaranteed at least second prize. H's prize value in that branch is $1210/27. The other 80% of folds leave the same three-player state as A. Thus H's weighted fold value is **$11534/297 ≈ $38.84**.

| Comparison, H only | Distribution A | Distribution B |
| --- | ---: | ---: |
| Expected chips if folded | 10 BB | 10 BB |
| Expected chips if called | 11.9 BB | 11.9 BB |
| Modeled prize value if folded | $37.34 | $38.84 |
| Modeled prize value if called | $38.43 | $38.43 |
| Call minus fold, exact | $5488/5049 | −$2060/5049 |
| Call minus fold, rounded | +$1.09 | −$0.41 |

**What changes the sign?** No part of the call ledger changes. The model's baseline changes because one possible fold eliminates a third-place player, increasing the value of H's remaining stack. Comparing call equity with ICM at a single guessed fold state could miss that effect. The example does not establish that these particular joint distributions are realizable by specific real cards or range weights, or that either action is correct in another event. It shows a consequence of the stipulated probability model.

**Practice, before looking back at the table:** If the probability of H > Y > X were moved from zero to 20% at the expense of H > X > Y, what stays constant and what changes? Check that both alternative distributions conserve 27 BB and $100 in every branch. The exact checker prints both ledgers under the `fold_baseline_sensitivity` key. For a real review, a counterfactual outcome may be unobservable: if H called, what would have happened had H folded? Record that uncertainty instead of inventing the remaining players' hand-order probabilities.

## Reproduce and keep a private record

Run `python poker-multiway-icm-verify.py --self-test` (or `py -3` on Windows). Run it without `--self-test` to print the exact branch results and expected prize values for all players. The supplied examples conserve 27 BB and the $100 prize pool in every branch and expectation. The script uses explicit checks that remain active under optimized Python.

For your own permitted after-session notes, write the pre-action and post-action stacks, each contribution and refund, who can win each pot, the possible ranking branches (including ties when applicable), applicable prize rules, assumptions and their sources, and the unresolved information. Do not copy these invented frequencies into an actual review.

*Prepared with AI assistance. Educational illustration only, not at-table assistance, an actual return estimate, or a promise of gambling profit.*
