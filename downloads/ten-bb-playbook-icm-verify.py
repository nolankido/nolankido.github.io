#!/usr/bin/env python3
"""Reproduce one fictional three-player 10 BB ICM call after play.

Fixed inputs only, exact rational arithmetic, no network and no file writes.
Not a solver, opponent-range estimate, real hand or betting recommendation.
"""
from fractions import Fraction as F
from itertools import permutations
import json

PAYOUTS = (100, 60, 40)
HERO = 0
FOLD = (9, 21, 5)        # hero / small blind / button after hero folds
CALL_WIN = (20, 10, 5)  # hero / small blind / button after call wins
CALL_LOSE = (0, 30, 5) # hero is out in third place, pays $40
LAST_PRIZE = F(40)
PRICE = F(9, 20)         # 9 BB more to call for a 20 BB matched pot


def finish_probabilities(stacks):
    """Enumerate all 3! finishing orders using classic ICM chip shares."""
    if len(stacks) != 3 or any(x <= 0 for x in stacks):
        raise ValueError("Three positive stacks required; bust-out handled separately")
    totals = [F(0), F(0), F(0)]
    for order in permutations(range(3)):
        probability = F(1)
        remaining = sum(stacks)
        for player in order:
            probability *= F(stacks[player], remaining)
            remaining -= stacks[player]
        totals[order.index(HERO)] += probability
    if sum(totals) != 1:
        raise AssertionError("Finishing probabilities must total one")
    return tuple(totals)


def icm_value(stacks):
    return sum(prob * prize for prob, prize in zip(finish_probabilities(stacks), PAYOUTS))


def model():
    if len({sum(FOLD), sum(CALL_WIN), sum(CALL_LOSE)}) != 1:
        raise AssertionError("Chip conservation failed")
    fold = icm_value(FOLD)
    win = icm_value(CALL_WIN)
    lose = LAST_PRIZE
    threshold = (fold - lose) / (win - lose)
    rows = []
    for percent in (45, 50, 55, 60):
        p = F(percent, 100)
        call_value = p * win + (1 - p) * lose
        call_delta = call_value - fold
        chip_delta = 20 * p - 9
        rows.append({
            "assumed_win_percent": percent,
            "chip_ev_call_vs_fold_bb": float(chip_delta),
            "icm_call_value_dollars": float(call_value),
            "icm_call_minus_fold_dollars": float(call_delta),
            "icm_call_minus_fold_exact": str(call_delta),
        })
    return {
        "scope": "fictional three-handed ordinary payouts; no ante, bounty, deal or ties; no opponent range",
        "payouts_dollars": PAYOUTS,
        "stack_order": ["hero big blind", "small blind", "button"],
        "fold_stacks_bb": FOLD,
        "call_win_stacks_bb": CALL_WIN,
        "call_lose_stacks_bb": CALL_LOSE,
        "extra_call_bb": 9,
        "final_matched_pot_bb": 20,
        "fold_prize_exact": str(fold),
        "win_prize_exact": str(win),
        "lose_prize_exact": str(lose),
        "chip_price_exact": str(PRICE),
        "chip_price_percent": float(100 * PRICE),
        "icm_break_even_exact": str(threshold),
        "icm_break_even_percent": float(100 * threshold),
        "additional_required_win_percentage_points": float(100 * (threshold - PRICE)),
        "hypothetical_win_probabilities": rows,
        "real_hand_or_solver_verdict": "unknown; no opponent range or solver strategy inferred",
    }


if __name__ == "__main__":
    print(json.dumps(model(), indent=2))
