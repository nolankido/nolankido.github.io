"""Exact, test-only predecessor for Turn 18's poker creator introduction.

Only the complete approved source and generated page can be rewound to their
previous Git blobs. No production builder imports this helper.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
    "_source/poker/nolan-kido-profile.html": (
        "1fb2b07c60905ca2dfd751e65a82c73d4ca4b160",
        "bd756542bdb5748ef067640858626afaa2d2e1cc",
    ),
    "poker/nolan-kido/index.html": (
        "74ee8930260b3fd4f72a30b6be665ab41767ffe2",
        "6e73686f7b8f3705986b929e2e17acf51d5117ac",
    ),
}
INSERTION = """  <section id="creator-introduction" aria-labelledby="creator-introduction-title">
    <h2 id="creator-introduction-title">A source-backed introduction for tournament media.</h2>
    <p>Event organizers, commentators and collaborators may use this short third-person introduction when linking to my poker work. It describes publicly checkable results and self-published media, not an affiliation with or endorsement by WSOP or any tournament operator.</p>
    <blockquote class="creator-introduction-quote">
      <p>Nolan Kido is a live tournament poker player and creator of a first-person tournament vlog. His published results include fifth place in the 2026 South Point Lucky 300, 13th in WSOP Circuit Cherokee 8-Max Pot-Limit Omaha, and 20th in the WSOP Circuit Thunder Valley Monster Stack. His videos explore decisions under tournament pressure, and his Portland Meadows written companion separates narrated hands from later analysis.</p>
    </blockquote>
    <p><strong>Check the record:</strong> <a href="https://pokerdb.thehendonmob.com/event.php?a=r&amp;n=1399113">South Point Lucky 300 result</a>, <a href="https://www.wsop.com/tournaments/result/17989/">WSOP Cherokee PLO result</a>, and <a href="https://www.wsop.com/tournaments/result/18650/">WSOP Thunder Valley result</a>. These are independent event listings; the videos and hand companion are my own accounts. The paragraph is not a complete playing record or evidence of professional status, net profit, a Circuit ring, or official media credentials.</p>
    <p><strong>See the work:</strong> <a href="#player-vlog-title">three published tournament videos</a> and <a href="/poker/episodes/portland-meadows-ep1/">the source-referenced Portland Meadows companion</a>. For interviews, event collaborations, or corrections, <a href="/contact/">contact Nolan Kido</a>. A link does not grant permission to reuse event marks, photos or footage.</p>
  </section>

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
    pair = BLOBS.get(key(path))
    if pair is None or blob(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    content = data.decode("utf-8") if binary else data
    if content.count(INSERTION) != 1:
        raise ValueError("Turn 18 creator section is missing or ambiguous")
    previous = content.replace(INSERTION, "", 1)
    restored = previous.encode("utf-8") if binary else previous
    if blob(restored) != pair[0]:
        raise ValueError("Turn 18 predecessor differs from reviewed Git blob")
    return restored
