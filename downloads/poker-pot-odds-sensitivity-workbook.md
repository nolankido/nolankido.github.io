# Pot Odds and Range Sensitivity: A Practical Decision Workbook

Nolan Kido | Original, free after-play poker study | November 22, 2026

**Read the lesson first:** https://nolankido.com/poker/pot-odds-workshop/

**Reproduce the fixed example arithmetic:** https://nolankido.com/downloads/poker-pot-odds-sensitivity-verify.py

This is an original **fictional exercise**, not a book excerpt, an observed opponent range, a solver calculation or a record of a hand played. Use it away from live play. It does not recommend an action against a real opponent.

## 1. Know the price. Be clear about the uncertain estimate.

For a heads-up, matched-pot call that closes betting, with no rake, side pots, bounties, or tournament-prize adjustment:

- **P** is the pot when the decision reaches you, including the opponent's latest bet and earlier contributions.
- **C** is the additional chips you must put in to call. Already-bet chips do not cost you again.
- **F = P + C** is the final eligible matched pot if you call and no one acts again.
- **q** is your assumed showdown equity against an explicitly described opponent range, including your expected share of tied pots.
- **Break-even equity = C / F.**
- **Call chip EV relative to folding = q x F - C.**

The recorded pot and legal action determine P and C. The actual board, holdings, opponent range and model determine q, which often remains uncertain. An exact call price does not validate a guessed range.

| After-play input | Your record |
| --- | --- |
| Game, street, players and relevant stacks | |
| Starting pot, blinds, antes and ordered contributions | |
| Pot now P, extra call C, and final eligible pot F | |
| Does calling close all action? Unmatched chips or side pots? | |
| Opponent range evidence and excluded holdings | |
| Equity estimate q and plausible lower/upper assumptions | |
| Rake, future betting, ICM, bounties, seats or other exclusions | |

## 2. A call whose sign changes with a range assumption

**Fictional heads-up river.** The pot is 20 BB before an opponent bets 10 BB. The call closes the action and there are no deductions.

- P = 20 + 10 = **30 BB**.
- C = **10 BB**.
- F = 30 + 10 = **40 BB**.
- Break-even equity = 10/40 = **1/4 = 25%**.

| Hypothetical showdown equity q | Chip EV of calling relative to folding |
| --- | ---: |
| 20% (1/5) | **-2 BB** |
| 25% (1/4) | **0 BB** |
| 30% (3/10) | **+2 BB** |

For example, at 20% the expression is 0.20 x 40 - 10 = -2 BB. At 30% it is 0.30 x 40 - 10 = +2 BB. **Neither equity estimate was measured.** The table is not permission to choose the more favorable input.

Suppose an after-play review can justify only an *illustrative* equity interval from **22% to 29%**. The conditional EV interval is **-1.2 to +1.6 BB**. Because it crosses zero, the sign changes under plausible inputs. Report that sensitivity instead of claiming a definitive answer.

The call EV changes by **0.4 BB per one percentage point of assumed equity** because the final matched pot is 40 BB. A six-point equity estimation error changes the modeled result by 2.4 BB. This is arithmetic, not an observed opponent error rate.

**Ask:** Which combinations are assigned to value, draws and bluffs? What board and blockers are known? How are ties counted? Which observation supports each weight? If none, call q an assumption, not a discovery.

## 3. Raising to an amount is different from raising by an amount

**Fictional heads-up street.** Start with 10 BB in the pot. You bet 4 BB. The opponent raises **to 14 BB total** on this street.

- Current pot P = 10 + 4 + 14 = **28 BB**.
- Incremental call C = 14 - 4 = **10 BB**.
- Final matched pot F = 28 + 10 = **38 BB**.
- Break-even equity = 10/38 = **5/19, about 26.32%**.

At a hypothetical 25% equity, call EV is **-0.5 BB**. At 30%, it is **+1.4 BB**. The pot accounting is unchanged between the two scenarios. Do not charge yourself the full 14 BB again: you already put in 4 BB.

**Ask:** Could someone else raise? Is there future betting? If either is possible, a one-street showdown equation is not a complete comparison of fold, call and reraise.

## 4. The bluff bettor and the caller have different prices

**Fictional heads-up river.** A bettor risks **6 BB** into a **10 BB** pot with *zero* showdown equity when called. Only fold or call is modeled; checking is assigned zero chip EV.

For the bettor, with f the assumed fold probability:

- Pure-bluff EV relative to checking = **f x 10 - (1 - f) x 6**.
- Break-even folds = 6/(10 + 6) = **3/8 = 37.5%**.

| Hypothetical folds f | Pure-bluff chip EV |
| --- | ---: |
| 30% | **-1.2 BB** |
| 37.5% | **0 BB** |
| 40% | **+0.4 BB** |
| 50% | **+2 BB** |

For the **caller** facing that bet, the current pot is 16 BB and a call of 6 BB creates 22 BB. The separate break-even showdown equity is **6/22 = 3/11, about 27.27%**. This is not the bettor's 37.5% fold threshold. They answer different questions for different actors.

If the bluff has showdown equity when called, the opponent can raise, or checking has value, the pure-bluff formula no longer represents the full decision.

## 5. Four questions to solve before reading the answers

Show P, C and F when there is a call, write the exact threshold, and state a *conditional* result. Do not invent a range from the answer key.

**Case A, another river price.** A heads-up pot begins at 12 BB. Your opponent bets 9 BB. Calling closes action. Find break-even equity and call EV when q is hypothetically 28% or 36%.

**Case B, a smaller raise-to.** The starting pot is 10 BB. You bet 3 BB and face a raise **to** 9 BB. Calculate the pot now, the additional call, final pot, break-even equity, and EV for an invented q of 20%.

**Case C, another bluff size.** A zero-showdown-equity bettor risks 6 BB to win a 12 BB pot with only fold/call responses. Calculate the fold threshold, bluff EV with 30% folds, and the separate caller price.

**Case D, a range band.** In a heads-up matched-pot call, P = 25 BB and C = 5 BB. An illustrative range study produces an equity interval of 15% to 19%. Calculate the threshold, the conditional EV interval, and EV change per one percentage point of assumed equity. Is a real-hand decision thereby solved?

For each, write one known fact and one piece of missing evidence. "Insufficient information about the opponent or future actions" can be the correct conclusion.

## 6. Stop conditions before publishing or using a conclusion

These are narrow chip models, not an action-complete strategy. Stop and rebuild the model if:

- A call does not close betting, or a raise, future card or check alternative still matters.
- Another player is involved, an uncalled amount must be refunded, or a side pot contains chips this player cannot win.
- Rake or fees change the pot, or tournament prize equity, satellite seats or bounties change the objective.
- Board, cards, ties, blockers or the actual opponent range are not stated well enough to justify q.
- A bluff has showdown value or the opponent can raise rather than merely fold or call.
- The venue prohibits external help during play. This worksheet and script are for study away from the table.

A correct calculation on incomplete inputs remains correct **inside its incomplete model**. It is not a solver verdict or an authorization to act.

## 7. Answer key to the four extra cases

**Case A:** P = 12 + 9 = 21 BB, C = 9 BB, F = 30 BB. Break-even q = 9/30 = **30%**. At q = 28%, EV = 0.28 x 30 - 9 = **-0.6 BB**. At q = 36%, EV = **+1.8 BB**.

**Case B:** P = 10 + 3 + 9 = **22 BB**, C = 9 - 3 = **6 BB**, F = 28 BB. Break-even q = 6/28 = **3/14, about 21.43%**. At q = 20%, EV = 0.20 x 28 - 6 = **-0.4 BB**.

**Case C:** Break-even f = 6/(12 + 6) = **1/3, about 33.33%**. At f = 30%, EV = 0.30 x 12 - 0.70 x 6 = **-0.6 BB**. The separate caller price is 6/(12 + 2 x 6) = **1/4 = 25%**.

**Case D:** F = 25 + 5 = **30 BB**; break-even q = 5/30 = **1/6, about 16.67%**. At 15%, EV = 0.15 x 30 - 5 = **-0.5 BB**. At 19%, EV = 0.19 x 30 - 5 = **+0.7 BB**. One point in equity changes conditional EV by **0.3 BB**. The band crosses zero, so no real-hand action follows without opponent and game evidence.

## 8. Reproduce the fixed arithmetic without a solver

The linked Python file uses only Python 3 standard-library `fractions.Fraction`. It makes no network calls, reads no private data, and writes no files. It reproduces the fixed inputs from Sections 2 to 4. From a local copy of the repository, on Windows PowerShell:

```powershell
py -3 downloads/poker-pot-odds-sensitivity-verify.py --self-test
py -3 downloads/poker-pot-odds-sensitivity-verify.py --json
```

The self-test checks exact rational break-even prices, conditional EVs, and invalid-input rejection. JSON preserves fractions such as `5/19`; decimal percentages shown here are rounded. Neither command produces an opponent range, a solver solution or tournament ICM equity.

**Keep the original after-play hand note separate from later analysis.** Save the pot, assumed range, uncertainty, result and next question without rewriting what you thought at the table.
