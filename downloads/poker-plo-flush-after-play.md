# Private PLO high flush-blocker and paired-board review

This is a blank, private-use worksheet for four-card Pot-Limit Omaha high.
Use after play. Never invent opponent cards or use this as live assistance.

## 1. Rules and known cards at the actual decision

- Variant and any special house rules:
- Street, action and time of observation:
- My four hole cards, with exact suits:
- Board cards, with exact suits and street order:
- Identified exposed rival hole cards, if any:
- Other exposed dead cards, if any:
- Unseen rivals are UNKNOWN, not a specific made hand:

## 2. The five-card hand must use two plus three

| Candidate holding or river | Exactly 2 private cards | Exactly 3 board cards | Legal high-hand category | Who is ahead under stated assumptions? |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |

- [ ] I used exactly two hole cards, not one or three.
- [ ] I used exactly three board cards, not four.
- [ ] I distinguished the nut flush from merely holding its ace blocker.

## 3. Count blockers in their proper information set

- Suited cards visibly known to me:
- Suited cards still unidentified:
- Does my blocker remove a named rival nut-flush holding? Which one?
- Does it also remove all lower flushes? Explain why or why not:
- If counting random four-card opponent hands, total deal combinations:
- Count rival holdings with two, three and four relevant suited cards:
- Specify whether rival actions were used to weight these holdings:

## 4. Board pairing and redraws

- Hero's exact current legal best five:
- Rival's exact legal best five, if known:
- Unknown river denominator (52 minus all identified physical cards):
- Paired-board ranks that actually improve the rival past the hero:
- Physical river cards available for each improving rank:
- Cards already blocked by hero, board or known rival hand:
- Repeated rivers counted under multiple threats and removed once:
- Hero wins / rival wins / ties under a fully specified showdown model:

Do not claim a winning-river percentage against an unknown range merely
because you can describe a type of hand the opponent might hold.

## 5. Decision boundary

- Pot and amount to call, without double counting existing wagers:
- Further action and future bets still possible:
- Main and side-pot eligibility, if relevant:
- Tournament prize or bounty differences, if relevant:
- What evidence would change this assumed opposing range?
- One card-count fact I verified:
- One limitation or unresolved question:

## Reproduce the separate fictional examples

Download `poker-plo-flush-pair-enumerator.py` from the guide, then run:

```text
python poker-plo-flush-pair-enumerator.py --self-test
```

Guide: https://nolankido.com/poker/plo-nut-flush-paired-board/

Official rules: https://www.pokerstars.com/poker/games/omaha/
and https://wsoponline.com/mi/learn-to-play-poker/omaha/rules/
