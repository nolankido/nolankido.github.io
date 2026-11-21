#!/usr/bin/env python3
"""Combine private NolanKido visibility observations without network or disk writes.

All source input stays on the operator's computer. Print only aggregate counts,
never search queries, page paths, referrer URLs, identifiers, or source paths.
"""
from __future__ import annotations

import argparse
from datetime import date
import importlib.util
import json
from pathlib import Path
import re
import sys

ORIGIN = "https://nolankido.com"
GSC_PROPERTIES = {"sc-domain:nolankido.com", "https://nolankido.com/"}
SOURCES = {
    "gsc_ai_search_impressions": GSC_PROPERTIES,
    "gsc_ai_discover_impressions": GSC_PROPERTIES,
    "bing_ai_citations": {"https://nolankido.com/", "https://nolankido.com"},
    "umami_ai_referral_pageviews": {"nolankido.com"},
}
WEB_METRICS = ("gsc_web_clicks", "gsc_web_impressions", "technology_exported_page_clicks")


class IntakeError(ValueError):
    pass


def count(value: object) -> bool:
    return type(value) is int and value >= 0


def report_month(month: str) -> None:
    if not re.fullmatch(r"20\d\d-(?:0[1-9]|1[0-2])", month):
        raise IntakeError("month must be YYYY-MM")
    year, mon = map(int, month.split("-"))
    if date(year, mon, 1) > date.today().replace(day=1):
        raise IntakeError("future reporting month is not valid")


def read_dashboard(path: Path | None, month: str) -> dict:
    if path is None:
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise IntakeError("cannot read valid dashboard JSON") from exc
    if not isinstance(obj, dict) or set(obj) != {"month", "metrics"} or obj["month"] != month:
        raise IntakeError("dashboard JSON month or keys do not match")
    metrics = obj["metrics"]
    if not isinstance(metrics, dict) or set(metrics) - set(SOURCES):
        raise IntakeError("dashboard metric keys are invalid")
    for name, item in metrics.items():
        if not isinstance(item, dict) or item.get("status") not in {"observed", "unavailable"}:
            raise IntakeError("dashboard metric status must be observed or unavailable")
        if item["status"] == "unavailable":
            if set(item) != {"status"}:
                raise IntakeError("unavailable dashboard metric cannot have a value")
            continue
        if (set(item) != {"status", "value", "property", "period_verified"}
                or not count(item["value"])
                or item["property"] not in SOURCES[name]
                or item["period_verified"] is not True):
            raise IntakeError("observed dashboard metrics require validated count, property and period confirmation")
    return metrics


def read_gsc(path: Path | None, month: str) -> dict | None:
    if path is None:
        return None
    # Reuse the site's existing strict local Search Console export verifier.
    module_path = Path(__file__).with_name("gsc-period-compare.py")
    spec = importlib.util.spec_from_file_location("gsc_period_compare", module_path)
    if spec is None or spec.loader is None:
        raise IntakeError("required GSC comparator is missing")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        parsed = module.read_summary(path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise IntakeError("GSC summary failed strict validation") from exc
    if parsed["month"] != month:
        raise IntakeError("GSC summary month does not match")
    return parsed


def make_scorecard(month: str, dashboard: dict, gsc: dict | None,
                   gsc_property: str | None, gsc_filters_confirmed: bool) -> dict:
    report_month(month)
    if gsc_property is not None and gsc_property not in GSC_PROPERTIES:
        raise IntakeError("GSC property must name the site's exact verified property")
    if gsc_filters_confirmed and (gsc is None or gsc_property is None):
        raise IntakeError("cannot confirm GSC filters without a summary and property")
    if gsc is not None and (gsc_property is None or gsc["month"] != month):
        raise IntakeError("GSC summary and named property are required and must match month")
    out = {}
    for name in WEB_METRICS:
        raw = None
        if gsc is not None:
            key = {"gsc_web_clicks": "property_web_clicks",
                   "gsc_web_impressions": "property_web_impressions",
                   "technology_exported_page_clicks": "technology_exported_page_clicks"}[name]
            raw = gsc["values"].get(key)
            if raw is not None and not count(raw):
                raise IntakeError("invalid GSC aggregate count")
        status = "not_collected" if gsc is None else ("source_unconfirmed" if not gsc_filters_confirmed else
                    ("observed_export" if raw is not None else "not_available"))
        out[name] = {"value": raw if status == "observed_export" else None, "status": status}
    for name in SOURCES:
        item = dashboard.get(name)
        if item is None:
            out[name] = {"value": None, "status": "not_collected"}
        elif item["status"] == "unavailable":
            out[name] = {"value": None, "status": "report_unavailable"}
        else:
            out[name] = {"value": item["value"], "status": "observed_operator_confirmed"}
    return {
        "month": month, "site": ORIGIN,
        "metrics": out,
        "gsc_property_confirmed_by_operator": gsc_property if gsc_filters_confirmed else None,
        "tool_checked_dashboard_authentication": False,
        "limitations": [
            "Private aggregates only. Never publish this scorecard or underlying exports to GitHub.",
            "A missing source is not a measured zero. A reported zero may originate in a dashboard export's unavailable display values.",
            "The operator must confirm original property, dates, reporting filters and data maturity.",
            "Google Search, Google AI Search, Google AI Discover, Bing AI citations and Umami referrer pageviews are separate series, never additive.",
            "A Bing AI citation is not a click or ranking. A referrer pageview is not a unique visitor or conversion.",
            "Technology page clicks come from exported page rows, not necessarily complete search demand.",
            "This report cannot establish indexing, a citation by ChatGPT, conversion value or causal lift.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Completed or current calendar month, YYYY-MM")
    parser.add_argument("--gsc-summary", type=Path, help="Private JSON from gsc-monthly-local-audit.py")
    parser.add_argument("--gsc-property", choices=sorted(GSC_PROPERTIES))
    parser.add_argument("--gsc-filters-confirmed", action="store_true",
                        help="Operator checked matching original GSC property, Web filter, month and data maturity")
    parser.add_argument("--dashboard-json", type=Path,
                        help="Private JSON of independently verified Google AI, Bing AI and Umami dashboard counts")
    args = parser.parse_args(argv)
    try:
        report_month(args.month)
        dashboard = read_dashboard(args.dashboard_json, args.month)
        gsc = read_gsc(args.gsc_summary, args.month)
        output = make_scorecard(args.month, dashboard, gsc, args.gsc_property,
                                args.gsc_filters_confirmed)
    except IntakeError as exc:
        print(f"Visibility intake error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
