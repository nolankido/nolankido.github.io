"""Test-only exact predecessor for Turn 39's homepage evidence shortcut.

Only a complete, reviewed Git blob is rewound. Unexpected modifications are
never hidden from an older regression test. The site builder does not import
this module.
"""
from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "f7fe553a7ec8fc93538b8899b2c5c95abf1caa0b"
RECORD = ROOT / "_tests/turn39-home-shortcut-change.json"


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
        raise ValueError("Turn 39 predecessor mismatch: " + name)
    return prior


def before(path, value):
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    prior = original(name, pair[0])
    return prior if isinstance(value, bytes) else prior.decode("utf-8")
