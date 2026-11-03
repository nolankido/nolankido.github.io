"""Test-only exact predecessor for Turn 12's reviewed cross-platform identity links.

Earlier release audits can read previous Git blobs without rewriting any public
page or hiding an unexpected edit. This module is never imported by the build.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "322225c8e7acad3269452a3437384920c6cf9ead"
BLOBS = {
    "_scripts/public_identity.py": ("fcfe54233127eca39ee81b471385afb8ea981d7e", "675b54af370d3015f96516ad89c145627e4d5248"),
    "_source/about.html": ("ed093dfd980b3176bb7024d86986897c0368e41c", "fdbecad12749d90b83071c4f4b3db14425ac665c"),
    "_source/person-schema.jsonld": ("c66d2d4d9c76e6286411f0b1d5162dba4ef4a2a8", "345b6042218b7b749b41afae8013426c9d77df82"),
    "_tests/test_homepage_turn04_history.py": ("8fea28a9e3f480502a76a89255921ef8f76fd67d", "2e04bea697be2ef4f8152ac3a87d9e40561b60a3"),
    "_tests/test_identity.py": ("46232f7d9decb8279705d80c16f95c54b332a368", "ab434fee319c51499cf91d48852a7744da4b1e89"),
    "_tests/test_identity_jsonld.py": ("442617327c5f1d4795f5ca48ff82097b7a7a1c14", "db3e842ff086563f0783ff6416f67a3daae43830"),
    "_tests/test_identity_turn03_history.py": ("a1d885f6a4e6d56f7ec1e22b5a6da23eb487fd91", "95fb3180cc0e8245f753348bee49b96cfec93f10"),
    "_tests/test_later_release_history.py": ("87c1e22501f7c6131ce6c3535f75ea5ef49c0ab4", "c7e8470cd192ec2ffa2dc1018f76e1e06539992e"),
    "_tests/test_profile_turn10.py": ("63acc9dd9df6f581c2de0c4c08df0542b93abefb", "41f3627f4f523a269ab91dfc3b3016c55855460b"),
    "_tests/test_public_profile.py": ("36a4fa22bf8ea6628fc70f8c721ee54257bb3cc9", "5d068e22dbbf96b93bdac4de0f9dc1876f67069f"),
    "_tests/test_search_visibility.py": ("d4c30a1c6cf3fb403ba1738c91f370deaf857c6d", "dfb6dd529f1305dfad9da1a117d97ec28be23fc2"),
    "_tests/test_turn08_laptop_history.py": ("1f111673aeb0c86eae9f4120e3c4a44339653410", "151bc7f5b603350d4498089e7c6b7510ddece612"),
    "_tests/test_turn09_reply_history.py": ("e9004d276756da77bb18a359d38518fc0ce02f7c", "8d4be370cca1c3c0ed0ebf0f6d17ae7326a28c99"),
    "_tests/test_turn11_video_discovery_history.py": ("885d4ab75834de6721daebea39a87780b92aa9aa", "9ec4af1164bdb80cc9cc258d5d11c6d5fcc36763"),
    "_tests/test_visibility_discovery.py": ("0e54965c610f9b8e693e8f35c39176a536ddb560", "361c56a0d2c2f4f4915a51c94f9e53a5eadfeb16"),
    "_tests/test_visibility_sprint_history.py": ("d0b4532e6cf76a7b4b1477bd52094b28d520c280", "e6ba18ee752b970696d90af31d29757774f26eed"),
    "about/index.html": ("b1ac15e35dfac43726cca2fd4ffc467b9813882d", "53f0230fef94558288629b017f99aa2ebb766f4e"),
    "assets/nolan-kido-identity.jsonld": ("14f37a37e3d83cfe52f76ba232919bc424da1f0f", "973aacf34c599a4c8984ef8734ad3ea466a1b351"),
    "index.html": ("f44422be7b1dcff55452ad0b62f324656667f826", "39cbd710f7949c68ba99750132fa47cfd7599ee4"),
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
    import turn13_topic_paths_history
    value = turn13_topic_paths_history.before(path, value)
    name = key(path)
    known = BLOBS.get(name)
    if known is None or blob(value) != known[1]:
        return value
    previous = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(previous) != known[0]:
        raise ValueError("Turn 12 predecessor blob mismatch: " + name)
    return previous if isinstance(value, bytes) else previous.decode("utf-8")
