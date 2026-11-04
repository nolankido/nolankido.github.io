#!/usr/bin/env python3
"""Offline, bounded fact gate for a public poker-vlog editing demonstration.

Uses only the public Portland Meadows Episode 1 companion facts. The tool reads
structured editing claims, NOT video, audio, images, solver output or private
metadata. No imports, calls or data transfers from remote services.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

VERSION = "1.0"
PUBLIC_COMPANION = "https://nolankido.com/poker/episodes/portland-meadows-ep1/"
FACTS = {
    "hand_64o": {
        "source": PUBLIC_COMPANION + "#hand-64o-record",
        "position": "SB",
        "hero_hand": "6-4 offsuit",
        "villain_hand": "A-K suited",
        "winner": "hero",
        "big_blind_chips": 15000,
        "reported_stack_chips": 148000,
        "reported_stack_is_approximate": True,
        "full_board_verified": False,
        "individual_suits_verified": False,
        "solver_verdict_verified": False,
        "current_cut_timecodes_verified": False,
    },
    "hand_77": {
        "source": PUBLIC_COMPANION + "#hand-77-record",
        "position": "BB",
        "hero_hand": "7-7",
        "villain_hand": "A-T offsuit",
        "winner": "hero",
        "big_blind_chips": 30000,
        "reported_stack_chips": 585000,
        "reported_stack_is_approximate": True,
        "button_open_to_chips": 75000,
        "full_board_verified": False,
        "individual_suits_verified": False,
        "solver_verdict_verified": False,
        "current_cut_timecodes_verified": False,
    },
    "event_payout": {
        "source": PUBLIC_COMPANION + "#event-numbers",
        "advertised_first_usd": 5100,
        "received_after_deal_usd": 2900,
        "net_profit_verified": False,
    },
}
ALLOWED = {
    "case", "position", "hero_hand", "villain_hand", "winner",
    "big_blind_chips", "reported_stack_chips", "stack_bb_display",
    "stack_marked_approximate", "button_open_to_chips", "open_to_bb_display",
    "individual_suits_displayed", "full_board_displayed",
    "illustrative_label_visible", "solver_verdict_claimed_verified",
    "archived_v7_timecode_reused_for_current_cut",
    "advertised_first_usd", "received_after_deal_usd",
    "net_profit_claimed",
}


def finding(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def validate_scene(scene: object) -> list[dict[str, str]]:
    """Inspect only explicitly supplied structured claims, not a rendered edit."""
    if not isinstance(scene, dict):
        return [finding("INVALID_SCENE", "The scene must be a JSON object.")]
    case = scene.get("case")
    if not isinstance(case, str) or case not in FACTS:
        return [finding("UNKNOWN_CASE", "Use hand_64o, hand_77 or event_payout.")]
    facts = FACTS[case]
    flags: list[dict[str, str]] = []
    for key in sorted(set(scene) - ALLOWED):
        flags.append(finding("UNKNOWN_FIELD", "Unrecognized field: " + key))

    for field in ("position", "hero_hand", "villain_hand", "winner",
                  "big_blind_chips", "reported_stack_chips",
                  "button_open_to_chips", "advertised_first_usd",
                  "received_after_deal_usd"):
        if field not in scene:
            continue
        if field not in facts:
            flags.append(finding("UNSUPPORTED_FIELD", field + " is not supported for this case."))
        elif scene[field] != facts[field] or (
            type(facts[field]) is int and type(scene[field]) is not int
        ):
            flags.append(finding("FACT_CONFLICT", field + " disagrees with the public account."))

    if "stack_bb_display" in scene:
        if "reported_stack_chips" not in facts:
            flags.append(finding("UNSUPPORTED_FIELD", "No stack is documented for this case."))
        else:
            expected = facts["reported_stack_chips"] / facts["big_blind_chips"]
            shown = scene["stack_bb_display"]
            if not number(shown) or abs(shown - expected) > 0.02:
                flags.append(finding("STACK_BB_MISMATCH", "Stack BB label disagrees with the conditional source calculation."))

    if "open_to_bb_display" in scene:
        if "button_open_to_chips" not in facts:
            flags.append(finding("UNSUPPORTED_FIELD", "No button raise-to amount is documented for this case."))
        else:
            expected = facts["button_open_to_chips"] / facts["big_blind_chips"]
            shown = scene["open_to_bb_display"]
            if not number(shown) or abs(shown - expected) > 0.02:
                flags.append(finding("OPEN_TO_BB_MISMATCH", "Raise-to BB label disagrees with the source amount."))

    if "stack_marked_approximate" in scene:
        if "reported_stack_chips" not in facts:
            flags.append(finding("UNSUPPORTED_FIELD", "No stack precision is documented for this case."))
        elif scene["stack_marked_approximate"] is not True:
            flags.append(finding("STACK_PRECISION", "The source calls this stack approximate, not exact."))

    label = scene.get("illustrative_label_visible") is True
    for field, code in (
        ("individual_suits_displayed", "UNVERIFIED_SUITS"),
        ("full_board_displayed", "UNVERIFIED_BOARD"),
    ):
        if field not in scene:
            continue
        supplied = scene[field]
        if type(supplied) is not bool:
            flags.append(finding("INVALID_FIELD", field + " must be a boolean."))
        elif supplied and not label:
            flags.append(finding(code, "The source does not verify this visual. Omit it or label the reconstruction illustrative."))
    if "illustrative_label_visible" in scene and type(scene["illustrative_label_visible"]) is not bool:
        flags.append(finding("INVALID_FIELD", "illustrative_label_visible must be a boolean."))

    for field, code, detail in (
        ("solver_verdict_claimed_verified", "UNVERIFIED_SOLVER", "No independently verified solver verdict is in this public record."),
        ("archived_v7_timecode_reused_for_current_cut", "STALE_TIMECODE", "Version 7 offsets have not been verified against the newer public cut."),
        ("net_profit_claimed", "UNVERIFIED_NET_PROFIT", "The public record does not establish net profit."),
    ):
        if field not in scene:
            continue
        if type(scene[field]) is not bool:
            flags.append(finding("INVALID_FIELD", field + " must be a boolean."))
        elif scene[field]:
            flags.append(finding(code, detail))

    return flags


CLEAN_64 = {
    "case": "hand_64o", "position": "SB", "hero_hand": "6-4 offsuit",
    "villain_hand": "A-K suited", "winner": "hero",
    "big_blind_chips": 15000, "reported_stack_chips": 148000,
    "stack_bb_display": 9.87, "stack_marked_approximate": True,
}
CLEAN_77 = {
    "case": "hand_77", "position": "BB", "hero_hand": "7-7",
    "villain_hand": "A-T offsuit", "winner": "hero",
    "big_blind_chips": 30000, "reported_stack_chips": 585000,
    "stack_bb_display": 19.5, "stack_marked_approximate": True,
    "button_open_to_chips": 75000, "open_to_bb_display": 2.5,
}
CLEAN_PAYOUT = {
    "case": "event_payout", "advertised_first_usd": 5100,
    "received_after_deal_usd": 2900,
}
DEMONSTRATIONS = [
    (
        "Invented visual details",
        {**CLEAN_64, "individual_suits_displayed": True, "full_board_displayed": True},
        CLEAN_64,
        {"UNVERIFIED_SUITS", "UNVERIFIED_BOARD"},
    ),
    (
        "Incorrect BB graphics",
        {**CLEAN_77, "stack_bb_display": 18.0, "open_to_bb_display": 2.0},
        CLEAN_77,
        {"STACK_BB_MISMATCH", "OPEN_TO_BB_MISMATCH"},
    ),
    (
        "Advertised prize shown as payment",
        {**CLEAN_PAYOUT, "received_after_deal_usd": 5100},
        CLEAN_PAYOUT,
        {"FACT_CONFLICT"},
    ),
    (
        "Hindsight and old-cut timecode overstated",
        {**CLEAN_64, "solver_verdict_claimed_verified": True,
         "archived_v7_timecode_reused_for_current_cut": True},
        CLEAN_64,
        {"UNVERIFIED_SOLVER", "STALE_TIMECODE"},
    ),
]


def demo() -> dict:
    rows = []
    passed = True
    for name, before, after, expected in DEMONSTRATIONS:
        before_codes = {x["code"] for x in validate_scene(before)}
        after_codes = {x["code"] for x in validate_scene(after)}
        match = before_codes == expected and not after_codes
        passed = passed and match
        rows.append({
            "synthetic_scene": name,
            "before_codes": sorted(before_codes),
            "after_codes": sorted(after_codes),
            "passed": match,
        })
    return {
        "demo": "Four deliberately constructed edit mistakes, not model outputs or real video audits",
        "source": PUBLIC_COMPANION,
        "scenes": rows,
        "flags_before": sum(len(row["before_codes"]) for row in rows),
        "flags_after": sum(len(row["after_codes"]) for row in rows),
        "self_test_passed": passed,
        "limit": "Structured claims only. A no-targeted-flags result never approves narration, graphics, rights or a final video.",
    }


def check_file(path: Path) -> int:
    try:
        if path.stat().st_size > 1024 * 1024:
            raise ValueError("Scene JSON file must be at most 1 MiB.")
        payload = json.loads(path.read_text(encoding="utf-8"),
                             parse_constant=lambda c: (_ for _ in ()).throw(ValueError("Invalid JSON number: " + c)))
        if not isinstance(payload, dict) or not isinstance(payload.get("scenes"), list):
            raise ValueError("Expected JSON object with a scenes array.")
        scenes = payload["scenes"]
        if not 1 <= len(scenes) <= 100:
            raise ValueError("Supply 1 to 100 scenes.")
    except (OSError, UnicodeError, ValueError) as exc:
        print("Input error: " + str(exc), file=sys.stderr)
        return 1
    results = [{"index": i + 1, "case": s.get("case") if isinstance(s, dict) else None,
                "findings": validate_scene(s)} for i, s in enumerate(scenes)]
    total = sum(len(row["findings"]) for row in results)
    print(json.dumps({
        "result": "flagged" if total else "no_targeted_flags",
        "findings": total,
        "scenes": results,
        "limit": "Does not read the video or audio. Human review is required even when no flag appears.",
    }, indent=2))
    return 2 if total else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true", help="Run public synthetic before/after fixtures.")
    group.add_argument("--example", action="store_true", help="Print a local JSON starter template.")
    group.add_argument("--check", metavar="SCENES.json", type=Path, help="Check local structured scene claims.")
    args = parser.parse_args(argv)
    if args.self_test:
        result = demo()
        print(json.dumps(result, indent=2))
        return 0 if result["self_test_passed"] else 1
    if args.example:
        print(json.dumps({"scenes": [CLEAN_64, CLEAN_77, CLEAN_PAYOUT]}, indent=2))
        return 0
    return check_file(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
