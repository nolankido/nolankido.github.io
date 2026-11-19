#!/usr/bin/env python3
"""Reproduce one fictional 10 BB money-bubble calculation, never a shove chart.

Guide: https://nolankido.com/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble
Python 3 standard library only. No network, user inputs, or file writes.
For after-play study, not real-time poker assistance.
"""

from fractions import Fraction as F
from functools import lru_cache
import json


# Four remain, three get ordinary cash prizes. Stack order: SB, CO, BTN, hero BB.
PRIZES = (50, 30, 20, 0)
START = (40, 30, 20, 10)
FOLD = (41, 30, 20, 9)
WIN = (30, 30, 20, 20)
LOSE = (50, 30, 20, 0)
HERO = 3


def finish_probabilities(stacks, hero):
    """Exact classic ICM finish probabilities by successive chip-share draws."""
    assert len(stacks) == 4 and all(stack > 0 for stack in stacks)

    @lru_cache(None)
    def visit(remaining):
        if hero not in remaining:
            return (F(0),) * 4
        place = 4 - len(remaining)
        total = sum(stacks[player] for player in remaining)
        result = [F(0)] * 4
        for winner in remaining:
            probability = F(stacks[winner], total)
            if winner == hero:
                result[place] += probability
            else:
                future = visit(tuple(player for player in remaining if player != winner))
                for index, share in enumerate(future):
                    result[index] += probability * share
        return tuple(result)

    probabilities = visit(tuple(range(4)))
    assert sum(probabilities) == 1
    return probabilities


def prize_equity(stacks, hero, prizes=PRIZES):
    return sum(prob * prize for prob, prize in zip(finish_probabilities(stacks, hero), prizes))


def example():
    assert sum(START) == sum(FOLD) == sum(WIN) == sum(LOSE) == 100
    fold_value = prize_equity(FOLD, HERO)
    win_value = prize_equity(WIN, HERO)
    loss_value = F(0)  # Hero is out fourth, and the fourth prize is zero.
    chip_threshold = F(9, 20)  # Nine additional BB into a 20 BB final pot.
    icm_threshold = (fold_value - loss_value) / (win_value - loss_value)

    for stacks in (FOLD, WIN):
        assert sum(prize_equity(stacks, player) for player in range(4)) == sum(PRIZES)
        for player in range(4):
            assert prize_equity(stacks, player, (100, 0, 0, 0)) == stacks[player]

    return {
        'scope': 'fictional four-player, three-paid no-ante call; no tie, bounty, deal or solver range',
        'stack_order': ['small blind', 'cutoff', 'button', 'hero big blind'],
        'before_posting_bb': START,
        'blinds_bb': [0.5, 1],
        'ante_bb': 0,
        'prizes_dollars': PRIZES,
        'hero_additional_call_bb': 9,
        'contested_final_pot_bb': 20,
        'uncalled_small_blind_refund_bb': 30,
        'branches': {
            name: {'stacks_bb': stacks, 'hero_model_prize_dollars': float(value),
                   'exact_value': str(value)}
            for name, stacks, value in (
                ('fold', FOLD, fold_value), ('call_win', WIN, win_value),
                ('call_lose', LOSE, loss_value),
            )
        },
        'chip_ev_call_threshold_percent': float(100 * chip_threshold),
        'classic_icm_call_threshold_percent': float(100 * icm_threshold),
        'classic_icm_threshold_exact': str(icm_threshold),
        'assumed_50_percent_call_model_dollars': float(F(1, 2) * win_value),
        'real_portland_meadows_range_or_icm_result': 'unknown; this calculation does not apply to that hand',
    }


if __name__ == '__main__':
    print(json.dumps(example(), indent=2))
