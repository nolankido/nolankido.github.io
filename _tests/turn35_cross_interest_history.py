"""Exact test-only predecessor for the public AI-and-poker article release.

Only complete reviewed Git blobs may be rewound. A different edit, path, or
response remains visible to historical tests. No production module imports it.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "b0162de5714168fbcc707682eb2cb723ce30e551"
RECORD = ROOT / "_tests/turn35-cross-interest-change.json"
ROUTE = "/technology/ai-poker-video-evidence/"


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
        raise ValueError("Turn 35 predecessor differs from reviewed Git blob: " + name)
    return old


def before(path, value):
    import turn36_about_reader_history
    value = turn36_about_reader_history.before(path, value)
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = original(name, pair[0])
    return old if isinstance(value, bytes) else old.decode("utf-8")


def is_added_file(path, value):
    import turn36_about_reader_history
    if turn36_about_reader_history.is_added_file(path, value):
        return True
    value = turn36_about_reader_history.before(path, value)
    known = records()["added"].get(key(path))
    return known is not None and blob(value) == known


def pages(items):
    """Remove this exact new article from a pre-Turn-35 publication view."""
    added = records()["page"]
    return [deepcopy(item) for item in items if item != added]


def live_targets(items):
    """An older live inventory cannot know this one later approved route."""
    import turn36_about_reader_history
    items = turn36_about_reader_history.live_targets(items)
    expected = records()["added"].get("technology/ai-poker-video-evidence/index.html")
    result = {}
    for route, response in items.items():
        if (route == ROUTE and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes) and blob(response[1]) == expected):
            continue
        result[route] = response
    return result
