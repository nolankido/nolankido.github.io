#!/usr/bin/env python3
"""Bounded, public-fixture Ollama loopback check. No accounts or external API.

Run with --dry-run before an Ollama model is installed. An actual test requires
a separately installed, downloaded local model, and must be explicitly invoked.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request

PROMPT = (
    "Classify this synthetic note into Task, Check, and Decision. "
    "Note: A fictional team has three meeting notes. Before sending a summary, "
    "they must compare each proposed action against the notes and obtain approval. "
    "Use exactly three labeled lines. Do not invent a deadline."
)


def check_model_name(model: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,95}", model):
        raise ValueError("Use one installed Ollama model name without whitespace")
    if model.lower().endswith(":cloud"):
        raise ValueError("Cloud-model aliases are prohibited by this local-only check")
    return model


def run(model: str, port: int, timeout: int, dry_run: bool = False) -> dict:
    check_model_name(model)
    if not 1024 <= port <= 65535:
        raise ValueError("Port must be between 1024 and 65535")
    if not 1 <= timeout <= 180:
        raise ValueError("Timeout must be 1..180 seconds")
    result = {
        "schema_version": 1, "execution": "dry_run" if dry_run else "local_ollama",
        "destination": f"http://127.0.0.1:{port}/api/generate",
        "model": model, "fixture_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        "wall_seconds": None, "eval_count": None, "eval_duration_ns": None,
        "tokens_per_second": None, "output_sha256": None, "human_quality_review": "not_performed",
        "note": "Illustrative public fixture, not a throughput benchmark until run on a stated machine",
    }
    if dry_run:
        return result
    payload = json.dumps({"model": model, "prompt": PROMPT, "stream": False,
                          "options": {"temperature": 0, "num_predict": 96}}).encode("utf-8")
    request = urllib.request.Request(
        result["destination"], data=payload, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Local endpoint redirected; refusing to follow any redirect")

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    start = time.perf_counter()
    with opener.open(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"Local Ollama HTTP {response.status}")
        raw = response.read(1024 * 1024 + 1)
    result["wall_seconds"] = round(time.perf_counter() - start, 4)
    if len(raw) > 1024 * 1024:
        raise ValueError("Local response exceeds 1 MiB")
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("response"), str):
        raise ValueError("Local response did not have a text field")
    result["output_sha256"] = hashlib.sha256(data["response"].encode("utf-8")).hexdigest()
    for key in ("eval_count", "eval_duration"):
        value = data.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            result["eval_duration_ns" if key == "eval_duration" else key] = value
    if result["eval_count"] is not None and result["eval_duration_ns"]:
        result["tokens_per_second"] = round(result["eval_count"] * 1e9 / result["eval_duration_ns"], 2)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gemma3:4b", help="Previously downloaded local Ollama model")
    parser.add_argument("--port", type=int, default=11434, help="Local-only Ollama port")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true", help="Print null measurements without a model call")
    args = parser.parse_args(argv)
    try:
        output = run(args.model, args.port, args.timeout, args.dry_run)
    except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print("Local test could not finish: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
