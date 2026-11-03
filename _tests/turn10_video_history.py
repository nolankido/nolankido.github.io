"""Exact, test-only predecessor for Turn 10's public poker video-link repair.

The old public link became private. Historical release tests may inspect the
prior approved bytes, but current pages must link to the accessible upload.
This adapter never modifies live content or hides unknown mutations.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "e7072a370184a6750fa1da640d13d8b5b47d73f5"
BLOBS = {
    "_source/poker/portland-meadows-ep1.html": ("30e3eefc4fafab55837a9a4587f34fd5894a8da4", "9d122384ab5c38768f2ed15102caa1b8062136c1"),
    "poker/episodes/portland-meadows-ep1/index.html": ("015f90eef1dcef84932fa3d68820a7f2ffe5d00b", "11eefdbac2cabcb3729d2b6d245680aae5296e52"),
    "_scripts/poker_episode.py": ("89a4de4ae9c6b8c6eb5fed68958df41e1ea09246", "806131b58d220322418ed88fca7e29e4dba7a7cb"),
    "_tests/test_portland_episode.py": ("e67a2fb6b0c52f9729d88d2e20064b38d5269882", "5c4db3db79047f0007a73405b0c71de247715997"),
    "_tests/test_real_portland_hands.py": ("e681a8cffdf0e600944c12431988dadcaeae2f48", "9a6bf8c7c7e9396f85bb7ca7c6ae6d8fcea330bf"),
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
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, value):
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != pair[0]:
        raise ValueError("Turn 10 predecessor Git blob mismatch: " + name)
    return old if isinstance(value, bytes) else old.decode("utf-8")
