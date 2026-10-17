"""Read-only mechanical QA for draft Poker Foundations transfer cards."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import re

ROOT = Path(__file__).resolve().parents[2]
FOLDER = Path(__file__).resolve().parent
VALUES = {c: n for n, c in enumerate("23456789TJQKA", 2)}
RANK_NAMES = dict(zip("23456789TJQKA", ("two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king", "ace")))
SUIT_NAMES = {"s": "spades", "h": "hearts", "d": "diamonds", "c": "clubs"}
SKILLS = ["S1", "S2", "S3", "S4", "S5", "S6"]
LESSONS = ["first-decisions", "starting-hand-decisions", "first-flop-decisions",
           "turn-and-river-decisions", "ranges-for-beginners", "betting-with-a-purpose"]
REPAIRS = {
    "S1": {"chips-owed", "best-five", "round-complete", "turn-order"}, "S2": {"position"}, "S3": {"made-and-drawing"},
    "S4": {"river-reset", "catching-a-bluff"}, "S5": {"known-and-possible", "remove-known-cards"},
    "S6": {"purpose"},
}

def card_names(cards):
    return "; ".join(RANK_NAMES[c[0]] + " of " + SUIT_NAMES[c[1]] for c in cards)

def check_names(section, case):
    assert "Private card names: " + card_names(case["hero"]) + "." in section
    if case["board"]:
        assert "Shared card names: " + card_names(case["board"]) + "." in section
    for n, cards in enumerate(case.get("candidates", []), 1):
        assert f"Candidate {n} card names: " + card_names(cards) + "." in section

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
    assert len(cards) in (5, 6, 7), "Best five from five to seven available cards"
    return max(five(hand) for hand in combinations(cards, 5))

FORMS = "ABCDEFGHIJKL"
BASELINE_CASES_SHA256 = "c8e8c4e3c12892825d3faef74d6669a262d33c15f4604eecbb4ecfb61f3dcf44"
EXPANSION_BASELINE = "8fc1d78b76e313be721d9bded0cb16d98501b81f"


def check_action(item):
    c = item["call"]
    assert set(c) == {"to", "paid", "answer"}
    assert all(type(v) is int and v >= 0 for v in c.values())
    assert c["to"] >= c["paid"] and c["to"] - c["paid"] == c["answer"]
    if "action" in item:
        action = item["action"]
        assert set(action) == {"owed", "check_allowed", "legal_actions"}
        assert type(action["owed"]) is int and type(action["check_allowed"]) is bool
        assert action["owed"] == c["answer"]
        assert action["check_allowed"] == (c["answer"] == 0)
        expected = ["fold", "call", "raise"] if c["answer"] else ["check", "raise" if c["to"] else "bet"]
        assert action["legal_actions"] == expected, item["id"]


def check_order(item):
    order = item["action_order"]
    assert set(order) == {"stage", "seats", "active", "folded", "acted", "next", "hero", "responders"}
    seats = order["seats"]
    assert seats == ["button", "small blind", "big blind", "under the gun", "hijack", "cutoff"]
    assert order["stage"] in ("preflop", "postflop")
    for field in ("active", "folded", "acted", "responders"):
        assert len(order[field]) == len(set(order[field]))
        assert set(order[field]) <= set(seats)
    active, folded = set(order["active"]), set(order["folded"])
    assert len(active) >= 2 and active.isdisjoint(folded) and active | folded == set(seats)
    start = 3 if order["stage"] == "preflop" else 1
    clockwise = seats[start:] + seats[:start]
    live = [seat for seat in clockwise if seat in active]
    done = order["acted"]
    assert done == live[:len(done)] and len(done) < len(live)
    assert order["next"] == order["hero"] == live[len(done)]
    assert order["responders"] == live[len(done)+1:]
    if order["stage"] == "preflop":
        assert not item["board"]
    elif not item["board"]:
        assert item.get("board_note") == "not shown (the flop is dealt)"


def has_straight(cards):
    ranks = {VALUES[c[0]] for c in cards}
    if 14 in ranks:
        ranks.add(1)
    return any(set(range(high-4, high+1)) <= ranks for high in range(5, 15))


def check_draw(item):
    draw = item["draw"]
    cards = item["hero"] + item["board"]
    assert set(draw) == {"suit", "suit_count", "completion_ranks"}
    assert len(item["board"]) == 3
    assert draw["suit"] in (None, "s", "h", "d", "c")
    assert type(draw["suit_count"]) is int
    assert draw["suit_count"] == (sum(c[1] == draw["suit"] for c in cards) if draw["suit"] else 0)
    expected = []
    if not has_straight(cards):
        for rank in VALUES:
            available = [rank + suit for suit in SUIT_NAMES if rank + suit not in cards]
            if available and has_straight(cards + available[:1]):
                expected.append(rank)
    assert draw["completion_ranks"] == expected, (item["id"], expected)


def check():
    data = json.loads((FOLDER / "cases.json").read_text(encoding="utf-8"))
    assert set(data) == {"version", "status", "course", "baseline_commit", "expansion_baseline_commit", "forms", "cases"}
    assert data["version"] == 2 and data["course"] == "poker-foundations"
    assert data["status"] == "draft-qualified-human-review-pending"
    assert data["expansion_baseline_commit"] == EXPANSION_BASELINE
    assert re.fullmatch(r"[0-9a-f]{40}", data["baseline_commit"])
    assert data["forms"] == list(FORMS)
    items = data["cases"]
    assert len(items) == 72
    assert [item["id"] for item in items] == [f"{skill}-{form}" for skill in SKILLS for form in FORMS]
    retained = [item for item in items if item["id"].split("-")[1] in "AB"]
    fingerprint = hashlib.sha256(json.dumps(retained, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert fingerprint == BASELINE_CASES_SHA256, "The original A/B case source and reasoning must remain intact"
    prior = json.loads((ROOT / "_reports/poker-beginner-baseline/tasks.json").read_text())
    prior_pairs = {(tuple(sorted(t["hero"])), tuple(sorted(t["board"]))) for t in prior["tasks"]}
    signatures = set()
    repair_sources = {}
    for item in items:
        case_id = item["id"]
        skill, form = case_id.split("-")
        assert item["skill"] == skill and form in FORMS
        assert item["lesson"] == LESSONS[SKILLS.index(skill)]
        assert all(isinstance(item[k], str) and item[k].strip() for k in ("title", "setup", "prompt", "misconception"))
        assert len(item["points"]) == 3 and all(isinstance(p, str) and p.strip() for p in item["points"])
        assert len(set(item["points"])) == 3
        if form not in "AB":
            assert isinstance(item["focus"], str) and 3 <= len(item["focus"].strip()) <= 100, case_id
            assert isinstance(item["design_note"], str) and len(item["design_note"].split()) >= 6
        hero, board = item["hero"], item["board"]
        assert len(hero) == 2 and len(board) in (0, 3, 5)
        cards = hero + board
        assert len(set(cards)) == len(cards)
        assert all(re.fullmatch(r"[2-9TJQKA][shdc]", c) for c in cards)
        signature = (tuple(sorted(hero)), tuple(sorted(board)))
        assert signature not in signatures and signature not in prior_pairs, case_id
        signatures.add(signature)
        assert item["repair"].startswith("/poker/" + item["lesson"] + "/#")
        assert item["repair"].split("#")[1] in REPAIRS[skill]
        assert len(item.get("point_repairs", [])) == 3
        extra = item.get("point_extra_repairs", [[], [], []])
        assert len(extra) == 3 and all(isinstance(links, list) for links in extra)
        for link in [item["repair"]] + item["point_repairs"] + [link for links in extra for link in links]:
            assert isinstance(link, str) and link.startswith("/poker/") and link.count("#") == 1
            path, anchor = link.split("#")
            lesson = path.rstrip("/").split("/")[-1]
            assert lesson in LESSONS + ["hand-rankings"]
            if lesson not in repair_sources:
                repair_sources[lesson] = (ROOT / "_source/poker" / (lesson + ".html")).read_text()
            assert 'id="' + anchor + '"' in repair_sources[lesson], (case_id, link)
        if board:
            assert tuple(item["expected_rank"]) == best(cards), case_id
        else:
            assert "expected_rank" not in item
        if "call" in item:
            check_action(item)
        if "full_raise" in item:
            raise_record = item["full_raise"]
            assert set(raise_record) == {"previous_total", "current_total", "last_full_increment", "minimum_total"}
            assert all(type(value) is int and value >= 0 for value in raise_record.values())
            assert raise_record["current_total"] == item["call"]["to"]
            assert raise_record["current_total"] - raise_record["previous_total"] == raise_record["last_full_increment"] > 0
            assert raise_record["minimum_total"] == raise_record["current_total"] + raise_record["last_full_increment"]
        if "action_order" in item:
            check_order(item)
        if "draw" in item:
            check_draw(item)
        if "river" in item:
            r = item["river"]
            assert set(r) == {"pot_before", "bet", "call", "paid", "after", "num", "den"}
            assert all(type(v) is int and v >= 0 for v in r.values())
            assert r["pot_before"] > 0 and r["bet"] > 0 and r["den"] > 0
            assert r["pot_before"] + r["bet"] + r["call"] == r["after"]
            assert r["bet"] == r["call"] and r["paid"] == 0
            assert Fraction(r["call"], r["after"]) == Fraction(r["num"], r["den"])
        if "candidates" in item:
            assert len(board) == 5 and 2 <= len(item["candidates"]) <= 4
            results = []
            candidate_sets = set()
            for opposing in item["candidates"]:
                assert len(opposing) == 2 and opposing[0] != opposing[1]
                assert all(re.fullmatch(r"[2-9TJQKA][shdc]", c) for c in opposing)
                pair = tuple(sorted(opposing))
                assert pair not in candidate_sets
                candidate_sets.add(pair)
                if any(c in cards for c in opposing):
                    results.append("impossible")
                else:
                    rival, own = best(opposing + board), best(cards)
                    results.append("stronger" if rival > own else "weaker" if rival < own else "tie")
            assert results == item["expected_comparisons"], (case_id, results)
        if "responses" in item:
            responses = item["responses"]
            assert item.get("context") == "checked_to_hero"
            assert len(responses) == len(item["candidates"])
            for n, response in enumerate(responses, 1):
                assert set(response) in ({"candidate"}, {"candidate", "action"})
                assert type(response["candidate"]) is int and response["candidate"] == n
                assert "action" not in response or response["action"] in ("call", "fold")
                assert item["expected_comparisons"][n-1] != "impossible"
        if form not in "AB":
            required = {"S1": ("call", "action"), "S2": ("action_order",),
                        "S3": ("expected_rank",), "S4": ("river",),
                        "S5": ("candidates",), "S6": ("candidates", "responses", "context")}
            assert all(field in item for field in required[skill]), case_id
        assert not item["misconception"].startswith("Mastered")
    for skill in SKILLS:
        assert len({item["focus"] for item in items if item["skill"] == skill and "focus" in item}) >= 6
    # Rendering is deterministic; every card, key, skill copy and review row must match source.
    spec = spec_from_file_location("transfer_packet_builder", FOLDER / "build_packet.py")
    builder = module_from_spec(spec)
    spec.loader.exec_module(builder)
    generated = builder.outputs(data)
    for name, expected in generated.items():
        path = FOLDER / name
        assert path.exists() and path.read_text(encoding="utf-8") == expected, name
    assert {p.name for p in (FOLDER / "cards").glob("*.md")} == {item["id"] + ".md" for item in items}
    assert {p.name for p in (FOLDER / "study").glob("*.md")} == {skill + ".md" for skill in SKILLS}
    for case in items:
        isolated = (FOLDER / "cards" / (case["id"] + ".md")).read_text()
        check_names(isolated, case)
        assert isolated.count("### ") == 1
        assert not any(point in isolated for point in case["points"])
        assert "<details>" not in isolated and "Computed high-hand vector" not in isolated
        if "design_note" in case:
            assert case["design_note"] not in isolated
    for name in ("self-study.md", *[f"study/{skill}.md" for skill in SKILLS]):
        body = (FOLDER / name).read_text()
        count = len(items) if name == "self-study.md" else 12
        assert body.count("<details>") == body.count("</details>") == count
    participant = (FOLDER / "participant-cards.md").read_text()
    assert "<details>" not in participant
    assert all(point not in participant for case in items for point in case["points"])
    protocol = (FOLDER / "protocol.md").read_text()
    assert all(case_id in protocol for case_id in ("S1-A", "S2-B", "S3-A", "S4-B", "S5-A", "S6-B"))
    assert "original A/B allocation" in protocol and "C–L" in protocol
    assert "new full private" in protocol and "No sessions have occurred" in protocol
    session = (FOLDER / "session-form.md").read_text()
    assert "Assigned case (S1-A through S6-L)" in session and "Consent status" in session
    assert "later paired" in session and "Assigned lesson seen: yes / no / unsure" in session
    for field in ("this exact case", "this case's answer key", "a similar problem"):
        assert re.search(r"Prior exposure to " + re.escape(field) + r": yes / no / unsure", session)
    for n in range(1, 4):
        assert f"Assisted reasoning point {n}:" in session
    summary = (FOLDER / "summary-form.md").read_text()
    for part in summary.split("### ")[1:]:
        rows = [line for line in part.splitlines() if line.startswith("| ")]
        assert len(rows) in (len(items)+2, len(items)*2+2)
        assert len({row.count("|") for row in rows}) == 1
    print("PASS: 72 draft cases; 12 retained A/B sources; cards, ranks, comparisons, calls, positions, draw completions, river fractions, repairs and separate views checked. Human review pending.")
    return len(items)


if __name__ == "__main__":
    check()
