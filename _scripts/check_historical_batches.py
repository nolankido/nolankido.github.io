#!/usr/bin/env python3
"""Diagnose optional historical unit tests in bounded, observable local runs.

Each test module runs in a fresh process. A timeout is an INCOMPLETE result,
never a pass. No GitHub Actions, network services or scheduled jobs are used.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from local_release_checks import forbid_workflows


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "_tests"
TEST_COUNT = re.compile(r"\bRan (\d+) tests? in ")
SKIPPED = re.compile(r"\bskipped=(\d+)")


def discover(pattern: str) -> list[str]:
    """Select only repository test-module filenames in deterministic order."""
    if (not pattern.startswith("test_") or "/" in pattern or "\\" in pattern
            or ".." in pattern or not pattern.endswith(".py")):
        raise ValueError("Pattern must match test_*.py names, not paths")
    return sorted(p.name for p in TESTS.glob(pattern)
                  if p.is_file() and p.name.startswith("test_") and p.suffix == ".py")


def run_file(filename: str, timeout_seconds: float) -> dict:
    """Return a faithful module outcome, including import errors and timeouts."""
    command = [sys.executable, "-m", "unittest", "discover", "-s", "_tests",
               "-p", filename, "-q"]
    started = time.monotonic()
    try:
        done = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, encoding="utf-8",
                              errors="replace", timeout=timeout_seconds, check=False)
        output = done.stdout or ""
        matches = TEST_COUNT.findall(output)
        count = int(matches[-1]) if matches else 0
        if done.returncode == 0 and count > 0 and re.search(r"(?m)^OK(?:\s|$)", output):
            status = "PASS"
        elif done.returncode != 0:
            status = "FAIL"
        else:
            status = "ERROR"  # A zero-test or malformed result is not success.
        return {
            "file": filename, "status": status, "tests": count,
            "skipped": int(SKIPPED.findall(output)[-1]) if SKIPPED.findall(output) else 0,
            "returncode": done.returncode, "seconds": round(time.monotonic() - started, 2),
            "output": output[-80000:],
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {
            "file": filename, "status": "TIMEOUT", "tests": None,
            "skipped": None, "returncode": None,
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
    parser.add_argument("--json-output", type=Path,
                        help="Optional local checkpoint, updated after every module")
    parser.add_argument("--failure-lines", type=int, default=14,
                        help="Display this many trailing output lines for non-passing modules")
    args = parser.parse_args(argv)
    if (args.start_index < 0 or args.file_limit < 1 or args.timeout_seconds <= 0
            or args.failure_lines < 0):
        parser.error("Indexes must be nonnegative and limits/timeouts must be positive")
    try:
        forbid_workflows()
        filenames = discover(args.pattern)
    except (RuntimeError, ValueError) as exc:
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
                  f"({result['tests'] if result['tests'] is not None else '?'} tests, "
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
    receipt["completed"] = True
    if args.json_output:
        checkpoint(args.json_output, receipt)
    counts = {status: sum(r["status"] == status for r in receipt["results"])
              for status in ("PASS", "FAIL", "TIMEOUT", "ERROR")}
    observed_tests = sum(r["tests"] or 0 for r in receipt["results"])
    print(f"Summary: {counts['PASS']} PASS, {counts['FAIL']} FAIL, "
          f"{counts['TIMEOUT']} TIMEOUT, {counts['ERROR']} ERROR; "
          f"{observed_tests} completed tests observed across {len(selected)} modules. "
          f"{len(filenames) - len(selected)} other matching modules not covered "
          f"by this invocation. No GitHub Actions invoked.", flush=True)
    return 0 if counts["PASS"] == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
