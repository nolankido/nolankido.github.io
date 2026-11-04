"""Exact test-only predecessor for Turn 26 Technology entry redesign.

Return only complete, reviewed predecessor files. Unknown modifications remain
visible to historical tests. Production page building never imports this module.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "e7d9fdb8ab000e996734a02af83cf65132411a58"
BLOBS = {
    "_source/technology/home.html": (
        "931663ca325e016f9639faf64e8d1b663c702f05",
        "499be21fb9642250eda75a4da7b27c96d9968ea1",
    ),
    "technology/index.html": (
        "9e8f4fb3e79ca67779971aaddc401494624f2108",
        "4e149763aa9fadedfa0be99cad5257a2f3321564",
    ),
    "find/index.html": (
        "d21045cc1559c9958f446d5df50cf5b4d7ccdd0a",
        "e41a4cd0cbb8f619ba676b03021720fd08c1ec5b",
    ),
}


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
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()


def before(path, value):
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    previous = subprocess.check_output(
        ["git", "show", PARENT + ":" + name], cwd=ROOT
    )
    if blob(previous) != known[0]:
        raise ValueError("Turn 26 predecessor Git blob mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")
