"""Test-only exact predecessor for the November 4 evidence-by-type index.

Only approved complete Git blobs rewind to the release parent. Unrecognized
mutations remain visible. No production build or browser uses this module.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "c259d366176f3411e89777646135262178cc75b3"

BLOBS = {
    "_source/start-here.html": (
        "293004244792dcf4381b21ea63e2ad559450873f",
        "7417842f3cfc09bfb3db2090e7f1c4897389cfe2",
    ),
    "start-here/index.html": (
        "864d6ea22ad65103fa3f0e8939d6a834f040d62c",
        "47752789967819363e6ce126dccdad29f87e8220",
    ),
    "_source/about.html": (
        "bee040701cff5bbdbcba6490a4fde7b29590a6a4",
        "72524ae1e62bc09a762802d44b69f38f7bd075bc",
    ),
    "about/index.html": (
        "45c6577c02dcc24249f46ea3712239218ced9200",
        "445aeb89c0935e26604e41ca0ccbaafa6bbd6bc2",
    ),
    "_source/pages.json": (
        "7525b635e03ea5e77433af6df66fae859458cdd9",
        "6a822d309b8763db55d07716e1d0007e6bb04196",
    ),
    "sitemap.xml": (
        "df81985f0bab039cddf437c664a390c1d2eaaee9",
        "bb320426197a0eb12710a6ce712e7fd64e3b17be",
    ),
}

OLD_PAGE = {
    "id": "start-here",
    "path": "/start-here/",
    "title": "A few good places to begin.",
    "seo_title": "Start Here | Nolan Kido",
    "description": "Choose a useful task or explore Nolan Kido's AI projects: customer replies, book continuity, and a cooking planner. Follow interests in life, poker, and creativity.",
    "kicker": "New here?",
    "source": "start-here.html",
    "updated": "2026-10-28",
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
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    previous = subprocess.check_output(
        ["git", "show", PARENT + ":" + name], cwd=ROOT
    )
    if blob(previous) != pair[0]:
        raise ValueError("Turn 30 predecessor Git blob mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")


def pages(records):
    new = dict(OLD_PAGE, updated="2026-11-04")
    return [dict(OLD_PAGE) if page == new else page for page in records]
