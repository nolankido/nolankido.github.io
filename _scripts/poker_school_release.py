"""Offline additive Poker School release guard.

The frozen Git blob inventory comes from main commit 9021d46. This module
rejects undeclared path changes. Exact prior content is independently checked
by test_poker_school_history. This guard alone never authorizes publication.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "9021d4604c9427c37dc6c788753ddf9675dfc7ba"
FROZEN = "_reports/poker-school-main-blobs.json"
MODIFIED = frozenset((
    '.github/workflows/site-checks.yml',
    '_reports/poker-search-intent/evaluate.py',
    '_reports/search-audit.json',
    '_scripts/build.py',
    '_scripts/check_live.py',
    '_source/pages.json',
    '_source/poker/home.html',
    '_source/poker/study.html',
    '_tests/browser.py',
    '_tests/choice_history.py',
    '_tests/local_fonts_history.py',
    '_tests/poker_progress_history.py',
    '_tests/position_maps_history.py',
    '_tests/rules_reference_history.py',
    '_tests/test_checkpoint.py',
    '_tests/test_content.py',
    '_tests/test_getting_started.py',
    '_tests/test_hand_lab.py',
    '_tests/test_learning_path.py',
    '_tests/test_local_fonts.py',
    '_tests/test_multiway_essay.py',
    '_tests/test_poker_course.py',
    '_tests/test_poker_practice.py',
    '_tests/test_poker_progress.py',
    '_tests/test_poker_search_intent.py',
    '_tests/test_poker_search_titles.py',
    '_tests/test_practical_navigation.py',
    '_tests/test_round_practice.py',
    '_tests/test_search_public_titles.py',
    '_tests/test_search_sections.py',
    '_tests/test_short_stack_flagship.py',
    '_tests/test_site.py',
    '_tests/test_study_list_release.py',
    '_tests/test_thunder_valley.py',
    '_tests/test_tournament_budget.py',
    '_tests/test_uncertainty.py',
    'find/index.html',
    'poker/find/index.html',
    'poker/index.html',
    'poker/study/index.html',
    'sitemap.xml',
))
ADDED = frozenset((
    '_reports/poker-school-main-blobs.json',
    '_reports/poker-school-offer.md',
    '_reports/poker-school-release-gate.md',
    '_reports/poker-school/capture_history.py',
    '_reports/poker-school/search-results.json',
    '_scripts/poker_school_release.py',
    '_source/poker/school.html',
    '_tests/poker-school-change.json',
    '_tests/poker_school_history.py',
    '_tests/test_poker_school.py',
    '_tests/test_poker_school_history.py',
    '_tests/test_poker_school_release.py',
    'assets/poker-school-interest.js',
    'assets/poker-school.css',
    'poker/school/index.html',
))
PROTECTED = (
    "assets/contact.js", "_source/privacy.html",
    "_source/poker/free-poker-learning-path.html",
)


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def compare(base, current):
    return {
        "added": set(current) - set(base),
        "deleted": set(base) - set(current),
        "modified": {p for p in base.keys() & current.keys() if base[p] != current[p]},
    }


def verify(base, current):
    delta = compare(base, current)
    if delta["deleted"] or delta["added"] != ADDED or delta["modified"] != MODIFIED:
        detail = {kind: {"unexpected": sorted(paths - expected),
                         "missing": sorted(expected - paths)}
                  for kind, paths, expected in (
                      ("added", delta["added"], ADDED),
                      ("modified", delta["modified"], MODIFIED),
                      ("deleted", delta["deleted"], set()),
                  )}
        raise ValueError("Unexpected release delta: " + repr(detail))
    for path in PROTECTED:
        if current.get(path) != base.get(path):
            raise ValueError("Locked contact, privacy or teaching source changed: " + path)
    return {"base": BASE, "unchanged": len(base) - len(delta["modified"]),
            "added": len(ADDED), "modified": len(MODIFIED), "deleted": 0,
            "status": "source_delta_checked", "release_authorized": False}


def audit(root=ROOT):
    raw_inventory = (root / FROZEN).read_bytes()
    if hashlib.sha256(raw_inventory).hexdigest() != '3b04cb26ffe77c204ecc2c00cfc9477aa4147730e6eadb35293416030f2b779e':
        raise ValueError("The pinned original inventory changed")
    frozen = json.loads(raw_inventory)
    if frozen.get("version") != 1 or frozen.get("base_commit") != BASE:
        raise ValueError("Wrong baseline revision")
    base = frozen.get("tracked_base_blobs")
    if not isinstance(base, dict) or len(base) != 1207:
        raise ValueError("Original inventory is incomplete")
    data = subprocess.check_output(
        ["git", "-c", f"safe.directory={root.resolve()}", "ls-files", "-z"], cwd=root
    )
    current = {}
    for blob in data.split(b"\0"):
        if not blob:
            continue
        path = blob.decode("utf-8")
        if path in current or path.startswith("/") or ".." in Path(path).parts or "\\" in path:
            raise ValueError("Invalid tracked path: " + path)
        target = root / path
        if not target.is_file() or target.is_symlink():
            raise ValueError("Missing or unusual tracked file: " + path)
        current[path] = git_blob_sha(target.read_bytes())
    return verify(base, current)


if __name__ == "__main__":
    try:
        report = audit()
        print(json.dumps(report, sort_keys=True))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print("Poker School additive release BLOCKED:", error)
        raise SystemExit(1)
