"""Exact test-only predecessor for Turn 11's public poker-video discovery.

Historical release tests may inspect the previous reviewed Git blobs. Only
complete, known Turn 11 files are restored; unknown mutations pass unchanged.
No production builder imports this module and no workflow is added.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "778b76c814a33ee251a44b0bbccb18deb9710acf"
BLOBS = {
    "AGENTS.md": ("496df4e12ce69b610d381f1b481e49a01a7c4167", "3281683a6a0b041cf1fe208a18f132f94cb292e0"),
    "_scripts/build_player_profile.py": ("e4fa0a52b608d7992b98477908973d33d1390975", "dbb0c60cca17957ff19f215a0f59b61c2b36da55"),
    "_scripts/player_sitemap.py": ("dd6d2a7d5efcb527b88bc18f4a1c7b469908f391", "29153dbd9b23090e5db7881380a81540f084fe1a"),
    "_scripts/poker_content.py": ("403cb0eda5df81da62bff8a78be2373c9d90cfbf", "b83f71028ec6aa8aff3070613c12ba8ddc19d54b"),
    "_source/poker/home.html": ("64f77d55e738c32281ed4cb6937a1d71f9452a12", "5d17ff9b40965af8c5fad66892e93f810a8b4a11"),
    "_source/poker/nolan-kido-profile.html": ("3423a32edc4fe25377b675c3c0ceefdc096e6ecb", "1fb2b07c60905ca2dfd751e65a82c73d4ca4b160"),
    "_tests/test_episode_turn06_history.py": ("ff06b5467762702452005fae83fc318d3f279154", "04a447e4d30f4ef82a127575398cabd94b55b5cf"),
    "_tests/test_player_find_turn_history.py": ("5e34518a7b947fcbda770feb039657ec653cc669", "7020b820803891100df371327d6be44821642d04"),
    "_tests/test_player_sitemap.py": ("55f7f61b55b5307c6976db82cf3364b0a6d32d46", "9c499f1bd8ae0856ec202c06c044896b7652b234"),
    "_tests/test_profile_links_turn05_history.py": ("f1464209d3d58843ea514c13dfd70d9a3f18c883", "4e9bc66a28b4f7d1eb8732f23e5d16bb8d69d97f"),
    "_tests/test_profile_sitemap_turn_history.py": ("05fd32b014b1ff6a09ff957bc93362c10655b91b", "a33cd9b3a2624e6c95af10445bab8c9dfdf4fd94"),
    "_tests/test_turn07_hand_history.py": ("db5a40cdead3b11aa84c514bec98afab69905924", "1ca50910e74a8c7c80ad438497d631155ce8dd66"),
    "_tests/test_turn08_laptop_history.py": ("a8b043671a0154c1a5df435c8848ddc16df79b89", "1f111673aeb0c86eae9f4120e3c4a44339653410"),
    "_tests/test_turn09_reply_history.py": ("3f055eb9688241d793b2098b7c5f5cd362059f3f", "e9004d276756da77bb18a359d38518fc0ce02f7c"),
    "_tests/test_visibility_poker_player.py": ("7ba36c6a5b91c5006cf243f0e4cf1c77624acb91", "820416f15f7e931c36913169130646b7799ab8fa"),
    "_tests/test_visibility_poker_player_history.py": ("8d660edbabb7c11618685f75c7828568329d0734", "489a187930cd6c8c15841c90e89ec64b55b50053"),
    "_tests/test_visibility_poker_player_page.py": ("cda5f75d971a6a3fef492b638778f4befaa4845f", "af13de5234924b1b9597f2c597058495ec4e5818"),
    "_tests/test_visibility_sprint_history.py": ("f25559e0be9dfd157b073fddc6d936ab2ae7d5a2", "d0b4532e6cf76a7b4b1477bd52094b28d520c280"),
    "find/index.html": ("04b7061fe0590e5c62319a323cf67474ae22acc5", "d957465ba160e52e7f8cc71c25d56ffe19bc56fd"),
    "poker/index.html": ("5f897691dc169e03eac1147e344aa7f1e13c0082", "12b805f7ac07749b36f727d0e69f9cb72398edb9"),
    "poker/nolan-kido/index.html": ("6a8d5c8fa2f15a3f63f71ea812c5c6ed86b18875", "74ee8930260b3fd4f72a30b6be665ab41767ffe2"),
    "sitemap.xml": ("5800da7415889aad4ffe0aa15a71b7e740d94122", "cca296ebc158d73267ea5d0e1d6ae71202ebd38f"),
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
    import turn32_standoff_source_history
    value = turn32_standoff_source_history.before(path, value)
    import turn31_episode_ledger_history
    value = turn31_episode_ledger_history.before(path, value)
    import turn18_poker_creator_history
    value = turn18_poker_creator_history.before(path, value)
    import turn13_topic_paths_history
    value = turn13_topic_paths_history.before(path, value)
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != known[0]:
        raise ValueError("Turn 11 Git predecessor blob mismatch: " + name)
    return old if isinstance(value, bytes) else old.decode("utf-8")
