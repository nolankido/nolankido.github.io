# Ten Big Blinds: Six-Check Tournament Decision Sheet

NolanPoker | Companion to the 10 BB Tournament Playbook | November 19, 2026

Full guide: https://nolankido.com/poker/10bb/

Use this worksheet for study away from the table. It is not a universal shove chart.

| Step | Ask before acting |
| --- | --- |
| **1. Count the chips** | What is live and what is a dead ante? What is in the pot now? What must I add, what is the final matched pot, and what remains behind? Check the blind clock and next forced payments. |
| **2. Identify the players** | What is my position? Who can still act? Who covers whom? Which other stacks matter? |
| **3. Name the decision** | First in, facing a raise, calling an all-in, or playing a later street? What actions are actually available? |
| **4. Estimate ranges** | What evidence supports the opponent's range? What is merely assumed? Which range change could change the answer? |
| **5. Compare complete choices** | What happens when opponents fold, call, or raise? Does a call end betting? What does checking earn in the same model? |
| **6. Check the objective** | Chip EV, ordinary tournament prizes, satellite seats, or bounties? Are payouts and all relevant stacks known? |

## Three calculations

**All-in calling price:** additional call / final matched pot. Compare with equity against the specified opponent range, including any tied-pot shares. For a non-all-in call, this immediate price does not guarantee the next card or free showdown.

**Shove chip EV (relative to folding):** P(opponents fold) × present pot + P(opponents call) × [equity when called × final matched pot − additional shove]. Include other branches as applicable.

**Prize value:** probability-weight each resulting stack state's model prize value (including a loss payout, if any); compare with folding. Match the actual payout structure and all relevant stacks.

## Practice review

1. State the action, calculation, or model comparison.
2. Explain the evidence and assumptions behind it.
3. Name one input that could reverse your conclusion.

**After the hand, record:** positions, starting-stack convention, dead/live contributions, action sequence, available cards, assumed ranges, objective, clock, and any missing evidence. The result alone does not prove whether the decision was sound.

## Worked example to revisit

Three-player no-ante ICM exercise: payouts $100/$60/$40; initial BTN/SB/BB stacks 5/20/10 BB. The BB calls 9 more to contest 20. The chip-only threshold is 45%, but the no-tie standard ICM prize-value threshold for the specified stacks and payouts is 63/107, about 58.88%. The losing branch still pays $40. See the full derivation in the companion guide.

### Reproduce the prize-value comparison

Expanded November 21, 2026. This is a fixed, fictional **three-player, three-paid, no-ante** example. It assumes ordinary ICM chip shares, no ties, no bounties or deals, and no further betting. It does not supply a real opponent range or a universal calling threshold. It is not a solver verdict for any actual hand.

The stack order below is **hero (big blind), small blind, button**. Total chips stay at 35 BB.

| Hero decision and outcome | Resulting stacks (BB) | Hero first | Hero second | Hero third | Hero modeled prize value |
| --- | --- | --- | --- | --- | --- |
| Fold | (9, 21, 5) | 9/35 | 3/7 | 11/35 | $64 |
| Call and win | (20, 10, 5) | 4/7 | 34/105 | 11/105 | $1696/21, about $80.76 |
| Call and lose | (0, 30, 5) | 0 | 0 | 1 | $40 |

For each non-bust state, standard ICM assigns first place in proportion to chip shares, then assigns second using the surviving chip shares across every finishing order. Third place is the remaining probability. This is a model convention, not a prediction that a real player will finish in that position.

**Fold value:** $100 × (9/35) + $60 × (3/7) + $40 × (11/35) = **$64**.

**Call-win value:** $100 × (4/7) + $60 × (34/105) + $40 × (11/105) = **$1696/21**, about **$80.76**.

**Call-lose value:** **$40**, because the hero is eliminated in third place, which is paid.

**Chip-only price:** 9 BB additional call ÷ 20 BB final matched pot = **9/20 = 45%**. This is a chip-price comparison, not an ICM decision.

Let `p` be a hypothetical probability of winning the all-in, with no tie outcome. Call model value is `p × (1696/21) + (1 − p) × 40`. Solve against the $64 fold value:

`p = (64 − 40) / (1696/21 − 40) = 63/107 ≈ 58.88%`.

The specific modeled ICM requirement is about **13.88 percentage points higher** than the 45% chip price.

### Try two assumptions before looking up the results

1. At an **assumed 55%** win probability, compute chip EV of calling relative to folding: `20 × 0.55 − 9 = ____ BB`.
2. Compute the associated model-prize difference: `0.55 × (1696/21) + 0.45 × 40 − 64 = $____`.
3. Repeat both at an **assumed 60%** win probability. Does the model choice change?
4. State which assumptions a real hand would still need: opponent's range, tie outcomes, remaining players, prize schedule, and any bounties or future betting.

**Answer key (round dollars to cents)**

| Assumed all-in win rate | Chip EV of calling vs folding | Call model prize value | Prize value compared with folding |
| --- | --- | --- | --- |
| 45% | 0 BB | $58.34 | −$5.66 |
| 50% | +1 BB | $60.38 | −$3.62 |
| 55% | +2 BB | $62.42 | −$1.58 |
| 60% | +3 BB | $64.46 | +$0.46 |

At 55%, the chip EV is positive but the expected prize value is below folding. At 60%, both are positive under **these fixed fictional assumptions**. Neither is a claim about any actual player or tournament. Do not apply this three-player example's 58.88% threshold to a bubble, satellite, bounty event, or a pot with a different stack or payout distribution.

**Independent offline check:** download [the exact-fraction Python script](https://nolankido.com/downloads/ten-bb-playbook-icm-verify.py), inspect it, and run `python ten-bb-playbook-icm-verify.py` away from the table. The script uses only Python's standard library, has fixed inputs, makes no network request, and does not write files.

Sources and scope: https://nolankido.com/poker/10bb/#sources
