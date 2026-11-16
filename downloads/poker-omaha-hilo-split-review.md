# Private Omaha hi-lo eight-or-better showdown review

Blank study worksheet. Copy to your own device. Do not upload private player
records or use any computational aid during a game where it is disallowed.

## 1. Rules and information boundary

- Format and house rule source: 
- Date of study (not necessarily game date): 
- Exactly four hole cards per player? 
- Exactly two private cards and three board cards in each evaluated hand? 
- Single main pot, or different side-pot eligibility? 
- Fees, odd chips or other rules that change settlement? 
- Revealed cards versus unknown ranges: 
- What was actually known **at the decision time**, not at showdown? 

## 2. Physical cards

| Location | Cards with exact suits | Known or hypothetical? |
| --- | --- | --- |
| Board flop | | |
| Turn | | |
| River | | |
| Player A, four cards | | |
| Player B, four cards | | |
| Player C, if any | | |

- Check for any repeated physical card: 
- Total distinct exposed cards: 
- Unseen deck cards if computing a future river: 52 minus known cards = 

## 3. Two independent hand constructions per player

High: enumerate the possible two-hole and three-board combinations, then select
the strongest conventional five-card high. Low: start again with all combinations,
reject duplicate ranks and ranks above eight (ace equals one), then compare
qualifying five-card lows in descending order from highest card.

| Player | Two private + three board for best high | High rank | Two private + three board for best low | Low ranks or none |
| --- | --- | --- | --- | --- |
| A | | | | |
| B | | | | |
| C | | | | |

- Does the board contain at least three **distinct** ranks from ace to eight? 
- Any wheels? Note that these may also be five-high straights for high: 
- Any low ties? Did any river change who wins low without removing qualification? 
- Winner(s) of high: 
- Winner(s) of qualifying low, if any: 

## 4. Pot award versus decision value

- Eligible pot in chips after any applicable fees: 
- High pool: full pot if there is no qualifying low, otherwise half: 
- High winner(s) and precise shares: 
- Low pool if qualifying: 
- Low winner(s) and precise shares: 
- Total award to each player: 
- Confirm all awards add to the eligible pot: 
- Pot contributions and each player's net result, **if actually known**: 
- Costs of any future decisions **not** modeled by a showdown award: 

## 5. Uncertainty and source control

- Known cards versus assumed opponent holdings: 
- If varying a card, is this a new deal or a single remaining river? 
- If reporting a percentage, write the exact numerator, denominator and condition: 
- Is the statistic about **low winner**, whole-pot award or something else? 
- Official house rules versus independently calculated result: 
- One thing to review away from play: 
- A misleading assumption to avoid next time: 

For the fixed fictional Turn 17 examples, reproduce with
`python poker-omaha-hilo-split-enumerator.py --self-test`.
The script is local and uses only the Python standard library.

Related: https://nolankido.com/poker/omaha-hilo-scoop-quarter-counterfeit/
