"""SHA-gated predecessor for Turn 27 public profile link and biography kit.

The site builder never imports this file. Only reviewed complete files are
rewound, and profile metadata is changed only when the full previous record
matches except for the reviewed revision date. Unknown edits remain visible.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "f2ce3bd71474bc0cec1ad39cf6feb7feb357ce43"
BLOBS = {
    "_source/bio.html": ("91a72e527d32f5529e0b420c56d4b62190ae0bb2", "4d9ce4e10fab24c496aa3f3bfa63a02008722993"),
    "bio/index.html": ("013bc794e38a180b3897b4455faa5f53955e323e", "2a4a202cfdcdace5e433f248935560b604553335"),
    "_source/pages.json": ("afac135c04fcf70f0fed662390c9edf97a243e96", "ad05c6093df60ae15a50244f3b33aae8be2e6e35"),
    "sitemap.xml": ("9fbbbb1b685172924c41dee36f7b767cc519964c", "9ca248491a5cca922a12efe93b40f3ac49712199"),
}
ADDED = {"downloads/nolan-kido-public-profile-kit.md": "8a16fe3707025dbfafa02a9f03d4d9108b65054f"}

OLD_BIO = {
    "id": "bio", "path": "/bio/", "title": "A brief introduction.",
    "seo_title": "Nolan Kido | Short Biography & Public Introductions",
    "description": "Copy Nolan Kido's public biography and find his practical AI projects, tools, and writing for introductions, profiles, and links.",
    "kicker": "Biography", "source": "bio.html", "updated": "2026-10-28",
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
    pair = BLOBS.get(key(path))
    if pair is None or blob(value) != pair[1]:
        return value
    old = subprocess.check_output(
        ["git", "show", PARENT + ":" + key(path)], cwd=ROOT
    )
    if blob(old) != pair[0]:
        raise ValueError("Turn 27 predecessor blob mismatch: " + key(path))
    return old if isinstance(value, bytes) else old.decode("utf-8")


def pages(records):
    """Rewind only the complete recognized bio manifest record."""
    new = dict(OLD_BIO, updated="2026-11-04")
    return [dict(OLD_BIO) if item == new else item for item in records]


def is_added_file(path, value):
    expected = ADDED.get(key(path))
    return expected is not None and blob(value) == expected
