"""Test-only exact Turn 42 predecessor bridge for older release regressions.

Only complete, reviewed Git blobs can be rewound. An unreviewed edit or
unknown path passes through unchanged. No production builder imports this.
"""

from functools import lru_cache
from hashlib import sha1
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PARENT = "722ede637f2fbb1fe000f78a067f7f7573327905"
RECORD = ROOT / "_tests/turn42-site-visibility-change.json"


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
        raise ValueError("Turn 42 predecessor mismatch: " + name)
    return prior


def before(path, value):
    name = key(path)
    pair = records()["files"].get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    prior = original(name, pair[0])
    return prior if isinstance(value, bytes) else prior.decode("utf-8")
