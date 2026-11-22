#!/usr/bin/env python3
"""Audit PBG-06's editorial beginner question-to-page routing, without a network.

This checker verifies published website routes and source-backed reader choices.
The prompts are editorial hypotheses, not actual Google search queries,
observed search volume, rankings, traffic or assistant citations.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://nolankido.com"
MAP = "_reports/poker-book-growth/pbg-06-intent-to-canonical-map-2026-11-22.json"
COURSES = "_source/poker/poker-books-and-courses.html"
PUBLIC = "poker/poker-books-and-courses/index.html"
FREE_ROUTES = (
    "/poker/holdem-basics/",
    "/poker/starting-hand-decisions/",
    "/poker/poker-math-reference/",
    "/poker/free-poker-learning-path/",
    "/poker/first-live-tournament/",
)
EXPECTED_OWNERS = {
    "beginner-course": "/poker/free-poker-learning-path/",
    "rules-hand-flow": "/poker/holdem-basics/",
    "pot-odds-math": "/poker/poker-math-reference/",
    "book-course-selection": "/poker/poker-books-and-courses/",
    "nolan-book-navigation": "/books/how-to-play-no-limit-texas-holdem/",
    "tournament-preparation": "/poker/first-live-tournament/",
    "comprehensive-reference": "/poker/no-limit-holdem-guide/",
}
OBSERVED_FIELDS = ("gsc_impressions", "gsc_clicks", "search_volume",
                   "average_rank", "bing_clicks", "assistant_citation_rate")


class LinkReader(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.feed(source)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def comparison_choice(source: str) -> str:
    match = re.search(
        r'<p><strong>Use the exact free answer first:</strong>(.*?)</p>',
        source, re.S)
    if not match or source.count("Use the exact free answer first:") != 1:
        raise ValueError("Expected exactly one free-answer chooser")
    return match.group(0)


def validate_data(data: object) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return ["Intent map must be a JSON object"]
    if (data.get("schema_version") != 1 or data.get("turn") != "PBG-06"
            or data.get("reviewed_on") != "2026-11-22"):
        errors.append("Unexpected map version, turn or review date")
    measured = data.get("measurement")
    if (not isinstance(measured, dict)
            or measured.get("status") != "not_collected"
            or any(measured.get(key, "_missing") is not None for key in OBSERVED_FIELDS)):
        errors.append("Unverified search/citation metrics must remain null")
    clusters = data.get("clusters")
    if not isinstance(clusters, list) or len(clusters) != 18:
        return errors + ["Expected precisely 18 editorial intents"]
    seen_ids, seen_owner, seen_questions = set(), set(), set()
    allowed = {"learn", "reference", "practice", "prepare", "compare", "navigate"}
    for index, row in enumerate(clusters, 1):
        if not isinstance(row, dict):
            errors.append("Invalid intent record")
            continue
        key, primary, support = row.get("id"), row.get("primary"), row.get("secondary")
        if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9-]+", key) or key in seen_ids:
            errors.append("Duplicate or malformed intent id")
        else:
            seen_ids.add(key)
        if row.get("editorial_order") != index or row.get("intent_type") not in allowed:
            errors.append("Invalid editorial order or intent class")
        for value in (primary, support):
            if (not isinstance(value, str) or not re.fullmatch(r"/(?:poker|books)/[a-z0-9-]+/", value)
                    and value != "/poker/"):
                errors.append("Invalid first-party routing path")
        if primary == support or primary in seen_owner:
            errors.append("Duplicate primary ownership or self-referential secondary")
        seen_owner.add(primary)
        questions = row.get("candidate_questions")
        if (not isinstance(questions, list) or len(questions) != 2
                or any(not isinstance(q, str) or len(q) < 18 or not q.endswith("?")
                       for q in questions)):
            errors.append("Each intent needs two real editorial questions")
        else:
            for question in questions:
                key_text = " ".join(question.lower().split())
                if key_text in seen_questions:
                    errors.append("Repeated candidate question")
                seen_questions.add(key_text)
        if not isinstance(row.get("reason"), str) or len(row["reason"]) < 50:
            errors.append("Missing route-choice explanation")
        if row.get("priority") not in {"high", "medium", "low"}:
            errors.append("Invalid editorial priority")
        for field in ("measured_search_clicks", "measured_impressions",
                      "measured_ai_citations"):
            if row.get(field, "_missing") is not None:
                errors.append("Fabricated intent performance or missing null")
    for key, route in EXPECTED_OWNERS.items():
        found = next((row for row in clusters if isinstance(row, dict)
                      and row.get("id") == key), {})
        if found.get("primary") != route:
            errors.append("High-risk overlapping intent is not assigned its correct owner")
    return errors


def audit(root: Path = ROOT) -> dict:
    errors = []
    checked = []
    try:
        data = json.loads((root / MAP).read_text(encoding="utf-8"))
        errors.extend(validate_data(data))
        site_map = ET.parse(root / "sitemap.xml")
        locations = {
            node.text for node in site_map.findall(".//{*}url/{*}loc")
            if node.text
        }
        manifest = json.loads((root / "_source/pages.json").read_text(encoding="utf-8"))
        routes = {page["path"] for page in manifest}
        unique_routes = set()
        if isinstance(data.get("clusters"), list):
            for row in data["clusters"]:
                if not isinstance(row, dict):
                    continue
                for target in ("primary", "secondary"):
                    route = row.get(target)
                    if isinstance(route, str) and route.startswith("/"):
                        unique_routes.add(route)
        for route in sorted(unique_routes):
            path = root / route.lstrip("/") / "index.html"
            valid = False
            try:
                page = path.read_text(encoding="utf-8")
                canonical = ORIGIN + route
                valid = (page.count('<link rel="canonical" href="' + canonical + '">') == 1
                         and len(re.findall(r"<h1\b", page)) == 1
                         and canonical in locations
                         and ('content="noindex' not in page.lower())
                         and (route in routes or route == "/books/how-to-play-no-limit-texas-holdem/"))
            except (OSError, UnicodeError):
                valid = False
            if not valid:
                errors.append("Missing or noncanonical primary/support URL: " + route)
            checked.append({"route": route, "source_canonical_present": valid})
        source = (root / COURSES).read_text(encoding="utf-8")
        public = (root / PUBLIC).read_text(encoding="utf-8")
        selected = comparison_choice(source)
        if selected != comparison_choice(public):
            errors.append("Routing chooser differs between source and public copy")
        if LinkReader(selected).links != list(FREE_ROUTES):
            errors.append("Book comparison must route to exactly five distinct free answers")
        book = "/books/how-to-play-no-limit-texas-holdem/"
        if (source.count('href="' + book + '"') != 1
                or source.count('href="' + book + '#poker-book-first-exercise"') != 1
                or public.count('href="' + book + '"') != 1
                or public.count('href="' + book + '#poker-book-first-exercise"') != 1):
            errors.append("Existing author-book route and free sample must be retained once")
        if "not an independent review" not in public.lower():
            errors.append("Disclosure of author ownership lost")
        if "data-umami-event=" in selected or "amazon.com" in selected:
            errors.append("Free route must not track or send to a retailer")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        errors.append("Audit input malformed or missing: " + type(exc).__name__)
    return {
        "status": "pass" if not errors else "fail",
        "turn": "PBG-06",
        "intent_count": len(data.get("clusters", [])) if "data" in locals() and isinstance(data, dict) else None,
        "checked_routes": checked,
        "private_search_data": None,
        "measured_rankings": None,
        "observed_ai_citations": None,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    result = audit(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
