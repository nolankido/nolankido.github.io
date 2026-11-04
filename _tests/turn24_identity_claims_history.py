"""Test-only SHA-gated predecessor for the November 4 identity evidence review.

Earlier release tests can inspect their exact reviewed predecessor without
accepting arbitrary changed identity claims as old releases. This adapter is
never imported by the site builder and does not run a network request.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "fa03f1b355d4b71291215168a7960fad97ec3ff0"
BLOBS = {
    "_source/person-schema.jsonld": (
        "345b6042218b7b749b41afae8013426c9d77df82",
        "d584469ccb2a9d1efcb8d7bd412e999e74861485",
    ),
    "assets/nolan-kido-identity.jsonld": (
        "973aacf34c599a4c8984ef8734ad3ea466a1b351",
        "79a735a9ddd9da2513a15f559e562e876e87f426",
    ),
    "_tests/test_identity_jsonld.py": (
        "db3e842ff086563f0783ff6416f67a3daae43830",
        "76f0225fc145b0a3ac853d2c190c671689e5c327",
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
        raise ValueError("Identity evidence predecessor mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")
