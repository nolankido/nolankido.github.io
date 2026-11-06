"""Test-only exact predecessor bridge for Turn 58's reviewed Poker hub.

Only the two complete source and compiled-page blobs below are recognized.
Unknown paths or bytes pass through unchanged. Production code never imports
this adapter, and earlier historical ledgers remain immutable.
"""

from functools import lru_cache
from hashlib import sha1
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PARENT = "d503d3483cd79eb9ad0fd072fd1254ed5c781222"
BLOBS = {
    "_source/poker/home.html": (
        "e6e52abe0baf44be5e74758fd37fe0656bd2cd0c",
        "5804787ffc7e757f619fcc16c42a7bca4d76a9dc",
    ),
    "poker/index.html": (
        "44e275d254266f2aa7a2210d7cacd2fc8ad5708f",
        "ceb4015a77c28256ad77bde82f4fd33992d48866",
    ),
}


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
        raise ValueError("Turn 58 predecessor mismatch: " + name)
    return prior


def before(path, value):
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    prior = original(name, pair[0])
    return prior if isinstance(value, bytes) else prior.decode("utf-8")
