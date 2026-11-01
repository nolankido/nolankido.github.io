"""Test-only, exact-blob predecessor for the Turn 5 Poker player evidence.

No production builder imports this adapter. Older immutable release tests see the
original source and generated page only when an exact reviewed successor matches.
Changed or unexpected bytes pass through so unrelated changes remain detectable.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
    "_source/poker/home.html": ("efa567b9ad69ebf4e9dc8e25fa59d7dec8c7bec2", "e31c8e1d0b974cc0f8069161e03bef1b2487bbdd"),
    "poker/index.html": ("8b4a369eeec001a753fd776c89af8213d6a0011a", "e69b9cb0fb7a2a425fab7a783153fe848311f067"),
}
INSERTION = "<section class=\"poker-player-evidence\" aria-labelledby=\"nolan-tournament-record-title\">\n  <h3 id=\"nolan-tournament-record-title\">Nolan Kido at live poker tournaments.</h3>\n  <p>I play live tournament poker as well as write about poker study and decision-making. Independent tournament records document results in no-limit hold'em and pot-limit Omaha. The point of this section is to distinguish the public record from the analysis and stories I may publish later.</p>\n  <ul>\n    <li><strong>June 25, 2026:</strong> Fifth place in the 1,652-entry Lucky 300 no-limit hold'em tournament at South Point. <a href=\"https://www.globalpokerindex.com/tournaments/2026/united-states/lucky-300-no-limit-hold-em-1590392/\">See the event results at Global Poker Index</a>.</li>\n    <li><strong>August 2026:</strong> Results at WSOP Circuit Cherokee include 13th in an eight-max pot-limit Omaha ring event and 35th in a no-limit hold'em ring event. <a href=\"https://www.globalpokerindex.com/poker-players/nolan-kido-1314580/\">See the dated Global Poker Index results</a>.</li>\n  </ul>\n  <p>For a broader public record, see the <a href=\"https://www.wsop.com/players/448066374/nolan-kido/\">official WSOP player profile</a> and <a href=\"https://www.globalpokerindex.com/poker-players/nolan-kido-1314580/\">Global Poker Index listing</a>. Reported cashes are gross event payouts, not net profit. Public listings do not account for every entry, reentry, travel cost, staking arrangement, or session without a cash.</p>\n  <p><a href=\"/poker/reviewing-a-hand/\">My approach to reviewing a poker hand</a> explains why I separate the information available during play from what I know after the result.</p>\n</section>"


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def git_blob(data):
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, data):
    pair = BLOBS.get(key(path))
    if pair is None or git_blob(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    content = data.decode("utf-8") if binary else data
    if content.count(INSERTION) != 1:
        raise ValueError("Turn 5 player evidence successor is ambiguous")
    earlier = content.replace(INSERTION, "", 1)
    result = earlier.encode("utf-8") if binary else earlier
    if git_blob(result) != pair[0]:
        raise ValueError("Turn 5 player evidence predecessor does not match released file")
    return result
