#!/usr/bin/env python3
"""Summarize owner-exported Google Search Console CSVs entirely offline.

No network calls, third-party libraries, scheduled execution, or files written.
Results are PRIVATE traffic measurements, not material for the public site repo.
The Web search type and data freshness cannot be verified from CSV contents.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


SECTIONS = ("technology", "poker", "living_well", "creative", "other")
ALIAS = {
    "date": ("date", "dates", "day", "top dates"),
    "page": ("top pages", "page", "pages", "url", "landing page"),
    "query": ("top queries", "query", "queries", "search query"),
    "clicks": ("clicks",),
    "impressions": ("impressions",),
}
CHART_DATE_FORMATS = ("iso", "mdy", "dmy")


class ExportError(ValueError):
    """Input is not an unambiguous, usable Search Console export."""


def _normalize_header(value: str) -> str:
    return re.sub(r"[\s_-]+", " ", value.strip().casefold())


def _required_columns(fieldnames: list[str] | None, required: tuple[str, ...], path: Path) -> dict[str, str]:
    if not fieldnames:
        raise ExportError(f"{path.name}: missing CSV headers")
    by_name: dict[str, str] = {}
    for header in fieldnames:
        key = _normalize_header(header)
        if key in by_name:
            raise ExportError(f"{path.name}: duplicate CSV column {key!r}")
        by_name[key] = header
    selected: dict[str, str] = {}
    for key in required:
        matches = [by_name[name] for name in ALIAS[key] if name in by_name]
        if len(matches) != 1:
            raise ExportError(f"{path.name}: expected one {key!r} column, found {len(matches)}")
        selected[key] = matches[0]
    return selected


def _count(value: str | None, path: Path, row_number: int, field: str) -> int:
    raw = (value or "").strip()
    if not re.fullmatch(r"(?:0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)", raw):
        raise ExportError(f"{path.name}: invalid {field} at data row {row_number}")
    return int(raw.replace(",", ""))


def _read_export(path: Path, dimension: tuple[str, ...]) -> list[dict[str, str | int]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            keys = _required_columns(reader.fieldnames, (*dimension, "clicks", "impressions"), path)
            rows: list[dict[str, str | int]] = []
            for index, row in enumerate(reader, start=2):
                if None in row:
                    raise ExportError(f"{path.name}: extra columns on data row {index}")
                item: dict[str, str | int] = {}
                for field in dimension:
                    item[field] = (row[keys[field]] or "").strip()
                    if not item[field]:
                        raise ExportError(f"{path.name}: blank {field} on data row {index}")
                for field in ("clicks", "impressions"):
                    item[field] = _count(row[keys[field]], path, index, field)
                rows.append(item)
            return rows
    except (UnicodeError, OSError, csv.Error) as exc:
        raise ExportError(f"{path.name}: cannot read CSV ({type(exc).__name__})") from exc


def _section(page: str) -> str | None:
    """Accept this site's exact host only, never lookalikes or other domains."""
    try:
        url = urlsplit(page)
        if (url.scheme not in ("http", "https") or url.hostname != "nolankido.com"
                or url.username or url.password or url.port):
            return None
    except ValueError:
        return None
    for prefix, label in (("/technology/", "technology"), ("/poker/", "poker"),
                          ("/living-well/", "living_well"), ("/creative/", "creative")):
        if url.path == prefix[:-1] or url.path.startswith(prefix):
            return label
    return "other"


def _query_kind(query: str) -> tuple[bool, bool]:
    normalized = re.sub(r"[^a-z0-9]+", " ", query.casefold()).strip()
    person = bool(re.search(r"\bnolan(?: y)? kido\b|\bnolankido\b", normalized))
    tagline = bool(re.search(r"\bai works human decides\b", normalized))
    return person, tagline


def _chart_day(value: str, date_format: str, path: Path, row_number: int) -> date:
    """Interpret a chart date only in the format the owner explicitly selected."""
    if date_format == "iso":
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ExportError(f"{path.name}: expected YYYY-MM-DD at data row {row_number}")
        parts = value.split("-")
        year, month, day = (int(item) for item in parts)
    else:
        if not re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", value):
            raise ExportError(f"{path.name}: expected slash-separated {date_format} date at data row {row_number}")
        first, second, year = (int(item) for item in value.split("/"))
        month, day = (first, second) if date_format == "mdy" else (second, first)
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise ExportError(f"{path.name}: invalid {date_format} date at data row {row_number}") from exc


def _chart_summary(chart: Path | None, month: str, last_day: int, date_format: str) -> dict:
    """Accept property totals only from a complete, distinct daily chart export."""
    if chart is None:
        return {"provided": False, "date_format": None, "calendar_days_validated": False,
                "days": None, "clicks": None, "impressions": None}
    rows = _read_export(chart, ("date",))
    observed: set[str] = set()
    for index, row in enumerate(rows, start=2):
        day = _chart_day(str(row["date"]), date_format, chart, index).isoformat()
        if not day.startswith(month + "-"):
            raise ExportError(f"{chart.name}: date outside declared month at data row {index}")
        if day in observed:
            raise ExportError(f"{chart.name}: duplicate date on data row {index}")
        observed.add(day)
    expected = {f"{month}-{number:02d}" for number in range(1, last_day + 1)}
    if observed != expected:
        raise ExportError(f"{chart.name}: incomplete daily chart ({len(observed)} of {len(expected)} distinct dates)")
    return {"provided": True, "date_format": date_format, "calendar_days_validated": True,
            "days": len(rows),
            "clicks": sum(int(row["clicks"]) for row in rows),
            "impressions": sum(int(row["impressions"]) for row in rows)}


def summarize(month: str, pages: Path, queries: Path | None = None,
              query_pages: Path | None = None, chart: Path | None = None,
              chart_date_format: str = "iso") -> dict:
    if not re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", month):
        raise ExportError("--month must be YYYY-MM")
    year, month_number = map(int, month.split("-"))
    if year < 2000:
        raise ExportError("--month must be a valid Search Console reporting month")
    if chart_date_format not in CHART_DATE_FORMATS:
        raise ExportError("--chart-date-format must be iso, mdy or dmy")
    if chart is None and chart_date_format != "iso":
        raise ExportError("--chart-date-format requires --chart")
    _, last_day = calendar.monthrange(year, month_number)
    chart_totals = _chart_summary(chart, month, last_day, chart_date_format)
    page_rows = _read_export(pages, ("page",))
    query_rows = _read_export(queries, ("query",)) if queries is not None else None
    pair_rows = _read_export(query_pages, ("query", "page")) if query_pages is not None else None

    section_totals = {key: {"clicks": 0, "impressions": 0, "visible_rows": 0} for key in SECTIONS}
    excluded_pages = 0
    for row in page_rows:
        section = _section(str(row["page"]))
        if section is None:
            excluded_pages += 1
            continue
        section_totals[section]["clicks"] += int(row["clicks"])
        section_totals[section]["impressions"] += int(row["impressions"])
        section_totals[section]["visible_rows"] += 1
    if not page_rows:
        for totals in section_totals.values():
            totals["clicks"] = None
            totals["impressions"] = None

    brands: dict[str, int | None] = {"person_brand_visible_clicks": None,
                                    "tagline_visible_clicks": None}
    if query_rows:
        brands = {key: 0 for key in brands}
        for row in query_rows:
            person, tagline = _query_kind(str(row["query"]))
            if person:
                brands["person_brand_visible_clicks"] += int(row["clicks"])
            if tagline:
                brands["tagline_visible_clicks"] += int(row["clicks"])

    nonbrand_tech: int | None = None
    excluded_pairs = 0
    if pair_rows:
        nonbrand_tech = 0
        for row in pair_rows:
            section = _section(str(row["page"]))
            if section is None:
                excluded_pairs += 1
                continue
            person, tagline = _query_kind(str(row["query"]))
            if section == "technology" and not (person or tagline):
                nonbrand_tech += int(row["clicks"])

    return {
        "declared_month": month,
        "declared_window": {"start": f"{month}-01", "end": f"{month}-{last_day:02d}"},
        "search_type_declared": "web",
        "export_date_range_verified": False,
        "chart_export": chart_totals,
        "page_export": {"rows": len(page_rows), "outside_site_rows": excluded_pages,
                        "observed_section_totals": section_totals},
        "query_export": {"provided": query_rows is not None,
                         "visible_rows": len(query_rows) if query_rows is not None else None,
                         **brands},
        "query_page_export": {"provided": pair_rows is not None,
                              "visible_rows": len(pair_rows) if pair_rows is not None else None,
                              "outside_site_rows": excluded_pairs if pair_rows is not None else None,
                              "visible_nonbrand_technology_clicks": nonbrand_tech},
        "property_web_clicks": chart_totals["clicks"],
        "property_web_impressions": chart_totals["impressions"],
        "interpretation": [
            "PRIVATE measurements: do not commit input CSVs or this output to a public repository.",
            "The selected property, Search type, freshness, and page/query date ranges must be verified in Search Console.",
            "An optional Chart CSV must have one unique date per calendar day in the selected, explicit date format; this does not prove the data is settled.",
            "Page and query rows can be truncated or withheld; displayed aggregates are observed export rows, not sitewide totals.",
            "Visible query clicks exclude hidden queries and are lower bounds; brand and tagline groups may overlap.",
            "Query+Page metrics require a combined export. Separate Queries and Pages exports cannot be joined.",
            "Property Web totals come only from a complete supplied daily chart, never summed page rows; otherwise they remain null.",
            "Values shown as unavailable in Search Console may export as zeros; verify availability at the source.",
            "No actual search uplift, indexing, AI citation, or causal change is inferred.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Reporting month YYYY-MM, verified separately in GSC")
    parser.add_argument("--pages", type=Path, required=True, help="Private GSC Web Search 'Pages.csv' export")
    parser.add_argument("--queries", type=Path, help="Optional private GSC 'Queries.csv' export")
    parser.add_argument("--query-pages", type=Path, help="Optional combined Query+Page CSV (must contain both dimensions)")
    parser.add_argument("--chart", type=Path, help="Optional private complete daily GSC Chart/Dates CSV")
    parser.add_argument("--chart-date-format", choices=CHART_DATE_FORMATS, default="iso",
                        help="Date format in --chart: iso (YYYY-MM-DD), mdy (M/D/YYYY) or dmy (D/M/YYYY); default iso")
    args = parser.parse_args(argv)
    try:
        data = summarize(args.month, args.pages, args.queries, args.query_pages,
                         args.chart, args.chart_date_format)
    except ExportError as exc:
        print(f"Export error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
