"""Test-only exact-blob predecessor for Turn 19 biography evidence routes.

The public biographies, downloads, identity metadata and existing links remain
unchanged. This adapter reverses only one approved navigation addition in two
files; mutations and unrecognized versions remain visible.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
    "_source/bio.html": (
        "7105fc4e80a61af4478c746aaaf08e58f028504c",
        "91a72e527d32f5529e0b420c56d4b62190ae0bb2",
    ),
    "bio/index.html": (
        "9b8ca21d9f7a8d69ec0546c3a7688972b2a2d60d",
        "013bc794e38a180b3897b4455faa5f53955e323e",
    ),
}
INSERTION = """<h3 id="profile-evidence-routes">Evidence for different introductions</h3>
<p>For an introduction about practical AI, link to <a href="/technology/#site-visibility-evidence">the source-linked website-change case</a> or <a href="/technology/#small-business-ai-pilot">the small-business AI pilot guide</a>. For a tournament, commentary or video-creator introduction, use <a href="/poker/nolan-kido/#creator-introduction">the sourced poker creator introduction</a>, which distinguishes independent finishes from published first-person episodes. These are checkable examples of work, not endorsements, official creator credentials, measured search growth or evidence of poker profit.</p>
"""


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def blob(data):
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, data):
    import turn27_profile_history
    data = turn27_profile_history.before(path, data)
    pair = BLOBS.get(key(path))
    if pair is None or blob(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    current = data.decode("utf-8") if binary else data
    if current.count(INSERTION) != 1:
        raise ValueError("Turn 19 evidence route insertion is missing or ambiguous")
    earlier = current.replace(INSERTION, "", 1)
    result = earlier.encode("utf-8") if binary else earlier
    if blob(result) != pair[0]:
        raise ValueError("Turn 19 predecessor did not match reviewed Git blob")
    return result
