#!/usr/bin/env python3
"""Diagnose optional historical unit tests in bounded, observable local runs.

Each test module runs in a fresh process. A timeout or a module with no
actual passing tests cannot pass. No GitHub Actions or scheduled jobs.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

from local_release_checks import forbid_workflows
from run_unit_module import RESULT_PREFIX, outcome, valid_record
from release_unit_plan import check_inventory


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "_tests"


def discover(pattern: str, *, folder: Path | None = None) -> list[str]:
    """Select only repository test-module filenames in deterministic order."""
    if (not pattern.startswith("test_") or "/" in pattern or "\\" in pattern
            or ".." in pattern or not pattern.endswith(".py")):
        raise ValueError("Pattern must match test_*.py names, not paths")
    folder = TESTS if folder is None else folder
    return sorted(p.name for p in folder.glob(pattern)
                  if p.is_file() and p.name.startswith("test_") and p.suffix == ".py")


def run_file(filename: str, timeout_seconds: float, *, root: Path | None = None) -> dict:
    """Return a faithful module outcome, including import errors and timeouts."""
    command = [sys.executable, str(Path(__file__).with_name("run_unit_module.py")), filename]
    started = time.monotonic()
    try:
        done = subprocess.run(command, cwd=ROOT if root is None else root, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, encoding="utf-8",
                              errors="replace", timeout=timeout_seconds, check=False)
        output = getattr(done, "stdout", None) or ""
        records = [line[len(RESULT_PREFIX):] for line in output.splitlines()
                   if line.startswith(RESULT_PREFIX)]
        try:
            record = json.loads(records[0]) if len(records) == 1 else None
        except ValueError:
            record = None
        status = outcome(record)
        # A record and process exit status must agree. A crashed child cannot
        # become successful by printing an otherwise passing record.
        expected_exit = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2, "ERROR": 2}[status]
        if done.returncode != expected_exit:
            status = "FAIL" if done.returncode != 0 else "ERROR"
        counts = record if valid_record(record) else {}
        return {
            "file": filename, "status": status,
            "tests": counts.get("tests"), "passed": counts.get("passed"),
            "skipped": counts.get("skipped"),
            "expected_failures": counts.get("expected_failures"),
            "returncode": done.returncode, "seconds": round(time.monotonic() - started, 2),
            "output": output[-80000:],
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {
            "file": filename, "status": "TIMEOUT", "tests": None, "passed": None,
            "skipped": None, "expected_failures": None, "returncode": None,
            "seconds": round(time.monotonic() - started, 2),
            "output": output[-80000:],
        }


def checkpoint(path: Path, data: dict) -> None:
    """Persist progress after each module so an interrupted run is auditable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", default="test_*.py",
                        help="Test-module filename glob (default: every optional test module)")
    parser.add_argument("--start-index", type=int, default=0,
                        help="Zero-based index in sorted matching filenames")
    parser.add_argument("--file-limit", type=int, default=12,
                        help="Maximum modules to run (default: 12)")
    parser.add_argument("--all", action="store_true",
                        help="Run all matching modules from the start index")
    parser.add_argument("--timeout-seconds", type=float, default=90,
                        help="Hard per-module timeout (default: 90 seconds)")
    parser.add_argument("--expected-inventory", type=Path,
                        help="Exact sorted module list for a full release invocation")
    parser.add_argument("--json-output", type=Path,
                        help="Optional local checkpoint, updated after every module")
    parser.add_argument("--failure-lines", type=int, default=14,
                        help="Display this many trailing output lines for non-passing modules")
    args = parser.parse_args(argv)
    if (args.start_index < 0 or args.file_limit < 1 or args.timeout_seconds <= 0
            or not math.isfinite(args.timeout_seconds) or args.failure_lines < 0):
        parser.error("Indexes must be nonnegative and limits/timeouts must be positive")
    try:
        forbid_workflows()
        filenames = discover(args.pattern)
        if args.expected_inventory is not None:
            if not args.all or args.start_index != 0 or args.pattern != "test_*.py":
                raise ValueError("Expected inventory requires an unfiltered full unit run")
            check_inventory(args.expected_inventory, filenames)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr, flush=True)
        return 2
    if not filenames or args.start_index >= len(filenames):
        print("ERROR: No test modules selected. Nothing was counted as passing.",
              file=sys.stderr, flush=True)
        return 2
    remaining = filenames[args.start_index:]
    selected = remaining if args.all else remaining[:args.file_limit]
    receipt = {
        "scope": "local historical unit test diagnosis",
        "pattern": args.pattern, "discovered_modules": len(filenames),
        "start_index": args.start_index, "selected_modules": selected,
        "timeout_seconds": args.timeout_seconds, "completed": False,
        "results": [],
    }
    print(f"Local historical test diagnosis: {len(selected)} of {len(filenames)} modules; "
          f"{args.timeout_seconds:g}s timeout per module", flush=True)
    if args.json_output:
        checkpoint(args.json_output, receipt)
    try:
        for index, filename in enumerate(selected, start=1):
            print(f"[{index}/{len(selected)}] RUN {filename}", flush=True)
            result = run_file(filename, args.timeout_seconds)
            receipt["results"].append(result)
            print(f"[{index}/{len(selected)}] {result['status']} {filename} "
                  f"({result['tests'] if result['tests'] is not None else '?'} tests run, "
                  f"{result.get('passed')} passed, {result.get('skipped')} skipped, "
                  f"{result.get('expected_failures')} expected failures, "
                  f"{result['seconds']:.2f}s)", flush=True)
            if result["status"] != "PASS" and args.failure_lines:
                lines = result["output"].splitlines()
                for line in lines[-args.failure_lines:]:
                    if len(line) > 400:
                        line = (line[:180] + f" ... [{len(line) - 360} chars omitted] ... "
                                + line[-180:])
                    print("    " + line, flush=True)
            if args.json_output:
                checkpoint(args.json_output, receipt)
    except KeyboardInterrupt:
        print("Interrupted: completed module results are preserved; rest NOT RUN.",
              file=sys.stderr, flush=True)
        return 130
    if args.expected_inventory is not None:
        try:
            check_inventory(args.expected_inventory, discover(args.pattern))
        except (OSError, ValueError) as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr, flush=True)
            return 2
    receipt["completed"] = True
    if args.json_output:
        checkpoint(args.json_output, receipt)
    counts = {status: sum(r["status"] == status for r in receipt["results"])
              for status in ("PASS", "FAIL", "TIMEOUT", "INCOMPLETE", "ERROR")}
    observed_tests = sum(r["tests"] or 0 for r in receipt["results"])
    passed_tests = sum(r.get("passed") or 0 for r in receipt["results"])
    skipped = sum(r.get("skipped") or 0 for r in receipt["results"])
    expected_failures = sum(r.get("expected_failures") or 0 for r in receipt["results"])
    print(f"Summary: {counts['PASS']} PASS, {counts['FAIL']} FAIL, "
          f"{counts['TIMEOUT']} TIMEOUT, {counts['INCOMPLETE']} INCOMPLETE, "
          f"{counts['ERROR']} ERROR; {observed_tests} tests run, {passed_tests} actual passes, "
          f"{skipped} skips, {expected_failures} expected failures across {len(selected)} modules. "
          f"{len(filenames) - len(selected)} other matching modules not covered "
          f"by this invocation. No GitHub Actions invoked.", flush=True)
    return 0 if counts["PASS"] == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
