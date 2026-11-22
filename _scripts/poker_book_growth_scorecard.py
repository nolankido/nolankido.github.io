#!/usr/bin/env python3
"""Summarize private book-link click counts without networking or saving files.

This utility never calls Umami. Its optional input is an operator-checked,
aggregate-only JSON document stored outside the public repository.
It does not estimate rankings, Kindle orders, unique purchasers, or attribution.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

PAGES = (
    "/books/",
    "/books/how-to-play-no-limit-texas-holdem/",
    "/books/one-workflow-at-a-time/",
)
EVENTS = {
    "poker-book-kindle-amazon-click": ("books-catalog", "book-page-hero"),
    "one-workflow-kindle-amazon-click": ("books-catalog", "book-page-hero"),
    "ai-works-human-decides-kindle-amazon-click": ("books-catalog",),
}
BOOK_PAGE = "/books/how-to-play-no-limit-texas-holdem/"


class ScorecardError(ValueError):
    pass


def _count(value: object) -> bool:
    return type(value) is int and value >= 0


def validate(month: str, record: object | None) -> None:
    if not re.fullmatch(r"20\d\d-(?:0[1-9]|1[0-2])", month):
        raise ScorecardError("month must use YYYY-MM")
    if record is None:
        return
    if not isinstance(record, dict) or set(record) != {
            "month", "property", "period_verified", "pageviews", "events"}:
        raise ScorecardError("private input must contain only approved aggregate keys")
    if (record["month"] != month or record["property"] != "nolankido.com"
            or record["period_verified"] is not True):
        raise ScorecardError("private input requires a confirmed site and matching month")
    pages, events = record["pageviews"], record["events"]
    if (not isinstance(pages, dict) or set(pages) - set(PAGES)
            or any(not _count(v) for v in pages.values())):
        raise ScorecardError("invalid pageview aggregate")
    if not isinstance(events, dict) or set(events) - set(EVENTS):
        raise ScorecardError("unapproved event name")
    for event, by_source in events.items():
        if (not isinstance(by_source, dict) or set(by_source) - set(EVENTS[event])
                or any(not _count(v) for v in by_source.values())):
            raise ScorecardError("event source or count invalid")


def summarize(month: str, record: dict | None = None) -> dict:
    validate(month, record)
    pages = record["pageviews"] if record is not None else {}
    events = record["events"] if record is not None else {}
    views = {name: pages.get(name) for name in PAGES}
    breakdown = {name: {source: events.get(name, {}).get(source)
                        for source in sources} for name, sources in EVENTS.items()}
    poker = breakdown["poker-book-kindle-amazon-click"]
    # Do not sum partially known locations or infer event counts from an absent row.
    total_poker = (sum(poker.values()) if all(v is not None for v in poker.values())
                   else None)
    # This is events per pageview, not an individual visitor conversion rate.
    eligible = views[BOOK_PAGE]
    book_events = poker["book-page-hero"]
    rate = (round(100 * book_events / eligible, 2)
            if eligible is not None and eligible > 0 and book_events is not None
            else None)
    return {
        "month": month,
        "month_complete": month < date.today().strftime("%Y-%m"),
        "collection": ("operator_verified_aggregate" if record is not None
                       else "not_collected"),
        "pageviews": views,
        "amazon_click_events": breakdown,
        "poker_all_placements_total_when_complete": total_poker,
        "poker_book_page_events_per_100_pageviews": rate,
        "unmeasured": {
            "google_search_clicks": None,
            "google_search_impressions": None,
            "bing_search_clicks": None,
            "ai_cited_urls": None,
            "amazon_book_orders": None,
            "royalties": None,
        },
        "interpretation": [
            "A null count is uncollected, not zero.",
            "A reported 0 must come from an operator-verified complete source view.",
            "Events count clicks, not Amazon landing visits or purchases.",
            "Repeated link clicks can make events per 100 pageviews exceed 100.",
            "Pageview and event report filters must use the same property and month.",
            "Source verification and period_verified are operator attestations, not remote account checks.",
            "Store private inputs and filled outputs outside the public GitHub repository.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Month YYYY-MM")
    parser.add_argument("--umami-json", type=Path, help="Optional PRIVATE aggregate-only JSON")
    args = parser.parse_args(argv)
    try:
        record = None
        if args.umami_json is not None:
            record = json.loads(args.umami_json.read_text(encoding="utf-8"))
        report = summarize(args.month, record)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        print("Book baseline input invalid or unavailable; no private values exposed", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
