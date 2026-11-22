# A flush completion is not necessarily a winning out

A free, no-wager practice companion for the [poker math reference](https://nolankido.com/poker/poker-math-reference/#clean-outs-turn-check) by Nolan Kido.

**Status:** Original, fictional website example. Not a chapter excerpt, actual hand, solver recommendation, player read, or prediction of winning results.

## One face-up turn model

| Input | Value |
| --- | --- |
| Hero | A♥ J♥ |
| Opponent | 7♦ Q♣ |
| Turn board | K♥ 7♥ 7♣ 2♦ |
| Pot before opponent bets | 60 chips |
| Opponent's turn bet | Their remaining 20 chips, all-in |
| Hero's incremental call | 20 chips |
| Fees, side pots, ties or further betting | None in this model |

For *this study model only*, both players' hole cards are known. An ordinary player cannot see the opponent's hole cards before making the decision. This model is therefore a conditional card-counting exercise, not a usable table read.

Before revealing the answers, write down:

1. How many physical cards are known? What is the correct unseen-card denominator?
2. How many river hearts would complete Hero's flush?
3. Which of those hearts would also give the opponent a better hand?
4. Exactly which rivers win for Hero? Are there ties?
5. What fraction of the final pot must Hero win to break even on the call?
6. Would treating every flush-completing heart as a winning out change the estimated call EV?
7. Would the same calculation justify a flop call if another turn bet were possible?

## Answer key

**Known cards:** Hero's 2, opponent's 2, and 4 community cards make **8 distinct physical cards**. The other **44** cards are possible rivers under this fully face-up model. Do not use 46, which would be the unseen count with only Hero's hole cards and a four-card board known.

**Nine flush completions:** Two hearts are in Hero's hand and two on the board, leaving nine hearts to arrive on the river:

2♥, 3♥, 4♥, 5♥, 6♥, 8♥, 9♥, 10♥, Q♥.

**Two dirty heart completions:**

- **2♥** pairs the 2♦ board card. Opponent's 7♦ with the two board sevens makes three sevens, plus the two twos make a **full house, sevens full of twos**. Hero's ace-high heart flush loses.
- **Q♥** pairs the opponent's Q♣. The opponent has three sevens and two queens, a **full house, sevens full of queens**. Again the flush loses.

The only winning rivers are 3♥, 4♥, 5♥, 6♥, 8♥, 9♥ and 10♥. An exhaustive seven-card comparison finds **7 wins, 37 losses and no ties** among the 44 possible river cards. The seven winning cards each make Hero an ace-high flush while the opponent still holds three sevens.

Therefore the **raw flush-completion probability** is 9/44, about **20.45%**, but the **exact showdown equity against these revealed opponent cards** is 7/44, about **15.91%**. In another hand, some winning cards need not complete the obvious draw, so always enumerate *all* winning outcomes rather than assuming clean flush completions exhaust them.

**Pot price:** With 60 in the pot before the all-in bet, the bet creates a pot of 80. Hero's 20 call makes a final pot of 100. The threshold is **20/100 = 20%**, assuming no fees, side pots, ties, or tournament payout adjustment.

**Expected value relative to folding:** A winning call gains 80 from the pot already out there, and a losing call loses the additional 20.

\[
EV(\text{call})=\frac{7\times80-37\times20}{44}=-\frac{45}{11}\approx-4.09\text{ chips}.
\]

Counting all nine hearts as winners would instead produce the mistaken estimate

\[
\frac{9\times80-35\times20}{44}=\frac{5}{11}\approx+0.45\text{ chips},
\]

which **reverses the sign** of the conclusion. Neither calculation establishes what to do against a real unknown betting range.

**Future action:** In this problem the opponent is all-in. This closes their future betting. In a different flop scenario with a player retaining chips, the probability of completing a draw *by the river* does not pay for only one bet and guarantee a free second card. Further bets, equity realization and possible folds need separate assumptions.

**Tournament context:** The calculation measures chip EV, not ICM prize equity. Tournament stack distributions, prize payouts and potential bounties may alter a decision even if the chip arithmetic is correct. See the [tournament equity guide](https://nolankido.com/poker/tournament-equity/).

## Independent reproduction

Download or run the standard-library-only [exact river enumeration](https://nolankido.com/downloads/holdem-clean-outs-turn-verify.py). The same script can be [inspected directly in GitHub](https://github.com/nolankido/nolankido.github.io/blob/main/downloads/holdem-clean-outs-turn-verify.py) if your browser does not display the Python download:

```powershell
py -3 holdem-clean-outs-turn-verify.py --json
```

The script enumerates the 44 legal river cards and independently selects each player's best five of seven cards. It checks that the winning river set has exactly seven hearts and the two dirty heart completions are 2♥ and Q♥. It performs **no network requests, writes no files, makes no real-money decision and does not use solver outputs**.

Additional free context: [Pot-odds workshop](https://nolankido.com/poker/pot-odds-workshop/), [Hold'em flush and redraw lab](https://nolankido.com/poker/flush-and-redraw/), and [GTO Wizard's discussion of equity realization](https://blog.gtowizard.com/equity-realization/).

*Prepared November 22, 2026. All cards, chip amounts and opponent holdings are hypothetical and used solely for after-play education.*
