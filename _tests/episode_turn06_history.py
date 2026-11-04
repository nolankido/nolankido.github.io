"""Exact, reviewed predecessor for the public Portland Meadows Episode 1 release.

Only a complete known successor Git blob can be reconstructed, using the local
Git parent commit. Unknown mutations pass through unchanged. No production
module imports this test-only adapter. The parent commit must be available in
the local checkout, as required by the site's existing release history checks.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "2184d1c3c15be1b3d8c12190fdca22c6f77650e5"
BLOBS = {"AGENTS.md":["746fdf4ae5ac07c031a2c8a209a90751f2dccc4a","644cb1a1d693a0e22c318442edd5060709a68910"],"_scripts/check_live.py":["5743bb6064180a814fe97044e54ec948ea40cd47","2d96fb2f47c26cc4176910c395d571b9ce572ca5"],"_scripts/check_search.py":["f458778af008272cddc49c6f830375e980de9df7","61d71d20cef8a3554191700dfc0fa18a98621c2a"],"_scripts/local_release_checks.py":["f26de68056421d1fcf41917951ecb7685bd8b48c","9afec3b01a2139bd7528501e3053428aabb3d8d0"],"_scripts/player_find.py":["88b63dbd7a0738e14804c97ac82b87343bd6a871","8bcc8df026f6548f7df3ab09b83d2a6b5277e776"],"_scripts/player_sitemap.py":["10595fe6c8908499876402a591daf53234e847dc","dd6d2a7d5efcb527b88bc18f4a1c7b469908f391"],"_scripts/poker_content.py":["9312ca8bc4db7c23a04b5b91650c33a0e4a90802","f4a829961aeb9e697d6a44f17f7b8aa9a598c0ce"],"_scripts/site_find.py":["4386c79895d3368c84e903dc676c87bd401adfd2","e101a339102b99e5c9ec177298ce91df7be047be"],"_source/find.html":["dc0ecbf8b326125ded9643299e186080a0088a56","4c7d1f0e0cfe5a90382b719e57ed1c4ca41ee0c5"],"_source/poker/home.html":["b9d9fb02e079a2a233942f75873515ea1f7f4240","64f77d55e738c32281ed4cb6937a1d71f9452a12"],"_source/poker/nolan-kido-profile.html":["1c366974c1de2a548cbca871e0b2e7b2f7376ea3","de89158b02a477510a7e7bd33088f00314edeada"],"_tests/test_player_find.py":["cba1ab872af3bc6955719e4422be81169f4bfe3c","bfdf47d90f49083d7ae9a6aba103dee41e549c62"],"_tests/test_player_sitemap.py":["2f92405261b0651f47dd14ffbaee41d97e9b00d4","926fc0e6d9ccefe273123ee65c29aa51d5f2c7c1"],"_tests/test_poker_content.py":["83be3afab6ab05db84483fffeaf1ddd80d7a7bb4","17285af36fc3b072bc5e133f3aa7086bd5dfcb8c"],"_tests/test_site.py":["ca1c7f7aca64b4ed30231aca09a94cb2772d5af1","84f96abb5aeb5713a49c480fb80d98e49eb6ceca"],"_tests/test_visibility_poker_player.py":["e4e68c892bb8bf8ff4998efdc058991b4ab2d057","7ba36c6a5b91c5006cf243f0e4cf1c77624acb91"],"_tests/test_visibility_poker_player_page.py":["2a0643735ecc896977447b470c9d7693490ff953","cda5f75d971a6a3fef492b638778f4befaa4845f"],"find/index.html":["9dff44288065aa209061af8b80cc1c3a451224b5","a4e15b712a1a4a81d8b514a86f91183304d34bf0"],"poker/index.html":["1038528eecb508cc212320798b1d892f5b621323","53be72996d3fc24506f15a05369a945f53c57151"],"poker/nolan-kido/index.html":["fb56af5af00bd8f27ab4f98296586eddeb97043f","f82ce5f85ac2eb6fceed3ac2141fe5881fda9813"],"sitemap.xml":["a9b30b5c1b60379b68cad7ba8b90a1ca2b26af5a","71b6b19b505b9e0118dd2e43c6147e73180fd2e3"]}
ADDED = {"_scripts/build_poker_episode.py":"d898e7611357c191117a45a810490e2d67322d77","_scripts/poker_episode.py":"89a4de4ae9c6b8c6eb5fed68958df41e1ea09246","_source/poker/portland-meadows-ep1.html":"d2d29d5aa5869ea4cd40d08c9de681fa7620f874","_tests/test_portland_episode.py":"1e46e5f5e7be25d1e19693b38532e4d220363fce","poker/episodes/portland-meadows-ep1/index.html":"f542dde2d95ebd809a270849c36e14df763b942d"}
EPISODE_ROUTE = "/poker/episodes/portland-meadows-ep1/"


def key(path):
    target = Path(path)
    if target.is_absolute():
        try:
            target = target.relative_to(ROOT)
        except ValueError:
            return target.as_posix()
    return target.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, value):
    import turn31_episode_ledger_history
    value = turn31_episode_ledger_history.before(path, value)
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = subprocess.check_output(["git", "show", PARENT + ":" + name], cwd=ROOT)
    if blob(old) != pair[0]:
        raise ValueError("Public Episode 1 historical predecessor blob mismatch: " + name)
    return old if isinstance(value, bytes) else old.decode("utf-8")


def source_records(records):
    return {path: value for path, value in records.items()
            if ADDED.get(key(path)) != blob(value)}


def files(paths):
    def keep(path):
        name = key(path)
        hash_value = ADDED.get(name)
        return hash_value is None or not (ROOT / name).is_file() or blob((ROOT / name).read_bytes()) != hash_value
    return type(paths)(path for path in paths if keep(path))


def live_targets(records):
    def keep(route, response):
        return not (route == EPISODE_ROUTE and isinstance(response, tuple)
                    and len(response) == 2 and type(response[0]) is int and response[0] == 200
                    and isinstance(response[1], bytes)
                    and blob(response[1]) == ADDED["poker/episodes/portland-meadows-ep1/index.html"])
    return {route: response for route, response in records.items() if keep(route, response)}
