"""Exact test-only predecessor for the Stand Off public Poker hub source review.

Only complete reviewed files rewind to the prior main commit. Unknown edits
remain visible. This file is never imported by production site builders.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "fab6e73fb93552831b39c9011dca813955224124"
BLOBS = {
    "_source/poker/home.html": ("7532ba69db61066c227af9ea63613dc20f2bb8ba", "2593a9a41e364299e4df857d9eccab9a8a212e60"),
    "poker/index.html": ("53b4029d021d54e43fb0e2f78d5d9f104ce018d7", "db8284d6b683cb1a43c811923f1d884067b74b7c"),
    "_source/pages.json": ("6a822d309b8763db55d07716e1d0007e6bb04196", "987b73f530fac98f1d8bf4eec6d8259df6ac3622"),
    "sitemap.xml": ("fd753f9bc50c527dd431d285455a65651aed25c0", "2b54d705371288acb4d0735c992759662ec441b5"),
    "_scripts/check_live.py": ("6ff27052edb9dcf174607e0d07c809952eefcfaf", "3cdf363c51c8187c3969c870bc89b6eae1276024"),
}
ADDED = {
    "downloads/portland-meadows-standoff-ak-source-ledger.json": "051d44f514d49f8a2fc7e5e8db91dc5cbc6f6162",
    "downloads/portland-meadows-standoff-ak-gate.py": "09a664ea154e101f813c2e1d599ada1e8064a45c",
}
OLD_POKER = {
    "id": "poker",
    "path": "/poker/",
    "title": "Learn poker with Nolan Kido.",
    "seo_title": "Learn Poker: Free Beginner Course & Resources | Nolan Kido",
    "description": "Start Poker Foundations, a free Texas Hold’em beginner course. Practice decisions, prepare for live play and explore guides and outside resources.",
    "kicker": "Nolan Kido / Poker",
    "source": "poker/home.html",
    "section": "poker",
    "updated": "2026-11-03",
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
    original = subprocess.check_output(
        ["git", "show", PARENT + ":" + name], cwd=ROOT
    )
    if blob(original) != known[0]:
        raise ValueError("Stand Off predecessor differs from reviewed Git blob: " + name)
    return original if isinstance(value, bytes) else original.decode("utf-8")


def pages(records):
    reviewed = dict(OLD_POKER, updated="2026-11-04")
    return [dict(OLD_POKER) if item == reviewed else item for item in records]


def is_added_file(path, content):
    expected = ADDED.get(key(path))
    return expected is not None and blob(content) == expected
