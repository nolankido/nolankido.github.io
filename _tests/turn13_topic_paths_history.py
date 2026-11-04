"""Test-only exact predecessor for Turn 13's AI, technology, and poker paths.

Only known, complete published Git blobs are restored for earlier release tests.
Unknown mutations remain untouched. Production page building never imports this.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "b5d6c23f8850364d39cb28ff982e11fde2895228"
BLOBS = {
    "_source/technology/home.html": ("a49075f5865b0877bf18b87909f2bb89b68bb84f", "c73d69826926401ed3df2aacfe1d172cd5242623"),
    "technology/index.html": ("f1a5dd1ac59325eb10d57a018fd086601516dc35", "b719460f51fc9da72510c907afa03c462f2eedae"),
    "_source/poker/home.html": ("5d17ff9b40965af8c5fad66892e93f810a8b4a11", "7532ba69db61066c227af9ea63613dc20f2bb8ba"),
    "poker/index.html": ("12b805f7ac07749b36f727d0e69f9cb72398edb9", "d1c37e562fae1466e4300b6dce5f667406c1924e"),
    "_tests/turn11_video_discovery_history.py": ("29e89c77117c613fee9cc6d0f72f18e2802490cf", "ad1ef4e5e26444e6969cecaff53fbe8d3ab62465"),
    "_tests/turn12_cross_platform_history.py": ("cc8f411b72ea58bc5e6a91b3637a6f02560fd0e6", "664062bc3fc431452d8a34b228cf50b45581771d"),
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
    import turn16_small_business_pilot_history
    value = turn16_small_business_pilot_history.before(path, value)
    import turn14_freshness_history
    value = turn14_freshness_history.before(path, value)
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    previous = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(previous) != known[0]:
        raise ValueError("Turn 13 predecessor blob mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")
