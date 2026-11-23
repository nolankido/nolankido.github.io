#!/usr/bin/env python3
"""Fixed fictional three-way tournament call: chips, side pots and prize ICM.

Standard library only. No opponent estimates, live advice, user data, network,
real-hand input, rake, bounties, ties, or betting after the call. All inputs
are fixed for the after-play worksheet; not a poker solver.

Run with Python 3.10+: python poker-multiway-icm-verify.py --self-test
"""
from fractions import Fraction as F
from itertools import permutations
import argparse
import json

PLAYERS = ('X', 'H', 'Y')
START = (4, 14, 9)  # BTN, hero SB, BB before posting
PRIZES = (70, 30, 0)
PAID = (4, 4, 9)  # Contributions before hero's closing decision
EXTRA = 5
# A single joint distribution of strict showdown rankings, conditional on
# the stated prior actions. The other three orders have zero assigned mass.
RANK_WEIGHTS = ((('H', 'Y', 'X'), F(1, 10)),
                (('X', 'H', 'Y'), F(3, 10)),
                (('X', 'Y', 'H'), F(3, 5)))


def require(condition, case):
    if not condition:
        raise ArithmeticError('Multiway ICM check failed: ' + case)


def settle(order, call):
    """Settle the actual remaining eligible players, including unmatched chips."""
    if tuple(sorted(order)) != tuple(sorted(PLAYERS)):
        raise ValueError('Expected one strict ranking of all three hands')
    if type(call) is not bool:
        raise ValueError('Call flag must be a boolean')
    contributions = list(PAID)
    if call:
        contributions[1] += EXTRA
    behind = [start - paid for start, paid in zip(START, contributions)]
    active = set(PLAYERS) if call else {'X', 'Y'}
    previous = 0
    for level in sorted(set(contributions)):
        contributors = [i for i, paid in enumerate(contributions) if paid >= level]
        amount = (level - previous) * len(contributors)
        previous = level
        if len(contributors) == 1:
            # The uncalled portion of the covering raise is returned to Y.
            behind[contributors[0]] += amount
        else:
            eligible = {PLAYERS[i] for i in contributors} & active
            require(bool(eligible), 'every contested pot has an eligible player')
            winner = next(name for name in order if name in eligible)
            behind[PLAYERS.index(winner)] += amount
    require(sum(behind) == sum(START) and min(behind) >= 0,
            'every chip is assigned exactly once')
    return tuple(behind)


def prize_values(stacks):
    """Classic ICM conditional on terminal stacks and stipulated bust order.

    In this fixture only hero can remain alone. If both opponents bust in
    the same hand, Y (larger starting stack) receives second, X third.
    This finish-order convention is part of the toy event, not a house rule.
    """
    if len(stacks) != 3 or any(type(v) is not int or v < 0 for v in stacks) or sum(stacks) != sum(START):
        raise ValueError('Expected a nonnegative integer three-stack state totaling 27')
    alive = tuple(i for i, n in enumerate(stacks) if n > 0)
    eliminated = sorted((i for i, n in enumerate(stacks) if n == 0), key=START.__getitem__)
    values = [F(0)] * 3
    for place, i in enumerate(eliminated):
        values[i] = F(PRIZES[2 - place])
    for order in permutations(alive):
        probability, chips = F(1), sum(stacks)
        for i in order:
            probability *= F(stacks[i], chips)
            chips -= stacks[i]
        for place, i in enumerate(order):
            values[i] += probability * PRIZES[place]
    require(sum(values) == sum(PRIZES), 'entire prize pool is allocated')
    return tuple(values)


def branch_report():
    require(sum(weight for _, weight in RANK_WEIGHTS) == 1 and all(weight >= 0 for _, weight in RANK_WEIGHTS),
            'ranking probabilities form a distribution')
    rows = []
    chips = {choice: F(0) for choice in ('fold', 'call')}
    expected = {choice: [F(0)] * 3 for choice in ('fold', 'call')}
    for ranking, weight in RANK_WEIGHTS:
        row = {'ranking': ' > '.join(ranking), 'probability': str(weight)}
        for choice in ('fold', 'call'):
            stacks = settle(ranking, choice == 'call')
            prizes = prize_values(stacks)
            chips[choice] += weight * stacks[1]
            for i, value in enumerate(prizes):
                expected[choice][i] += weight * value
            row[choice] = {'stacks_X_H_Y': list(stacks),
                           'prize_equities_X_H_Y': [str(p) for p in prizes]}
        rows.append(row)
    require(all(sum(values) == 100 for values in expected.values()), 'expected prize pool conservation')
    main_win = sum(w for order, w in RANK_WEIGHTS if order[0] == 'H')
    side_win = sum(w for order, w in RANK_WEIGHTS if order.index('H') < order.index('Y'))
    require(chips['call'] - chips['fold'] == 12 * main_win + 10 * side_win - EXTRA,
            'eligible-pot chip EV agrees with branch ledger')
    return {'scope': 'Fictional closed-action after-play study only; no actual ranges or strategy',
            'starting_stacks_X_H_Y': list(START), 'prizes': list(PRIZES),
            'additional_call_bb': EXTRA, 'main_pot_bb': 12, 'side_pot_bb': 10,
            'main_win_probability': str(main_win), 'side_win_probability': str(side_win),
            'branches': rows,
            'hero_expected_chips': {k: str(v) for k, v in chips.items()},
            'expected_prizes_X_H_Y': {k: [str(v) for v in vals] for k, vals in expected.items()},
            'hero_call_minus_fold_chips': str(chips['call'] - chips['fold']),
            'hero_call_minus_fold_prizes': str(expected['call'][1] - expected['fold'][1])}


def verify():
    report = branch_report()
    expected_states = (((0, 10, 17), (0, 27, 0)),
                       ((12, 10, 5), (12, 15, 0)),
                       ((12, 10, 5), (12, 5, 10)))
    for row, (fold, call) in zip(report['branches'], expected_states):
        require(tuple(row['fold']['stacks_X_H_Y']) == fold and tuple(row['call']['stacks_X_H_Y']) == call,
                'expected fold/call settlement for ' + row['ranking'])
    require(report['hero_expected_chips'] == {'fold': '10', 'call': '51/5'}, 'expected chips')
    require(report['main_win_probability'] == '1/10' and report['side_win_probability'] == '2/5', 'pot probabilities')
    require(F(report['expected_prizes_X_H_Y']['fold'][1]) == F(11312, 297), 'fold prize value')
    require(F(report['expected_prizes_X_H_Y']['call'][1]) == F(5366, 153), 'call prize value')
    require(report['hero_call_minus_fold_chips'] == '1/5' and
            report['hero_call_minus_fold_prizes'] == '-15226/5049', 'opposite objective comparisons')
    require(prize_values((0, 27, 0)) == (F(0), F(70), F(30)), 'stipulated simultaneous elimination order')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='Verify the fixed study ledger')
    args = parser.parse_args()
    result = verify()
    if args.self_test:
        print('PASS: fictional three-way main/side pot and prize ICM arithmetic')
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
