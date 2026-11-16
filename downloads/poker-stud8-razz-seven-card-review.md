# Private seven-card Stud8 and razz review

Blank study worksheet for use away from play. Do not submit completed private
hand notes to the website or use a computational aid where game rules prohibit it.

## 1. Identify the game and controlling rules

- Game: Stud Hi/Lo Eight-or-Better / Razz / Stud High / Other:
- Where were the rules checked (official site or room)?
- Is there an eight-or-better low qualifier?
- Are high and low both eligible for an award?
- Are there unusual house rules, a shared seventh card or a bring-in exception?
- All players eligible for the same pot, or side pots?
- Pot available after applicable charges and any special odd-chip rule:

## 2. Preserve the information at the relevant street

| Person | Hidden cards actually known at that time | Visible upcards at that time | Later exposed showdown cards |
| --- | --- | --- | --- |
| Hero | | | |
| Player B | | | |
| Player C | | | |
| Player D | | | |

- Did you write in a card that became known only after the decision?
- Complete number of distinct cards known or face up at this street:
- Rank/suit cards already unavailable for future deals:
- The resulting physically unknown deck size, if needed:
- Is this a decision-time information set or a completely exposed showdown?

## 3. Score each complete seven-card hand at showdown

Every ordinary seven-card player hand has `C(7,5) = 21` five-card subsets.
Stud8 chooses best conventional high and best five-distinct-rank ace-to-five
low at most eight independently. Razz chooses the best ace-to-five low, without
any eight qualifier. Straights and flushes do not penalize low. Pairs do.

| Player | Seven cards with exact suits | Best five for high, if Stud8 | Best five qualifying low, if any | Best five razz low |
| --- | --- | --- | --- | --- |
| A | | | | |
| B | | | | |
| C | | | | |

- Highest card of best low and the following ranks in descending order:
- Duplicate ranks? Does Stud8 low still qualify?
- Does your chosen best high use the same five cards as your best low?
- Best high player(s), Stud8 only:
- Best qualifying low player(s), Stud8 only:
- Best low player(s), razz only:

## 4. Settle only the eligible pot

- Stud8 high pool (full if no low qualifies, half otherwise):
- Stud8 qualifying low pool (half if any low qualifies):
- High tie distribution:
- Low tie distribution:
- Razz entire-pot best low distribution:
- Exact award to each player:
- Check that every award sums to the eligible pot:
- Contributions/net result are separate and need additional facts:

## 5. Street mechanics and uncertainty

- Third-street upcards and bring-in under this specific rule set:
- Fourth-street visible hands and who starts action:
- Fifth/sixth/seventh exposed hand and who starts action:
- Did a suit break a bring-in card tie? Do not carry it into showdown ranking.
- Which downcards and other players' future cards remain unknown?
- If using a count, what exactly is its numerator and denominator?
- Which new card would change the current result, not merely a visible rank?
- One question to verify away from the table:

To reproduce the fixed fictional Turn 18 examples with Python 3.10+:
`python poker-stud8-razz-seven-card-check.py --self-test`

Related: https://nolankido.com/poker/stud-hilo-razz-hand-reading/
