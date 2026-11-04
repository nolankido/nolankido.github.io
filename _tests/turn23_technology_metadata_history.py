"""SHA-gated historical predecessor for Turn 23 Technology metadata freshness.

Only exact reviewed Git blobs rewind. This test fixture is never imported by
production site generation and cannot erase arbitrary future modifications.
"""
from hashlib import sha1
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PARENT = "7ee90e508112f98bfa66c8c55d2bba3d2dc0ccea"
BLOBS = {
    "_source/pages.json": ("52cccc0d0cbf9ade65d30eabb86f731801cf1e51", "832d0448dd232f6e976e86e8f291394754e49041"),
    "_scripts/practical_path.py": ("8f5af9746bc72283fe9ab9e988e5cce2cb26cff9", "f181b45417921a53b3d7976f3edf8694a02ee539"),
    "technology/index.html": ("b2c87d335e4c42e7867d3a7ee6e366c43074feac", "745dc2c01581a0a69a1de483a45453bd72738855"),
    "find/index.html": ("d957465ba160e52e7f8cc71c25d56ffe19bc56fd", "12b46d5afd317c8f436a2f3b820bc41262c65ab3"),
    "sitemap.xml": ("bb24de85096ad3be6a77f05bced00b902878dc6c", "d4ec3ff2d90a65013f3b59d404d8ee3172ebf87c"),
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
    import turn27_profile_history
    value = turn27_profile_history.before(path, value)
    import turn25_identity_evidence_history
    value = turn25_identity_evidence_history.before(path, value)
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    original = subprocess.check_output(
        ["git", "show", PARENT + ":" + name], cwd=ROOT
    )
    if blob(original) != pair[0]:
        raise ValueError("Turn 23 historical predecessor mismatch: " + name)
    return original if isinstance(value, bytes) else original.decode("utf-8")
