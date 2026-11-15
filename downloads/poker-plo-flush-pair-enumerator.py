#!/usr/bin/env python3
"""Offline four-card PLO high: nut-flush blockers and paired-board rivers.

All examples are fixed and fictional. There is no network access, interaction
with poker clients, personal data, prediction of a live opponent or betting
recommendation. Run with Python 3.10+: python poker-plo-flush-pair-enumerator.py --self-test
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from math import comb

RANKS = '23456789TJQKA'
SUITS = 'cdhs'
RANK_VALUE = {rank: i for i, rank in enumerate(RANKS, start=2)}
DECK = tuple(r + s for r in RANKS for s in SUITS)

MONOTONE_FLOP = ('Ts', '8s', '3s')
ACE_BLOCKER_HERO = ('As', 'Kh', 'Qd', 'Jc')
NO_SPADE_HERO = ('Ah', 'Kh', 'Qd', 'Jc')

TURN_BOARD = ('Qs', '8s', '3s', '7d')
SET_HERO = ('As', 'Ks', 'Jh', '7h')
NO_SEVEN_BLOCK_HERO = ('As', 'Ks', 'Jh', 'Td')
SET_RIVAL = ('Qh', 'Qd', '2c', '4c')
ONE_QUEEN_RIVAL = ('Qh', 'Jd', 'Tc', '9c')


def remaining(*groups: tuple[str, ...]) -> tuple[str, ...]:
    known = [card for group in groups for card in group]
    if any(card not in DECK for card in known) or len(known) != len(set(known)):
        raise ValueError('Unknown or duplicated physical card')
    removed = set(known)
    return tuple(c for c in DECK if c not in removed)


def high_five(cards: tuple[str, ...]) -> tuple[int, ...]:
    if len(cards) != 5 or len(set(cards)) != 5:
        raise ValueError('Need five distinct physical cards')
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


def omaha_high(holes: tuple[str, ...], board: tuple[str, ...]) -> tuple[int, ...]:
    if len(holes) != 4 or len(board) not in (3, 4, 5):
        raise ValueError('Expected four private cards and three to five board cards')
    remaining(holes, board)  # Validate cards and disjointness.
    return max(high_five(pair + triple)
               for pair in combinations(holes, 2)
               for triple in combinations(board, 3))


def four_card_flush_holdings(hero: tuple[str, ...]) -> dict[str, int]:
    """Count uniform four-card rival deals on a three-spade flop."""
    unseen = remaining(hero, MONOTONE_FLOP)
    assert len(unseen) == 45
    flush_hands = 0
    ace_flush_hands = 0
    for rival in combinations(unseen, 4):
        spades = sum(card[1] == 's' for card in rival)
        if spades >= 2:
            flush_hands += 1
            if 'As' in rival:
                ace_flush_hands += 1
    return {'all': comb(45, 4), 'flush': flush_hands, 'ace_flush': ace_flush_hands}


def faceup_rivers(hero: tuple[str, ...], rival: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    outcomes = {'hero': [], 'rival': [], 'tie': []}
    for river in remaining(hero, rival, TURN_BOARD):
        board = TURN_BOARD + (river,)
        hero_score = omaha_high(hero, board)
        rival_score = omaha_high(rival, board)
        key = 'hero' if hero_score > rival_score else 'rival' if rival_score > hero_score else 'tie'
        outcomes[key].append(river)
    return {key: tuple(cards) for key, cards in outcomes.items()}


def verify() -> None:
    # Two-hole restriction prevents an ace-spade-only flush on the monotone flop.
    assert omaha_high(ACE_BLOCKER_HERO, MONOTONE_FLOP)[0] != 5
    assert omaha_high(SET_HERO, TURN_BOARD) == (5, 14, 13, 12, 8, 3)
    assert omaha_high(SET_RIVAL, TURN_BOARD)[0] == 3
    assert high_five(('As', '2h', '3d', '4c', '5s')) == (4, 5)
    assert high_five(('As', '2s', '3s', '4s', '5s')) == (8, 5)
    assert high_five(('Qh', 'Qd', 'Qs', '8s', '8d'))[0] == 6
    blocker = four_card_flush_holdings(ACE_BLOCKER_HERO)
    no_blocker = four_card_flush_holdings(NO_SPADE_HERO)
    assert blocker == {'all': 148995, 'flush': 25830, 'ace_flush': 0}
    assert no_blocker == {'all': 148995, 'flush': 31185, 'ace_flush': 6699}
    assert len([card for card in remaining(ACE_BLOCKER_HERO, MONOTONE_FLOP) if card[1] == 's']) == 9
    assert len([card for card in remaining(NO_SPADE_HERO, MONOTONE_FLOP) if card[1] == 's']) == 10

    set_case = faceup_rivers(SET_HERO, SET_RIVAL)
    assert len(set_case['rival']) == 9 and len(set_case['hero']) == 31 and not set_case['tie']
    assert set(set_case['rival']) == {'Qc', '8c', '8d', '8h', '3c', '3d', '3h', '7c', '7s'}
    baseline = faceup_rivers(NO_SEVEN_BLOCK_HERO, SET_RIVAL)
    assert len(baseline['rival']) == 10 and len(baseline['hero']) == 30 and not baseline['tie']
    assert set(baseline['rival']) - set(set_case['rival']) == {'7h'}
    pair_case = faceup_rivers(SET_HERO, ONE_QUEEN_RIVAL)
    assert len(pair_case['rival']) == 0 and len(pair_case['hero']) == 40 and not pair_case['tie']


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='Assert every published fictional count')
    args = parser.parse_args()
    verify()
    for label, hero in (('Ace-spade blocker', ACE_BLOCKER_HERO),
                        ('No spade blocker', NO_SPADE_HERO)):
        count = four_card_flush_holdings(hero)
        print(f'{label}: {count["flush"]}/{count["all"]} random four-card rivals hold two or more spades; '
              f'{count["ace_flush"]}/{count["all"]} hold As plus another spade')
    for label, hero, rival in (
        ('Nut flush versus set, seven blocked', SET_HERO, SET_RIVAL),
        ('Nut flush versus set, seven unblocked', NO_SEVEN_BLOCK_HERO, SET_RIVAL),
        ('Nut flush versus top pair', SET_HERO, ONE_QUEEN_RIVAL),
    ):
        outcome = faceup_rivers(hero, rival)
        print(f'{label}: {len(outcome["rival"])}/40 opponent wins, '
              f'{len(outcome["hero"])}/40 hero wins, {len(outcome["tie"])}/40 ties')
        print('  Opponent-winning rivers:', ', '.join(outcome['rival']) or '(none)')
    if args.self_test:
        print('PASS: verified all Omaha high rules, combinations, blocker counts and rivers')


if __name__ == '__main__':
    main()
