#!/usr/bin/env python3
"""Audit fixed, fictional poker frequency denominators and two interval models.

Python 3.10+ standard library only. No hand histories, input data, network
requests, personal information, solver or at-table advice.

Usage:
    python poker-opponent-frequency-verify.py
    python poker-opponent-frequency-verify.py --json
    python poker-opponent-frequency-verify.py --self-test
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import comb, sqrt
from statistics import NormalDist


Z = NormalDist().inv_cdf(0.975)


def observed_rate(successes: int, eligible: int) -> Fraction:
    if type(successes) is not int or type(eligible) is not int:
        raise ValueError("Counts must be integers, not estimated fractions")
    if eligible <= 0 or successes < 0 or successes > eligible:
        raise ValueError("Must have 0 <= successes <= eligible and eligible > 0")
    return Fraction(successes, eligible)


def wilson_interval(successes: int, eligible: int) -> tuple[float, float]:
    p = float(observed_rate(successes, eligible))
    d = 1 + Z * Z / eligible
    center = (p + Z * Z / (2 * eligible)) / d
    half = Z * sqrt(p * (1 - p) / eligible + Z * Z / (4 * eligible**2)) / d
    return max(0.0, center - half), min(1.0, center + half)


def beta_cdf(x: float, alpha: int, beta: int) -> float:
    """For integer alpha/beta, beta CDF is an exact-form binomial upper tail."""
    if type(alpha) is not int or type(beta) is not int or min(alpha, beta) <= 0:
        raise ValueError("This fixed-case verifier requires positive integer Beta shapes")
    if not 0 <= x <= 1:
        raise ValueError("Beta CDF needs x in 0..1")
    n = alpha + beta - 1
    return sum(comb(n, k) * x**k * (1 - x)**(n - k)
               for k in range(alpha, n + 1))


def beta_quantile(tail: float, alpha: int, beta: int) -> float:
    if not 0 < tail < 1:
        raise ValueError("Tail quantile must be between zero and one")
    lo, hi = 0.0, 1.0
    for _ in range(85):
        middle = (lo + hi) / 2
        if beta_cdf(middle, alpha, beta) < tail:
            lo = middle
        else:
            hi = middle
    return (lo + hi) / 2


def percent(p: float) -> str:
    return f"{100 * p:.1f}%"


def interval_percent(pair: tuple[float, float]) -> list[str]:
    return [percent(pair[0]), percent(pair[1])]


def report() -> dict:
    first = observed_rate(3, 12)
    second = observed_rate(8, 40)
    prior = (6, 24)
    posterior = (prior[0] + 3, prior[1] + 9)
    alternate = (1 + 3, 1 + 9)
    return {
        "scope": "Constructed, conditionally comparable Bernoulli opportunities; not real-player data or strategy",
        "initial_opportunities": {
            "hands_dealt": 50,
            "eligible_3bet_opportunities": 12,
            "observed_3bets": 3,
            "observed_rate": percent(float(first)),
            "ineligible_hands": 50 - 12,
            "wrong_dealt_hand_denominator_rate": percent(float(Fraction(3, 50))),
            "wilson_95": interval_percent(wilson_interval(3, 12)),
        },
        "comparison": {
            "eligible_opportunities": 40,
            "observed_3bets": 8,
            "observed_rate": percent(float(second)),
            "wilson_95": interval_percent(wilson_interval(8, 40)),
        },
        "zero_successes": {
            "observed_3bets": 0,
            "eligible_opportunities": 12,
            "wilson_95": interval_percent(wilson_interval(0, 12)),
        },
        "fictional_beta_prior": {
            "prior_shapes": list(prior),
            "prior_mean": percent(prior[0] / sum(prior)),
            "posterior_shapes": list(posterior),
            "posterior_mean": percent(posterior[0] / sum(posterior)),
            "equal_tailed_credible_95": [
                percent(beta_quantile(0.025, *posterior)),
                percent(beta_quantile(0.975, *posterior)),
            ],
            "alternative_prior_shapes": [1, 1],
            "alternative_posterior_shapes": list(alternate),
            "alternative_posterior_mean": percent(alternate[0] / sum(alternate)),
        },
        "other_denominator_trap": {
            "observed_flop_cbet": 7,
            "eligible_flop_cbet_opportunities": 8,
            "flops_seen": 30,
            "conditional_rate": percent(float(observed_rate(7, 8))),
            "invalid_as_conditional_rate": percent(float(Fraction(7, 30))),
        },
        "limitations": [
            "Opportunity definitions and eligibility may vary by tracker",
            "Observations may differ by position, stack, prior action and game",
            "Wilson nominal coverage requires a sufficiently appropriate sampling model",
            "Beta credible results depend on an illustrative prior and likelihood",
            "No real opponent's range, action, identity or future outcome is inferred",
            "Use only after play and when recording/analysis is permitted",
        ],
    }


def self_test() -> None:
    r = report()
    assert observed_rate(3, 12) == Fraction(1, 4)
    assert observed_rate(8, 40) == Fraction(1, 5)
    assert observed_rate(0, 12) == 0
    assert r["initial_opportunities"]["ineligible_hands"] == 38
    assert r["initial_opportunities"]["wrong_dealt_hand_denominator_rate"] == "6.0%"
    assert r["initial_opportunities"]["wilson_95"] == ["8.9%", "53.2%"]
    assert r["comparison"]["wilson_95"] == ["10.5%", "34.8%"]
    assert r["zero_successes"]["wilson_95"] == ["0.0%", "24.2%"]
    assert r["fictional_beta_prior"]["posterior_shapes"] == [9, 33]
    assert r["fictional_beta_prior"]["posterior_mean"] == "21.4%"
    assert r["fictional_beta_prior"]["equal_tailed_credible_95"] == ["10.6%", "34.9%"]
    assert r["fictional_beta_prior"]["alternative_posterior_mean"] == "28.6%"
    assert r["other_denominator_trap"]["conditional_rate"] == "87.5%"
    assert r["other_denominator_trap"]["invalid_as_conditional_rate"] == "23.3%"
    assert abs(beta_cdf(beta_quantile(0.025, 9, 33), 9, 33) - 0.025) < 1e-10
    assert abs(beta_cdf(beta_quantile(0.975, 9, 33), 9, 33) - 0.975) < 1e-10
    for invalid in ((4, 3), (-1, 12), (1, 0), (1.5, 12), (True, 12)):
        try:
            observed_rate(*invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted invalid count: " + repr(invalid))
    for invalid in ((0, 1), (1, 0), (-1, 3)):
        try:
            beta_cdf(0.4, *invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted invalid Beta shape: " + repr(invalid))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--json", action="store_true", help="Print fixed example outputs")
    modes.add_argument("--self-test", action="store_true", help="Check fixed math and rejection rules")
    args = parser.parse_args()
    self_test()
    if args.self_test:
        print("PASS: fixed fictional opportunity denominators, Wilson intervals and Beta sensitivity")
    elif args.json:
        print(json.dumps(report(), sort_keys=True, indent=2))
    else:
        data = report()
        print("Small-sample poker evidence workbook: all data are fictional")
        for key in ("initial_opportunities", "comparison", "zero_successes",
                    "fictional_beta_prior", "other_denominator_trap"):
            print(key + ": " + json.dumps(data[key], sort_keys=True))
        print("Not a live opponent model, eligible-hand tracking tool or action recommendation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
