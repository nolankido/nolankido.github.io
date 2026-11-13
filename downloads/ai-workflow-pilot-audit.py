#!/usr/bin/env python3
"""Audit a small paired AI-workflow timing log without transmitting records.

Only arithmetic, input completeness, and user-entered review labels are checked.
This does not establish that the recorded times or quality labels are true.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from io import StringIO
from pathlib import Path
import re
import sys


FIELDS = (
    "case_id",
    "manual_minutes",
    "ai_preparation_minutes",
    "ai_review_minutes",
    "ai_repair_minutes",
    "quality_status",
)
QUALITY = {"accepted", "rejected", "unreviewed"}
MONEY = Decimal("0.01")


def minutes(value: str, name: str, *, positive: bool = False) -> Decimal:
    """Accept nonnegative finite decimal minutes to hundredths, never guessed blanks."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", value.strip()):
        raise ValueError(f"{name}: enter a number from 0 to 100000 with at most two decimal places")
    result = Decimal(value.strip())
    if result > 100000 or (positive and result == 0):
        raise ValueError(f"{name}: value outside the permitted range")
    return result.quantize(MONEY)


def read_rows(handle) -> list[dict]:
    reader = csv.DictReader(handle)
    if reader.fieldnames != list(FIELDS):
        raise ValueError("CSV headers must exactly match the downloadable example, in order")
    records = []
    seen = set()
    for row_number, row in enumerate(reader, start=2):
        if row_number > 1001:
            raise ValueError("Maximum 1000 cases per audit")
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Row {row_number}: missing or extra fields")
        case_id = row["case_id"].strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", case_id):
            raise ValueError(f"Row {row_number}: use a short anonymous case ID")
        if case_id in seen:
            raise ValueError(f"Row {row_number}: duplicate case ID {case_id}")
        seen.add(case_id)
        status = row["quality_status"].strip()
        if status not in QUALITY:
            raise ValueError(f"Row {row_number}: quality_status must be accepted, rejected, or unreviewed")
        record = {"case_id": case_id, "quality_status": status}
        for field in FIELDS[1:-1]:
            record[field] = minutes(row[field], f"Row {row_number} {field}", positive=field == "manual_minutes")
        records.append(record)
    if not records:
        raise ValueError("No cases recorded. Do not treat an empty log as a zero-time trial")
    return records


def summarize(records: list[dict], setup: Decimal, upkeep: Decimal) -> dict:
    manual = sum((r["manual_minutes"] for r in records), Decimal("0.00"))
    assisted = sum((r["ai_preparation_minutes"] + r["ai_review_minutes"] + r["ai_repair_minutes"]
                    for r in records), Decimal("0.00"))
    total = assisted + setup + upkeep
    status_counts = {status: sum(r["quality_status"] == status for r in records) for status in sorted(QUALITY)}
    gate = status_counts["rejected"] == 0 and status_counts["unreviewed"] == 0
    return {
        "cases": len(records),
        "status_counts": status_counts,
        "manual_minutes": manual,
        "assisted_task_minutes": assisted,
        "setup_minutes": setup,
        "upkeep_minutes": upkeep,
        "assisted_total_minutes": total,
        "difference_minutes": manual - total,
        "quality_gate_met": gate,
    }


def print_report(result: dict) -> None:
    counts = result["status_counts"]
    print(f"Cases: {result['cases']} (accepted {counts['accepted']}, rejected {counts['rejected']}, unreviewed {counts['unreviewed']})")
    print(f"Manual task total: {result['manual_minutes']:.2f} min")
    print(f"AI preparation, review and repair: {result['assisted_task_minutes']:.2f} min")
    print(f"One-time setup: {result['setup_minutes']:.2f} min")
    print(f"Window upkeep: {result['upkeep_minutes']:.2f} min")
    print(f"Assisted total: {result['assisted_total_minutes']:.2f} min")
    print(f"Time difference (manual minus assisted): {result['difference_minutes']:+.2f} min")
    print("Quality gate: " + ("ALL RECORDED CASES ACCEPTED" if result["quality_gate_met"] else "NOT MET: rejected or unreviewed cases"))
    print("This audit checks entered arithmetic and labels, not observation accuracy, causal impact, or fitness for deployment.")


def self_test() -> None:
    header = ",".join(FIELDS)
    example = header + "\n" + "\n".join([
        "P01,24,6,8,2,accepted",
        "P02,21,7,9,1,accepted",
        "P03,26,8,14,6,rejected",
        "P04,23,6,10,2,accepted",
        "P05,20,5,8,1,accepted",
        "P06,25,7,10,2,accepted",
    ]) + "\n"
    outcome = summarize(read_rows(StringIO(example)), Decimal("45.00"), Decimal("15.00"))
    assert outcome["manual_minutes"] == Decimal("139.00")
    assert outcome["assisted_task_minutes"] == Decimal("112.00")
    assert outcome["assisted_total_minutes"] == Decimal("172.00")
    assert outcome["difference_minutes"] == Decimal("-33.00")
    assert not outcome["quality_gate_met"]
    for bad in [
        header + "\n",  # No cases, not zero time.
        example.replace("P06,25", "P01,25"),  # Duplicate anonymous ID.
        example.replace("P02,21", "P02,"),  # Missing observation.
        example.replace("P04,23", "P04,-23"),  # Negative time.
        example.replace("P05,20", "P05,20.123"),  # Excess precision.
        example.replace("P03,26", "P03,26.0").replace(",rejected", ",approved"),  # Invalid status.
    ]:
        try:
            read_rows(StringIO(bad))
        except ValueError:
            continue
        raise AssertionError("Bad fixture unexpectedly accepted")
    print("Self-test passed: synthetic totals, quality gate, and six invalid-input controls")


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline AI workflow paired-case timing audit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in synthetic positive and negative checks")
    parser.add_argument("--input", type=Path, help="Local CSV in the documented six-column format")
    parser.add_argument("--setup-minutes", help="Observed one-time setup, explicitly enter 0 if none")
    parser.add_argument("--upkeep-minutes", help="Observed total upkeep during this window, explicitly enter 0 if none")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        if not args.input or args.setup_minutes is None or args.upkeep_minutes is None:
            parser.error("--input, --setup-minutes and --upkeep-minutes are all required unless using --self-test")
        setup = minutes(args.setup_minutes, "setup_minutes")
        upkeep = minutes(args.upkeep_minutes, "upkeep_minutes")
        with args.input.open("r", encoding="utf-8-sig", newline="") as handle:
            result = summarize(read_rows(handle), setup, upkeep)
        print_report(result)
        return 0
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(f"Cannot audit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
