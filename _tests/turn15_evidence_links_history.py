"""Test-only exact predecessor for Turn 15 public evidence-link discovery.

Only complete, reviewed Git blobs are restored to the preceding commit.
Unknown edits pass unchanged. No production builder or workflow uses this.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "cc398df559e4d29a2273e5358709d64fd4c0405a"
BLOBS = {
    "_source/home.html": ("323be2d4d02a90ffc31022bc2d962f486931c5b0", "a3822944a1ba0f31938209e13ffec207fb14d0f5"),
    "index.html": ("416d9f7c95bb0996aca42f2eb344ccf445af93b1", "789e4a3d06d714f8cfd1890734f9394ed1583c14"),
    "_source/about.html": ("fdbecad12749d90b83071c4f4b3db14425ac665c", "bc6864f9fbee8e5caabcfb3db098caaefc0ffa20"),
    "about/index.html": ("53f0230fef94558288629b017f99aa2ebb766f4e", "95df1171cc8a6b5d1dfc71edc3042f4669f00ce2"),
    "_tests/turn14_freshness_history.py": ("cd2b2f1ea999e7d5bddb219975a400b372bdc599", "2777e72a1391691abb37f2d2a20f7655152c048a"),
    "_tests/test_turn14_sitemap_freshness.py": ("9cededd9af00c63c5533cf696f26bf2c9d4eec16", "354f6f55a7eccb4ab1bb3f6924f32fa558c43a94"),
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
    import turn25_identity_evidence_history
    value = turn25_identity_evidence_history.before(path, value)
    # Reviewed later identity claims must be rewound before archived blob checks.
    import turn24_identity_claims_history
    value = turn24_identity_claims_history.before(path, value)
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != known[0]:
        raise ValueError("Turn 15 predecessor blob mismatch: " + name)
    return old if isinstance(value, bytes) else old.decode("utf-8")
