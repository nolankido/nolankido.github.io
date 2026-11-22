#!/usr/bin/env python3
"""Reproduce a fictional face-up Hold'em turn call with exact card enumeration.

No network, account access, wagers, live-play guidance, files written, or solver output.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json

RANKS = "23456789TJQKA"
SUITS = "cdhs"
HERO = ("Ah", "Jh")
VILLAIN = ("7d", "Qc")
TURN_BOARD = ("Kh", "7h", "7c", "2d")
POT_BEFORE_BET = 60
BET = 20


def straight_high(values: set[int]) -> int:
    ranks = set(values)
    if 14 in ranks:
        ranks.add(1)
    return next((high for high in range(14, 4, -1)
                 if all(high - offset in ranks for offset in range(5))), 0)


def five_score(cards: tuple[str, ...]) -> tuple[int, ...]:
    if len(cards) != 5:
        raise ValueError("Exactly five cards required")
    ranks = [RANKS.index(card[0]) + 2 for card in cards]
    counts = Counter(ranks)
    groups = sorted(((n, rank) for rank, n in counts.items()), reverse=True)
    desc = sorted(ranks, reverse=True)
    flush = len({card[1] for card in cards}) == 1
    straight = straight_high(set(ranks))
    if flush and straight:
        return (8, straight)
    if groups[0][0] == 4:
        return (7, groups[0][1], groups[1][1])
    if [g[0] for g in groups] == [3, 2]:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5, *desc)
    if straight:
        return (4, straight)
    if groups[0][0] == 3:
        return (3, groups[0][1], *sorted((x[1] for x in groups[1:]), reverse=True))
    if [g[0] for g in groups] == [2, 2, 1]:
        return (2, max(groups[0][1], groups[1][1]),
                min(groups[0][1], groups[1][1]), groups[2][1])
    if groups[0][0] == 2:
        return (1, groups[0][1], *sorted((x[1] for x in groups[1:]), reverse=True))
    return (0, *desc)


def best_seven(cards: tuple[str, ...]) -> tuple[int, ...]:
    if len(cards) != 7 or len(set(cards)) != 7:
        raise ValueError("Require seven different cards")
    return max(five_score(hand) for hand in combinations(cards, 5))


def enumerate_rivers(
    hero: tuple[str, str] = HERO,
    villain: tuple[str, str] = VILLAIN,
    board: tuple[str, str, str, str] = TURN_BOARD,
) -> dict[str, object]:
    known = (*hero, *villain, *board)
    deck = tuple(rank + suit for rank in RANKS for suit in SUITS)
    if len(known) != 8 or len(set(known)) != 8 or any(card not in deck for card in known):
        raise ValueError("Eight distinct legal face-up cards required")
    unseen = [card for card in deck if card not in known]
    wins, losses, ties, hearts = [], [], [], []
    for river in unseen:
        board5 = (*board, river)
        hero_score = best_seven((*hero, *board5))
        villain_score = best_seven((*villain, *board5))
        if hero_score > villain_score:
            wins.append(river)
        elif hero_score < villain_score:
            losses.append(river)
        else:
            ties.append(river)
        if river.endswith("h"):
            hearts.append(river)
    return {"unknown": len(unseen), "wins": wins, "losses": losses,
            "ties": ties, "hearts": hearts,
            "dirty_hearts": sorted(set(hearts) - set(wins))}


def audit() -> dict[str, object]:
    count = enumerate_rivers(hero=HERO, villain=VILLAIN, board=TURN_BOARD)
    unknown = count["unknown"]
    win = len(count["wins"])
    lose = len(count["losses"])
    tie = len(count["ties"])
    raw = len(count["hearts"])
    final_pot = POT_BEFORE_BET + 2 * BET
    pot_before_call = POT_BEFORE_BET + BET
    equity = Fraction(win * 2 + tie, 2 * unknown)
    raw_rate = Fraction(raw, unknown)
    threshold = Fraction(BET, final_pot)
    ev = equity * final_pot - BET
    false_raw_ev = raw_rate * final_pot - BET
    expected = {"2h", "Qh"}
    correct = (unknown == 44 and win == 7 and lose == 37 and tie == 0
               and raw == 9 and set(count["dirty_hearts"]) == expected
               and all(card.endswith("h") for card in count["wins"])
               and pot_before_call == 80 and final_pot == 100
               and equity == Fraction(7, 44) and raw_rate == Fraction(9, 44)
               and threshold == Fraction(1, 5) and ev == Fraction(-45, 11)
               and false_raw_ev == Fraction(5, 11))
    return {
        "status": "pass" if correct else "fail",
        "scope": "fictional_face_up_turn_all_in_no_fees_no_ties",
        "known_cards": list((*HERO, *VILLAIN, *TURN_BOARD)),
        "unknown_rivers": unknown,
        "raw_heart_completions": raw,
        "dirty_hearts": count["dirty_hearts"],
        "winning_river_cards": count["wins"],
        "winning_rivers": win,
        "losing_rivers": lose,
        "tied_rivers": tie,
        "actual_equity_fraction": str(equity),
        "actual_equity_percent": round(100 * float(equity), 2),
        "raw_heart_completion_fraction": str(raw_rate),
        "call_price_fraction": str(threshold),
        "call_price_percent": round(100 * float(threshold), 2),
        "final_pot_chips": final_pot,
        "call_ev_fraction_chips": str(ev),
        "call_ev_chips": round(float(ev), 2),
        "mistaken_raw_heart_ev_fraction_chips": str(false_raw_ev),
        "mistaken_raw_heart_ev_chips": round(float(false_raw_ev), 2),
        "caveat": "Exact conditional teaching model with revealed opponent cards, not real-time knowledge or a strategy recommendation."
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    options = parser.parse_args(argv)
    data = audit()
    if options.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("Clean outs: {}/{} winning rivers, {} hearts complete, dirty hearts {}".format(
            data["winning_rivers"], data["unknown_rivers"],
            data["raw_heart_completions"], ", ".join(data["dirty_hearts"])))
        print("Call price {}%; exact chip EV {}. Status: {}".format(
            data["call_price_percent"], data["call_ev_chips"], data["status"]))
    return 0 if data["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
