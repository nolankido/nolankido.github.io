#!/usr/bin/env python3
"""Offline, bounded source-trace check for Nolan Kido's recorded notes task.

Reads the public October 27 source/output text. Does not call an AI model,
validate external project claims, audit a calendar or send a network request.
The synthetic self-test is deliberately constructed, not observed AI failures.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

# Exact tasks and source-note constraints from the public N1-N8 record.
# This is a specific case checker, not a generic truth or quality model.
RULES = (
    ("Prepare a permanent Review Reply Writer page", ("N1", "N2"), "ready to prepare", ("historical", "current-source quality")),
    ("Prepare a permanent Preflight / canonKeeper page", ("N1", "N3"), "ready to prepare", ("correct findings", "incorrect findings", "unresolved cases")),
    ("Prepare a permanent Dinner on Time page", ("N1", "N4"), "ready to prepare", ("deterministic", "not a live Alexa service", "no runtime AI")),
    ("Connect verified public-work profiles", ("N5",), "ready to prepare", ("github", "dev")),
    ("Complete the required fields and connections for each case", ("N8",), "editorial requirement", ("six requirements",)),
    ("Preserve the main subject order", ("N5",), "editorial requirement", ("technology", "living well", "poker", "creative work")),
    ("Keep unsupported outcomes and commitments out of the copy", ("N7",), "editorial requirement", ("no deadline", "time saving")),
    ("Personal tournament story", ("N6",), "requires source material", ("no publishable",)),
    ("Completed Living Well trial report", ("N6",), "requires source material", ("no publishable",)),
    ("Local-laptop comparison", ("N6",), "requires source material", ("no publishable",)),
    ("Personal travel plan", ("N6",), "requires source material", ("no publishable",)),
)
MARKER = "===== VERBATIM ASSISTANT OUTPUT ====="
DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
NOTE = re.compile(r"\bN[1-8]\b")


def parse_rows(document: str) -> list[dict[str, str]]:
    """Read only the verbatim output tables, not the input notes or prose."""
    if document.count(MARKER) != 1:
        raise ValueError("Expected one verbatim-output boundary in the public record")
    output = document.split(MARKER, 1)[1]
    result = []
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 4:
            raise ValueError("Expected exactly four Markdown table columns")
        if cells[0] == "Task" or all(set(c) <= {"-", ":"} for c in cells):
            continue
        result.append(dict(zip(("task", "evidence", "action", "status"), cells)))
    if not result:
        raise ValueError("No checklist rows found in the recorded output")
    return result


def audit(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    findings = []

    def flag(code: str, task: str, detail: str) -> None:
        findings.append({"code": code, "task": task, "detail": detail})

    expected = {task: (set(refs), status, limits) for task, refs, status, limits in RULES}
    found = {}
    for row in rows:
        task = row["task"]
        if task in found:
            flag("DUPLICATE_TASK", task, "Task appears more than once")
            continue
        found[task] = row
        if task not in expected:
            flag("UNRECOGNIZED_TASK", task, "Not one of the 11 documented tasks")
            continue
        refs, status, limits = expected[task]
        actual_refs = set(NOTE.findall(row["evidence"]))
        if actual_refs != refs:
            flag("SOURCE_MISMATCH", task, "Expected " + ", ".join(sorted(refs)) + "; got " + ", ".join(sorted(actual_refs)))
        if row["status"] != status:
            flag("STATUS_MISMATCH", task, "Expected " + status + "; got " + row["status"])
        combined = (row["evidence"] + " " + row["action"]).lower()
        for phrase in limits:
            if phrase.lower() not in combined:
                flag("MISSING_BOUNDARY", task, "Source condition absent: " + phrase)
        if DATE.search(row["action"]):
            flag("UNSUPPORTED_DATE", task, "An absolute action date was inserted without source authorization")
    for task in expected:
        if task not in found:
            flag("MISSING_TASK", task, "Documented task is absent")
    return findings


def sample_rows() -> list[dict[str, str]]:
    """Constructed valid rows for a deterministic checker self-test only."""
    return [dict(task=task, evidence=", ".join(refs) + ": " + "; ".join(limits),
                 action="Check the listed public source before acting", status=status)
            for task, refs, status, limits in RULES]


def self_test() -> bool:
    import copy
    base = sample_rows()
    scenarios = [("baseline", base, [])]
    wrong = copy.deepcopy(base)
    wrong[-1]["status"] = "ready to prepare"
    scenarios.append(("invented readiness", wrong, ["STATUS_MISMATCH"]))
    wrong = copy.deepcopy(base)
    wrong[-1]["evidence"] = wrong[-1]["evidence"].replace("N6", "N5")
    scenarios.append(("wrong source", wrong, ["SOURCE_MISMATCH"]))
    wrong = copy.deepcopy(base)
    wrong[2]["evidence"] = wrong[2]["evidence"].replace("no runtime AI", "runtime AI")
    scenarios.append(("removed runtime limit", wrong, ["MISSING_BOUNDARY"]))
    wrong = copy.deepcopy(base)
    wrong[6]["action"] += "; publish by 2026-12-01"
    scenarios.append(("invented deadline", wrong, ["UNSUPPORTED_DATE"]))
    cases = [{"scenario": title, "codes": [f["code"] for f in audit(rows)]} for title, rows, _ in scenarios]
    good = all(row["codes"] == expected for row, (_, _, expected) in zip(cases, scenarios))
    print(json.dumps({"synthetic": True, "passed": good, "cases": cases,
                      "limit": "Constructed controls, not observed AI output mistakes or a general error rate."}, indent=2))
    return good


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--check", type=Path, metavar="PUBLIC_RECORD.txt")
    args = parser.parse_args()
    if args.self_test:
        return 0 if self_test() else 1
    try:
        if args.check.stat().st_size > 250_000:
            raise ValueError("Input exceeds the small public-record checker limit")
        rows = parse_rows(args.check.read_text(encoding="utf-8"))
        findings = audit(rows)
    except (OSError, UnicodeError, ValueError) as exc:
        print("Input error: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"rows": len(rows), "flags": len(findings), "findings": findings,
                      "limit": "Checks only source-note IDs, task statuses, and selected explicit conditions. It does not establish external truth, real action completion, or measured time savings."}, indent=2))
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
