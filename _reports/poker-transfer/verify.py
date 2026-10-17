"""Read-only mechanical QA for draft Poker Foundations transfer cards."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
FOLDER = Path(__file__).resolve().parent
VALUES = {c: n for n, c in enumerate("23456789TJQKA", 2)}
SKILLS = ["S1", "S2", "S3", "S4", "S5", "S6"]
LESSONS = ["first-decisions", "starting-hand-decisions", "first-flop-decisions",
           "turn-and-river-decisions", "ranges-for-beginners", "betting-with-a-purpose"]
REPAIRS = {
    "S1": {"chips-owed"}, "S2": {"position"}, "S3": {"made-and-drawing"},
    "S4": {"river-reset", "catching-a-bluff"}, "S5": {"known-and-possible", "remove-known-cards"},
    "S6": {"purpose"},
}

def five(cards):
    ranks = sorted((VALUES[c[0]] for c in cards), reverse=True)
    count = Counter(ranks)
    groups = sorted(((n, v) for v, n in count.items()), reverse=True)
    uniq = set(ranks)
    if 14 in uniq:
        uniq.add(1)
    straight = next((high for high in range(14, 4, -1)
                     if set(range(high-4, high+1)).issubset(uniq)), 0)
    flush = len({c[1] for c in cards}) == 1
    if straight and flush:
        return (8, straight)
    if groups[0][0] == 4:
        return (7, groups[0][1], groups[1][1])
    if groups[0][0] == 3 and groups[1][0] == 2:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5, *ranks)
    if straight:
        return (4, straight)
    if groups[0][0] == 3:
        return (3, groups[0][1], *sorted((v for v, n in count.items() if n == 1), reverse=True))
    pairs = sorted((v for v, n in count.items() if n == 2), reverse=True)
    if len(pairs) == 2:
        return (2, *pairs, next(v for v, n in count.items() if n == 1))
    if len(pairs) == 1:
        return (1, pairs[0], *sorted((v for v, n in count.items() if n == 1), reverse=True))
    return (0, *ranks)

def best(cards):
    assert len(cards) in (5, 7), "Only flop or river best-five comparisons"
    return max(five(hand) for hand in combinations(cards, 5))

def check():
    data = json.loads((FOLDER / "cases.json").read_text(encoding="utf-8"))
    assert set(data) == {"version", "status", "course", "baseline_commit", "cases"}
    assert data["version"] == 1 and data["course"] == "poker-foundations"
    assert data["status"] == "draft-qualified-human-review-pending"
    assert len(data["baseline_commit"]) == 40
    items = data["cases"]
    assert len(items) == 12
    assert [i["id"] for i in items] == [f"{s}-{v}" for s in SKILLS for v in "AB"]
    prior = json.loads((ROOT / "_reports/poker-beginner-baseline/tasks.json").read_text())
    prior_pairs = {(tuple(t["hero"]), tuple(t["board"])) for t in prior["tasks"]}
    signatures = set()
    for item in items:
        skill, form = item["id"].split("-")
        assert item["skill"] == skill and form in "AB"
        assert item["lesson"] == LESSONS[SKILLS.index(skill)]
        assert all(isinstance(item[k], str) and item[k].strip()
                   for k in ("title", "setup", "prompt", "misconception"))
        assert len(item["points"]) == 3 and all(isinstance(p, str) and p.strip() for p in item["points"])
        hero, board = item["hero"], item["board"]
        assert len(hero) == 2 and len(board) in (0, 3, 5)
        cards = hero + board
        assert len(set(cards)) == len(cards)
        assert all(re.fullmatch(r"[2-9TJQKA][shdc]", c) for c in cards)
        signature = (tuple(hero), tuple(board))
        assert signature not in signatures and signature not in prior_pairs
        signatures.add(signature)
        assert item["repair"].startswith("/poker/" + item["lesson"] + "/#")
        anchor = item["repair"].split("#")[1]
        assert anchor in REPAIRS[skill]
        assert len(item.get("point_repairs", [])) == 3
        for link in item["point_repairs"]:
            assert isinstance(link, str) and link.startswith("/poker/") and link.count("#") == 1
            repair_path, repair_anchor = link.split("#")
            lesson = repair_path.rstrip("/").split("/")[-1]
            assert lesson in LESSONS + ["hand-rankings"]
            repair_source = (ROOT / "_source/poker" / (lesson + ".html")).read_text()
            assert 'id="' + repair_anchor + '"' in repair_source
        lesson_source = (ROOT / "_source/poker" / (item["lesson"] + ".html")).read_text()
        assert 'id="' + anchor + '"' in lesson_source
        if board:
            assert tuple(item["expected_rank"]) == best(cards), item["id"]
        else:
            assert "expected_rank" not in item
        if "call" in item:
            c = item["call"]
            assert set(c) == {"to", "paid", "answer"}
            assert all(type(v) is int and v >= 0 for v in c.values())
            assert c["to"] > c["paid"] and c["to"] - c["paid"] == c["answer"]
        if "river" in item:
            r = item["river"]
            assert all(type(v) is int and v >= 0 for v in r.values())
            assert r["pot_before"] + r["bet"] + r["call"] == r["after"]
            assert r["bet"] == r["call"] and r["paid"] == 0
            assert Fraction(r["call"], r["after"]) == Fraction(r["num"], r["den"])
        if "candidates" in item:
            assert len(board) == 5 and len(item["candidates"]) in (2, 3)
            results = []
            for opposing in item["candidates"]:
                assert len(opposing) == 2 and opposing[0] != opposing[1]
                assert all(re.fullmatch(r"[2-9TJQKA][shdc]", c) for c in opposing)
                if any(c in cards for c in opposing):
                    results.append("impossible")
                else:
                    rival = best(opposing + board)
                    own = best(cards)
                    results.append("stronger" if rival > own else "weaker" if rival < own else "tie")
            assert results == item["expected_comparisons"], item["id"]
        assert not item["misconception"].startswith("Mastered")
    assert sum("river" in i for i in items) == 2
    assert sum("candidates" in i for i in items) == 4
    assert sum("call" in i for i in items) == 2
    for protocol_file in ("protocol.md", "session-form.md", "summary-form.md"):
        content = (FOLDER / protocol_file).read_text(encoding="utf-8")
        assert "No sessions" in content or "No sessions or results" in content or "No field" in content or "No sessions have occurred" in content or "Template only" in content
        assert all(s in content for s in SKILLS) if protocol_file == "protocol.md" else True
    protocol = (FOLDER / "protocol.md").read_text(encoding="utf-8")
    assigned = ("S1-A", "S2-B", "S3-A", "S4-B", "S5-A", "S6-B", "S1-B", "S2-A")
    assert all(case_id in protocol for case_id in assigned)
    assert all("P" + str(n).zfill(2) in protocol for n in range(1, 9))
    assert "T1–T6" in protocol and "not" in protocol.lower()
    assert all(f"(cards/{case_id}.md)" in protocol for case_id in assigned)
    assert "new full private" in protocol
    assert "Assigned case (S1-A through S6-B)" in (FOLDER / "session-form.md").read_text(encoding="utf-8")
    assert "Consent status" in (FOLDER / "session-form.md").read_text(encoding="utf-8")
    assert "later paired" in (FOLDER / "session-form.md").read_text(encoding="utf-8")
    assert "Prior similar-problem exposure" in (FOLDER / "summary-form.md").read_text(encoding="utf-8")
    assert all(f"| {case['id']} |" in (FOLDER / "summary-form.md").read_text(encoding="utf-8") for case in items)
    for case in items:
        isolated = (FOLDER / "cards" / (case["id"] + ".md")).read_text(encoding="utf-8")
        assert case["setup"] in isolated and case["prompt"] in isolated
        assert "Private cards: " + ", ".join(case["hero"]) in isolated
        assert "Shared cards: " + (", ".join(case["board"]) or "not dealt") + "." in isolated
        for n, candidate in enumerate(case.get("candidates", []), 1):
            assert f"Candidate {n}: " + ", ".join(candidate) + "." in isolated
        assert isolated.count("### ") == 1
        assert "### " + case["id"] + ":" in isolated
        assert "one-case" not in isolated or "One fictional case" in isolated
        assert not any(point in isolated for point in case["points"])
        assert not any("### " + other["id"] + ":" in isolated for other in items if other is not case)
    for name in ("participant-cards.md", "facilitator-key.md", "self-study.md"):
        body = (FOLDER / name).read_text(encoding="utf-8")
        for case in items:
            assert body.count("### " + case["id"] + ":") == 1, (name, case["id"])
        assert "No monetary stakes" in body or "fictional" in body.lower()
        for case in items:
            start = body.index("### " + case["id"] + ":")
            end = body.find("\n### ", start + 1)
            section = body[start:end if end != -1 else len(body)]
            if name != "facilitator-key.md":
                assert case["setup"] in section and case["prompt"] in section
            else:
                assert all(point in section for point in case["points"])
            if name != "participant-cards.md":
                label = "Point {} repair" if name == "facilitator-key.md" else "Revisit point {}"
                for n, link in enumerate(case["point_repairs"], 1):
                    assert f"[{label.format(n)}](https://nolankido.com{link})" in section
    participant = (FOLDER / "participant-cards.md").read_text()
    assert "<details>" not in participant and "Computed high-hand vector" not in participant
    assert all(p not in participant for case in items for p in case["points"])
    guide = (FOLDER / "facilitator-key.md").read_text()
    assert all(case["misconception"] in guide for case in items)
    assert guide.count("[Point 3 repair]") == len(items)
    assert "has not acted" not in items[2]["setup"] and "checks first" not in items[3]["setup"]
    assert "worse holding below folds" not in items[11]["setup"]
    # The setup supplies the scene, not the missing-input reasoning being elicited.
    assert "frequenc" not in items[10]["setup"].lower()
    assert "frequenc" not in items[11]["setup"].lower()
    assert "frequenc" not in items[8]["setup"].lower()
    assert "at least 30 counters each still behind" in items[3]["setup"]
    assert items[11]["point_repairs"][0] == "/poker/hand-rankings/#compare"
    session = (FOLDER / "session-form.md").read_text()
    summary = (FOLDER / "summary-form.md").read_text()
    for field in ("this exact case", "this case's answer key", "a similar problem"):
        assert re.search(r"Prior exposure to " + re.escape(field) + r": yes / no / unsure", session)
    for n in range(1, 4):
        assert f"Assisted reasoning point {n}:" in session
    for column in ("Assisted attempted (any help)", "Assisted explanation supported (all three)",
                   "Prior exact-case exposure (yes / no / unsure)",
                   "Prior answer-key exposure (yes / no / unsure)",
                   "Prior similar-problem exposure (yes / no / unsure)"):
        assert column in summary
    rows = [line for line in summary.splitlines() if line.startswith("| ")]
    assert len(rows) == 14 and len({row.count("|") for row in rows}) == 1
    assert "overlapping" in summary and "separate tables" in summary
    form = (FOLDER / "review-form.md").read_text()
    for item in items:
        assert form.count("| " + item["id"] + " | unreviewed |") == 1
    assert "Outcome (not prefilled)" in form
    print("PASS: 12 original pairwise transfer cases, independent best-five ranks, cards, blockers, calls, river fractions, exact repairs and split views. Human review pending.")
    return len(items)

if __name__ == "__main__":
    check()
