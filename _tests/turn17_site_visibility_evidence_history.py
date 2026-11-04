"""Test-only exact predecessor for Turn 17's public visibility evidence record.

Only reviewed, full Git blobs are rewound. Unknown modifications pass through.
No production builder imports this historical fixture.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "bfb7ca696054ab359cdb651f947132c6b0ee234d"
BLOBS = {
    "_source/technology/home.html": ("a4e9f1901588a9448ac7bb6da2f55c8ab3d5c0d2", "fe243f9be6044cb042e81298e0356b40570d7b17"),
    "technology/index.html": ("2c06cbe03b7b6524572441159b04440e0b958b07", "0ae9fe7bae69a764e29bfbe2e5925c588a2b4786"),
    "_tests/turn16_small_business_pilot_history.py": ("6c7f88cf99fbfaf4c3a9dd8c6d4dbabfee07b6c6", "d0ba69041b44409cd7cfefb41082ddca2f1777f5"),
    "_tests/test_turn16_small_business_pilot.py": ("ce8a83fbc07d62b68865922444a3e429a80cfd0f", "6b2278dfa6d1701a164aa968131e9988e9a24c76"),
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
    import turn21_poker_vlog_qa_history
    value = turn21_poker_vlog_qa_history.before(path, value)
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    previous = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(previous) != known[0]:
        raise ValueError("Turn 17 predecessor Git blob mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")
