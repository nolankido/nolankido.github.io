#!/usr/bin/env python3
"""Summarize owner-exported Google Search Console CSVs entirely offline.

No network calls, third-party libraries, scheduled execution, or files written.
Results are PRIVATE traffic measurements, not material for the public site repo.
The declared month and Web search type cannot be verified from CSV contents.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


SECTIONS = ("technology", "poker", "living_well", "creative", "other")
ALIAS = {
    "page": ("top pages", "page", "pages", "url", "landing page"),
    "query": ("top queries", "query", "queries", "search query"),
    "clicks": ("clicks",),
    "impressions": ("impressions",),
}


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


def summarize(month: str, pages: Path, queries: Path | None = None,
              query_pages: Path | None = None) -> dict:
    if not re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", month):
        raise ExportError("--month must be YYYY-MM")
    year, month_number = map(int, month.split("-"))
    if year < 2000:
        raise ExportError("--month must be a valid Search Console reporting month")
    _, last_day = calendar.monthrange(year, month_number)
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
        "page_export": {"rows": len(page_rows), "outside_site_rows": excluded_pages,
                        "observed_section_totals": section_totals},
        "query_export": {"provided": query_rows is not None,
                         "visible_rows": len(query_rows) if query_rows is not None else None,
                         **brands},
        "query_page_export": {"provided": pair_rows is not None,
                              "visible_rows": len(pair_rows) if pair_rows is not None else None,
                              "outside_site_rows": excluded_pairs if pair_rows is not None else None,
                              "visible_nonbrand_technology_clicks": nonbrand_tech},
        "property_web_clicks": None,
        "property_web_impressions": None,
        "interpretation": [
            "PRIVATE measurements: do not commit input CSVs or this output to a public repository.",
            "The month, Search type, and completeness of exports must be verified manually in Search Console.",
            "Page and query rows can be truncated or withheld; displayed aggregates are observed export rows, not sitewide totals.",
            "Visible query clicks exclude hidden queries and are lower bounds; brand and tagline groups may overlap.",
            "Query+Page metrics require a combined export. Separate Queries and Pages exports cannot be joined.",
            "Property Web clicks/impressions require the GSC chart totals; never infer them from page rows.",
            "No actual search uplift, indexing, AI citation, or causal change is inferred.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Reporting month YYYY-MM, verified separately in GSC")
    parser.add_argument("--pages", type=Path, required=True, help="Private GSC Web Search 'Pages.csv' export")
    parser.add_argument("--queries", type=Path, help="Optional private GSC 'Queries.csv' export")
    parser.add_argument("--query-pages", type=Path, help="Optional combined Query+Page CSV (must contain both dimensions)")
    args = parser.parse_args(argv)
    try:
        data = summarize(args.month, args.pages, args.queries, args.query_pages)
    except ExportError as exc:
        print(f"Export error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
