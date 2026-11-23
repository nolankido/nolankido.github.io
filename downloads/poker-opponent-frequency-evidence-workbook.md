# What Does a Small Sample Say About a Poker Opponent?

An original opportunity-denominator and statistical-uncertainty workbook
Nolan Kido | November 22, 2026 | Free after-play study

Main guide: https://nolankido.com/poker/poker-under-uncertainty/#frequencies
Independent fixed-case arithmetic: https://nolankido.com/downloads/poker-opponent-frequency-verify.py

**Purpose:** Learn to separate a count of actions from the *eligible opportunities* to take those actions. The examples are invented, not player statistics or advice for a live hand. No account, hand upload, paid solver, or network access is required. Complete this away from play and follow the room's or site's assistance rules. A sample is not a read on a particular opponent.

## 1. Define the event before counting

For the **3-bet opportunity** example, the question is: When another player had already made a preflop raise and this player could legally reraise, what did this player do? Use a consistent tracker definition, and confirm what hands or facing-action states that definition includes.

| Field | Fictional review record |
| --- | --- |
| Total hands dealt to the fictional player | 50 |
| Hands in which the player faced an eligible 3-bet opportunity | 12 |
| Eligible times the player reraised | 3 |
| Eligible times the player did not reraise | 9 |
| Hands with no eligible reraise opportunity | 38 |
| Opponent's full cards, intentions, actual range, and context-specific frequencies | Unknown |

The numerator is **3 reraises** and the relevant denominator for this conditional statistic is **12 eligible opportunities**, yielding **3 / 12 = 25% observed 3-bet frequency**.

The ratio **3 / 50 = 6%** answers the different question "how many of all hands dealt included an observed 3-bet?" It is **not** the frequency of 3-betting *when the player could do so*. An observer who remembers only three reraises but not the opportunity denominator cannot calculate a defensible 3-bet rate from that count alone.

This invented record does not show position, action sequence details, stack depth, ante, table size, card distribution, bet sizing, or whether all 12 opportunities are comparable. Those unknowns matter more than a precise-looking decimal.

## 2. Do the work before opening the answer

1. Write the numerator, the relevant opportunity denominator, and the observed frequency: ______ / ______ = ______%.
2. Why does dividing by 50 change the meaning of the statistic? _______________________.
3. Is an observed 25% the *known true probability* that the player will reraise the next eligible hand? Why or why not? _______________________.
4. List three conditions that could make these 12 opportunities non-comparable: _______________________.
5. A different *fictional* sample has 8 reraises in 40 eligible opportunities. What is its observed rate? Which sample should generally give a narrower binomial-model interval? _______________________.
6. If the player has zero reraises in 12 eligible opportunities, is their true rate proved to be zero? _______________________.
7. Under the explicitly assumed Beta(6,24) prior below, how does observing 3 successes and 9 failures change the prior? _______________________.

## 3. An interval is not a player read

Under the **simplifying assumption** that eligible trials have one stable probability and act like independent Bernoulli observations, the two-sided 95% Wilson *score confidence interval* for **3 / 12** is about **8.9% to 53.2%**.

For the second fictional sample, **8 / 40 = 20%**, the same Wilson method gives about **10.5% to 34.8%**. The interval for the larger sample is narrower, though not narrow enough to guarantee any specific future opponent action. These intervals describe the long-run coverage of the Wilson procedure *when its model assumptions apply*. They do not mean there is a 95% probability that this particular opponent's fixed unknown rate is inside the interval.

The calculation uses the 97.5th percentile of the standard normal, z approximately 1.959964. For observed proportion p = x/n, set d = 1 + z²/n. The center is (p + z²/(2n)) / d, and the half-width is z × sqrt(p(1-p)/n + z²/(4n²)) / d. The endpoints are center minus and plus half-width. Do not use a simple p ± 1.96 × standard error here and assume its small-sample coverage is accurate.

Changing the 12 observations into hundreds of unrecorded or ineligible hands does **not** increase the sample size. If observations mix distinct stack depths, positions, previous actions or table states, even 40 eligible observations may not follow a common-probability binomial model.

## 4. One explicit prior gives a different kind of answer

Suppose, **for teaching only**, that the conditional 3-bet probability has a Beta(6,24) prior. This is not an empirically validated population estimate. Its prior mean is **6 / 30 = 20%**, with prior concentration 30. The 3 successes and 9 failures produce a Beta(**9,33**) posterior.

The posterior mean is **9 / 42 = 21.43%**, not the 25% raw sample proportion. The equal-tailed **95% Bayesian credible interval**, *conditional on that prior and likelihood*, is about **10.6% to 34.9%**. Unlike the Wilson interval, the posterior interval is a probability statement about the model's parameter given the **specified** assumptions. Neither interval makes the poker situation automatically comparable or establishes the opponent's real decision strategy.

With an alternative Beta(1,1) uniform prior, those same observations yield Beta(4,10), with posterior mean **4 / 14 = 28.57%**. This difference is prior sensitivity, not evidence that a player changed behavior.

**Do not transfer a prior between populations, games, or positions without evidence.** For illustration, a modeled conditional frequency cannot become a verified 3-betting range, and a whole-range frequency does not identify exact holding combinations or their action probabilities.

## 5. A second denominator trap

A hypothetical tracker reports a flop continuation bet **7 times** when this player had **8 eligible continuation-bet opportunities**, and the player happened to see **30 flops** altogether.

Under that stipulated convention, the conditional continuation-bet observation is **7 / 8 = 87.5%**, not 7 / 30 = 23.3%. It may be an unreliable small sample, and software definitions can differ. It is not evidence that 87.5% of all flop hands will be bet, nor that any particular flop bet is a bluff.

A statistic also needs its **time window**, **eligibility rule**, **position or action conditioning**, **data source**, and **permission to collect or use that data**. Do not record identifying third-party information just to complete this worksheet. Treat missing opportunity counts as unknown rather than substituting dealt hands.

## 6. Blank, private evidence record

| Question | Your post-session notes |
| --- | --- |
| Precisely defined action or outcome | |
| Eligible opportunity definition | |
| Observed successes x | |
| Verified opportunities n | |
| Excluded situations and why excluded | |
| Position, stack, stage, prior actions and other context | |
| Time window, permitted source and recording limits | |
| Which facts are recorded versus reconstructed | |
| Conditions under which one stable p might be implausible | |
| Reported observed x/n, with denominator attached | |
| Optional interval and exact statistical assumptions | |
| Missing evidence and one next research question | |

Leave fields blank when unknown. Use this only for authorized post-session study; the worksheet contains no submission fields and never requires a real opponent's identity.

## 7. Reveal and audit the fixed example answers

1. **3 / 12 = 25%.** The denominator is eligible 3-bet opportunities.
2. **3 / 50 = 6%** counts reraises per dealt hand, not per eligible reraise opportunity.
3. **No.** The observed rate is a sample summary, not a known future probability or hand range.
4. Position, starting stack, bet sizing or facing-action history, tournament stage, and table composition are examples of relevant possible differences.
5. **8 / 40 = 20%**. Under the common-probability binomial model, its Wilson interval, about **10.5% to 34.8%**, is narrower than the **8.9% to 53.2%** interval for 3 / 12.
6. **No.** Even **0 / 12** has a Wilson upper endpoint of roughly **24.2%** under the stipulated model.
7. Beta(6+3, 24+9) = **Beta(9,33)**. Posterior mean = 9/42 = **21.43%**. The alternative Beta(1,1) prior gives Beta(4,10) with mean **28.57%**.

**Further check:** Run the [fixed-case Python verifier](https://nolankido.com/downloads/poker-opponent-frequency-verify.py) with \`python poker-opponent-frequency-verify.py --self-test\` or \`--json\`. It uses only Python's standard library; it does not request data or advise on real hands. The verifier reports the same fictional Wilson and Beta results and rejects invalid counts.

**Editorial boundary:** This is a separate, original companion to the already published [Poker Under Uncertainty](https://nolankido.com/poker/poker-under-uncertainty/#frequencies) guide, not a copied book chapter, real HUD export, population statistic or strategy recommendation. Prepared with AI assistance. The mathematical method is conditional on the model, and the underlying game information remains unknown.
