"""Exact test-only predecessor for the homepage evidence turn.

Older historical release tests may see only reviewed Turn 38 file revisions.
Unknown bytes always remain visible. This helper is not used by the builder.
"""
from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "ca1686a83d1ff5b426ed44d49e3a7af46ce85149"
RECORD = ROOT / "_tests/turn38-home-proof-change.json"


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
        raise ValueError("Turn 38 predecessor mismatch: " + name)
    return old


def before(path, value):
    import turn39_home_shortcut_history
    value = turn39_home_shortcut_history.before(path, value)
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = original(name, pair[0])
    return old if isinstance(value, bytes) else old.decode("utf-8")


def is_added_file(path, value):
    import turn39_home_shortcut_history
    value = turn39_home_shortcut_history.before(path, value)
    expected = records()["added"].get(key(path))
    return expected is not None and blob(value) == expected
