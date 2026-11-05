"""Exact test-only predecessor for the locally verified Turn 34 repairs.

Historical assertions use the previous release's complete files and metadata.
Unknown edits remain visible. No production module imports this adapter.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha1
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "80170a3909e2a70fcbbb34ea667953b2af77e45f"
RECORD = Path("_tests/turn34-release-integrity-change.json")


@lru_cache(maxsize=1)
def records():
    return json.loads((ROOT / RECORD).read_text(encoding="utf-8"))


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


@lru_cache(maxsize=None)
def original(name, expected):
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != expected:
        raise ValueError("Turn 34 predecessor mismatch: " + name)
    return old


def before(path, value):
    import turn35_cross_interest_history
    value = turn35_cross_interest_history.before(path, value)
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = original(name, pair[0])
    return old if isinstance(value, bytes) else old.decode("utf-8")


def is_added_file(path, value):
    import turn35_cross_interest_history
    if turn35_cross_interest_history.is_added_file(path, value):
        return True
    value = turn35_cross_interest_history.before(path, value)
    expected = records()["added"].get(key(path))
    return expected is not None and blob(value) == expected


def pages(items):
    import turn35_cross_interest_history
    items = turn35_cross_interest_history.pages(items)
    old, current = records()["start_here"]
    return [deepcopy(old) if item == current else item for item in items]


def live_targets(items):
    import turn35_cross_interest_history
    items = turn35_cross_interest_history.live_targets(items)
    added = records()["live_targets"]
    result = {}
    for route, response in items.items():
        if (route in added and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes)
                and blob(response[1]) == added[route]):
            continue
        result[route] = response
    return result
