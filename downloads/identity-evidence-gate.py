#!/usr/bin/env python3
"""Offline comparison for the Nolan Kido public identity-metadata correction.

This verifies selected structural invariants in two JSON-LD records. It does
NOT verify credentials, ownership of accounts, search ranking, AI citations,
or the truth of any free-text description. No network or file writes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

PERSON_ID = "https://nolankido.com/about/#nolan-kido"
RESEARCH_ID = "https://doi.org/10.1111/j.1475-679X.2012.00447.x"
SENSITIVE = ("jobTitle", "alumniOf", "hasCredential", "affiliation", "worksFor")


def nodes(document: object) -> dict[str, dict]:
    if not isinstance(document, dict) or document.get("@context") != "https://schema.org":
        raise ValueError("Expected a schema.org JSON-LD object")
    graph = document.get("@graph")
    if not isinstance(graph, list) or not graph:
        raise ValueError("Missing nonempty @graph")
    by_type: dict[str, dict] = {}
    for item in graph:
        if not isinstance(item, dict) or not isinstance(item.get("@type"), str):
            raise ValueError("Every graph node needs one @type")
        kind = item["@type"]
        if kind in by_type:
            raise ValueError("Repeated node type: " + kind)
        by_type[kind] = item
    required = {"WebSite", "Person", "ScholarlyArticle"}
    if set(by_type) != required:
        raise ValueError("Expected exactly WebSite, Person, and ScholarlyArticle nodes")
    return by_type


def review(before: object, after: object) -> tuple[list[str], list[str]]:
    older, newer = nodes(before), nodes(after)
    issues: list[str] = []
    findings: list[str] = []
    bp, ap = older["Person"], newer["Person"]
    for field in ("@id", "name", "alternateName", "url", "identifier", "sameAs"):
        if bp.get(field) != ap.get(field):
            issues.append("Person " + field + " changed; review identity continuity")
    if ap.get("@id") != PERSON_ID:
        issues.append("Person @id is not the documented canonical identity")
    if newer["WebSite"] != older["WebSite"]:
        issues.append("WebSite node changed outside the proposed identity edit")
    if newer["ScholarlyArticle"] != older["ScholarlyArticle"]:
        issues.append("ScholarlyArticle node changed outside the proposed identity edit")
    if newer["ScholarlyArticle"].get("@id") != RESEARCH_ID:
        issues.append("ScholarlyArticle DOI does not match the recorded publication")
    urls = ap.get("sameAs")
    if not isinstance(urls, list) or len(urls) != len(set(map(str, urls))):
        issues.append("Person sameAs is missing or contains duplicate entries")
    for field in SENSITIVE:
        if field in ap:
            issues.append("Sensitive field still published: " + field)
        elif field in bp:
            findings.append("Removed field requiring source review: " + field)
    if bp.get("description") == ap.get("description"):
        findings.append("Free-text description unchanged")
    else:
        findings.append("Free-text description changed; factual review still required")
    if ap.get("description") is None or not isinstance(ap["description"], str):
        issues.append("A public description is missing")
    other = (set(ap) - set(bp)) - {"description"}
    if other:
        issues.append("Unexpected new Person fields: " + ", ".join(sorted(other)))
    return issues, findings


def example() -> tuple[dict, dict]:
    before = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": "https://nolankido.com/#website"},
            {"@type": "Person", "@id": PERSON_ID, "name": "Nolan Kido",
             "url": "https://nolankido.com/about/", "alternateName": ["Nolan Y. Kido"],
             "identifier": {"value": "example"}, "sameAs": ["https://github.com/nolankido"],
             "jobTitle": "unverified example", "hasCredential": [{"name": "unverified"}],
             "description": "An unverified role claim"},
            {"@type": "ScholarlyArticle", "@id": RESEARCH_ID},
        ],
    }
    after = json.loads(json.dumps(before))
    p = after["@graph"][1]
    del p["jobTitle"]
    del p["hasCredential"]
    p["description"] = "A bounded, checkable description"
    return before, after


def self_test() -> bool:
    old, clean = example()
    tests = []
    issues, notes = review(old, clean)
    tests.append(not issues and len([n for n in notes if n.startswith("Removed")]) == 2)
    bad = json.loads(json.dumps(clean))
    bad["@graph"][1]["jobTitle"] = "new unsupported title"
    tests.append(any("jobTitle" in e for e in review(old, bad)[0]))
    bad = json.loads(json.dumps(clean))
    bad["@graph"][1]["sameAs"].append("https://example.com/other-person")
    tests.append(any("sameAs" in e for e in review(old, bad)[0]))
    bad = json.loads(json.dumps(clean))
    bad["@graph"][2]["@id"] = "https://doi.org/not-the-same"
    tests.append(any("ScholarlyArticle" in e for e in review(old, bad)[0]))
    bad = json.loads(json.dumps(clean))
    bad["@graph"][1]["@id"] = "https://example.com/wrong#person"
    tests.append(any("Person @id" in e for e in review(old, bad)[0]))
    good = all(tests)
    print(("PASS" if good else "FAIL") + ": " + str(sum(tests)) + "/5 synthetic checks")
    return good


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, help="A downloaded pre-change JSON-LD file")
    parser.add_argument("--after", type=Path, help="A downloaded post-change JSON-LD file")
    parser.add_argument("--self-test", action="store_true", help="Run only synthetic local cases")
    options = parser.parse_args()
    if options.self_test:
        if options.before or options.after:
            parser.error("--self-test cannot be combined with input files")
        return 0 if self_test() else 1
    if not (options.before and options.after):
        parser.error("Supply both --before and --after")
    try:
        # Small public records only. Do not supply personal or confidential files.
        records = []
        for path in (options.before, options.after):
            if path.stat().st_size > 1_000_000:
                raise ValueError("Input too large for the bounded public-record checker")
            records.append(json.loads(path.read_text(encoding="utf-8")))
        issues, findings = review(*records)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("INPUT ERROR: " + str(exc), file=sys.stderr)
        return 1
    for item in findings:
        print("NOTE: " + item)
    for item in issues:
        print("FLAG: " + item)
    if issues:
        print("FLAGGED: structural or provenance-related review needed")
        return 2
    print("PASS: scoped structural checks only. Independent human evidence review is still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
