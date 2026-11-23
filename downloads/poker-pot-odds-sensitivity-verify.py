#!/usr/bin/env python3
"""Reproduce three *fictional* poker decision-price examples with exact fractions.

Standard-library only. No imports of AI, solvers, network clients, external files,
player data, hands or ranges. This is study away from play, not RTA.

Usage:
  python downloads/poker-pot-odds-sensitivity-verify.py
  python downloads/poker-pot-odds-sensitivity-verify.py --json
  python downloads/poker-pot-odds-sensitivity-verify.py --self-test
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json


def _nonnegative(name: str, value: F) -> None:
    if value < 0:
        raise ValueError(name + ' must be nonnegative')


def _probability(name: str, value: F) -> None:
    if value < 0 or value > 1:
        raise ValueError(name + ' must be between 0 and 1')


def call_price(pot_at_decision: F, additional_call: F) -> F:
    """Assumes one matched, eligible pot and that calling closes the action."""
    _nonnegative('pot at decision', pot_at_decision)
    if additional_call <= 0:
        raise ValueError('additional call must be positive')
    return additional_call / (pot_at_decision + additional_call)


def call_ev(pot_at_decision: F, additional_call: F, equity: F) -> F:
    """Chip EV relative to folding. Equity includes the player's share of ties."""
    _probability('equity', equity)
    call_price(pot_at_decision, additional_call)
    return equity * (pot_at_decision + additional_call) - additional_call


def facing_raise_to(starting_pot: F, hero_bet: F, villain_raise_to: F) -> tuple[F, F, F]:
    """Returns (current pot, *additional* call, final matched pot)."""
    _nonnegative('starting pot', starting_pot)
    if hero_bet <= 0 or villain_raise_to <= hero_bet:
        raise ValueError('raise-to must exceed a positive previous bet')
    current = starting_pot + hero_bet + villain_raise_to
    extra_call = villain_raise_to - hero_bet
    return current, extra_call, current + extra_call


def pure_bluff_fold_price(starting_pot: F, bluff_bet: F) -> F:
    _nonnegative('starting pot', starting_pot)
    if starting_pot <= 0 or bluff_bet <= 0:
        raise ValueError('bluff pot and bet must be positive')
    return bluff_bet / (starting_pot + bluff_bet)


def pure_bluff_ev(starting_pot: F, bluff_bet: F, fold_probability: F) -> F:
    """Zero equity when called; check alternative is modeled as zero chip EV."""
    _probability('fold probability', fold_probability)
    pure_bluff_fold_price(starting_pot, bluff_bet)
    return fold_probability * starting_pot - (1 - fold_probability) * bluff_bet


def caller_price_against_bet(starting_pot: F, bluff_bet: F) -> F:
    """Separate price for the *caller*, not the bettor's bluff threshold."""
    pure_bluff_fold_price(starting_pot, bluff_bet)
    return bluff_bet / (starting_pot + 2 * bluff_bet)


def fraction(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def make_report() -> dict:
    river_p, river_c = F(30), F(10)
    raise_p, raise_c, raise_final = facing_raise_to(F(10), F(4), F(14))
    bluff_p, bluff_b = F(10), F(6)
    return {
        'scope': 'fictional, heads-up, matched chip pots; no rake, future betting, ICM, side pots, or player ranges',
        'river_call': {
            'pot_before_bet': 20,
            'opponent_bet': 10,
            'pot_at_decision': 30,
            'additional_call': 10,
            'final_pot': 40,
            'break_even_equity': fraction(call_price(river_p, river_c)),
            'equity_to_ev': {fraction(eq): fraction(call_ev(river_p, river_c, eq))
                             for eq in (F(1, 5), F(1, 4), F(3, 10))},
            'sensitivity_equity_interval': ['11/50', '29/100'],
            'sensitivity_ev_interval': [fraction(call_ev(river_p, river_c, F(11, 50))),
                                        fraction(call_ev(river_p, river_c, F(29, 100)))],
            'ev_change_per_equity_percentage_point': fraction((river_p + river_c) / 100),
        },
        'raise_to': {
            'starting_pot': 10,
            'hero_bet': 4,
            'villain_raise_to': 14,
            'pot_at_decision': fraction(raise_p),
            'additional_call': fraction(raise_c),
            'final_pot': fraction(raise_final),
            'break_even_equity': fraction(call_price(raise_p, raise_c)),
            'equity_to_ev': {fraction(eq): fraction(call_ev(raise_p, raise_c, eq))
                             for eq in (F(1, 4), F(3, 10))},
        },
        'pure_bluff': {
            'pot_before_bet': 10,
            'bluff_bet': 6,
            'fold_break_even': fraction(pure_bluff_fold_price(bluff_p, bluff_b)),
            'caller_break_even_equity': fraction(caller_price_against_bet(bluff_p, bluff_b)),
            'fold_probability_to_ev': {fraction(rate): fraction(pure_bluff_ev(bluff_p, bluff_b, rate))
                                       for rate in (F(3, 10), F(3, 8), F(2, 5), F(1, 2))},
        },
    }


def self_test() -> None:
    # Independent literal checkpoints, not a solver or estimate of an opponent.
    assert call_price(F(30), F(10)) == F(1, 4)
    assert [call_ev(F(30), F(10), q) for q in (F(1, 5), F(1, 4), F(3, 10))] == [F(-2), F(0), F(2)]
    assert [call_ev(F(30), F(10), q) for q in (F(11, 50), F(29, 100))] == [F(-6, 5), F(8, 5)]
    assert (F(30) + F(10)) / 100 == F(2, 5)
    p, c, final = facing_raise_to(F(10), F(4), F(14))
    assert (p, c, final) == (F(28), F(10), F(38))
    assert call_price(p, c) == F(5, 19)
    assert [call_ev(p, c, q) for q in (F(1, 4), F(3, 10))] == [F(-1, 2), F(7, 5)]
    assert pure_bluff_fold_price(F(10), F(6)) == F(3, 8)
    assert caller_price_against_bet(F(10), F(6)) == F(3, 11)
    assert [pure_bluff_ev(F(10), F(6), q) for q in (F(3, 10), F(3, 8), F(2, 5), F(1, 2))] == [F(-6, 5), F(0), F(2, 5), F(2)]
    for operation in (lambda: call_ev(F(30), F(10), F(101, 100)),
                      lambda: pure_bluff_ev(F(10), F(6), F(-1, 10)),
                      lambda: facing_raise_to(F(10), F(4), F(3)),
                      lambda: call_price(F(-1), F(10))):
        try:
            operation()
        except ValueError:
            continue
        raise AssertionError('Invalid input was accepted')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--self-test', action='store_true', help='Check exact published model outputs')
    group.add_argument('--json', action='store_true', help='Emit fixed-input fractional results as JSON')
    args = parser.parse_args()
    self_test()
    if args.self_test:
        print('PASS: exact fictional pot-odds, raise-to, and pure-bluff model checkpoints')
    elif args.json:
        print(json.dumps(make_report(), indent=2, sort_keys=True))
    else:
        report = make_report()
        print('Original pot-odds sensitivity workbook: exact fictional chip models')
        for name in ('river_call', 'raise_to', 'pure_bluff'):
            print(name + ': ' + json.dumps(report[name], sort_keys=True))
        print('Not an opponent model, live-play assistant, range solution, or tournament-prize calculation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
