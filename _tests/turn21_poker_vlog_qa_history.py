"""Test-only exact predecessor for Turn 21 poker vlog truth-to-screen QA.

Only approved Git blob revisions are reversed. Unexpected edits pass through
unchanged. The production site builder does not import this test fixture.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
    "_source/technology/home.html": (
        "fe243f9be6044cb042e81298e0356b40570d7b17",
        "c7ffe2486205a27f29bc0f494f7019cb8699af25",
    ),
    "technology/index.html": (
        "0ae9fe7bae69a764e29bfbe2e5925c588a2b4786",
        "0f164e93bceed0d54d962a73adf3a5a69aa27051",
    ),
}
INSERTION = "<section class=\"section folio-row\" id=\"poker-vlog-qa\" aria-labelledby=\"poker-vlog-qa-title\">\n  <div class=\"section-meta\"><p class=\"section-label\">Creative production / A human evidence gate</p></div>\n  <div class=\"section-content prose\">\n    <h2 class=\"section-title\" id=\"poker-vlog-qa-title\">How I check an AI-assisted poker vlog edit against the hand record.</h2>\n    <p>AI can help arrange a story, draft an overlay or organize a revision list. It cannot establish an unrecorded card suit, reconstruct a missing board, or turn my later analysis into something I knew at the table. My public <a href=\"/poker/episodes/portland-meadows-ep1/\">Portland Meadows Episode 1 companion</a> supplies two documented hands for a practical truth-to-screen check. This is a proposed repeatable release standard, not proof that every earlier upload passed it.</p>\n    <div class=\"project-table-scroll\" role=\"region\" aria-label=\"Public poker hand facts and graphics boundaries\" tabindex=\"0\">\n      <table>\n        <caption>What a graphics and narration review can use from the published companion</caption>\n        <thead><tr><th scope=\"col\">Moment</th><th scope=\"col\">Source-supported facts</th><th scope=\"col\">Do not silently fill in</th></tr></thead>\n        <tbody>\n          <tr><th scope=\"row\"><a href=\"/poker/episodes/portland-meadows-ep1/#hand-64o-record\">6-4 offsuit near the money bubble</a></th><td>Small blind, 13 players left with 10 paid, about 148,000 chips at a 15,000 big blind, approximately 9.87 BB; shove called by A-K suited</td><td>Individual hole-card suits, complete board, exact effective stack or a numerical solver endorsement</td></tr>\n          <tr><th scope=\"row\"><a href=\"/poker/episodes/portland-meadows-ep1/#hand-77-record\">Pocket sevens four-handed</a></th><td>Big blind, about 585,000 chips at a 30,000 big blind, 19.5 BB; button's 75,000 open is 2.5 BB; reshove called by A-T offsuit, sevens hold</td><td>Full runout, opponent's full opening range, unobserved thoughts or a verified ICM conclusion</td></tr>\n          <tr><th scope=\"row\"><a href=\"/poker/episodes/portland-meadows-ep1/#event-numbers\">Tournament result graphic</a></th><td>Advertised first prize was $5,100; my reported payment after the four-way deal was $2,900</td><td>Confusing advertised first prize with received payout, or describing either amount as net profit</td></tr>\n        </tbody>\n      </table>\n    </div>\n    <ol>\n      <li><strong>Lock the source before editing.</strong> Give each hand a fact record, a public evidence link, and an explicit unknowns field. Treat private footage notes and later recollections as different evidence categories.</li>\n      <li><strong>Reconcile voiceover with every on-screen assertion.</strong> Check positions, stack units, raise-to amounts, pot arithmetic, stated hand, board progression and outcome at the moment the viewer sees them. If a suit is unknown, either omit it or clearly mark a purely illustrative reconstruction.</li>\n      <li><strong>Separate in-the-moment thought from hindsight.</strong> A retrospective range or solver-style question must not be presented as a contemporaneous calculation or a verified solver result.</li>\n      <li><strong>Review the actual release cut.</strong> Earlier version 7 chapter offsets in the companion were not checked against the current public upload. Never carry old timestamps into a chapter list merely because the story is similar.</li>\n      <li><strong>Give a person the final decision.</strong> Accept, revise or hold each sequence; check music, footage, venue rules and participant privacy separately. An AI edit suggestion does not supply those permissions.</li>\n    </ol>\n    <p><a href=\"/downloads/poker-vlog-truth-to-screen-qa.md\" download>Download the public truth-to-screen QA worksheet (.md)</a> with these source-backed examples and a blank scene-by-scene acceptance record. It requires no account, model request or API, and keeps private production notes out of this site.</p>\n    <p class=\"small-copy\"><strong>Evidence limit:</strong> This method is an original editorial control built from an existing public video companion. It does not establish improved viewer retention, verified solver decisions, edit speed, permission to film, or the quality of unpublished footage. <a href=\"/poker/hand-to-vlog/\">The creator workbench</a> covers the broader proposed story and graphics workflow.</p>\n  </div>\n</section>\n"


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
    pair = BLOBS.get(key(path))
    if pair is None or blob(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    current = data.decode("utf-8") if binary else data
    if current.count(INSERTION) != 1:
        raise ValueError("Turn 21 approved QA section is absent")
    restored = current.replace(INSERTION, "", 1)
    predecessor = restored.encode("utf-8") if binary else restored
    if blob(predecessor) != pair[0]:
        raise ValueError("Turn 21 predecessor Git blob mismatch")
    return predecessor
