"""Test-only exact predecessor for Turn 16's small-business pilot addition.

The adapter rewinds only the six reviewed Git blobs, leaving unknown edits
untouched. It is never imported by the production site generator.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "fd3c1e53f0fcd927ba76b184bce7bff6ebc425d1"
BLOBS = {
    "_source/technology/home.html": ("c73d69826926401ed3df2aacfe1d172cd5242623", "a4e9f1901588a9448ac7bb6da2f55c8ab3d5c0d2"),
    "technology/index.html": ("7a06f32f4b14b085bd3bea53bf6090c78f4b9b4e", "2c06cbe03b7b6524572441159b04440e0b958b07"),
    "_tests/turn13_topic_paths_history.py": ("ac2d5361dc11199eba97f02cb8f74405016fc4d5", "c9f0d01ebf242afb074cf6f42bd6ab83f1d69c2c"),
    "_tests/test_turn13_topic_paths.py": ("e5cd98e83b6ce1e8c55c256219fa99af0c05fa1e", "e1858d2801860a4d59b3ecedb0561da23f2cbb4a"),
    "_tests/test_turn14_sitemap_freshness.py": ("354f6f55a7eccb4ab1bb3f6924f32fa558c43a94", "a59eb5a52754babfc5070b3a554c9ac7c28c17f3"),
    "_tests/test_turn15_evidence_links.py": ("23bbcd57645b0833a426c8046ce71ba78252d11c", "becef5be9eb9119f0b2581124861fa89ce28692c"),
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
    import turn17_site_visibility_evidence_history
    value = turn17_site_visibility_evidence_history.before(path, value)
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != known[0]:
        raise ValueError("Turn 16 predecessor blob mismatch: " + name)
    return old if isinstance(value, bytes) else old.decode("utf-8")
