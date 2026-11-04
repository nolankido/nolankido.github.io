"""Exact, test-only predecessor for Turn 9's independent AI reply case.

Only complete known Git successor blobs are restored. Unknown edits survive.
This file is not imported by a published build and does not use CI.
"""
from hashlib import sha1
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = "fa6a2f7429df991bcea0ef4f204b6e1ec95238da"
BLOBS = {"AGENTS.md":["426f82683b3701d2a8a7d21b22868eedbfed271d","496df4e12ce69b610d381f1b481e49a01a7c4167"],"_scripts/build.py":["c8626c0f8991fe8a16c15d4f696f7a60911ca7d6","2438cf11a946d581e1fdd4eece2621a64d6b3848"],"_scripts/check_live.py":["e1912d8eed402ead0de7808a46bde28c597d6fa5","613d869a91b47bdd425ce4d90662c71748de5464"],"_scripts/check_search.py":["107d309d0af493dfc521e20f227465d2bf230ec1","cc134efdc4c970c138e50fe273fedf3d4181ba60"],"_scripts/follow.py":["2891e246f5e0a6bb7a8d2272f452bd7d6cee4daf","130aeee01252252747e89c930660d4df47a2cb67"],"_scripts/local_release_checks.py":["61f159666a5ace1bdc415fca6d94baa802075182","5ab712808546a673221230a978eea488d206f155"],"_scripts/player_find.py":["a147aa8be73ba8e69d879277b3fe3d18a71ab482","13131f92e5a9b430f5e544140061aa118d432bd0"],"_source/technology/home.html":["86cf55e46a3b66c7d8a9b4da59af1e3075cb0258","a49075f5865b0877bf18b87909f2bb89b68bb84f"],"_source/technology/local-ai-review-replies.html":["6e2e0c92c10ad3c64192369dd3ae23dcb654c2b9","97f17341eb76e4ff500effdc4ab3c3b53e5a0132"],"_tests/later_release_history.py":["94fb065e07dd2887b31fe90d466d00d03aa2884d","28cb838bf8a468daa55c75d3921af892a6c78bb4"],"_tests/test_later_release_history.py":["6feed9be0394644936553ab850c903297930df30","87c1e22501f7c6131ce6c3535f75ea5ef49c0ab4"],"_tests/test_local_laptop_case.py":["3108287d43e54e315bc921d414605133908e53cf","524f329fc7d33ed9b9a9e08d3daf140286092474"],"_tests/test_player_find.py":["a8192a27641453081dbd82cbf5d57d17c2e0e853","916fe5074d1696c5255801ec0bbe6142672d4923"],"_tests/test_practical_discovery.py":["d6a8dbe65d999fe9c4e78bf4ba6c8e855eb2466b","30734410fc2a119581be16ac94c1cc953e20e7c3"],"_tests/test_reading_return.py":["20354494f4a98f4d25668615042034a0e6c2b059","1ee25871070395be51c815fddb6516e7dc71b796"],"_tests/test_search_sections.py":["3e063188028dec56bcf3ff35f8bdedf5085f0584","d1848792e7fb5bf0aab66b1900e83b230a2e9ad1"],"_tests/test_site.py":["1b6b5db343ba0320d597906b55db2ae92afd348d","dddcc9c778f3e4b4fbcc11f150ec501405fe22a9"],"_tests/test_turn08_laptop_history.py":["24272f558f5fcbab52907b81f316e055853c2373","a8b043671a0154c1a5df435c8848ddc16df79b89"],"_tests/test_visibility_discovery.py":["8cd12a341e5362c5bc7fa2a77928872ab3d12a71","0e54965c610f9b8e693e8f35c39176a536ddb560"],"_tests/test_visibility_sprint_history.py":["850ee91d61450fe6bc53cc1ba9838926c6cf3925","f25559e0be9dfd157b073fddc6d936ab2ae7d5a2"],"find/index.html":["6a7abf0af1b59601440e9d30be221bd95857eefe","04b7061fe0590e5c62319a323cf67474ae22acc5"],"sitemap.xml":["b24d999682724dc58f6129cb4e1cae3fd51b5596","5800da7415889aad4ffe0aa15a71b7e740d94122"],"technology/feed.xml":["de007d935ab548a1f47be7b46df10c3b23a8f3d0","14e130d80d43dd5e02002154249d8d29d8895d32"],"technology/index.html":["3bb1dbce6a86598a060519af0769d856bc019ab6","f1a5dd1ac59325eb10d57a018fd086601516dc35"],"technology/local-ai-review-replies/index.html":["e980f495c4ae5d1c3d827d7ff86409ee34098c87","294f090b78385e1aa28242139b80f9f4bf6b3d70"],"writing.xml":["f5b5a0c1fefdbed80964f8f080e5c3e69da6b4ea","6fddbd20c3c26cb88f3a9f8955bb02bc073afab1"]}
ADDED = {"_reports/visibility-sprint/sprint50-turn09-2026-11-03.md":"5492ff1dea14f9f5b3b786a3e2e28631113b9e1f","_scripts/build_reply_audit_case.py":"1f510a032ae30e98a5e683808d6c03ce3faeef24","_scripts/manual_reply_audit_feed.py":"3a8df0ab53469cd7e20ede23a2d139244056fcc8","_scripts/reply_audit_case.py":"3b68bcab482cb03d333ff963f6dcd19e71df15a6","_source/technology/review-reply-evidence-audit.html":"b0b8b7915c4ca3d65a87ba6f0f6aa06a2181d292","_tests/test_reply_audit_case.py":"281813c52c6c6ba28abc801c5217beb53c22e7dd","_tests/test_turn09_reply_history.py":"3f055eb9688241d793b2098b7c5f5cd362059f3f","downloads/review-reply-independent-audit.py":"e611c8a30f3ff2170590c6a02c6487ad0d58ed3f","technology/review-reply-evidence-audit/index.html":"636e10dfdfab316f2ea5d6fbb3050b12de405956"}
ROUTES = {"/technology/":"technology/index.html","/technology/local-ai-review-replies/":"technology/local-ai-review-replies/index.html","/find/":"find/index.html","/sitemap.xml":"sitemap.xml","/technology/feed.xml":"technology/feed.xml","/writing.xml":"writing.xml"}
NEW_ROUTES = {"/technology/review-reply-evidence-audit/":"technology/review-reply-evidence-audit/index.html","/downloads/review-reply-independent-audit.py":"downloads/review-reply-independent-audit.py"}


def key(path):
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.relative_to(ROOT)
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def blob(value):
    raw = value.encode('utf-8') if isinstance(value, str) else value
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + bytes([0]) + raw).hexdigest()


def before(path, value):
    import turn20_reply_boundaries_history as turn20
    value = turn20.before(path, value)
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    old = subprocess.check_output(['git', 'show', PARENT + ':' + name], cwd=ROOT)
    if blob(old) != pair[0]:
        raise ValueError('Turn 9 predecessor blob disagrees with parent: ' + name)
    return old if isinstance(value, bytes) else old.decode('utf-8')


def outputs(records):
    return {path: before(path, value) for path, value in records.items()}


def source_records(records):
    import turn20_reply_boundaries_history as turn20
    return {path: before(path, value) for path, value in records.items()
            if ADDED.get(key(path)) != blob(turn20.before(path, value))
            and not turn20.is_added_file(path, value)}


def files(paths):
    import turn20_reply_boundaries_history as turn20
    def keep(path):
        name = key(path)
        if not (ROOT / name).is_file():
            return True
        raw = (ROOT / name).read_bytes()
        if turn20.is_added_file(name, raw):
            return False
        digest = ADDED.get(name)
        return digest is None or blob(turn20.before(name, raw)) != digest
    return type(paths)(path for path in paths if keep(path))


def live_targets(records):
    import turn20_reply_boundaries_history as turn20
    result = {}
    for route, response in records.items():
        extra = NEW_ROUTES.get(route)
        if (extra in ADDED and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes)
                and blob(turn20.before(extra, response[1])) == ADDED[extra]):
            continue
        name = ROUTES.get(route)
        if (name in BLOBS and isinstance(response, tuple) and len(response) == 2
                and type(response[0]) is int and response[0] == 200
                and isinstance(response[1], bytes)
                and blob(turn20.before(name, response[1])) == BLOBS[name][1]):
            result[route] = (200, before(name, response[1]))
        else:
            result[route] = response
    return result
