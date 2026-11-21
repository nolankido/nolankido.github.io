#!/usr/bin/env python3
"""Independent, exact three-player ICM tournament-prize audit.

Companion: https://nolankido.com/poker/tournament-equity/#icm-reproduce
Standard-library only, fixed fictional inputs, no network or file writes.
Not a poker solver, chart, in-game aid or real-hand recommendation.
"""
from fractions import Fraction as F
from itertools import permutations
import json

STACKS_BEFORE = (10, 10, 10)  # hero, opponent, uninvolved player
HERO_WINS = (20, 0, 10)
HERO_LOSES = (0, 20, 10)
PRIZE_LADDERS = (
    ("standard_50_30_20", (50, 30, 20)),
    ("front_loaded_60_40_0", (60, 40, 0)),
    ("winner_only_100_0_0", (100, 0, 0)),
)


def icm_values(stacks: tuple[int, ...], prizes: tuple[int, ...]) -> tuple[F, ...]:
    """Enumerate each finish order under classical chip-share ICM exactly."""
    if len(stacks) != 3 or len(prizes) != 3:
        raise ValueError("Use exactly three players and three prizes")
    if any(type(x) is not int or x < 0 for x in stacks + prizes):
        raise ValueError("Stacks and prizes must be nonnegative integers")
    if sum(stacks) <= 0 or sum(prizes) <= 0 or list(prizes) != sorted(prizes, reverse=True):
        raise ValueError("Positive total chips, prize pool and descending prizes required")
    active = [i for i, chips in enumerate(stacks) if chips]
    eliminated = [i for i, chips in enumerate(stacks) if not chips]
    if len(eliminated) > 1:
        raise ValueError("This toy example handles at most one eliminated player")

    total = sum(stacks)
    values = [F(0) for _ in stacks]
    for finish_order in permutations(active):
        probability = F(1)
        remaining = total
        for player in finish_order:
            probability *= F(stacks[player], remaining)
            remaining -= stacks[player]
        for rank, player in enumerate(finish_order):
            values[player] += probability * prizes[rank]
    if eliminated:
        values[eliminated[0]] = F(prizes[-1])
    if sum(values) != sum(prizes):
        raise AssertionError("ICM prize pool is not conserved")
    return tuple(values)


def scenario(prizes: tuple[int, int, int]) -> dict:
    before = icm_values(STACKS_BEFORE, prizes)
    win = icm_values(HERO_WINS, prizes)
    lose = icm_values(HERO_LOSES, prizes)
    if len({sum(STACKS_BEFORE), sum(HERO_WINS), sum(HERO_LOSES)}) != 1:
        raise AssertionError("Chips not conserved across scenarios")
    if win[0] <= lose[0]:
        raise AssertionError("The winner must improve in the modeled prize structure")
    required = (before[0] - lose[0]) / (win[0] - lose[0])
    return {
        "prizes_dollars": prizes,
        "before_stacks": STACKS_BEFORE,
        "win_stacks": HERO_WINS,
        "lose_stacks": HERO_LOSES,
        "before_prize_equities_exact": [str(x) for x in before],
        "win_prize_equities_exact": [str(x) for x in win],
        "lose_prize_equities_exact": [str(x) for x in lose],
        "hero_prize_break_even_exact": str(required),
        "hero_prize_break_even_percent": float(required * 100),
        "equal_chip_transfer_break_even_exact": "1/2",
    }


def verify() -> dict:
    scenarios = {name: scenario(prizes) for name, prizes in PRIZE_LADDERS}
    thresholds = {name: F(row["hero_prize_break_even_exact"]) for name, row in scenarios.items()}
    if thresholds != {
        "standard_50_30_20": F(4, 7),
        "front_loaded_60_40_0": F(5, 8),
        "winner_only_100_0_0": F(1, 2),
    }:
        raise AssertionError("The payout sensitivity thresholds no longer agree")

    base = icm_values(STACKS_BEFORE, (50, 30, 20))
    win = icm_values(HERO_WINS, (50, 30, 20))
    lose = icm_values(HERO_LOSES, (50, 30, 20))
    q = F(55, 100)  # Hypothetical showdown probability, not a measured range.
    call_equities = [q * x + (1 - q) * y for x, y in zip(win, lose)]
    if sum(call_equities) != 100:
        raise AssertionError("The probability-weighted expected prizes are not conserved")
    if call_equities[0] - base[0] != -F(1, 2):
        raise AssertionError("55% hero sensitivity failed")
    if win[2] != lose[2] or win[2] - base[2] != F(10, 3):
        raise AssertionError("Uninvolved player's prize gain failed")
    return {
        "purpose": "Independent exact-fraction audit of a fictional three-player ICM transfer",
        "limits": "No blinds, ante, ties, bounties, payout deals, skill or future-game effects; no strategy or hand-equity estimate",
        "stack_order": ["hero", "opponent", "uninvolved player"],
        "chip_total": sum(STACKS_BEFORE),
        "payout_ladders_same_total_pool_dollars": 100,
        "scenarios": scenarios,
        "hypothetical_55_percent_standard_ladder": {
            "hero_call_equity_exact": str(call_equities[0]),
            "hero_fold_equity_exact": str(base[0]),
            "hero_call_minus_fold_exact": str(call_equities[0] - base[0]),
            "hero_expected_chips": 11,
            "hero_chips_if_fold": 10,
            "uninvolved_player_equity_exact": str(call_equities[2]),
            "uninvolved_player_gain_over_no_gamble_exact": str(call_equities[2] - base[2]),
            "all_players_expected_prizes_exact": [str(v) for v in call_equities],
        },
        "checks": "pass: conserved chips, conserved prize pool and exact ICM thresholds",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
