"""Exact parent snapshot for a public, source-reviewed local AI laptop release.

Restore only complete known Git-blob successors to the previous release. No
historical baseline fixture is modified, and unknown bytes pass through. This
test-only adapter is never imported by production code or deployed as CI.
"""
from __future__ import annotations
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "546dde1820e042039db4e22baf2cbd389f944714"
BLOBS = {"AGENTS.md":["940f9dbed15d9e9bf5ae2a10dc0a1bf088c07ba3","426f82683b3701d2a8a7d21b22868eedbfed271d"],"_scripts/build.py":["0726754687dc1f5ce0afd0b0be0fed3f9f682b37","c8626c0f8991fe8a16c15d4f696f7a60911ca7d6"],"_scripts/check_live.py":["2d96fb2f47c26cc4176910c395d571b9ce572ca5","e1912d8eed402ead0de7808a46bde28c597d6fa5"],"_scripts/check_search.py":["61d71d20cef8a3554191700dfc0fa18a98621c2a","107d309d0af493dfc521e20f227465d2bf230ec1"],"_scripts/follow.py":["d39965e0289d89fd81ee38d651c9ec8839137c38","2891e246f5e0a6bb7a8d2272f452bd7d6cee4daf"],"_scripts/local_release_checks.py":["cf9c56458dcc9c3e94301d116c3d6e626b2262b3","61f159666a5ace1bdc415fca6d94baa802075182"],"_scripts/player_find.py":["8bcc8df026f6548f7df3ab09b83d2a6b5277e776","a147aa8be73ba8e69d879277b3fe3d18a71ab482"],"_source/technology/home.html":["fe3cacd26f5f293c32f631d5620e63f90821e3e9","86cf55e46a3b66c7d8a9b4da59af1e3075cb0258"],"_source/technology/local-ai-test-record.html":["361ad5c14479b4752104b31cc7c4842321e3877f","dd3aeb43437417fa2d40319189201193834a096a"],"_tests/test_player_find.py":["bfdf47d90f49083d7ae9a6aba103dee41e549c62","58fc2a86a99f0fae897a660ffe81ed730c2121c9"],"_tests/test_player_sitemap.py":["926fc0e6d9ccefe273123ee65c29aa51d5f2c7c1","26d559c0c684d70897bc67265e931755e7699fec"],"_tests/test_practical_discovery.py":["c89cb20a2c34fb60059d0b78542f5884cf5b5004","0170dcead2cb49f0e9fd51358a8242fc84557e01"],"_tests/test_reading_return.py":["8308e09987c8c989d79ddba8b7e96c7f45037e09","79ecfc04a8dc950dcc334663234020b27755b12b"],"_tests/test_site.py":["84f96abb5aeb5713a49c480fb80d98e49eb6ceca","1b6b5db343ba0320d597906b55db2ae92afd348d"],"find/index.html":["a4e15b712a1a4a81d8b514a86f91183304d34bf0","6a7abf0af1b59601440e9d30be221bd95857eefe"],"sitemap.xml":["71b6b19b505b9e0118dd2e43c6147e73180fd2e3","b24d999682724dc58f6129cb4e1cae3fd51b5596"],"technology/feed.xml":["bce113d030fc19f3be68ea3af0c337d03e74b846","de007d935ab548a1f47be7b46df10c3b23a8f3d0"],"technology/index.html":["8ae2ba282471fbeef4cf22d67f56ab60584766d0","3bb1dbce6a86598a060519af0769d856bc019ab6"],"technology/local-ai-test-record/index.html":["03843881f11a51d5fce7c30c225953756b35f5a6","2e53eb160f56b2dcd7c682c8408b35dbec9a02ad"],"writing.xml":["165f969f382fbf57520e30eb50d1264a1c3391f2","f5b5a0c1fefdbed80964f8f080e5c3e69da6b4ea"]}
ADDED = {"_reports/visibility-sprint/sprint50-turn08-local-ai-laptop-2026-11-02.md":"36a5cc0a34ea37e1bfe7b020e3d7f9a615e7bee4","_scripts/build_local_laptop_case.py":"e8902ca643c092e7d02fdc14a6d022e57a4db918","_scripts/local_laptop_case.py":"81dee9c6fe316a7ebe3430c6356eb8d47d6039ba","_scripts/manual_local_ai_feed.py":"c1050f0b8b3bd71f1274882e3eaa9ded61160a00","_source/technology/local-ai-gaming-laptop.html":"abce47db5c682cc0f6e78c7d34183c7429570613","_tests/test_local_laptop_case.py":"3108287d43e54e315bc921d414605133908e53cf","downloads/local-ai-loopback-check.py":"2d99ca3b5bdaf22278069ee78d833e0fdfc13b29","technology/local-ai-gaming-laptop/index.html":"7c21d5bb63075f98cae1422e3b6ed498a91b08ee"}
ROUTES = {"/technology/":"technology/index.html","/technology/local-ai-test-record/":"technology/local-ai-test-record/index.html","/find/":"find/index.html","/sitemap.xml":"sitemap.xml","/technology/feed.xml":"technology/feed.xml","/writing.xml":"writing.xml"}
ADDED_ROUTES = {"/technology/local-ai-gaming-laptop/":"technology/local-ai-gaming-laptop/index.html","/downloads/local-ai-loopback-check.py":"downloads/local-ai-loopback-check.py"}


def key(path):
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.relative_to(ROOT)
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, content):
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(content) != pair[1]:
        return content
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != pair[0]:
        raise ValueError("Turn 8 predecessor digest mismatch: " + name)
    return old if isinstance(content, bytes) else old.decode("utf-8")


def outputs(records):
    return {path: before(path, content) for path, content in records.items()}


def source_records(records):
    return {path: before(path, content) for path, content in records.items()
            if ADDED.get(key(path)) != blob(content)}


def files(paths):
    def keep(path):
        name = key(path)
        digest = ADDED.get(name)
        return digest is None or not (ROOT / name).is_file() or blob((ROOT / name).read_bytes()) != digest
    return type(paths)(path for path in paths if keep(path))


def live_targets(records):
    result = {}
    for route, response in records.items():
        new_name = ADDED_ROUTES.get(route)
        if (new_name in ADDED and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes)
                and blob(response[1]) == ADDED[new_name]):
            continue
        name = ROUTES.get(route)
        if (name in BLOBS and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes)
                and blob(response[1]) == BLOBS[name][1]):
            result[route] = (200, before(name, response[1]))
        else:
            result[route] = response
    return result
