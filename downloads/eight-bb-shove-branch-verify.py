#!/usr/bin/env python3
"""Reproduce one fictional eight-big-blind cutoff shove against a covering BB.

Fixed nine-handed big-blind-ante fixture, one conditional caller, no ties.
Standard library only, no files, network, opponent ranges or in-play advice.
"""
from fractions import Fraction as F
import json

STARTING_POT = F(5, 2)  # SB 0.5 + live BB 1 + one dead BB ante 1.
CO_SHOVE = F(8)        # CO starts unposted with 8 BB.
BB_LIVE = F(1)
BB_ADDITIONAL_CALL = CO_SHOVE - BB_LIVE
FINAL_POT = STARTING_POT + CO_SHOVE + BB_ADDITIONAL_CALL
CO_CALLED_WIN_NET = FINAL_POT - CO_SHOVE
CO_CALLED_LOSS_NET = -CO_SHOVE


def shove_ev(fold_probability, win_if_called):
    """Chip EV relative to CO folding before investing any chips."""
    f, q = F(fold_probability), F(win_if_called)
    if not (0 <= f <= 1 and 0 <= q <= 1):
        raise ValueError("Probabilities must lie between zero and one")
    return f * STARTING_POT + (1 - f) * (
        q * CO_CALLED_WIN_NET + (1 - q) * CO_CALLED_LOSS_NET
    )


def fold_break_even(win_if_called):
    """Minimum all-fold chance when the called branch has negative chip EV."""
    q = F(win_if_called)
    called_ev = shove_ev(0, q)
    if called_ev >= 0:
        return F(0)
    return -called_ev / (STARTING_POT - called_ev)


def called_win_break_even(fold_probability):
    """Indifference showdown win probability when the call branch exists."""
    f = F(fold_probability)
    if not (0 <= f < 1):
        raise ValueError("Conditional win chance is undefined if everyone always folds")
    return ((1 - f) * CO_SHOVE - f * STARTING_POT) / (
        (1 - f) * FINAL_POT
    )


def audit():
    if FINAL_POT != F(35, 2) or CO_CALLED_WIN_NET != F(19, 2):
        raise AssertionError("Full blind and ante ledger changed")
    thresholds = {
        "BB_extra_call_chip_price": BB_ADDITIONAL_CALL / FINAL_POT,
        "CO_win_chance_if_always_called": called_win_break_even(0),
        "CO_all_fold_chance_if_called_win_40pct": fold_break_even(F(2, 5)),
        "CO_win_if_called_at_all_fold_30pct": called_win_break_even(F(3, 10)),
        "CO_all_fold_chance_if_called_win_30pct": fold_break_even(F(3, 10)),
        "CO_no_equity_all_fold_chance_with_BBA": fold_break_even(0),
        "CO_no_equity_all_fold_chance_without_ante": CO_SHOVE / (CO_SHOVE + F(3, 2)),
    }
    expected = {
        "BB_extra_call_chip_price": F(2, 5),
        "CO_win_chance_if_always_called": F(16, 35),
        "CO_all_fold_chance_if_called_win_40pct": F(2, 7),
        "CO_win_if_called_at_all_fold_30pct": F(97, 245),
        "CO_all_fold_chance_if_called_win_30pct": F(11, 21),
        "CO_no_equity_all_fold_chance_with_BBA": F(16, 21),
        "CO_no_equity_all_fold_chance_without_ante": F(16, 19),
    }
    if thresholds != expected:
        raise AssertionError("Break-even thresholds differ from the exact audit")

    cases = (
        ("30pct_folds_40pct_called_wins", F(3, 10), F(2, 5), F(1, 20)),
        ("28pct_folds_40pct_called_wins", F(7, 25), F(2, 5), -F(1, 50)),
        ("30pct_folds_30pct_called_wins", F(3, 10), F(3, 10), -F(47, 40)),
        ("exact_fold_boundary", F(2, 7), F(2, 5), F(0)),
        ("exact_called_win_boundary", F(3, 10), F(97, 245), F(0)),
    )
    observed = {}
    for label, f, q, required_ev in cases:
        value = shove_ev(f, q)
        if value != required_ev:
            raise AssertionError("Conditional branch error: " + label)
        observed[label] = {
            "joint_all_fold_probability": str(f),
            "win_probability_conditional_on_BB_call": str(q),
            "EV_shove_minus_fold_bb": str(value),
        }
    return {
        "scope": "Fictional 8 BB CO first in; BTN and SB fold; BB-only caller; 0.5/1 BB plus one 1 BB BBA",
        "limits": "Two terminal shove branches only; no ties, opponent range, ICM, bounty, small-open/limp EV or real recommendation",
        "initial_dead_and_live_pot_bb": str(STARTING_POT),
        "CO_unposted_shove_bb": str(CO_SHOVE),
        "BB_live_blind_bb": str(BB_LIVE),
        "BB_dead_ante_bb": "1",
        "BB_additional_call_bb": str(BB_ADDITIONAL_CALL),
        "contested_pot_if_called_bb": str(FINAL_POT),
        "CO_called_win_net_bb": str(CO_CALLED_WIN_NET),
        "CO_called_loss_net_bb": str(CO_CALLED_LOSS_NET),
        "exact_thresholds": {k: str(v) for k, v in thresholds.items()},
        "fictional_sensitivity": observed,
        "checks": "pass: exact chip ledger, asymmetric decision prices and conditional branch roots",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
