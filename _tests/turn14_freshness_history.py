"""Exact test-only predecessor for Turn 14's reviewed content-freshness dates.

Only exact, independently SHA-verified Git blobs are replaced with their
committed predecessors. Unreviewed content passes through unchanged.
Production site generation does not import this module.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "5a8eb457039a7df67826cf043496da3668708e22"
BLOBS = {
    "_source/pages.json": ("8d2a81882cda2aaea56eb11f352dd1f3a98f9902", "52cccc0d0cbf9ade65d30eabb86f731801cf1e51"),
    "sitemap.xml": ("cca296ebc158d73267ea5d0e1d6ae71202ebd38f", "bb24de85096ad3be6a77f05bced00b902878dc6c"),
    "index.html": ("39cbd710f7949c68ba99750132fa47cfd7599ee4", "416d9f7c95bb0996aca42f2eb344ccf445af93b1"),
    "technology/index.html": ("b719460f51fc9da72510c907afa03c462f2eedae", "7a06f32f4b14b085bd3bea53bf6090c78f4b9b4e"),
    "poker/index.html": ("d1c37e562fae1466e4300b6dce5f667406c1924e", "53b4029d021d54e43fb0e2f78d5d9f104ce018d7"),
    "_tests/turn13_topic_paths_history.py": ("ebb54509ba3fab8b4ae27de6b27f19a1bbcdd977", "ac2d5361dc11199eba97f02cb8f74405016fc4d5"),
    "_tests/test_turn12_cross_platform_history.py": ("b1f8993de69d11e9e8b5d42aad461cbcc1ce36bb", "31fb83ccbd440664c093580c93422d92bd1f78bb"),
    "_tests/test_turn13_topic_paths.py": ("b044b1b2b1b80a96b15f7f640273902fd4409e2c", "e5cd98e83b6ce1e8c55c256219fa99af0c05fa1e"),
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
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    original = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(original) != known[0]:
        raise ValueError("Turn 14 Git predecessor blob mismatch: " + name)
    return original if isinstance(value, bytes) else original.decode("utf-8")
