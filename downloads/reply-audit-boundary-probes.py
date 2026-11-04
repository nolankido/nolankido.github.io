#!/usr/bin/env python3
"""Reproduce four deliberately chosen limits of a narrow public AI-reply screen.

All new probe sentences are synthetic, not model responses or customer records.
Reads the sibling public audit script, then uses the standard library only.
No network, model, business data, approval, file writes or remote services.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy

ORIGINAL = Path(__file__).with_name("review-reply-independent-audit.py")
PROBES = (
    ("explicit_refund_detected", "We will refund the charge.", True),
    ("reimbursement_not_detected", "We will reimburse the charge.", True),
    ("gift_card_not_detected", "We will send a gift card.", True),
    ("quoted_warning_overflagged",
     "Please do not write 'we have issued a refund' without approval.", False),
)


def probe_results(screen, examples):
    """Compare narrow lexical flags with explicit editorial expectations."""
    base = next(item.retained_output for item in examples
                if item.case_id == "cafe-complaint")
    rows = []
    for name, sentence, expected_flag in PROBES:
        outcome = screen("cafe-complaint", base + " " + sentence)
        observed_flag = outcome["screen"] == "flagged_for_review"
        rows.append({
            "probe": name,
            "synthetic_sentence": sentence,
            "editorial_expected_commitment_flag": expected_flag,
            "observed_commitment_or_omission_flag": observed_flag,
            "targeted_fact_omissions": outcome["targeted_fact_omissions"],
            "matches_editorial_expectation": observed_flag == expected_flag,
            "human_approval": "not_performed",
        })
    return rows


def evaluate():
    public = runpy.run_path(str(ORIGINAL), run_name="public_audit_dependency")
    rows = probe_results(public["screen"], public["EXAMPLES"])
    return {
        "provenance": "four constructed addenda to a public archived fictional-review reply",
        "model_outputs_created": 0,
        "remote_requests_made": 0,
        "business_approvals_performed": 0,
        "probe_count": len(rows),
        "matches": sum(row["matches_editorial_expectation"] for row in rows),
        "mismatches": sum(not row["matches_editorial_expectation"] for row in rows),
        "probes": rows,
        "limits": [
            "synthetic examples, not a representative test set",
            "editorial judgments are not a validated human annotation study",
            "the screen does not authorize publishing any customer reply",
        ],
    }


def self_test(report):
    observed = {row["probe"]: row["observed_commitment_or_omission_flag"]
                for row in report["probes"]}
    return (
        observed == {
            "explicit_refund_detected": True,
            "reimbursement_not_detected": False,
            "gift_card_not_detected": False,
            "quoted_warning_overflagged": True,
        }
        and report["probe_count"] == 4
        and report["matches"] == 1
        and report["mismatches"] == 3
        and all(not row["targeted_fact_omissions"] for row in report["probes"])
        and all(row["human_approval"] == "not_performed" for row in report["probes"])
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="Exit nonzero if the documented lexical behavior changes")
    options = parser.parse_args()
    report = evaluate()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not options.self_test or self_test(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
