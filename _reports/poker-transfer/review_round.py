"""Offline, case-bound qualified-review handoff for the Poker Foundations draft.

No learner submissions, external services, network access, or publication actions.
A machine-readable record is only a self-reported review artifact, never proof
of a human reviewer's identity or authorization to publish.
"""
import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FOLDER = Path(__file__).resolve().parent
LETTERS = "ABCDEFGHIJKL"
EXPECTED_IDS = [f"S{skill}-{letter}" for skill in range(1, 7) for letter in LETTERS]
TRIAGE_IDS = [
    "S1-A", "S1-B", "S1-I", "S2-A", "S2-B", "S2-D",
    "S3-A", "S3-B", "S3-L", "S4-A", "S4-B", "S4-J",
    "S5-A", "S5-B", "S5-D", "S6-A", "S6-B", "S6-G",
]
DIMENSIONS = ("mechanics", "clarity", "reasoning", "repairs", "accessibility")
DECISIONS = ("unreviewed", "accept", "revise", "block")


class ReviewError(ValueError):
    """A pack is stale, inconsistent, invalid or unsafe to write."""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def readable(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def source():
    raw = (FOLDER / "cases.json").read_text(encoding="utf-8").encode("utf-8")
    data = json.loads(raw)
    items = data["cases"]
    if (data.get("status") != "draft-qualified-human-review-pending"
            or [item["id"] for item in items] != EXPECTED_IDS):
        raise ReviewError("The expected 72-case draft bank is missing or reordered")
    return {item["id"]: item for item in items}, sha(raw)


def keys():
    body = (FOLDER / "facilitator-key.md").read_text(encoding="utf-8")
    matches = list(re.finditer(r'(?m)^<a id="(s[1-6]-[a-l])"></a>$', body))
    names = [match.group(1) for match in matches]
    if len(names) != len(EXPECTED_IDS) or len(set(names)) != len(names):
        raise ReviewError("The answer key has missing or duplicate case anchors")
    found = {}
    for index, match in enumerate(matches):
        case_id = match.group(1).upper()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        found[case_id] = body[match.start():end].strip() + "\n"
    if len(found) != 72 or set(found) != set(EXPECTED_IDS):
        raise ReviewError("The answer key is missing cases or has duplicate anchors")
    return found


def git_head():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
        text=True, check=False,
    )
    commit = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ReviewError("Use a Git checkout with a pinned commit for the review pack")
    scoped = subprocess.run([
        "git", "status", "--porcelain", "--",
        "_reports/poker-transfer/cases.json", "_reports/poker-transfer/cards",
        "_reports/poker-transfer/facilitator-key.md",
        "_reports/poker-transfer/review_round.py",
    ], cwd=ROOT, capture_output=True, text=True, check=False)
    if scoped.returncode or scoped.stdout.strip():
        raise ReviewError("Commit the review source, key, cards and generator before preparing a packet")
    return commit


def select(mode, case_list=None):
    if mode == "triage":
        if case_list:
            raise ReviewError("Triage has a fixed 18-case scope")
        return list(TRIAGE_IDS)
    if mode == "full":
        if case_list:
            raise ReviewError("Full review always includes every case")
        return list(EXPECTED_IDS)
    if mode != "custom" or not case_list:
        raise ReviewError("Custom review requires explicit comma-separated case IDs")
    ids = [part.strip().upper() for part in case_list.split(",")]
    if not all(ids) or len(ids) != len(set(ids)) or not set(ids) <= set(EXPECTED_IDS):
        raise ReviewError("Case IDs must be valid, distinct and nonempty")
    return ids


def ensure_output_destination(dest):
    destination = dest.expanduser().resolve()
    root = ROOT.resolve()
    if destination == root or root in destination.parents:
        raise ReviewError("Private review material must be kept outside this public repository")
    if destination.exists():
        raise ReviewError("Review directory already exists; refusing to overwrite it")
    return destination


def private_write(path, content):
    path.write_bytes(content)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def first_pass(ids, questions):
    sections = [
        "# Independent first-pass review questions",
        "DRAFT. No human approval is implied. Review each case before opening the "
        "answer key. Record independent reasoning, unclear terms, missing assumptions "
        "and accessibility problems in a private copy of the review form.",
        "These are individual learner cards reproduced from the pinned source. "
        "No case or course has yet been qualified for a supervised session.",
    ]
    for case_id in ids:
        card = questions[case_id]
        old_header = ("**Draft for qualified review. One fictional case only.** "
                      "This card contains no answer or other case. For a supervised session, "
                      "use the exact reviewer-approved case and record previous exposure. "
                      "No gambling account or wager is needed.")
        if old_header not in card:
            raise ReviewError("Unexpected learner-card introduction for " + case_id)
        reviewed_header = ("**Reviewer first pass only.** This section contains one "
                           "draft question, with no answer. It is not approval to "
                           "administer the case to a learner.")
        sections.append(card.replace(old_header, reviewed_header).rstrip())
    return "\n\n---\n\n".join(sections) + "\n"


def facilitator(ids, answer_keys):
    sections = [
        "# Answer key for the selected review scope",
        "DRAFT. Open only after completing the independent first pass. These are "
        "proposed explanation points and repairs, not reviewer findings or calibrated scores.",
    ]
    sections.extend(answer_keys[case_id].rstrip() for case_id in ids)
    return "\n\n---\n\n".join(sections) + "\n"


def review_sheet(ids, mode):
    lines = [
        "# Qualified reviewer response template",
        "Blank template, not a signed review. Make a private working copy of this "
        "form before writing any answers; leave this original blank for bundle "
        "integrity checks. The packet fingerprint and exact commit are in manifest.json.",
        "## Reviewer and revision",
        "Reviewer private reference: ______",
        "Relevant rules and beginner-teaching qualifications: ______",
        "Authoring involvement and conflicts: ______",
        "Review date and signature or externally stored attestation reference: ______",
        "Course teaching packet revision and its separately recorded review status: ______",
        "## Review procedure",
        "First solve the question alone. Then compare the answer key and precise "
        "repairs. Judge legal cards, amounts and actions; prompt clarity; assumptions "
        "and prerequisites; each of the three requested reasoning points; repair "
        "accuracy; and readability/accessibility. Record an independent calculation "
        "or concrete reason, not merely an accept label.",
        "Statuses for each criterion: unreviewed / accept / revise / block. "
        "Record material and teaching issues with an issue ID and correction commit. "
        "Unresolved material errors, unreviewed criteria or reviewer disagreements "
        "prevent approval. Recheck changed cases against a new packet.",
        f"## Case decisions for {mode} scope ({len(ids)} cases)",
    ]
    for case_id in ids:
        lines.extend([
            f"### {case_id}",
            "Mechanics: unreviewed  Clarity: unreviewed  Reasoning: unreviewed  "
            "Repairs: unreviewed  Accessibility: unreviewed",
            "Disposition: unreviewed",
            "Independent evidence for reasoning point 1: ______",
            "Independent evidence for reasoning point 2: ______",
            "Independent evidence for reasoning point 3: ______",
            "Overall independent mechanics/teaching evidence: ______",
            "Issue IDs, severity, disagreement and resolution: ______",
            "Exact case hash: see manifest.json (do not copy another case's conclusion)",
        ])
    lines.extend([
        "## Scope decision",
        "Selection and omissions: ______",
        "Open material or teaching issues: ______",
        "Changes requiring new source hashes and reviewer recheck: ______",
        "Signed, dated outcome for the exact scope: ______",
        "A completed triage review never approves the entire 72-case bank. "
        "A full 72-case review does not substitute for separate review of the "
        "underlying six-lesson teaching packet or real adult beginner observation. "
        "A machine cannot authenticate this signoff.",
    ])
    return "\n\n".join(lines) + "\n"


def make_packet(destination, mode="triage", case_list=None, source_commit=None):
    ids = select(mode, case_list)
    items, source_hash = source()
    answer_keys = keys()
    if source_commit is None:
        source_commit = git_head()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ReviewError("Source commit must be a full 40-character Git SHA")
    questions = {}
    entries = []
    for case_id in ids:
        card = (FOLDER / "cards" / (case_id + ".md")).read_text(encoding="utf-8")
        if "### " + case_id + ":" not in card or "<details>" in card:
            raise ReviewError("Missing or answer-bearing isolated card: " + case_id)
        if "### " + case_id + ":" not in answer_keys[case_id]:
            raise ReviewError("Answer key mismatch for " + case_id)
        questions[case_id] = card
        entries.append({
            "id": case_id, "case_sha256": sha(canonical(items[case_id])),
            "question_sha256": sha(card.encode("utf-8")),
            "key_sha256": sha(answer_keys[case_id].encode("utf-8")),
        })
    rendered_bundles = {
        "01-independent-questions.md": first_pass(ids, questions).encode("utf-8"),
        "02-facilitator-key.md": facilitator(ids, answer_keys).encode("utf-8"),
        "03-review-form.md": review_sheet(ids, mode).encode("utf-8"),
    }
    manifest = {
        "schema": 1, "status": "draft-human-review-pending",
        "source_commit": source_commit, "case_source_sha256": source_hash,
        "mode": mode, "case_ids": ids, "entries": entries,
        "bundle_sha256": {name: sha(content) for name, content in rendered_bundles.items()},
        "qualified_review_decision": None, "learner_observations": None,
        "note": "A content hash is not human attestation or publication approval.",
    }
    manifest_bytes = readable(manifest)
    record = {
        "schema": 1, "manifest_sha256": sha(manifest_bytes),
        "source_commit": source_commit,
        "reviewer": {
            "private_id": "", "qualification": "", "conflicts": "",
            "signed_date": "", "attestation_reference": "",
        },
        "course_review": {"decision": "unreviewed", "evidence_reference": ""},
        "cases": [
            {
                "id": entry["id"], "case_sha256": entry["case_sha256"],
                **{dimension: "unreviewed" for dimension in DIMENSIONS},
                "disposition": "unreviewed", "independent_evidence": "",
                "reasoning_point_evidence": ["", "", ""],
                "open_issue_ids": [],
            }
            for entry in entries
        ],
    }
    destination = ensure_output_destination(Path(destination))
    destination.mkdir(parents=True)
    try:
        os.chmod(destination, 0o700)
    except OSError:
        pass
    private_write(destination / "manifest.json", manifest_bytes)
    for filename, content in rendered_bundles.items():
        private_write(destination / filename, content)
    private_write(destination / "review-record.json", readable(record))
    return {"case_count": len(ids), "mode": mode, "status": "draft-human-review-pending",
            "source_commit": source_commit, "output": str(destination),
            "note": "Keep completed review records private. No approval has occurred."}


def audit_packet(directory):
    directory = Path(directory).expanduser().resolve()
    manifest_bytes = (directory / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    record = json.loads((directory / "review-record.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or record.get("schema") != 1:
        raise ReviewError("Unsupported review packet schema")
    items, source_hash = source()
    if manifest.get("case_source_sha256") != source_hash:
        raise ReviewError("The source case file changed: regenerate this packet and re-review")
    ids = select(manifest.get("mode"), ",".join(manifest.get("case_ids", []))
                 if manifest.get("mode") == "custom" else None)
    if ids != manifest.get("case_ids"):
        raise ReviewError("Review scope does not match the packet mode")
    if record.get("manifest_sha256") != sha(manifest_bytes):
        raise ReviewError("Review record no longer matches the generated manifest")
    if record.get("source_commit") != manifest.get("source_commit"):
        raise ReviewError("Review record points to a different material commit")
    bundles = manifest.get("bundle_sha256")
    expected_names = {"01-independent-questions.md", "02-facilitator-key.md", "03-review-form.md"}
    if not isinstance(bundles, dict) or set(bundles) != expected_names:
        raise ReviewError("The assembled reviewer bundle manifest is incomplete")
    for filename in expected_names:
        if sha((directory / filename).read_bytes()) != bundles[filename]:
            raise ReviewError("An assembled reviewer file was changed: " + filename)
    if len(manifest.get("entries", [])) != len(ids):
        raise ReviewError("Missing case entries in the manifest")
    answer_keys = keys()
    for case_id, entry in zip(ids, manifest["entries"]):
        question = (FOLDER / "cards" / (case_id + ".md")).read_text(encoding="utf-8").encode("utf-8")
        if (entry.get("id") != case_id
                or entry.get("case_sha256") != sha(canonical(items[case_id]))
                or entry.get("question_sha256") != sha(question)
                or entry.get("key_sha256") != sha(answer_keys[case_id].encode("utf-8"))):
            raise ReviewError("Case or rendered question/key changed: " + case_id)
    reviews = record.get("cases")
    if not isinstance(reviews, list) or len(reviews) != len(ids):
        raise ReviewError("Each reviewed case must have one complete record")
    counts = {state: 0 for state in DECISIONS}
    for case_id, entry, decision in zip(ids, manifest["entries"], reviews):
        if not isinstance(decision, dict):
            raise ReviewError("Invalid case review record")
        if decision.get("id") != case_id or decision.get("case_sha256") != entry["case_sha256"]:
            raise ReviewError("Review decision is attached to a wrong or stale case")
        disposition = decision.get("disposition")
        if disposition not in DECISIONS:
            raise ReviewError("Invalid review disposition for " + case_id)
        criteria = [decision.get(dimension) for dimension in DIMENSIONS]
        if any(value not in DECISIONS for value in criteria):
            raise ReviewError("Invalid point of review for " + case_id)
        if disposition == "accept" and any(value != "accept" for value in criteria):
            raise ReviewError("Cannot accept a case with an incomplete or adverse criterion")
        if disposition == "unreviewed" and any(value != "unreviewed" for value in criteria):
            raise ReviewError("An active review needs an explicit disposition")
        issues = decision.get("open_issue_ids")
        if not isinstance(issues, list) or any(not isinstance(x, str) or not x.strip() for x in issues):
            raise ReviewError("Malformed issue references for " + case_id)
        if disposition == "accept" and issues:
            raise ReviewError("Cannot accept a case with unresolved issues")
        evidence = decision.get("independent_evidence")
        if not isinstance(evidence, str) or (
                disposition != "unreviewed" and not evidence.strip()):
            raise ReviewError("A reviewed case requires independent evidence")
        point_evidence = decision.get("reasoning_point_evidence")
        if (not isinstance(point_evidence, list) or len(point_evidence) != 3
                or any(not isinstance(point, str) for point in point_evidence)):
            raise ReviewError("Each case requires three separate point-evidence fields")
        if disposition == "accept" and not all(point.strip() for point in point_evidence):
            raise ReviewError("Cannot accept without evidence for all three points: " + case_id)
        counts[disposition] += 1
    course = record.get("course_review")
    reviewer = record.get("reviewer")
    if not isinstance(course, dict) or course.get("decision") not in DECISIONS:
        raise ReviewError("Separate course review decision is invalid")
    course_reference = course.get("evidence_reference")
    if not isinstance(course_reference, str) or (
            course["decision"] != "unreviewed" and not course_reference.strip()):
        raise ReviewError("Separate course decision needs a nonblank string evidence reference")
    if not isinstance(reviewer, dict):
        raise ReviewError("Missing reviewer attestation fields")
    fields = ("private_id", "qualification", "conflicts", "signed_date", "attestation_reference")
    if any(not isinstance(reviewer.get(field), str) for field in fields):
        raise ReviewError("Malformed reviewer attestation fields")
    fields_present = all(reviewer[field].strip() for field in fields)
    if reviewer["signed_date"]:
        try:
            if date.fromisoformat(reviewer["signed_date"]).isoformat() != reviewer["signed_date"]:
                raise ValueError("Date must use YYYY-MM-DD")
        except ValueError as exc:
            raise ReviewError("Invalid reviewer date") from exc
    if counts["block"] or course["decision"] == "block":
        status = "blocked"
    elif counts["revise"] or course["decision"] == "revise":
        status = "revision_required"
    elif counts["unreviewed"] or not fields_present:
        status = "human_review_pending"
    elif manifest["mode"] != "full":
        status = "scoped_review_recorded_not_full_approval"
    elif course["decision"] != "accept":
        status = "course_review_pending"
    else:
        status = "full_review_record_claimed_authentication_required"
    return {
        "status": status, "mode": manifest["mode"],
        "total_cases": len(ids), "case_dispositions": counts,
        "reviewer_attestation_fields_present": fields_present,
        "separate_course_review": course["decision"],
        "release_authorized": False,
        "limitations": "Hashes check consistency only. Independently confirm authentic reviewer "
                       "signoff and case scope, then collect genuine adult observations. "
                       "This tool never authorizes publication.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="Write a local-only blank review packet")
    prepare.add_argument("--mode", choices=("triage", "full", "custom"), default="triage")
    prepare.add_argument("--cases", help="Comma-separated case IDs (only for custom mode)")
    prepare.add_argument("--out", type=Path, required=True,
                         help="New directory outside the public repository")
    audit = sub.add_parser("audit", help="Check local packet scope and private review-record integrity")
    audit.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = make_packet(args.out, mode=args.mode, case_list=args.cases)
        else:
            result = audit_packet(args.packet)
        print(json.dumps(result, indent=2))
        if args.command == "audit":
            # A claimed signoff is not authenticated. Never return exit 0 as a review clearance.
            return 3 if result["status"] == "full_review_record_claimed_authentication_required" else 2
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("REVIEW GATE FAILED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
