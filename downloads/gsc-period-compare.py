#!/usr/bin/env python3
"""Compare two private gsc-monthly-local-audit.py JSON summaries, entirely offline.

Python standard library only. This tool does not access Search Console or verify the
property, filters, date range, data freshness, or completeness of the original export.
Never commit real input/output to a public repository.
"""
from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date
from pathlib import Path

SECTIONS = ("technology", "poker", "living_well", "creative", "other")
SITE_PROPERTIES = ("sc-domain:nolankido.com", "https://nolankido.com/")

class ComparisonError(ValueError):
    """A summary cannot support the proposed comparison."""


def count(value, name):
    if type(value) is not int or value < 0:
        raise ComparisonError(f"{name}: expected a nonnegative integer")
    return value


def nullable_count(value, name):
    return None if value is None else count(value, name)


def object_at(data, key):
    obj = data.get(key)
    if not isinstance(obj, dict):
        raise ComparisonError(f"missing or invalid {key}")
    return obj


def month_days(month):
    if not isinstance(month, str) or not re.fullmatch(r"20\d{2}-(?:0[1-9]|1[0-2])", month):
        raise ComparisonError("declared_month must be YYYY-MM, year 2000-2099")
    year, number = (int(x) for x in month.split("-"))
    last = calendar.monthrange(year, number)[1]
    return last, date(year, number, last)


def read_summary(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"cannot read summary {path.name}: {type(exc).__name__}") from exc
    if not isinstance(data, dict):
        raise ComparisonError("monthly summary must be a JSON object")
    month = data.get("declared_month")
    days, end = month_days(month)
    window = object_at(data, "declared_window")
    if window.get("start") != month + "-01" or window.get("end") != end.isoformat():
        raise ComparisonError(f"{month}: declared window must cover the complete month")
    if data.get("search_type_declared") != "web":
        raise ComparisonError(f"{month}: expected declared Web search type")
    if type(data.get("export_date_range_verified")) is not bool:
        raise ComparisonError(f"{month}: missing export verification status")
    # Source-export truth cannot be proven by a claim in the summary JSON.
    chart = object_at(data, "chart_export")
    if type(chart.get("provided")) is not bool or type(chart.get("calendar_days_validated")) is not bool:
        raise ComparisonError(f"{month}: invalid chart status")
    clicks = nullable_count(data.get("property_web_clicks"), f"{month} Web clicks")
    impressions = nullable_count(data.get("property_web_impressions"), f"{month} Web impressions")
    if chart["provided"]:
        if not chart["calendar_days_validated"] or chart.get("days") != days:
            raise ComparisonError(f"{month}: chart dates not validated for the full month")
        if clicks is None or impressions is None or chart.get("clicks") != clicks or chart.get("impressions") != impressions:
            raise ComparisonError(f"{month}: chart and Web totals disagree")
    elif (chart["calendar_days_validated"] or clicks is not None or impressions is not None):
        raise ComparisonError(f"{month}: property Web totals must be null without a complete daily chart")
    pages = object_at(data, "page_export")
    page_rows = count(pages.get("rows"), f"{month} page rows")
    excluded = count(pages.get("outside_site_rows"), f"{month} excluded page rows")
    if excluded > page_rows:
        raise ComparisonError(f"{month}: excluded pages exceed exported pages")
    sections = pages.get("observed_section_totals")
    if not isinstance(sections, dict) or set(sections) != set(SECTIONS):
        raise ComparisonError(f"{month}: invalid section totals")
    for section in SECTIONS:
        record = sections[section]
        if not isinstance(record, dict):
            raise ComparisonError(f"{month}: invalid {section} section")
        count(record.get("visible_rows"), f"{month} {section} visible rows")
        for field in ("clicks", "impressions"):
            val = nullable_count(record.get(field), f"{month} {section} {field}")
            if (page_rows == 0) != (val is None):
                raise ComparisonError(f"{month}: empty Pages export must not yield section totals")
    if sum(sections[x]["visible_rows"] for x in SECTIONS) != page_rows - excluded:
        raise ComparisonError(f"{month}: page row classifications do not reconcile")
    queries = object_at(data, "query_export")
    pairs = object_at(data, "query_page_export")
    for name, block, fields in (
        ("query", queries, ("person_brand_visible_clicks", "tagline_visible_clicks")),
        ("query_page", pairs, ("visible_nonbrand_technology_clicks",)),
    ):
        if type(block.get("provided")) is not bool:
            raise ComparisonError(f"{month}: missing {name} export status")
        rows = block.get("visible_rows")
        if block["provided"]:
            count(rows, f"{month} {name} rows")
        elif rows is not None:
            raise ComparisonError(f"{month}: rows present without {name} export")
        for field in fields:
            value = nullable_count(block.get(field), f"{month} {field}")
            # Existing monthly tool reports null for an absent or empty query export.
            if (rows is None or rows == 0) and value is not None:
                raise ComparisonError(f"{month}: {field} cannot be known without rows")
            if rows and value is None:
                raise ComparisonError(f"{month}: {field} missing from populated export")
    # No site URLs or search terms are copied to the output.
    observed_pages = page_rows - excluded
    return {
        "month": month, "days": days, "end": end,
        "values": {
            "property_web_clicks": clicks,
            "property_web_impressions": impressions,
            "technology_exported_page_clicks": sections["technology"]["clicks"] if observed_pages else None,
            "poker_exported_page_clicks": sections["poker"]["clicks"] if observed_pages else None,
            "visible_person_name_query_clicks": queries["person_brand_visible_clicks"],
            "visible_tagline_query_clicks": queries["tagline_visible_clicks"],
            "visible_nonbrand_technology_query_page_clicks": pairs["visible_nonbrand_technology_clicks"],
        },
        "page_rows": page_rows,
        "excluded_page_rows": excluded,
        "query_rows": queries["visible_rows"],
        "query_page_rows": pairs["visible_rows"],
    }


def compare(baseline, followup, property_name, same_filters_confirmed, as_of=None):
    if property_name not in SITE_PROPERTIES:
        raise ComparisonError("--property must name the site's exact Search Console property")
    if not same_filters_confirmed:
        raise ComparisonError("confirm matching property, Web search type, countries, devices and filters with --same-filters-confirmed")
    if baseline["month"] >= followup["month"]:
        raise ComparisonError("baseline month must precede follow-up month")
    today = as_of or date.today()
    if baseline["end"] >= today or followup["end"] >= today:
        raise ComparisonError("both comparison months must have ended before the comparison date")
    results = {}
    for name, before in baseline["values"].items():
        after = followup["values"][name]
        delta = None if before is None or after is None else after - before
        percent = None if delta is None or before == 0 else round(delta * 100 / before, 2)
        results[name] = {"baseline": before, "followup": after, "change": delta,
                         "change_pct": percent,
                         "status": "unavailable" if delta is None else ("no_percent_baseline" if before == 0 else "observed_export_comparison")}
    for metric in ("property_web_clicks", "property_web_impressions"):
        item = results[metric]
        before, after = item["baseline"], item["followup"]
        item["baseline_per_day"] = None if before is None else round(before / baseline["days"], 4)
        item["followup_per_day"] = None if after is None else round(after / followup["days"], 4)
    return {
        "scope": "private GSC Web exports; no live Search Console query performed",
        "property_declared_by_operator": property_name,
        "property_and_filters_verified_by_tool": False,
        "same_filters_confirmed_by_operator": True,
        "baseline_month": baseline["month"], "followup_month": followup["month"],
        "calendar_days": {"baseline": baseline["days"], "followup": followup["days"]},
        "metrics": results,
        "limitations": [
            "Private summaries and output must never be committed to a public repo or pasted into a public issue.",
            "Property, Web filter, country/device, date selection, export completeness and data freshness cannot be verified from these JSON summaries.",
            "Property totals require validated daily Chart rows; Pages tables are truncated or differently aggregated and are only observed export rows.",
            "Visible query counts exclude hidden queries; brand and tagline metrics may overlap; a displayed zero is not proof of total absence.",
            "Do not infer AI Overview, AI Mode, ChatGPT citations, indexation, conversions or causality from Search Console Web metrics.",
            "Compare equal seasonality and month length before interpreting changes; no improvement is attributed to a site release.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True, help="Private monthly JSON from the existing GSC summarizer")
    parser.add_argument("--followup", type=Path, required=True, help="Another private monthly JSON from the existing GSC summarizer")
    parser.add_argument("--property", choices=SITE_PROPERTIES, required=True, help="Operator-confirmed Search Console property")
    parser.add_argument("--same-filters-confirmed", action="store_true", help="Confirm matching Web search type, property, country/device and other filters in the UI")
    args = parser.parse_args(argv)
    try:
        result = compare(read_summary(args.baseline), read_summary(args.followup), args.property, args.same_filters_confirmed)
    except ComparisonError as exc:
        print(f"Comparison error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
