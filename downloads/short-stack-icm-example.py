#!/usr/bin/env python3
"""Fixed four-player teaching arithmetic. Not a solver or an at-table tool.

Guide: https://nolankido.com/poker/short-stack-decisions/#icm-call
Python 3, standard library only. Run to print the assumptions and calculations.
No hand ranges, network requests, user inputs or file writes.
"""
from fractions import Fraction as F
from functools import lru_cache
import json

PRIZES = (50, 30, 20, 0)
START = (40, 30, 20, 10)  # SB, C, hero BB, D; before posting, no ante.
FOLD = (41, 30, 19, 10)
WIN = (20, 30, 40, 10)
LOSE = (60, 30, 0, 10)
HERO = 2


def finish_probabilities(stacks, hero):
    """Classic ICM: choose each next finisher by remaining chip share."""
    assert len(stacks) == 4 and all(x > 0 for x in stacks)
    @lru_cache(None)
    def walk(alive):
        if hero not in alive:
            return (F(0),) * 4
        rank = 4 - len(alive)
        result = [F(0)] * 4
        total = sum(stacks[i] for i in alive)
        for winner in alive:
            chance = F(stacks[winner], total)
            if winner == hero:
                result[rank] += chance
            else:
                rest = walk(tuple(i for i in alive if i != winner))
                for place, probability in enumerate(rest):
                    result[place] += chance * probability
        return tuple(result)
    result = walk(tuple(range(4)))
    assert sum(result) == 1
    return result


def prize_value(stacks, hero, prizes=PRIZES):
    return sum(p * prize for p, prize in zip(finish_probabilities(stacks, hero), prizes))


def example():
    assert sum(START) == sum(FOLD) == sum(WIN) == sum(LOSE) == 100
    fold = prize_value(FOLD, HERO)
    win = prize_value(WIN, HERO)
    lose = F(0)  # Hero is eliminated fourth; fourth prize is zero.
    chip = F(19, 40)
    threshold = (fold - lose) / (win - lose)
    for stacks in [FOLD, WIN]:
        assert sum(prize_value(stacks, i) for i in range(4)) == sum(PRIZES)
        assert prize_value(stacks, HERO, (100, 0, 0, 0)) == F(100 * stacks[HERO], sum(stacks))
    return {
        'assumptions': {
            'game': 'four remaining, standard NLHE tournament, SB shoves after C/D fold',
            'stack_order': ['SB', 'C', 'hero BB', 'D'],
            'starting_stacks_bb': START, 'blinds_bb': [0.5, 1], 'ante_bb': 0,
            'prizes_dollars': PRIZES, 'bounties_deals_deductions': False,
            'ties': 'excluded from the two-outcome comparison',
            'hero_additional_call_bb': 19, 'contested_pot_bb': 40,
            'uncalled_SB_refund_bb': 20,
            'range_or_hand_equity': 'not supplied; required probability only',
        },
        'branches': {
            name: {'stacks_bb': stacks, 'hero_prize_equity': float(value),
                   'exact_value': str(value),
                   'hero_finish_probabilities': [str(p) for p in finish_probabilities(stacks, HERO)] if name != 'lose' else ['0', '0', '0', '1']}
            for name, stacks, value in [('fold', FOLD, fold), ('win', WIN, win), ('lose', LOSE, lose)]
        },
        'chip_ev_threshold_percent': float(chip * 100),
        'classic_icm_threshold_percent': float(threshold * 100),
        'classic_icm_threshold_exact': str(threshold),
        'zero_equity_joint_fold_boundaries_percent': {
            '2bb_raise_2.5bb_pot': float(F(2, 2 + F(5, 2)) * 100),
            '20bb_shove_2.5bb_pot': float(F(20, 20 + F(5, 2)) * 100),
            '15bb_shove_no_ante': float(F(15, 15 + F(3, 2)) * 100),
            '15bb_shove_1bb_BBA': float(F(15, 15 + F(5, 2)) * 100),
        },
    }


if __name__ == '__main__':
    print(json.dumps(example(), indent=2))
