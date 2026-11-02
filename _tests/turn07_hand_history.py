"""Exact predecessor for Turn 7's real-hand and RSS publication.

Older golden release contracts see the complete reviewed parent bytes, only
when the current file is the exact known successor Git blob. Unknown changes
are never hidden. This is test-only and is not imported by runtime builders.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "393ee4c2f8fa01509873f121c4d0b197a42700c0"
BLOBS = {"AGENTS.md":["644cb1a1d693a0e22c318442edd5060709a68910","940f9dbed15d9e9bf5ae2a10dc0a1bf088c07ba3"],"_scripts/build.py":["384f466d218b879faa85854cdeb8c48441e14807","0726754687dc1f5ce0afd0b0be0fed3f9f682b37"],"_scripts/follow.py":["942076434461c45616e73146dffdb243ff271b44","d39965e0289d89fd81ee38d651c9ec8839137c38"],"_scripts/local_release_checks.py":["9afec3b01a2139bd7528501e3053428aabb3d8d0","cf9c56458dcc9c3e94301d116c3d6e626b2262b3"],"_scripts/poker_content.py":["f4a829961aeb9e697d6a44f17f7b8aa9a598c0ce","403cb0eda5df81da62bff8a78be2373c9d90cfbf"],"_source/poker/nolan-kido-profile.html":["de89158b02a477510a7e7bd33088f00314edeada","3423a32edc4fe25377b675c3c0ceefdc096e6ecb"],"_source/poker/portland-meadows-ep1.html":["d2d29d5aa5869ea4cd40d08c9de681fa7620f874","30e3eefc4fafab55837a9a4587f34fd5894a8da4"],"_tests/test_portland_episode.py":["1e46e5f5e7be25d1e19693b38532e4d220363fce","e67a2fb6b0c52f9729d88d2e20064b38d5269882"],"poker/episodes/portland-meadows-ep1/index.html":["f542dde2d95ebd809a270849c36e14df763b942d","015f90eef1dcef84932fa3d68820a7f2ffe5d00b"],"poker/feed.xml":["e8a318ef39692194727f606517a3d6f5a488af0e","5341b56668b141942f5845dd74adfb5fc3d8efe9"],"poker/index.html":["53be72996d3fc24506f15a05369a945f53c57151","5f897691dc169e03eac1147e344aa7f1e13c0082"],"poker/nolan-kido/index.html":["f82ce5f85ac2eb6fceed3ac2141fe5881fda9813","6a8d5c8fa2f15a3f63f71ea812c5c6ed86b18875"],"writing.xml":["51c8647ae9693cf2073b644b9745d7e64afcf2b5","165f969f382fbf57520e30eb50d1264a1c3391f2"]}
ADDED = {"_reports/visibility-sprint/sprint50-turn07-2026-11-02.md":"150163caa59f52cacd237e2bb78446e94fcdf3fe","_scripts/manual_poker_feed.py":"76c02dd9ede41126468efe58fe8cd3a3cfb14ed0","_tests/test_manual_poker_feed.py":"b2f73f929d29eff5dd5694ed88d71dd4f5c23cf5","_tests/test_real_portland_hands.py":"e681a8cffdf0e600944c12431988dadcaeae2f48"}
ROUTES = {"/poker/":"poker/index.html","/poker/nolan-kido/":"poker/nolan-kido/index.html","/poker/episodes/portland-meadows-ep1/":"poker/episodes/portland-meadows-ep1/index.html","/poker/feed.xml":"poker/feed.xml","/writing.xml":"writing.xml"}


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


def before(path, data):
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(data) != pair[1]:
        return data
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != pair[0]:
        raise ValueError("Turn 7 predecessor Git blob mismatch: " + name)
    return old if isinstance(data, bytes) else old.decode("utf-8")


def outputs(records):
    return {path: before(path, data) for path, data in records.items()}


def source_records(records):
    return {path: before(path, data) for path, data in records.items()
            if ADDED.get(key(path)) != blob(data)}


def files(paths):
    def keep(path):
        name = key(path)
        expected = ADDED.get(name)
        return expected is None or not (ROOT / name).is_file() or blob((ROOT / name).read_bytes()) != expected
    return type(paths)(path for path in paths if keep(path))


def live_targets(records):
    restored = {}
    for route, response in records.items():
        name = ROUTES.get(route)
        if (name in BLOBS and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes)
                and blob(response[1]) == BLOBS[name][1]):
            restored[route] = (200, before(name, response[1]))
        else:
            restored[route] = response
    return restored
