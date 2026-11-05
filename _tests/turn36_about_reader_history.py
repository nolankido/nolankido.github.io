"""Verified pre-Turn-36 view for older release-integrity tests only.

An exact reviewed Git blob may be rewound, but unknown edits stay visible.
This module is test infrastructure and is never imported by the site builder.
"""
from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "feaf3226ec353f9d4376a1aad589cddeee3015eb"
RECORD = ROOT / "_tests/turn36-about-reader-change.json"
ASSET_ROUTE = "/assets/about-reader.css"


@lru_cache(maxsize=1)
def records():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def key(path):
    name = Path(path)
    if name.is_absolute():
        try:
            name = name.relative_to(ROOT)
        except ValueError:
            return name.as_posix()
    return name.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


@lru_cache(maxsize=None)
def original(name, expected):
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != expected:
        raise ValueError("Turn 36 predecessor mismatch: " + name)
    return old


def before(path, value):
    import turn37_link_integrity_history
    value = turn37_link_integrity_history.before(path, value)
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = original(name, pair[0])
    return old if isinstance(value, bytes) else old.decode("utf-8")


def is_added_file(path, value):
    import turn37_link_integrity_history
    if turn37_link_integrity_history.is_added_file(path, value):
        return True
    value = turn37_link_integrity_history.before(path, value)
    expected = records()["added"].get(key(path))
    return expected is not None and blob(value) == expected


def live_targets(items):
    """Remove only the new CSS asset from a previous release inventory."""
    import turn37_link_integrity_history
    items = turn37_link_integrity_history.live_targets(items)
    expected = records()["added"].get("assets/about-reader.css")
    result = {}
    for route, response in items.items():
        if (route == ASSET_ROUTE and isinstance(response, tuple) and len(response) == 2
                and response[0] == 200 and isinstance(response[1], bytes)
                and blob(response[1]) == expected):
            continue
        result[route] = response
    return result
