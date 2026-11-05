"""Test-only exact Turn 41 predecessor adapter for historical release checks.

Only the five fully reviewed release-check and page blobs are recognized. All unknown content
passes through, so a new or tampered change cannot be hidden from old tests.
"""

from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PARENT = "3c395223378df22f18c982daefb35c28d6142114"
RECORD = ROOT / "_tests/turn41-channel-route-change.json"


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
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()


@lru_cache(maxsize=None)
def original(name, expected):
    prior = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(prior) != expected:
        raise ValueError("Turn 41 predecessor mismatch: " + name)
    return prior


def before(path, value):
    import turn42_site_visibility_history
    value = turn42_site_visibility_history.before(path, value)
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    prior = original(name, pair[0])
    return prior if isinstance(value, bytes) else prior.decode("utf-8")
