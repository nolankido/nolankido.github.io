"""Render the draft practice bank from one source. No learner data or network."""
from pathlib import Path
import argparse
import json

FOLDER = Path(__file__).resolve().parent
SKILL_LABELS = {
    "S1": "Calls and available actions",
    "S2": "Position and turn order",
    "S3": "Made hands and draws",
    "S4": "River price and expected pot share",
    "S5": "Known cards and opposing ranges",
    "S6": "Betting purpose and checking",
}
RANK_NAMES = dict(zip("23456789TJQKA", (
    "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "jack", "queen", "king", "ace")))
SUIT_NAMES = {"s": "spades", "h": "hearts", "d": "diamonds", "c": "clubs"}
PRIVATE_NOTE = "**Private note:** First explanation: ______. Confidence: sure / partly sure / guessing. Prompt or help received: ______. Unclear step: ______."


def names(cards):
    return "; ".join(RANK_NAMES[c[0]] + " of " + SUIT_NAMES[c[1]] for c in cards)


def text(lines):
    return "\n\n".join(lines).rstrip() + "\n"


def question(case):
    lines = ["### " + case["id"] + ": " + case["title"], case["setup"],
             "Private cards: " + ", ".join(case["hero"]) + ". Shared cards: " +
             (", ".join(case["board"]) or case.get("board_note", "not dealt")) + "."]
    card_line = "Private card names: " + names(case["hero"]) + "."
    if case["board"]:
        card_line += " Shared card names: " + names(case["board"]) + "."
    lines.append(card_line)
    for n, cards in enumerate(case.get("candidates", []), 1):
        lines.append(f"Candidate {n}: " + ", ".join(cards) + ".\n\n" +
                     f"Candidate {n} card names: " + names(cards) + ".")
    lines.extend(["**Try without opening an answer:** " + case["prompt"], PRIVATE_NOTE])
    return lines


def repairs(case, facilitator=False):
    lines = ["**Repair by reasoning point:**"]
    label = "Point {} repair" if facilitator else "Revisit point {}"
    lines.append("\n".join(f"{n}. [{label.format(n)}](https://nolankido.com{link})"
                           for n, link in enumerate(case["point_repairs"], 1)))
    for n, links in enumerate(case.get("point_extra_repairs", [[], [], []]), 1):
        for link in links:
            title = "Compare the best five cards" if link.startswith("/poker/hand-rankings/") else "Related lesson explanation"
            lines.append(f"Additional point {n} repair: [{title}](https://nolankido.com{link}).")
    return lines


def reasoning(case, facilitator=False):
    lines = [f"{n}. {point}" for n, point in enumerate(case["points"], 1)]
    if facilitator:
        if "expected_rank" in case:
            lines.append("Computed high-hand vector (category 0 to 8, ranks 2 to 14): `" +
                         json.dumps(case["expected_rank"], separators=(",", ":")) + "`.")
        if "call" in case:
            c = case["call"]
            lines.append(f"Call: {c['to']} minus {c['paid']} already paid = {c['answer']} more.")
        if "river" in case:
            r = case["river"]
            lines.append(f"River arithmetic: {r['pot_before']} + {r['bet']} + {r['call']} = {r['after']}; additional call / final pot = {r['num']}/{r['den']}.")
        if "expected_comparisons" in case:
            lines.append("Candidate evidence, each opponent compared with the learner's best five: " +
                         "; ".join(f"{n}: {value}" for n, value in enumerate(case["expected_comparisons"], 1)) + ".")
        if "design_note" in case:
            lines.append("**Author's design note, for review:** " + case["design_note"])
    lines.extend(["**Likely misconception:** " + case["misconception"],
                  "**Starting repair:** https://nolankido.com" + case["repair"],
                  *repairs(case, facilitator)])
    return lines


def study_body(cases, title, prefix=""):
    lines = ["# " + title,
             "**Draft for qualified teaching review.** These fictional exercises are available for private self-study. They have not established learning gains or equivalent difficulty. Open one question, explain your answer, then open its reasoning. No monetary stakes, account or submission is needed.",
             "This file contains answers in closed disclosures. A supervised independent attempt uses an isolated learner card instead."]
    if prefix:
        lines.append("[All six skills](../self-study.md)")
    else:
        lines.append("## Choose one skill")
        lines.extend(f"- [{label}: 12 cases](study/{skill}.md)" for skill, label in SKILL_LABELS.items())
        lines.append("The complete 72-case copy follows. The smaller skill files contain the same questions and answers.")
    for case in cases:
        lines.extend([f'<a id="{case["id"].lower()}"></a>', *question(case),
                      "<details>\n<summary>Compare your explanation</summary>\n\n" +
                      text(reasoning(case)) + "\n</details>"])
    return text(lines)


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                       "| " + " | ".join("---" for _ in headers) + " |",
                       *("| " + " | ".join(row) + " |" for row in rows)])


def summary(cases):
    ids = [case["id"] for case in cases]
    lines = ["# Blank transfer-practice observations: private aggregate",
             "**Template only. No sessions or results have been reported.** Make a private copy. Bind observations to the actual course release, this packet's commit, the exact selected cases and the qualified review decision. The original T1–T6 baseline, original A/B allocation and expanded bank are separate scopes. Do not combine their observations.",
             "Course release commit: ______  Transfer packet commit: ______  Human reviewer outcome: ______",
             "Actual dates/time zone: ______  Consent and storage process (private): ______",
             "Planned recruited: ______  Actual consented: ______  Completed/partial/withdrawn: ______",
             "Select only the rows used in the approved session plan. Unused blank rows are not zero outcomes.",
             "### Attempt counts",
             table(["Case", "Assigned", "Independent attempted", "Independent explanation supported (all three)",
                    "Assisted attempted (any help)", "Assisted explanation supported (all three)",
                    "Hint/repair used", "Incomplete or skipped", "Notes without identifiers"],
                   [[case_id] + [""] * 8 for case_id in ids]),
             "### Exposure and lesson counts",
             table(["Case", "Prior exact-case exposure (yes / no / unsure)",
                    "Prior answer-key exposure (yes / no / unsure)",
                    "Prior similar-problem exposure (yes / no / unsure)",
                    "Assigned lesson seen (yes / no / unsure)", "Actual lesson/revision and counts (or unknown)"],
                   [[case_id] + [""] * 5 for case_id in ids]),
             "### Time since learning",
             "For each exact case retain every actual elapsed interval and its count, plus unknown and not-applicable counts. Use another row when needed; do not combine unlike delays into one result.",
             table(["Case", "Exact elapsed interval(s) and count(s)", "Unknown interval count", "Lesson not seen / not applicable count"],
                   [[case_id] + [""] * 3 for case_id in ids]),
             "### Reasoning-point outcomes by phase",
             "In each point cell record separate raw counts as supported / error / not demonstrated / not attempted. Preserve all three points for both phases; these counts do not replace the all-three totals.",
             table(["Case", "Phase", "Point 1 counts", "Point 2 counts", "Point 3 counts"],
                   [[case_id, phase, "", "", ""] for case_id in ids for phase in ("independent", "assisted")]),
             "Record yes / no / unsure separately for the exact case, answer key and similar problem. Never infer one exposure field from another. Missing responses remain missing.",
             "Any attempt after prompt repetition, navigation help, a hint or a repair is assisted. Independent and assisted counts are overlapping, so do not add them as distinct people. Keep first and later attempts in separate tables with their case IDs and exact intervals. A larger bank does not make different forms equivalent or unfamiliar.",
             "Observed errors and exact repairs: ______  Ambiguous items and review decisions: ______",
             "Missing, withdrawn or incomplete observations: ______  Proposed changes from actual evidence: ______",
             "**Interpretation:** This qualitative template cannot establish population success rates, equivalent forms, causal learning gains, retention or optimal poker play. Blank cells do not indicate zero successes or failures."]
    return text(lines)


def review(cases):
    return text(["# Blank qualified teaching review: expanded practice bank",
                 "**Draft. No reviewer acceptance or learner observations are recorded here.** Review the exact packet commit and each selected case. Mechanical checks are separate from teaching judgment.",
                 "Reviewer and relevant qualification, recorded privately: ______  Review date: ______",
                 "Packet commit: ______  Course teaching revision: ______  Reviewed scope: ______",
                 table(["Case", "Cards and arithmetic", "Prompt clarity", "Reasoning and repairs", "Teaching use", "Required changes"],
                       [[case["id"]] + ["unreviewed"] * 4 + [""] for case in cases]),
                 "Inspect the isolated question before opening the key. Check answer cues, assumed vocabulary, missing information, legal actions, every requested reasoning point, precise repairs and accessibility of card names. A list of possible hands does not establish frequencies. Scope acceptance to the reviewed cases; partial review does not approve the whole bank.",
                 "**Outcome (not prefilled):** unreviewed / accept / revise / block. Signed decision retained privately: ______. Open issues and resolution commit: ______.",
                 "This does not approve the underlying course unless a separate review says so. Actual learner sessions, calibrated difficulty and retention outcomes remain unestablished."])


def outputs(data):
    cases = data["cases"]
    result = {}
    participant = ["# Facilitator index of learner questions",
                   "**Draft fictional exercises.** Copy or open only the assigned isolated case for an independent attempt. This combined file exposes other questions and is intended for selection, not a participant-controlled session. Answers are in a separate key."]
    key = ["# Facilitator-only reasoning key and misconception map",
           "**Draft, not reviewed or calibrated.** All scenarios and holdings are fictional. This public key contains answers. Ask about prior exposure and show it only after an independent explanation. The three proposed reasoning points are qualitative review criteria, not a mastery grade."]
    for case in cases:
        result[f"cards/{case['id']}.md"] = text([
            "# Poker Foundations transfer task " + case["id"],
            "**Draft for qualified review. One fictional case only.** This card contains no answer or other case. For a supervised session, use the exact reviewer-approved case and record previous exposure. No gambling account or wager is needed.",
            *question(case)])
        participant.extend(question(case))
        key.extend([f'<a id="{case["id"].lower()}"></a>',
                    "### " + case["id"] + ": " + case["title"], *reasoning(case, True)])
    result["participant-cards.md"] = text(participant)
    result["facilitator-key.md"] = text(key)
    result["self-study.md"] = study_body(cases, "Poker Foundations: 72 practice cases")
    for skill, label in SKILL_LABELS.items():
        result[f"study/{skill}.md"] = study_body([c for c in cases if c["skill"] == skill], label, "../")
    index = ["# Practice-bank coverage and selection",
             "**Instructor and reviewer index. Contains design intentions that can cue answers.** Give a learner only the selected individual card. The 72 cases comprise the retained 12 A/B cases and 60 additional C–L cases. These labels identify content coverage, not measured difficulty, calibrated forms or proven unfamiliarity."]
    for skill, label in SKILL_LABELS.items():
        group = [case for case in cases if case["skill"] == skill]
        index.extend(["## " + skill + ": " + label,
                      table(["Case", "Question", "Authored focus", "Review note"], [
                          [f"[{case['id']}](cards/{case['id']}.md)", case["title"],
                           case.get("focus", "retained A/B situation"),
                           case.get("design_note", "Original prompt and key retained from PR #107.")]
                          for case in group])])
    result["coverage.md"] = text(index)
    result["review-form.md"] = review(cases)
    result["summary-form.md"] = summary(cases)
    return result


def build(check=False, folder=FOLDER):
    data = json.loads((folder / "cases.json").read_text(encoding="utf-8"))
    rendered = outputs(data)
    for name, content in rendered.items():
        path = folder / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise AssertionError("Practice output differs from source: " + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    for subfolder in ("cards", "study"):
        actual = {p.relative_to(folder).as_posix() for p in (folder / subfolder).glob("*.md")}
        expected = {p for p in rendered if p.startswith(subfolder + "/")}
        if actual != expected:
            raise AssertionError("Unexpected practice output files in " + subfolder)
    print(f"PASS: {len(data['cases'])} cases and {len(rendered)} deterministic practice outputs {'checked' if check else 'rendered'}.")
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    build(parser.parse_args().check)
