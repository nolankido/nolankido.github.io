#!/usr/bin/env python3
"""Offline fictional seven-card Stud8 and razz showdown demonstrations.

Score every five-card subset of seven personal cards. Stud eight-or-better
scores high and qualifying ace-to-five low separately. Razz scores one
ace-to-five low with NO eight-or-better qualifier, including possible pairs.
These closed-action examples model one equally eligible pot, no fee, rake,
side pots, odd-chip rule, opponent range, real game history or betting line.

Python 3.10+: python poker-stud8-razz-seven-card-check.py --self-test
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
SUIT_VALUE = {suit: value for value, suit in enumerate(SUITS)}

QUARTER_PLAYERS = {
    'A': ('As', '2s', '3s', '4s', '7s', '5h', '9d'),
    'B': ('Ah', '2d', '3d', '4h', '5d', 'Qh', 'Js'),
    'C': ('Kc', 'Kd', 'Ks', '8c', '9c', 'Tc', 'Jh'),
}
SCOOP_PLAYERS = {
    'A': ('Ah', '2h', '3h', '4h', '5h', 'Qs', 'Kd'),
    'B': ('6c', '7c', '8d', '9d', 'Td', 'Jh', 'Qc'),
}
VARIANT_PLAYERS = {
    'A': ('Kh', 'Kd', 'Kc', 'Qh', 'Qd', 'Jc', 'Ts'),
    'B': ('Ah', '2h', '3h', '4c', '9d', 'Td', 'Js'),
}
RAZZ_TIE_PLAYERS = {
    'A': ('As', '2c', '3d', '4h', '5s', '9h', 'Kd'),
    'B': ('Ah', '2d', '3c', '4s', '5h', 'Tc', 'Qc'),
}

THIRD_UPCARDS = {'A': '2c', 'B': 'Qh', 'C': 'Qd', 'D': '7s'}
FOURTH_UPCARDS = {'A': ('2c', '8d'), 'B': ('Qh', '9c'), 'C': ('Qd', '7c')}
KNOWN_HERO = ('Ah', '4h', '7c')
OTHER_UPCARDS = ('3s', '5d', 'Kc')
OTHER_UPCARDS_MORE_THREES = ('3s', '5d', '3d')


def remaining(*groups: tuple[str, ...]) -> tuple[str, ...]:
    exposed = [card for group in groups for card in group]
    if len(exposed) != len(set(exposed)) or any(card not in DECK for card in exposed):
        raise ValueError('Duplicate or impossible physical card')
    known = set(exposed)
    return tuple(card for card in DECK if card not in known)


def rank_high_five(cards: tuple[str, ...]) -> tuple[int, ...]:
    """Standard high score; larger tuple wins. Straights/flushes do count."""
    if len(cards) != 5:
        raise ValueError('Exactly five cards required')
    remaining(cards)
    values = [RANK_VALUE[card[0]] for card in cards]
    grouped = sorted(((count, rank) for rank, count in Counter(values).items()), reverse=True)
    unique = set(values)
    straight = (5 if unique == {14, 2, 3, 4, 5} else
                max(unique) if len(unique) == 5 and max(unique) - min(unique) == 4 else 0)
    flush = len(set(card[1] for card in cards)) == 1
    if flush and straight:
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


def ace_five_five(cards: tuple[str, ...]) -> tuple[int, ...]:
    """Ace-to-five low score, including paired lows. SMALLER tuple wins.

    Category 0 = all different ranks; 1 = one pair; 2 = two pair;
    3 = trips; 4 = full house; 5 = quads. Straights and flushes do not
    count. Among equal categories, compare repeated ranks from smallest
    to largest, then descending remaining kickers. This extends the usual
    descending five-rank comparison to rare paired Razz showdowns.
    """
    if len(cards) != 5:
        raise ValueError('Exactly five cards required')
    remaining(cards)
    values = [1 if card[0] == 'A' else RANK_VALUE[card[0]] for card in cards]
    counts = Counter(values)
    groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
    if groups[0][0] == 4:
        return (5, groups[0][1], groups[1][1])
    if groups[0][0] == 3 and groups[1][0] == 2:
        return (4, groups[0][1], groups[1][1])
    if groups[0][0] == 3:
        return (3, groups[0][1], *sorted((v for v in values if v != groups[0][1]), reverse=True))
    if groups[0][0] == 2 and groups[1][0] == 2:
        pairs = sorted((groups[0][1], groups[1][1]), reverse=True)
        return (2, *pairs, next(v for v in values if v not in pairs))
    if groups[0][0] == 2:
        return (1, groups[0][1], *sorted((v for v in values if v != groups[0][1]), reverse=True))
    return (0, *sorted(values, reverse=True))


def seven_scores(cards: tuple[str, ...]
                 ) -> tuple[tuple[int, ...], tuple[int, ...] | None, tuple[int, ...]]:
    """Return (best high, Stud8 qualifying low or None, best razz low)."""
    if len(cards) != 7:
        raise ValueError('Exactly seven personal cards required')
    remaining(cards)
    all_fives = tuple(combinations(cards, 5))
    high = max(rank_high_five(hand) for hand in all_fives)
    lows = [ace_five_five(hand) for hand in all_fives]
    razz = min(lows)
    eligible = [score for score in lows if score[0] == 0 and score[1] <= 8]
    return high, min(eligible) if eligible else None, razz


def stud8_awards(players: dict[str, tuple[str, ...]], pot: int = 300) -> dict[str, Fraction]:
    _validate_players(players, pot)
    scores = {name: seven_scores(hand) for name, hand in players.items()}
    high = max(score[0] for score in scores.values())
    high_winners = [name for name, score in scores.items() if score[0] == high]
    lows = [score[1] for score in scores.values() if score[1] is not None]
    results = {name: Fraction(0) for name in players}
    high_pool = Fraction(pot, 2) if lows else Fraction(pot)
    for name in high_winners:
        results[name] += high_pool / len(high_winners)
    if lows:
        best_low = min(lows)
        low_winners = [name for name, score in scores.items() if score[1] == best_low]
        for name in low_winners:
            results[name] += Fraction(pot, 2 * len(low_winners))
    if sum(results.values()) != Fraction(pot):
        raise ArithmeticError('Stud8 awards do not conserve the eligible pot')
    return results


def razz_awards(players: dict[str, tuple[str, ...]], pot: int = 300) -> dict[str, Fraction]:
    _validate_players(players, pot)
    scores = {name: seven_scores(hand)[2] for name, hand in players.items()}
    best_low = min(scores.values())
    winners = [name for name, score in scores.items() if score == best_low]
    results = {name: Fraction(pot, len(winners)) if name in winners else Fraction(0)
               for name in players}
    if sum(results.values()) != Fraction(pot):
        raise ArithmeticError('Razz awards do not conserve the eligible pot')
    return results


def _validate_players(players: dict[str, tuple[str, ...]], pot: int) -> None:
    if len(players) < 2 or not isinstance(pot, int) or pot < 0:
        raise ValueError('Need two or more players and a nonnegative integer pot')
    if any(len(hand) != 7 for hand in players.values()):
        raise ValueError('Each player must have seven cards')
    remaining(*players.values())


def bring_in(upcards: dict[str, str], variant: str) -> str:
    """Third street for these complete exposed rank/suit examples.

    Stud8 uses the lowest upcard, lowest suit to break a rank tie.
    Razz uses the highest upcard, highest suit to break a rank tie.
    This is not a general house ruling for all-in ante exceptions.
    """
    if variant not in ('stud8', 'razz') or not upcards:
        raise ValueError('Choose stud8 or razz with exposed cards')
    remaining(tuple(upcards.values()))
    # For this learning exercise use upcards 2 through K only. Different
    # ace conventions at bring-in are deliberately outside this fixture.
    if any(card[0] == 'A' for card in upcards.values()):
        raise ValueError('Ace bring-in conventions are outside this exercise')
    key = lambda name: (RANK_VALUE[upcards[name][0]], SUIT_VALUE[upcards[name][1]])
    return (min if variant == 'stud8' else max)(upcards, key=key)


def fourth_street_first(upcards: dict[str, tuple[str, str]], variant: str) -> str:
    """Compare the upcards in two unambiguous fourth-street examples."""
    if variant not in ('stud8', 'razz') or len(upcards) < 2:
        raise ValueError('Expected exposed fourth-street comparisons')
    if any(len(cards) != 2 for cards in upcards.values()):
        raise ValueError('Need precisely two exposed cards per player')
    remaining(*upcards.values())

    def key(name: str) -> tuple[int, ...]:
        cards = upcards[name]
        if variant == 'stud8':
            values = [RANK_VALUE[card[0]] for card in cards]
            return (1, values[0]) if values[0] == values[1] else (0, *sorted(values, reverse=True))
        values = [1 if card[0] == 'A' else RANK_VALUE[card[0]] for card in cards]
        return (1, values[0]) if values[0] == values[1] else (0, *sorted(values, reverse=True))

    ranks = {name: key(name) for name in upcards}
    winner = (max if variant == 'stud8' else min)(ranks, key=ranks.get)
    if sum(value == ranks[winner] for value in ranks.values()) > 1:
        raise ValueError('Tied exposed hands need a separate seat-order rule')
    return winner


def exposed_rank_count(hero: tuple[str, ...], other_upcards: tuple[str, ...],
                       rank: str = '3') -> tuple[int, int]:
    """Unknown deck and remaining copies of one rank, NOT winning outs."""
    if rank not in RANKS:
        raise ValueError('Unknown rank')
    unseen = remaining(hero, other_upcards)
    return len(unseen), sum(card[0] == rank for card in unseen)


def require(condition: bool, case: str) -> None:
    """Preserve fixed fixture checks under Python -O and -OO."""
    if not condition:
        raise AssertionError('Stud8/Razz fixed check failed: ' + case)


def verify() -> None:
    require((rank_high_five(('As', '2s', '3s', '4s', '5s')) == (8, 5)), 'wheel straight flush high')
    require((ace_five_five(('As', '2s', '3s', '4s', '5s')) == (0, 5, 4, 3, 2, 1)), 'ace-to-five wheel low')
    require((ace_five_five(('As', '2s', '3d', '4h', '9c')) == (0, 9, 4, 3, 2, 1)), 'nine-high low')
    require((ace_five_five(('Ac', 'Ad', 'Th', '9s', '8c')) < ace_five_five(('2c', '2d', '7s', '6h', '5c'))), 'paired ace low order')
    require((ace_five_five(('Kc', 'Qc', 'Jc', 'Tc', '9c')) < ace_five_five(('2c', '2d', '7s', '6h', '5c'))), 'king-high versus ace low order')

    high_a, low_a, _ = seven_scores(QUARTER_PLAYERS['A'])
    high_b, low_b, _ = seven_scores(QUARTER_PLAYERS['B'])
    high_c, low_c, _ = seven_scores(QUARTER_PLAYERS['C'])
    require((high_a == (5, 14, 7, 4, 3, 2) and low_a == (0, 5, 4, 3, 2, 1)), 'quarter player A high and low')
    require((high_b == (4, 5) and low_b == (0, 5, 4, 3, 2, 1)), 'quarter player B high and low')
    require((high_c[0] == 3 and low_c is None), 'quarter player C no low')
    require((stud8_awards(QUARTER_PLAYERS, 300) == {
        'A': Fraction(225), 'B': Fraction(75), 'C': Fraction(0)}), 'Stud8 quarter split 225/75/0')

    require((seven_scores(SCOOP_PLAYERS['A'])[:2] == ((8, 5), (0, 5, 4, 3, 2, 1))), 'scoop player A high and low')
    require((seven_scores(SCOOP_PLAYERS['B'])[1] is None), 'scoop player B has no low')
    require((stud8_awards(SCOOP_PLAYERS, 200) == {'A': Fraction(200), 'B': Fraction(0)}), 'Stud8 scoop award')

    require((seven_scores(VARIANT_PLAYERS['A'])[1] is None), 'variant player A no qualifying low')
    require((seven_scores(VARIANT_PLAYERS['B'])[1] is None), 'variant player B no qualifying low')
    require((seven_scores(VARIANT_PLAYERS['A'])[0] == (6, 13, 12)), 'variant A full house high')
    require((seven_scores(VARIANT_PLAYERS['B'])[2] == (0, 9, 4, 3, 2, 1)), 'variant B nine-low razz score')
    require((stud8_awards(VARIANT_PLAYERS, 200) == {'A': Fraction(200), 'B': Fraction(0)}), 'Stud8 variant high award')
    require((razz_awards(VARIANT_PLAYERS, 200) == {'A': Fraction(0), 'B': Fraction(200)}), 'Razz variant low award')

    require((razz_awards(RAZZ_TIE_PLAYERS, 200) == {'A': Fraction(100), 'B': Fraction(100)}), 'Razz wheel tie payout')
    require((bring_in(THIRD_UPCARDS, 'stud8') == 'A'), 'Stud8 third-street bring-in')
    require((bring_in(THIRD_UPCARDS, 'razz') == 'B'), 'Razz third-street bring-in')
    require((fourth_street_first(FOURTH_UPCARDS, 'stud8') == 'B'), 'Stud8 fourth-street first')
    require((fourth_street_first(FOURTH_UPCARDS, 'razz') == 'A'), 'Razz fourth-street first')
    require((exposed_rank_count(KNOWN_HERO, OTHER_UPCARDS) == (46, 3)), 'six visible cards leave three threes')
    require((exposed_rank_count(KNOWN_HERO, OTHER_UPCARDS_MORE_THREES) == (46, 2)), 'additional third exposed leaves two threes')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='Assert all published fictional outcomes')
    args = parser.parse_args()
    verify()
    for label, players, pot in (
        ('Stud8 three-way quarter', QUARTER_PLAYERS, 300),
        ('Stud8 scoop', SCOOP_PLAYERS, 200),
        ('Stud8 no qualifying low', VARIANT_PLAYERS, 200),
    ):
        print(f'{label}: {stud8_awards(players, pot)}')
        print('  high, qualified low, Razz low:',
              {name: seven_scores(hand) for name, hand in players.items()})
    print('Razz same seven cards as no-low Stud8:', razz_awards(VARIANT_PLAYERS, 200))
    print('Razz wheel tie:', razz_awards(RAZZ_TIE_PLAYERS, 200))
    print('Third-street bring-in: Stud8', bring_in(THIRD_UPCARDS, 'stud8'),
          ', Razz', bring_in(THIRD_UPCARDS, 'razz'))
    print('Fourth-street first: Stud8', fourth_street_first(FOURTH_UPCARDS, 'stud8'),
          ', Razz', fourth_street_first(FOURTH_UPCARDS, 'razz'))
    print('Hero plus three upcards:', exposed_rank_count(KNOWN_HERO, OTHER_UPCARDS),
          'versus second exposed three:',
          exposed_rank_count(KNOWN_HERO, OTHER_UPCARDS_MORE_THREES))
    if args.self_test:
        print('PASS: Stud8/razz showdown, low qualifier, tie, street and exposure fixtures')


if __name__ == '__main__':
    main()
