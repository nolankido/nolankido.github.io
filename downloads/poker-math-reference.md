# Poker math quick reference

Heads-up, first bet into the pot, no rake, no further betting, and no side pots. Call equity counts ties by their share of the pot. Pure bluffs lose every time they are called. These are chip-EV break-even thresholds, not recommendations to call or bluff. Use away from play; close the playing client when its policy requires it.

P = pot before a first bet; B = that bet.
Call equity = B / (P + 2B).
Pure-bluff break-even fold rate = B / (P + B).

| First bet size | Call equity | Folds for bluff |
|---|---:|---:|
| Quarter pot | 16.67% | 20.00% |
| One-third pot | 20.00% | 25.00% |
| Half pot | 25.00% | 33.33% |
| Two-thirds pot | 28.57% | 40.00% |
| Three-quarters pot | 30.00% | 42.86% |
| Pot | 33.33% | 50.00% |
| One-and-a-half pot | 37.50% | 60.00% |
| Twice pot | 40.00% | 66.67% |

For a general call: extra call / (current pot including all outstanding wagers + extra call).
Use only the pot you can win; an all-in side-pot situation needs separate accounting.
SPR = effective chips remaining / current pot, both measured at the same decision.
Pot-limit raise: first account for the call, then a raise by the pot after that call.
General pure-bluff threshold = incremental risk / (incremental risk + reward).
Do not reuse a first-bet size table for a raise without recalculating risk and reward.
Drawing to a hand is not the same as winning with it. Tournament payout effects are not included.

Worked examples, assumptions and sources: https://nolankido.com/poker/poker-math-reference/
Published October 8, 2026. Prepared with AI assistance. Fixed fictional study examples.
