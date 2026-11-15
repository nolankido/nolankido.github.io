# Private PLO high hand review: wraps, blockers and redraws

Use after a session. Leave private identifying details out. This is for standard
four-card Omaha high and is not a live assistance tool or an action chart.

## 1. Information actually available at the decision

- Street and action sequence:
- My four hole cards, with suits:
- Community board, in order and with suits:
- Opponents' hole cards that were actually visible, if any:
- Other known exposed dead cards, if any:
- Unknown opponents: label as UNKNOWN, never invent exact cards:
- Side pots or special house/variant rules, if relevant:

## 2. Name the question before counting

- [ ] Does one *next* card give me any legal straight?
- [ ] Which next cards beat one *fully specified* opponent hand?
- [ ] Which rivers win after the turn with both hands exposed?
- [ ] This question needs an opponent *range*. Exact physical outs alone are insufficient.

## 3. Enforce the exact two-plus-three rule

For each proposed completion, show one five-card selection:

| Candidate board card | Exactly two of my hole cards | Exactly three board cards | Best legal five | Winner known? |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |

- Did I accidentally use a third hole card? [ ] Yes [ ] No
- Did I accidentally use four board cards? [ ] Yes [ ] No

## 4. Unseen cards, blockers and distinct outcomes

- Number of named known physical cards:
- Total remaining possibilities: 52 minus known physical cards =
- Candidate physical completion cards before exposed blockers:
- Exposed, identified blockers among those cards:
- Remaining distinct cards completing the target hand:
- Cards that complete the hand *and* win against a specified hand:
- Overlap between straight/flush/full-house threats removed once:
- Actual distinct opponent-winning river cards, if both hands known:
- Ties, if any:
- Probability with its explicitly stated information set:

If only my cards and the flop are known, there are 45 unseen cards. A face-up
flop with both players' four-card hands revealed leaves 41. A face-up turn with
both four-card hands revealed leaves 40. Other named dead cards change these
denominators.

## 5. Separate the card result from the betting decision

- Pot and amount to call, without double-counting bets:
- What future streets and betting remain:
- Range assumptions, evidence and uncertainty:
- Cash, tournament or split-pot format; any payout or side-pot implications:
- One fact independently checked:
- One assumption that would change the conclusion:
- Next narrow study question:

## Reproducible fictional reference

The accompanying `poker-plo-wrap-enumerator.py` runs offline:

```text
python poker-plo-wrap-enumerator.py --self-test
```

Guide: https://nolankido.com/poker/plo-wrap-redraw-blockers/

Rule sources: https://www.pokerstars.com/poker/games/omaha/
and https://wsoponline.com/mi/learn-to-play-poker/omaha/rules/
