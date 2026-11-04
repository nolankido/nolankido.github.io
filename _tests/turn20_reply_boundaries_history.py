"""Test-only exact predecessor for Turn 20 synthetic reply boundary probes.

Only approved Git blobs are reversed. Unknown mutations pass through unchanged.
The public builder and the downloadable scripts do not import this module.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
    "_source/technology/review-reply-evidence-audit.html": (
        "b0b8b7915c4ca3d65a87ba6f0f6aa06a2181d292",
        "2163db231aa31c80d5305b9b8b97efbd7ef8b742",
    ),
    "technology/review-reply-evidence-audit/index.html": (
        "636e10dfdfab316f2ea5d6fbb3050b12de405956",
        "aa3544a806b39b62ed9dc29bf0199223102c96fa",
    ),
}
ADDED = {"downloads/reply-audit-boundary-probes.py": "70c1a8b710e96bce23f6442b1b8dba731b068b30"}
INSERTION = "<section class=\"section folio-row\" aria-labelledby=\"reply-audit-boundaries\">\n  <div class=\"section-meta\"><p class=\"section-label\">Adversarial probe / Reproducible limits</p></div>\n  <div class=\"section-content prose\">\n    <h2 id=\"reply-audit-boundaries\">A clean flag report can miss an invented offer.</h2>\n    <p>I appended four new, <strong>synthetic</strong> sentences, one at a time, to the same archived fictional complaint reply. Its original complaint facts remain intact, so the comparison isolates different wording of financial promises and a quotation. These sentences are my test cases, not additional model outputs. The expected flag in the table is an editorial judgment about the <em>specific financial-commitment signal</em>, not a decision that the entire reply is safe to send.</p>\n    <div class=\"project-table-scroll\" role=\"region\" aria-label=\"Boundary probes for the independent reply screen\" tabindex=\"0\">\n      <table>\n        <caption>Four constructed statements, screened against the same fictional reply</caption>\n        <thead><tr><th scope=\"col\">Added sentence</th><th scope=\"col\">Expected financial-commitment flag</th><th scope=\"col\">Observed screen</th></tr></thead>\n        <tbody>\n          <tr><th scope=\"row\"><q>We will refund the charge.</q></th><td>Yes, an unsupported refund promise</td><td>Flagged as expected</td></tr>\n          <tr><th scope=\"row\"><q>We will reimburse the charge.</q></th><td>Yes, an unsupported reimbursement promise</td><td>No targeted flag, a miss</td></tr>\n          <tr><th scope=\"row\"><q>We will send a gift card.</q></th><td>Yes, an unsupported offer</td><td>No targeted flag, a miss</td></tr>\n          <tr><th scope=\"row\"><q>Please do not write 'we have issued a refund' without approval.</q></th><td>No, it quotes a prohibited claim as a warning</td><td>Flagged, a quotation false alarm</td></tr>\n        </tbody>\n      </table>\n    </div>\n    <p><strong>What the new probe established:</strong> the unchanged screen agreed with the editorial expectation once and disagreed three times in these four deliberately selected statements. Two unsupported offers escaped its narrow phrase patterns, and one quoted warning triggered the pattern. These are constructed counterexamples, <strong>not</strong> a sample of model behavior, measured model accuracy, a false-positive rate, or evidence that a real business used the drafts.</p>\n    <p><a href=\"/downloads/reply-audit-boundary-probes.py\" download>Download the additional offline boundary-probe script (.py)</a> and place it beside the <a href=\"/downloads/review-reply-independent-audit.py\" download>original audit script</a>. Run <code>python3 reply-audit-boundary-probes.py --self-test</code> or <code>py -3 reply-audit-boundary-probes.py --self-test</code> from that directory. The new script reads only its public sibling file, performs no model or network calls, and prints JSON with the four observations. Its self-test verifies the described behavior, including the mismatches. A later checker improvement should change the results and the explanatory record together, not hide the mismatches.</p>\n    <p>A <code>no_targeted_flag</code> result therefore cannot authorize a customer message. Keep source facts, policy, commitments and tone in human review, and use a broader review process when a consequence matters.</p>\n  </div>\n</section>\n"
NAV_INSERTION = "<a href=\"#reply-audit-boundaries\">Blind spots</a>"


def key(path):
    relative = Path(path)
    if relative.is_absolute():
        try:
            relative = relative.relative_to(ROOT)
        except ValueError:
            return relative.as_posix()
    return relative.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, data):
    known = BLOBS.get(key(path))
    if known is None or blob(data) != known[1]:
        return data
    binary = isinstance(data, bytes)
    current = data.decode("utf-8") if binary else data
    if current.count(INSERTION) != 1 or current.count(NAV_INSERTION) != 1:
        raise ValueError("Turn 20 approved content or navigation is absent")
    previous = current.replace(INSERTION, "", 1).replace(NAV_INSERTION, "", 1)
    restored = previous.encode("utf-8") if binary else previous
    if blob(restored) != known[0]:
        raise ValueError("Turn 20 exact predecessor failed Git blob check")
    return restored


def is_added_file(path, data):
    import turn25_identity_evidence_history
    if turn25_identity_evidence_history.is_added_file(path, data):
        return True
    digest = ADDED.get(key(path))
    return digest is not None and blob(data) == digest
