# Ten big blinds near the money: after-play study sheet

Companion to [6–10 BB tournament decisions](https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble).

**Use after play only.** Keep your completed copy privately. No account, solver subscription, web form, live table advice, or personal information is required. Record facts before results. A numerical conclusion is unavailable when essential inputs are missing.

## 1. Freeze the decision before looking at the outcome

| Question | Your record | Evidence class: recorded / calculated / assumed / unknown |
| --- | --- | --- |
| Tournament type, players left and places paid | | |
| Exact payout ladder, seats or bounty terms | | |
| Blinds and who posted each ante | | |
| Hero stack before posts; stack now behind | | |
| Every relevant opponent stack before posts | | |
| Button, positions and action in order | | |
| Total live bet, already paid live blind, amount still owed | | |
| Who covers whom; any unmatched refund or side pot | | |
| Candidate actions: fold / call / smaller raise / shove | | |
| Opponent range source, if any, and alternative assumptions | | |
| Objective and model: chips / ordinary ICM / satellite / bounty | | |

**Stop rule:** Do not report a solver verdict, a calling range or an ICM percentage for an actual hand unless the exact decision state, tree, ranges and relevant prizes are verifiable. A revealed hand is not the opponent's complete range.

## 2. Check a fully fictional four-player call

This is a fresh teaching hand, **not** Nolan's Portland Meadows shove. Four remain and three cash for **$50 / $30 / $20 / $0**. Small blind begins with **40 BB**, cutoff **30**, button **20**, hero big blind **10**, all before posts. Blinds are **0.5/1 BB**, **no ante**. Cutoff and button fold; small blind shoves 40 BB total and covers hero. No bounties, deals, fees, ties, or later betting.

1. Hero already has **1 BB live**, so calling adds **10 - 1 = 9 BB**.
2. The covering small blind gets **30 BB unmatched back** on a call; the contested pot is **10 + 10 = 20 BB**.
3. Direct, closed-action chip break-even win probability: **9 / 20 = 45%**.
4. Folded state, SB / CO / BTN / hero: **41 / 30 / 20 / 9 BB**.
5. Call and win state: **30 / 30 / 20 / 20 BB**.
6. Call and lose state: **50 / 30 / 20 / 0 BB**.
7. Exact classic ICM enumeration gives hero modeled prize value **$12.286143** on a fold, **$21.785714** on a call-win, and **$0** on a call-loss. All sums conserve **100 BB**.
8. Call's ICM break-even chance with no ties: **12.286143 / 21.785714 ≈ 56.40%**, calculated before rounding the displayed dollars.

Run the [offline standard-library reproduction](https://nolankido.com/downloads/ten-bb-bubble-icm.py) to inspect the exact rational results. A **hypothetical** 50% win chance would clear the 45% chip price while falling short of the 56.40% modeled prize threshold. No equity or shove range is assigned to an actual holding.

## 3. Separate the documented live hand

The [Portland Meadows Episode 1 hand record](https://nolankido.com/poker/episodes/portland-meadows-ep1/#hand-64o-record) reports **13 left, 10 paid**, blinds **8,000/15,000** with a separate **15,000 big-blind ante**, and Nolan in the small blind with 6-4 offsuit. The reported 148,000 chips equal **148,000 / 15,000 ≈ 9.87 BB** if they describe the stack before posting. Nolan reports shoving, being called by A-K suited and winning.

This source does **not** establish the exact effective stack, all remaining stacks, payouts, full calling range, individual suits or complete board. The four-player no-ante example above does not solve this distinct 13-left, big-blind-ante hand. Keep the narrated result separate from the decision review.

## 4. Complete your own post-session analysis

- The action I am trying to evaluate, written without the eventual result:
- The exact amount risked, matched pot, live credits and any dead contributions:
- Assumptions that change if I shove first in versus call a shove:
- Other relevant stacks and the exact prizes I could verify:
- A narrow chip calculation I can independently reproduce:
- If appropriate, a fully specified ICM or seat-equity comparison:
- What remains unresolved, and why the result does not settle the decision:
- One assumption to test next, without rewriting the original hand:

For a first lesson, use [Poker Foundations](https://nolankido.com/poker/free-poker-learning-path/). For exact pot arithmetic, see the [poker math reference](https://nolankido.com/poker/poker-math-reference/). For more after-play exercises, use the [Poker Study Practice Room](https://nolankido.com/poker/practice-room/).

*Prepared November 18, 2026, with AI assistance. The numeric case is fictional, independently reproducible classic ICM arithmetic, not a range recommendation, real-time assistance, or a claim of positive gambling returns.*
