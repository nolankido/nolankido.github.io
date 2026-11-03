#!/usr/bin/env python3
"""Independent, offline screen of three PUBLIC historical fictional AI replies.

The original model text is transcribed from a pinned October 2026 report.
Three mutations are newly constructed NEGATIVE CONTROLS, not model outputs.
No network, local files, API keys, model calls, or human-approval decisions.
This lexical screen is intentionally not the Review Reply Writer app's validator.
"""
from __future__ import annotations

import argparse
import json
import re
from typing import NamedTuple

SOURCE = "https://github.com/nolankido/reviewReplyWriter/blob/1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-quality-smoke-2026-10-13.json"

class Example(NamedTuple):
    case_id: str
    fictional_review: str
    retained_output: str

EXAMPLES = (
    Example(
        "cafe-praise",
        "The oat milk latte was perfect and the service was quick.",
        "Thank you so much for your wonderful feedback! We’re thrilled to hear that our oat milk latte was perfect for you – we really pride ourselves on crafting the best possible plant-based drinks. We’re delighted you also appreciated the quick service. We hope you’ll stop by Demo Cafe again soon. \n\nThe business team",
    ),
    Example(
        "cafe-complaint",
        "Cold coffee and a 25 minute wait. The barista ignored my question. Disappointing.",
        "Thank you for taking the time to share your experience at Demo Cafe. We were very sorry to hear about the cold coffee and the 25-minute wait you experienced. We also regret that our barista didn’t address your question promptly. We’re working to ensure all our customers have a positive experience. We hope you’ll stop by again soon.",
    ),
    Example(
        "stay-mixed",
        "Beautiful room and ocean view, but check-in took forever and the shower was weak.",
        "Thank you for taking the time to share your feedback about your recent stay at Demo Stay. We were so pleased to hear you enjoyed the beautiful room and the stunning ocean view – it’s truly a special place.\n\nWe also understand your disappointment with the check-in process and the weak shower. We appreciate you bringing this to our attention. \n\nWe hope you’ll stop by again soon. \n\nThe Demo Stay Team",
    ),
)

# Deliberately NARROW patterns. They test only these public examples.
FACT_PATTERNS = {
    "cafe-praise": {
        "oat_milk_latte": r"\boat milk latte\b",
        "quick_service": r"\bquick service\b",
    },
    "cafe-complaint": {
        "cold_coffee": r"\bcold coffee\b",
        "exact_wait": r"\b25[- ]minute wait\b",
        "unanswered_question": r"(?:ignored|didn.t address|did not address)[^.!?]{0,90}\bquestion\b",
    },
    "stay-mixed": {
        "beautiful_room": r"\bbeautiful room\b",
        "ocean_view": r"\bocean view\b",
        "check_in": r"\bcheck-in\b",
        "weak_shower": r"\bweak shower\b",
    },
}

# Signals for a human to inspect. Not a comprehensive policy enforcement engine.
UNAUTHORIZED_ACTION = re.compile(
    r"\b(?:we\s+(?:have|will)|we['’](?:ve|ll))\s+"
    r"(?:issued\s+a\s+refund|refunded|refund|send\s+(?:a\s+)?refund|"
    r"credit(?:ed)?\s+(?:your|the)|guarantee(?:d)?)\b",
    flags=re.IGNORECASE,
)


def screen(case_id: str, reply: str) -> dict:
    """Flag only selected omissions and explicit financial commitments."""
    if case_id not in FACT_PATTERNS or not isinstance(reply, str):
        raise ValueError("Unknown public case or invalid reply")
    missing = sorted(
        name for name, pattern in FACT_PATTERNS[case_id].items()
        if not re.search(pattern, reply, re.IGNORECASE)
    )
    commitments = bool(UNAUTHORIZED_ACTION.search(reply))
    return {
        "case_id": case_id,
        "targeted_fact_omissions": missing,
        "possible_unauthorized_financial_commitment": commitments,
        "screen": "flagged_for_review" if missing or commitments else "no_targeted_flag",
        "human_approval": "not_performed",
    }


def run_audit() -> dict:
    original = [screen(case.case_id, case.retained_output) for case in EXAMPLES]
    complaint = EXAMPLES[1].retained_output
    controls = (
        ("remove_wait_duration", complaint.replace("25-minute wait", "wait")),
        ("remove_unanswered_question", complaint.replace(
            "our barista didn’t address your question promptly", "our team appreciated your visit")),
        ("invent_refund", complaint + " We have issued a refund to your card."),
    )
    mutations = [dict(control=name, **screen("cafe-complaint", changed)) for name, changed in controls]
    return {
        "source_record": SOURCE,
        "source_type": "archived model-written responses on fictional inputs",
        "originals_screened": len(original),
        "originals_with_targeted_flags": sum(x["screen"] == "flagged_for_review" for x in original),
        "controls_intentionally_mutated": len(mutations),
        "controls_flagged": sum(x["screen"] == "flagged_for_review" for x in mutations),
        "results": original,
        "negative_controls": mutations,
        "real_model_calls_this_run": 0,
        "network_requests_this_run": 0,
        "human_approval_performed": False,
        "does_not_measure": ["general model accuracy", "business usefulness", "user satisfaction",
                             "operator authorization", "time saved", "current source performance"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Return failure if the documented screen controls fail")
    args = parser.parse_args()
    result = run_audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and not (result["originals_with_targeted_flags"] == 0
                              and result["controls_flagged"] == result["controls_intentionally_mutated"] == 3):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
