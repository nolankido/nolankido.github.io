"""Only the exact Turn 37 code and verification files can be rewound for old tests."""
from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "6a5d017d49722f9ae06126761098c3e42244bf30"
RECORD = ROOT / "_tests/turn37-link-integrity-change.json"
TARGET_ROUTE = "/downloads/reply-audit-boundary-probes.py"


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
    prior = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(prior) != expected:
        raise ValueError("Turn 37 predecessor mismatch: " + name)
    return prior


def before(path, value):
    import turn38_home_proof_history
    value = turn38_home_proof_history.before(path, value)
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    prior = original(name, pair[0])
    return prior if isinstance(value, bytes) else prior.decode("utf-8")


def is_added_file(path, value):
    import turn38_home_proof_history
    value = turn38_home_proof_history.before(path, value)
    expected = records()["added"].get(key(path))
    return expected is not None and blob(value) == expected


def live_targets(items):
    """Earlier inventories did not yet verify the linked synthetic probe download."""
    expected = records()["verified_download"]
    result = {}
    for route, response in items.items():
        if (route == TARGET_ROUTE and isinstance(response, tuple) and len(response) == 2
                and response[0] == 200 and isinstance(response[1], bytes)
                and blob(response[1]) == expected):
            continue
        result[route] = response
    return result
