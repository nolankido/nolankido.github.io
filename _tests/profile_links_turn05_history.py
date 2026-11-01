"""Review-only history bridge for direct links to the new player page.

Reconstructs only four exact predecessor files. Unknown edits pass through.
This module is never loaded by the production builder.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GIT_BLOBS = {
    "_source/poker/home.html": (
        "e31c8e1d0b974cc0f8069161e03bef1b2487bbdd",
        "b9d9fb02e079a2a233942f75873515ea1f7f4240",
    ),
    "poker/index.html": (
        "e69b9cb0fb7a2a425fab7a783153fe848311f067",
        "1038528eecb508cc212320798b1d892f5b621323",
    ),
    "_source/about.html": (
        "e602e542a43d82e8f7c43a84f514e809f2bedc19",
        "ed093dfd980b3176bb7024d86986897c0368e41c",
    ),
    "about/index.html": (
        "29754e4fffc090d1bb6d0c3d6cd2255d028cfa49",
        "b1ac15e35dfac43726cca2fd4ffc467b9813882d",
    ),
}
POKER_ADD = '<p class="poker-player-profile-link"><a href="/poker/nolan-kido/">Read Nolan Kido’s tournament player profile and verified results</a>.</p>'
ABOUT_ADD = ' <a href="/poker/nolan-kido/">My tournament player profile</a> links to independently recorded event results.'


def key(path):
    path = Path(path)
    if path.is_absolute():
        try:
            path = path.relative_to(ROOT)
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def digest(data):
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, data):
    name = key(path)
    pair = GIT_BLOBS.get(name)
    if pair is None or digest(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    current = data.decode("utf-8") if binary else data
    removed = POKER_ADD if name in ("_source/poker/home.html", "poker/index.html") else ABOUT_ADD
    if current.count(removed) != 1:
        raise ValueError("Reviewed player-profile link is missing or ambiguous")
    prior = current.replace(removed, "", 1)
    previous = prior.encode("utf-8") if binary else prior
    if digest(previous) != pair[0]:
        raise ValueError("Player-profile link predecessor bytes are not verified")
    return previous
