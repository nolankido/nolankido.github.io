"""Test-only SHA-gated predecessor for Turn 29's notes-to-actions case.

Only complete reviewed Git blobs are rewound to the preceding release.
Unknown source changes remain visible. This is never a production import.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "061324dc666d4a5be9b1c0d63b1f11305cbb96f6"
BLOBS = {
    "_source/pages.json": ("ad05c6093df60ae15a50244f3b33aae8be2e6e35", "7525b635e03ea5e77433af6df66fae859458cdd9"),
    "_source/technology/organize-public-notes.html": ("701cdca4760a33fd5d820c19e1a76a80e3214f2f", "9a3ba6bfa4e6a7aee91cda569d7f3f6870a345b0"),
    "technology/organize-public-notes/index.html": ("bcd3a521da7a5e9ad6f7bc50443cf4f2d43509a6", "011fa33ee262b652ed9deac3948421e9abc693ae"),
    "find/index.html": ("e41a4cd0cbb8f619ba676b03021720fd08c1ec5b", "09ccf0890effc7194ae75b04c7484e812694a338"),
    "sitemap.xml": ("9ca248491a5cca922a12efe93b40f3ac49712199", "df81985f0bab039cddf437c664a390c1d2eaaee9"),
}
ADDED = {"downloads/source-notes-audit.py": "1d330939c47764341dbddad8f6e39280a60b47a7"}

OLD_PAGE = {
    "id": "organize-public-notes",
    "section": "technology",
    "path": "/technology/organize-public-notes/",
    "title": "Using AI to turn source notes into a checked action list.",
    "seo_title": "Organize Notes with AI: Actual Input, Output & Review | Nolan Kido",
    "description": "Follow eight public source notes through an actual AI-generated publication checklist. Inspect the prompt, complete output, source checks, and unresolved items.",
    "kicker": "Technology / Recorded everyday workflow",
    "source": "technology/organize-public-notes.html",
    "date": "2026-10-27",
    "evidence_article": True,
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
    import turn30_evidence_index_history
    value = turn30_evidence_index_history.before(path, value)
    name = key(path)
    expected = BLOBS.get(name)
    if expected is None or blob(value) != expected[1]:
        return value
    previous = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(previous) != expected[0]:
        raise ValueError("Turn 29 predecessor does not match reviewed Git blob: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")


def pages(records):
    import turn30_evidence_index_history
    records = turn30_evidence_index_history.pages(records)
    new = dict(OLD_PAGE, updated="2026-11-04")
    return [dict(OLD_PAGE) if entry == new else entry for entry in records]


def is_added_file(path, value):
    expected = ADDED.get(key(path))
    return expected is not None and blob(value) == expected
