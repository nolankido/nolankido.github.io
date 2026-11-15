#!/usr/bin/env python3
"""Offline, reproducible examples for Nolan Kido's four-card PLO high guide.

No network access, personal information, random numbers or live poker advice.
Every Omaha high hand uses exactly two hole cards and three board cards.
Run: python downloads/poker-plo-wrap-enumerator.py --self-test
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations

RANKS = "23456789TJQKA"
SUITS = "cdhs"
DECK = tuple(rank + suit for rank in RANKS for suit in SUITS)
RANK_VALUE = {rank: value for value, rank in enumerate(RANKS, start=2)}

WRAP_HERO = ("Qs", "9s", "8h", "7h")
WRAP_FLOP = ("Jh", "Tc", "4d")
BLOCKER_OPPONENT = ("Kd", "Qd", "5c", "5s")
REDRAW_TURN = ("Jh", "Tc", "4d", "8c")
REDRAW_OPPONENT = ("Ac", "Kc", "9d", "2d")


def validate(*groups: tuple[str, ...]) -> None:
    cards = [card for group in groups for card in group]
    if any(card not in DECK for card in cards) or len(set(cards)) != len(cards):
        raise ValueError("Unknown or duplicated physical card")


def five_card_high(cards: tuple[str, ...]) -> tuple[int, ...]:
    """Return a comparable high-hand tuple, including ace-low straights."""
    if len(cards) != 5 or len(set(cards)) != 5:
        raise ValueError("High-hand evaluator requires five unique cards")
    ranks = [RANK_VALUE[card[0]] for card in cards]
    counts = Counter(ranks)
    groups = sorted(((n, rank) for rank, n in counts.items()), reverse=True)
    flush = len({card[1] for card in cards}) == 1
    unique = set(ranks)
    straight_high = 5 if unique == {14, 2, 3, 4, 5} else (
        max(unique) if len(unique) == 5 and max(unique) - min(unique) == 4 else 0
    )
    if flush and straight_high:
        return (8, straight_high)
    if groups[0][0] == 4:
        return (7, groups[0][1], groups[1][1])
    if groups[0][0] == 3 and groups[1][0] == 2:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5, *sorted(ranks, reverse=True))
    if straight_high:
        return (4, straight_high)
    if groups[0][0] == 3:
        return (3, groups[0][1], *sorted((r for r in ranks if r != groups[0][1]), reverse=True))
    if groups[0][0] == 2 and groups[1][0] == 2:
        pairs = sorted((groups[0][1], groups[1][1]), reverse=True)
        return (2, *pairs, next(r for r in ranks if r not in pairs))
    if groups[0][0] == 2:
        return (1, groups[0][1], *sorted((r for r in ranks if r != groups[0][1]), reverse=True))
    return (0, *sorted(ranks, reverse=True))


def best_omaha_high(holes: tuple[str, ...], board: tuple[str, ...]) -> tuple[int, ...]:
    """Select exactly two holes and exactly three board cards."""
    if len(holes) != 4 or len(board) not in (3, 4, 5):
        raise ValueError("Requires four hole cards and a flop, turn or river board")
    validate(holes, board)
    return max(
        five_card_high(two + three)
        for two in combinations(holes, 2)
        for three in combinations(board, 3)
    )


def remaining_cards(*known_groups: tuple[str, ...]) -> tuple[str, ...]:
    validate(*known_groups)
    known = set(card for group in known_groups for card in group)
    return tuple(card for card in DECK if card not in known)


def wrap_next_card_completions(
    opponents: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    known = (WRAP_HERO, WRAP_FLOP) if opponents is None else (
        WRAP_HERO, WRAP_FLOP, opponents
    )
    return tuple(
        card
        for card in remaining_cards(*known)
        if best_omaha_high(WRAP_HERO, WRAP_FLOP + (card,))[0] >= 4
    )


def redraw_river_outcomes() -> dict[str, tuple[str, ...]]:
    result: dict[str, list[str]] = {"hero": [], "opponent": [], "tie": []}
    for river in remaining_cards(WRAP_HERO, REDRAW_TURN, REDRAW_OPPONENT):
        board = REDRAW_TURN + (river,)
        hero = best_omaha_high(WRAP_HERO, board)
        opponent = best_omaha_high(REDRAW_OPPONENT, board)
        outcome = "hero" if hero > opponent else "opponent" if opponent > hero else "tie"
        result[outcome].append(river)
    return {key: tuple(cards) for key, cards in result.items()}


def run_checks() -> None:
    assert five_card_high(("Ac", "2h", "3s", "4d", "5c")) == (4, 5)
    assert five_card_high(("Ac", "2c", "3c", "4c", "5c")) == (8, 5)
    assert five_card_high(("Kh", "Kd", "Kc", "2h", "2d"))[0] == 6
    assert five_card_high(("As", "Ah", "Ad", "Ac", "2h"))[0] == 7
    assert best_omaha_high(("As", "Kd", "Qc", "Jh"), ("2s", "7s", "9s", "Js", "3d"))[0] != 5
    first = wrap_next_card_completions()
    assert len(remaining_cards(WRAP_HERO, WRAP_FLOP)) == 45
    assert Counter(card[0] for card in first) == {"K": 4, "Q": 3, "9": 3, "8": 3, "7": 3}
    blocked = wrap_next_card_completions(BLOCKER_OPPONENT)
    assert len(remaining_cards(WRAP_HERO, WRAP_FLOP, BLOCKER_OPPONENT)) == 41
    assert len(blocked) == 14
    assert set(first) - set(blocked) == {"Kd", "Qd"}
    assert best_omaha_high(WRAP_HERO, REDRAW_TURN) == (4, 12)
    outcome = redraw_river_outcomes()
    assert len(outcome["opponent"]) == 11, outcome
    assert len(outcome["hero"]) == 29, outcome
    assert not outcome["tie"]
    assert set(outcome["opponent"]) == {
        card for card in remaining_cards(WRAP_HERO, REDRAW_TURN, REDRAW_OPPONENT)
        if card[1] == "c" or card[0] == "Q"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Assert all published fixture counts")
    args = parser.parse_args()
    run_checks()
    basic = wrap_next_card_completions()
    blocked = wrap_next_card_completions(BLOCKER_OPPONENT)
    outcome = redraw_river_outcomes()
    print("Fictional four-card Omaha high; exactly two hole cards and three board cards")
    print(f"Flop wrap: {len(basic)}/45 next cards complete a straight: {', '.join(basic)}")
    print(f"With known blocker hand: {len(blocked)}/41, removing Kd and Qd")
    print(f"Face-up turn redraw: {len(outcome['opponent'])}/40 opponent wins; "
          f"{len(outcome['hero'])}/40 hero wins; {len(outcome['tie'])}/40 ties")
    print(f"Opponent-winning rivers: {', '.join(outcome['opponent'])}")
    if args.self_test:
        print("PASS: checked rank ordering, Omaha construction, wraps, blockers and rivers")


if __name__ == "__main__":
    main()
