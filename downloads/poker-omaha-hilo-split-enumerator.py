#!/usr/bin/env python3
"""Offline, fictional four-card Omaha hi-lo eight-or-better showdown checker.

Each high and low candidate separately chooses exactly two of four hole cards
and three of the board. The caller supplies complete exposed holdings and a
single equal-eligibility pot. No rake, fees, side pots, odd chips, betting,
opponent ranges, player data, poker-client access or network calls are modeled.

Python 3.10+: python poker-omaha-hilo-split-enumerator.py --self-test
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations

RANKS = '23456789TJQKA'
SUITS = 'cdhs'
RANK_VALUE = {rank: value for value, rank in enumerate(RANKS, start=2)}
DECK = tuple(rank + suit for rank in RANKS for suit in SUITS)

QUARTER_BOARD = ('Ah', 'Ad', '2c', '3d', 'Kd')
QUARTER_PLAYERS = {
    'A': ('Ac', 'As', '4h', '5h'),
    'B': ('4c', '5c', 'Qh', 'Jh'),
    'C': ('Kc', 'Ks', '9h', '9d'),
}

SCOOP_BOARD = ('Ah', '2d', '3c', 'Kd', 'Qs')
SCOOP_PLAYERS = {
    'A': ('4h', '5h', 'Ac', 'Ad'),
    'B': ('6c', '7c', '9h', '9d'),
}

NO_LOW_BOARD = ('Kc', 'Kd', 'Qh', 'Jh', '9s')
NO_LOW_PLAYERS = {
    'A': ('Kh', 'Ks', 'As', '2s'),
    'B': ('Ah', '3c', '4c', '5d'),
}

TURN_BOARD = ('3c', '5d', '7h', 'Kc')
TURN_A = ('As', '2s', 'Qd', 'Jd')
TURN_A_PROTECTED = ('As', '2s', '4c', 'Jd')
TURN_B = ('Ah', '4h', 'Qh', 'Js')
COUNTERFEIT_RIVER = '2h'


def remaining(*groups: tuple[str, ...]) -> tuple[str, ...]:
    """Validate unique, real cards, then return the unexposed deck."""
    exposed = [card for group in groups for card in group]
    if any(card not in DECK for card in exposed) or len(set(exposed)) != len(exposed):
        raise ValueError('Unknown card or duplicated physical card')
    blocked = set(exposed)
    return tuple(card for card in DECK if card not in blocked)


def high_five(cards: tuple[str, ...]) -> tuple[int, ...]:
    """High-hand ranking: larger tuple wins, including ace-low wheel straights."""
    if len(cards) != 5 or len(set(cards)) != 5 or any(card not in DECK for card in cards):
        raise ValueError('High score requires five distinct real cards')
    values = [RANK_VALUE[card[0]] for card in cards]
    grouped = sorted(((count, rank) for rank, count in Counter(values).items()), reverse=True)
    unique = set(values)
    straight = (5 if unique == {14, 2, 3, 4, 5} else
                max(unique) if len(unique) == 5 and max(unique) - min(unique) == 4 else 0)
    flush = len(set(card[1] for card in cards)) == 1
    if straight and flush:
        return (8, straight)
    if grouped[0][0] == 4:
        return (7, grouped[0][1], grouped[1][1])
    if grouped[0][0] == 3 and grouped[1][0] == 2:
        return (6, grouped[0][1], grouped[1][1])
    if flush:
        return (5, *sorted(values, reverse=True))
    if straight:
        return (4, straight)
    if grouped[0][0] == 3:
        return (3, grouped[0][1], *sorted((v for v in values if v != grouped[0][1]), reverse=True))
    if grouped[0][0] == 2 and grouped[1][0] == 2:
        pairs = sorted((grouped[0][1], grouped[1][1]), reverse=True)
        return (2, *pairs, next(v for v in values if v not in pairs))
    if grouped[0][0] == 2:
        return (1, grouped[0][1], *sorted((v for v in values if v != grouped[0][1]), reverse=True))
    return (0, *sorted(values, reverse=True))


def low_five(cards: tuple[str, ...]) -> tuple[int, ...] | None:
    """Ace-to-five eight-or-better: smaller descending-rank tuple wins."""
    if len(cards) != 5 or len(set(cards)) != 5 or any(card not in DECK for card in cards):
        raise ValueError('Low score requires five distinct real cards')
    values = [1 if card[0] == 'A' else RANK_VALUE[card[0]] for card in cards]
    if max(values) > 8 or len(set(values)) != 5:
        return None
    return tuple(sorted(values, reverse=True))


def omaha_scores(holes: tuple[str, ...], board: tuple[str, ...]
                 ) -> tuple[tuple[int, ...], tuple[int, ...] | None]:
    if len(holes) != 4 or len(board) not in (3, 4, 5):
        raise ValueError('Need four hole cards and three to five board cards')
    remaining(holes, board)
    selections = [pair + triple for pair in combinations(holes, 2)
                  for triple in combinations(board, 3)]
    high = max(high_five(cards) for cards in selections)
    lows = [score for cards in selections if (score := low_five(cards)) is not None]
    return high, min(lows) if lows else None


def awards(players: dict[str, tuple[str, ...]], board: tuple[str, ...],
           pot: int = 240) -> dict[str, Fraction]:
    """Exact chip shares for one fully eligible, zero-rake, closed-action pot."""
    if len(players) < 2 or not isinstance(pot, int) or pot < 0 or len(board) != 5:
        raise ValueError('Need at least two players, final board and nonnegative integer pot')
    remaining(board, *players.values())
    if any(len(holes) != 4 for holes in players.values()):
        raise ValueError('Every player needs exactly four private cards')
    scores = {name: omaha_scores(holes, board) for name, holes in players.items()}
    best_high = max(high for high, _ in scores.values())
    high_winners = [name for name, (high, _) in scores.items() if high == best_high]
    qualified_lows = [low for _, low in scores.values() if low is not None]
    result = {name: Fraction(0) for name in players}
    if qualified_lows:
        high_pool, low_pool = Fraction(pot, 2), Fraction(pot, 2)
        best_low = min(qualified_lows)
        low_winners = [name for name, (_, low) in scores.items() if low == best_low]
        for name in low_winners:
            result[name] += low_pool / len(low_winners)
    else:
        high_pool = Fraction(pot)
    for name in high_winners:
        result[name] += high_pool / len(high_winners)
    if sum(result.values()) != Fraction(pot):
        raise ArithmeticError('Omaha/8 awarded shares do not conserve the contested pot')
    return result


def faceup_low_rivers(hero: tuple[str, ...], rival: tuple[str, ...]
                      ) -> dict[str, tuple[str, ...]]:
    """All unseen river cards given both complete four-card hands on the turn."""
    outcomes = {'hero': [], 'rival': [], 'tie': [], 'neither': []}
    for river in remaining(hero, rival, TURN_BOARD):
        _, a = omaha_scores(hero, TURN_BOARD + (river,))
        _, b = omaha_scores(rival, TURN_BOARD + (river,))
        if a is None and b is None:
            key = 'neither'
        elif b is None or (a is not None and a < b):
            key = 'hero'
        elif a is None or b < a:
            key = 'rival'
        else:
            key = 'tie'
        outcomes[key].append(river)
    return {key: tuple(cards) for key, cards in outcomes.items()}


def require(condition: bool, case: str) -> None:
    """Keep all fixed example checks active even under Python -O and -OO."""
    if not condition:
        raise AssertionError('Omaha/8 fixed case failed: ' + case)


def verify() -> None:
    require((high_five(('As', '2h', '3d', '4c', '5s')) == (4, 5)), 'high-hand wheel straight')
    require((high_five(('As', '2s', '3s', '4s', '5s')) == (8, 5)), 'high-hand wheel straight flush')
    require((low_five(('As', '2s', '3s', '4s', '5s')) == (5, 4, 3, 2, 1)), 'eight-or-better ace low')
    require((low_five(('As', '2s', '3d', '4c', '2h')) is None), 'paired low excluded')
    require((low_five(('As', '2s', '3d', '4c', '9h')) is None), 'nine-high low excluded')

    require((omaha_scores(QUARTER_PLAYERS['A'], QUARTER_BOARD) == ((7, 14, 13), (5, 4, 3, 2, 1))), 'quarter winner best high and low')
    require((omaha_scores(QUARTER_PLAYERS['B'], QUARTER_BOARD)[1] == (5, 4, 3, 2, 1)), 'quarter second-player low')
    require((omaha_scores(QUARTER_PLAYERS['C'], QUARTER_BOARD)[1] is None), 'third player no qualifying low')
    require((awards(QUARTER_PLAYERS, QUARTER_BOARD, 300) == {
        'A': Fraction(225), 'B': Fraction(75), 'C': Fraction(0)}), 'three-player pot quarters')
    require((awards(SCOOP_PLAYERS, SCOOP_BOARD, 240) == {
        'A': Fraction(240), 'B': Fraction(0)}), 'scoop pot')
    require((awards(NO_LOW_PLAYERS, NO_LOW_BOARD, 240) == {
        'A': Fraction(240), 'B': Fraction(0)}), 'no qualifying low entire high pot')
    require((all(omaha_scores(holes, NO_LOW_BOARD)[1] is None for holes in NO_LOW_PLAYERS.values())), 'no-low board excludes all lows')

    before_a = omaha_scores(TURN_A, TURN_BOARD)[1]
    before_b = omaha_scores(TURN_B, TURN_BOARD)[1]
    require((before_a == (7, 5, 3, 2, 1) and before_b == (7, 5, 4, 3, 1)), 'fourth-street low comparison')
    river_board = TURN_BOARD + (COUNTERFEIT_RIVER,)
    require((omaha_scores(TURN_A, river_board)[1] == (7, 5, 3, 2, 1)), 'counterfeited hero low')
    require((omaha_scores(TURN_B, river_board)[1] == (5, 4, 3, 2, 1)), 'counterfeiting opponent low')
    require((awards({'A': TURN_A, 'B': TURN_B}, river_board) == {'A': Fraction(0), 'B': Fraction(240)}), 'counterfeited pot awarded')
    require((omaha_scores(TURN_A_PROTECTED, river_board)[1] == (5, 4, 3, 2, 1)), 'protected low remaining tied')
    require((awards({'A': TURN_A_PROTECTED, 'B': TURN_B}, river_board) == {
        'A': Fraction(120), 'B': Fraction(120)}), 'protected low tied award')
    results = faceup_low_rivers(TURN_A, TURN_B)
    require((len(results['rival']) == 3 and set(results['rival']) == {'2c', '2d', '2h'}), 'three counterfeit rivers')
    require((len(results['hero']) == 37 and not results['tie'] and not results['neither']), '37 other winning low rivers')
    require((sum(len(cards) for cards in results.values()) == 40), '40 face-up river outcomes')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='Check every published fictional result')
    args = parser.parse_args()
    verify()
    for title, board, players, pot in (
        ('Three-player quarter', QUARTER_BOARD, QUARTER_PLAYERS, 300),
        ('Scoop', SCOOP_BOARD, SCOOP_PLAYERS, 240),
        ('No qualifying low', NO_LOW_BOARD, NO_LOW_PLAYERS, 240),
        ('Counterfeit river 2h', TURN_BOARD + ('2h',), {'A': TURN_A, 'B': TURN_B}, 240),
        ('Protected low river 2h', TURN_BOARD + ('2h',), {'A': TURN_A_PROTECTED, 'B': TURN_B}, 240),
    ):
        scores = {name: omaha_scores(hand, board) for name, hand in players.items()}
        print(f'{title}: board {" ".join(board)}; high/low {scores}; shares {awards(players, board, pot)}')
    outcomes = faceup_low_rivers(TURN_A, TURN_B)
    print(f'Face-up turn, 40 rivers: A best low on {len(outcomes["hero"])}; '
          f'B best low on {len(outcomes["rival"])}; tied on {len(outcomes["tie"])}')
    print('B takes low on:', ', '.join(outcomes['rival']))
    if args.self_test:
        print('PASS: independent high/low selection, exact pot conservation and every river')


if __name__ == '__main__':
    main()
