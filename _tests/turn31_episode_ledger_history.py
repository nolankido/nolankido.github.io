"""Test-only exact predecessor for Turn 31's public Episode 1 ledger.

Only complete approved Git blobs can be restored to the preceding main commit.
Unknown mutations survive; this module is not used by production publishing.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "0906e6ae2d51b062dd6d3bf34b86d6be6e432657"

BLOBS = {
    "_source/poker/portland-meadows-ep1.html": ("9d122384ab5c38768f2ed15102caa1b8062136c1", "c8280f318cb7423b762cfa311f74c4e4e81a0a0d"),
    "poker/episodes/portland-meadows-ep1/index.html": ("11eefdbac2cabcb3729d2b6d245680aae5296e52", "ab85a76f93593a3d3acb567e04e7d833bb9a14d7"),
    "_scripts/build_poker_episode.py": ("d898e7611357c191117a45a810490e2d67322d77", "223c0635575767e1d8202caf29550bf8f16402c6"),
    "_scripts/poker_episode.py": ("806131b58d220322418ed88fca7e29e4dba7a7cb", "5b0f6152d53dd6a5faebbc36dacdf3c3e3607b85"),
    "_scripts/player_sitemap.py": ("29153dbd9b23090e5db7881380a81540f084fe1a", "049f83c73d774b4ad92ea58c946c82cb04fc0d13"),
    "_scripts/check_live.py": ("613d869a91b47bdd425ce4d90662c71748de5464", "6ff27052edb9dcf174607e0d07c809952eefcfaf"),
    "sitemap.xml": ("bb320426197a0eb12710a6ce712e7fd64e3b17be", "fd753f9bc50c527dd431d285455a65651aed25c0"),
}

ADDED = {
    "downloads/portland-meadows-ep1-scene-claims.json": "2adb839060706506493d1f454055dd5c8536f2bd",
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
    previous = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(previous) != pair[0]:
        raise ValueError("Turn 31 predecessor is not the reviewed Git blob: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")


def is_added_file(path, value):
    expected = ADDED.get(key(path))
    return expected is not None and blob(value) == expected
