"""Exact test-only predecessor for Turn 25's public AI identity evidence case.

Older release comparisons should observe their own reviewed byte snapshots.
Only exact complete Git blobs can be rewound. Unexpected mutations stay visible.
This helper never participates in production site generation.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "a1e2f1c64e185c3d97fc813f47c75968cc769ab9"
BLOBS = {
    "_source/technology/home.html": ("31a8cc92fd8d2d7cb60b02cea76dbe6e3402c93e", "931663ca325e016f9639faf64e8d1b663c702f05"),
    "technology/index.html": ("745dc2c01581a0a69a1de483a45453bd72738855", "9e8f4fb3e79ca67779971aaddc401494624f2108"),
    "_source/about.html": ("c1643c333646178066f5c3a9c60ffcf5aef76d3c", "bee040701cff5bbdbcba6490a4fde7b29590a6a4"),
    "about/index.html": ("15514244822c975e28e0b0a3db0158babb5ba58a", "45c6577c02dcc24249f46ea3712239218ced9200"),
    "_source/home.html": ("a3822944a1ba0f31938209e13ffec207fb14d0f5", "e08286a2d33a7e9be70d9e8e71d1baf17d934e1e"),
    "index.html": ("789e4a3d06d714f8cfd1890734f9394ed1583c14", "63161055098ddbd7fe6727c37c2ec26becec2e6f"),
    "find/index.html": ("ab3e72025301cd42771eff160a09d96fdd19894f", "d21045cc1559c9958f446d5df50cf5b4d7ccdd0a"),
}
ADDED = {
    "downloads/identity-evidence-gate.py": "fc79c43d211a74d631e13440c5a69d40516ed89a",
    "downloads/identity-evidence-case-workbook.md": "dd741df19073f191190ab347d66220f9f3dbb4f6",
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
        raise ValueError("Turn 25 predecessor Git blob mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")


def is_added_file(path, value):
    known = ADDED.get(key(path))
    return known is not None and blob(value) == known
