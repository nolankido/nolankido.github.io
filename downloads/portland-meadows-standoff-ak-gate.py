#!/usr/bin/env python3
"""Bounded offline check for the Portland Meadows Stand Off A-K source ledger.

This reads an archived participant production-summary record, NOT the video,
private camera files, a solver, or a tournament organizer's source. A clean
check means only that selected fields still match this reviewed record.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

LEDGER = Path(__file__).with_name("portland-meadows-standoff-ak-source-ledger.json")

SOURCE_VALUES = {
    "schema_version": 1,
    "author": "Nolan Kido",
    "public_video_url": "https://www.youtube.com/watch?v=I75GOBVXij4",
}
EVENT_VALUES = {
    "buy_in_usd": 200,
    "starting_stack_chips": 30000,
    "reported_stage": "round 10 of 12",
    "clock_observation_players_left": 17,
    "clock_observation_entries": 78,
    "sb_chips": 3000,
    "bb_chips": 6000,
    "bb_ante_chips": 6000,
    "result": "Player reports busting in round 10 and not cashing",
}
DECISION_VALUES = {
    "hero_position": "button",
    "hole_cards_reported": "A-K",
    "hole_card_suits_from_v9_source": "A clubs, K diamonds",
    "starting_stack_approx_chips": 61000,
    "opener_position": "early position",
    "opener_raise_to_chips": 15000,
    "middle_caller_called_chips": 15000,
    "first_decision": "Hero flat-calls 15000",
    "after_flat_approx_chips": 46000,
    "bb_previous_blind_chips": 6000,
    "bb_additional_to_call_before_jam_chips": 9000,
    "hero_calls_additional_approx_chips": 46000,
    "big_blind_revealed": "K-K",
    "opener_revealed": "Q-Q",
    "action_after_first_decision": [
        "big blind shoves",
        "early-position opener reshoves",
        "middle caller folds",
        "hero calls approximately 46000 more",
    ],
}
MUST_BE_FALSE = {
    "record": (
        "current_cut_reviewed", "source_clip_and_hole_card_stills_publicly_included",
        "episode_calendar_date_independently_confirmed",
        "frame_accurate_video_chapters_verified",
        "opponent_identification_authorized",
    ),
    "event": ("payout_amount_known", "payout_structure_independently_verified"),
    "decision": (
        "hole_card_suits_independently_checked_in_current_upload",
        "full_board_verified", "villain_card_suits_verified",
        "exact_effective_stacks_verified", "numerical_icm_solution_verified",
        "solver_verdict_verified", "final_human_review_of_uploaded_video_complete",
    ),
}
TEXT_BOUNDARIES = {
    "source_kind": ("archived v9", "not an independently checked current YouTube cut"),
    "public_release_status": ("Supplementary source review only", "not a timecode-verified"),
    "editorial_rule": ("First decision to flat", "second decision facing two shoves",
                       "No invented board"),
    "later_read": ("retrospective hypothesis", "not a validated range"),
}

EXPECTED_FIELDS = {
    "root": {"schema_version", "title", "author", "public_video_url", "source_kind", "public_release_status", "current_cut_reviewed", "source_clip_and_hole_card_stills_publicly_included", "episode_calendar_date_independently_confirmed", "frame_accurate_video_chapters_verified", "opponent_identification_authorized", "event", "decision", "editorial_rule"},
    "event": {"format", "buy_in_usd", "starting_stack_chips", "reported_stage", "clock_observation_players_left", "clock_observation_entries", "sb_chips", "bb_chips", "bb_ante_chips", "result", "payout_amount_known", "payout_structure_independently_verified"},
    "decision": {"hero_position", "hole_cards_reported", "hole_card_suits_from_v9_source", "hole_card_suits_independently_checked_in_current_upload", "starting_stack_approx_chips", "opener_position", "opener_raise_to_chips", "middle_caller_called_chips", "first_decision", "after_flat_approx_chips", "bb_previous_blind_chips", "bb_additional_to_call_before_jam_chips", "action_after_first_decision", "hero_calls_additional_approx_chips", "big_blind_revealed", "opener_revealed", "full_board_verified", "villain_card_suits_verified", "exact_effective_stacks_verified", "numerical_icm_solution_verified", "solver_verdict_verified", "later_read", "immediate_after_hand_opinion", "final_human_review_of_uploaded_video_complete"},
}

def flag(items: list[dict[str, str]], code: str, path: str, detail: str) -> None:
    items.append({"code": code, "field": path, "detail": detail})


def validate(value: object) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return [{"code": "INVALID_DOCUMENT", "field": "root",
                 "detail": "Expected a JSON object."}]
    event, hand = value.get("event"), value.get("decision")
    if not isinstance(event, dict) or not isinstance(hand, dict):
        return [{"code": "INVALID_DOCUMENT", "field": "event/decision",
                 "detail": "Both event and decision must be objects."}]
    for label, obj in (("root", value), ("event", event), ("decision", hand)):
        for field in sorted(set(obj) - EXPECTED_FIELDS[label]):
            flag(results, "UNREVIEWED_FIELD", label + "." + field,
                 "This private or unsupported field is not part of the approved public record.")
        for field in sorted(EXPECTED_FIELDS[label] - set(obj)):
            flag(results, "MISSING_FIELD", label + "." + field,
                 "The original public field has been removed.")
    for label, obj, required in (
        ("root", value, SOURCE_VALUES),
        ("event", event, EVENT_VALUES),
        ("decision", hand, DECISION_VALUES),
    ):
        for key, expected in required.items():
            actual = obj.get(key)
            if actual != expected or type(actual) is not type(expected):
                flag(results, "SOURCE_CONFLICT", label + "." + key,
                     "Recorded value or data type has changed.")
    for label, obj in (("record", value), ("event", event), ("decision", hand)):
        for key in MUST_BE_FALSE[label]:
            if obj.get(key) is not False:
                flag(results, "UNVERIFIED_AS_FACT", label + "." + key,
                     "This source does not establish the proposed verification.")
    for key, required in TEXT_BOUNDARIES.items():
        obj = hand if key == "later_read" else value
        actual = obj.get(key)
        if not isinstance(actual, str) or any(phrase.lower() not in actual.lower() for phrase in required):
            flag(results, "MISSING_BOUNDARY", key,
                 "Required provenance or retrospective limit was removed.")
    def amount(key: str) -> int | None:
        value = hand.get(key)
        return value if type(value) is int else None
    starting, first_call = amount("starting_stack_approx_chips"), amount("opener_raise_to_chips")
    remainder, second_call = amount("after_flat_approx_chips"), amount("hero_calls_additional_approx_chips")
    posted, bb_increment = amount("bb_previous_blind_chips"), amount("bb_additional_to_call_before_jam_chips")
    if starting is None or first_call is None or remainder is None or remainder != starting - first_call:
        flag(results, "STACK_ARITHMETIC", "decision.after_flat_approx_chips",
             "Approximate stack less initial call no longer matches.")
    if remainder is None or second_call is None or second_call != remainder:
        flag(results, "STACK_ARITHMETIC", "decision.hero_calls_additional_approx_chips",
             "Second decision amount differs from recorded remainder.")
    if first_call is None or posted is None or bb_increment is None or bb_increment != first_call - posted:
        flag(results, "BLIND_ARITHMETIC", "decision.bb_additional_to_call_before_jam_chips",
             "Additional call from the posted big blind no longer matches.")
    if not isinstance(hand.get("later_read"), str) or "the hotel" not in hand["later_read"].lower():
        flag(results, "RETROSPECTIVE_REQUIRED", "decision.later_read",
             "The range interpretation must remain a later personal reassessment.")
    if "current" in str(value.get("public_release_status", "")).lower() and value.get("current_cut_reviewed") is True:
        flag(results, "UNVERIFIED_AS_FACT", "current_cut_reviewed",
             "A source packet is not a current-video audiovisual audit.")
    return results


def load(path: Path) -> object:
    if path.stat().st_size > 100_000:
        raise ValueError("A source ledger must be under 100 KB.")
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=lambda x: (_ for _ in ()).throw(
                          ValueError("Invalid JSON constant " + x)))


def self_test() -> bool:
    base = load(LEDGER)
    scenarios = [("unchanged record", base, [])]
    changes = [
        ("overstated uploaded-cut review", "current_cut_reviewed", True, "UNVERIFIED_AS_FACT"),
        ("altered hero cards", "hole_cards_reported", "A-Q", "SOURCE_CONFLICT"),
        ("invented opponent suits", "villain_card_suits_verified", True, "UNVERIFIED_AS_FACT"),
        ("miscounted remainder", "after_flat_approx_chips", 43000, "STACK_ARITHMETIC"),
        ("reversed action", "action_after_first_decision",
         ["early-position opener reshoves", "big blind shoves"], "SOURCE_CONFLICT"),
        ("lost later-read caveat", "later_read", "Big blind must have QQ+.",
         "MISSING_BOUNDARY"),
    ]
    for name, field, replacement, expected in changes:
        modified = deepcopy(base)
        area = modified if field == "current_cut_reviewed" else modified["decision"]
        area[field] = replacement
        scenarios.append((name, modified, [expected]))
    reports = [{"test": name, "codes": sorted({f["code"] for f in validate(doc)}),
                "expected_present": sorted(expected)}
               for name, doc, expected in scenarios]
    ok = reports[0]["codes"] == [] and all(
        all(code in row["codes"] for code in row["expected_present"])
        for row in reports[1:])
    print(json.dumps({
        "synthetic": True, "passed": ok, "cases": reports,
        "limit": "Constructed mutations are not mistakes observed in the published video."
    }, indent=2))
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--check", metavar="LEDGER.json", type=Path)
    exclusive.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            return 0 if self_test() else 1
        document = load(args.check)
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print("Input error: " + str(error), file=sys.stderr)
        return 1
    findings = validate(document)
    print(json.dumps({
        "result": "flagged" if findings else "no_targeted_flags",
        "findings": findings, "flag_count": len(findings),
        "limit": "Static source consistency only; not a video, tournament, solver or audio QA."
    }, indent=2))
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
