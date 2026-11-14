#!/usr/bin/env python3
"""Summarize a privately completed AI-answer citation panel, without networking.

This checks a human-recorded CSV. It cannot verify whether a link really appeared
in an assistant response or whether it resolved after redirects. The researcher
must inspect the final clickable link and keep evidence privately.

Example:
    py -3 ai-citation-panel-audit.py --month 2026-10 --expected-trials 16 --csv panel.csv

No third-party packages, HTTP requests, user identifiers, files written, or
original citation URLs are included in the aggregate JSON output.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

FIELDS = (
    'date', 'prompt_id', 'assistant', 'mode', 'status',
    'clickable_link_verified', 'linked_url', 'text_only_mention',
)
STATUSES = {'completed', 'incomplete', 'not_checked'}
YES_NO = {'yes', 'no'}
IDENT = re.compile(r'^[A-Za-z][A-Za-z0-9 ._+\-]{0,59}$')
MONTH = re.compile(r'^\d{4}-(?:0[1-9]|1[0-2])$')
DOMAINS = {'nolankido.com', 'www.nolankido.com'}


class InvalidPanel(ValueError):
    """A row is ambiguous or cannot support a valid citation calculation."""


def month_check(value: str) -> None:
    if not MONTH.fullmatch(value):
        raise InvalidPanel('Month must be YYYY-MM.')
    try:
        date.fromisoformat(value + '-01')
    except ValueError as exc:
        raise InvalidPanel('Month is not a calendar month.') from exc


def verified_site_link(value: str) -> bool:
    """Validate syntax and exact host. Human verification is still required."""
    if not value or any(c.isspace() or ord(c) < 32 for c in value):
        return False
    try:
        parts = urlsplit(value)
        return (parts.scheme == 'https' and parts.hostname in DOMAINS
                and parts.username is None and parts.password is None
                and parts.port is None and bool(parts.netloc)
                and parts.path.startswith('/'))
    except ValueError:
        return False


def parse_csv(path: Path, month: str) -> list[dict]:
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(FIELDS):
                raise InvalidPanel('CSV headers must exactly match the published template.')
            rows = []
            seen = set()
            for index, raw in enumerate(reader, start=2):
                if None in raw or any(value is None for value in raw.values()):
                    raise InvalidPanel(f'Row {index}: wrong number of CSV columns.')
                row = {key: value.strip() for key, value in raw.items()}
                if not any(row.values()):
                    continue
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row['date']):
                        raise ValueError("Expected YYYY-MM-DD")
                    observed = date.fromisoformat(row['date'])
                except ValueError as exc:
                    raise InvalidPanel(f'Row {index}: invalid ISO observation date.') from exc
                if observed.strftime('%Y-%m') != month:
                    raise InvalidPanel(f'Row {index}: observation date is outside selected month.')
                if row['prompt_id'] not in {str(i) for i in range(1, 9)}:
                    raise InvalidPanel(f'Row {index}: prompt_id must be 1 through 8 (unbranded only).')
                for field in ('assistant', 'mode'):
                    if not IDENT.fullmatch(row[field]):
                        raise InvalidPanel(f'Row {index}: invalid {field} label.')
                key = (row['prompt_id'], row['assistant'].casefold(), row['mode'].casefold())
                if key in seen:
                    raise InvalidPanel(f'Row {index}: repeated prompt/assistant/mode trial.')
                seen.add(key)
                if row['status'] not in STATUSES:
                    raise InvalidPanel(f'Row {index}: status must be completed, incomplete or not_checked.')
                for field in ('clickable_link_verified', 'text_only_mention'):
                    if row[field] not in YES_NO:
                        raise InvalidPanel(f'Row {index}: {field} must be yes or no.')
                cited = row['clickable_link_verified'] == 'yes'
                mention = row['text_only_mention'] == 'yes'
                if cited and not verified_site_link(row['linked_url']):
                    raise InvalidPanel(f'Row {index}: verified citation needs an HTTPS link to the exact site.')
                if not cited and row['linked_url']:
                    raise InvalidPanel(f'Row {index}: do not record a linked URL without manual verification.')
                if cited and mention:
                    raise InvalidPanel(f'Row {index}: a text-only mention cannot also be a clickable citation.')
                if row['status'] != 'completed' and (cited or mention or row['linked_url']):
                    raise InvalidPanel(f'Row {index}: incomplete trials cannot have recorded outcomes.')
                rows.append(row)
            return rows
    except UnicodeError as exc:
        raise InvalidPanel('CSV must be UTF-8.') from exc


def summarize(rows: list[dict], month: str, expected_trials: int) -> dict:
    if expected_trials < 8 or expected_trials > 160 or expected_trials % 8 != 0:
        raise InvalidPanel('Expected trials must be 8 times the number of preselected modes (8 to 160).')
    if len(rows) > expected_trials:
        raise InvalidPanel('More recorded rows than planned trials. Recheck mode count.')
    panels = {(row['assistant'].casefold(), row['mode'].casefold()) for row in rows}
    if len(panels) > expected_trials // 8:
        raise InvalidPanel('More assistant/mode combinations than the planned panel.')
    for panel in panels:
        labels = {(r['assistant'], r['mode']) for r in rows
                  if (r['assistant'].casefold(), r['mode'].casefold()) == panel}
        if len(labels) != 1:
            raise InvalidPanel('Use the exact same assistant/mode spelling throughout a panel.')

    completed = [row for row in rows if row['status'] == 'completed']
    cited = sum(row['clickable_link_verified'] == 'yes' for row in completed)
    mentions = sum(row['text_only_mention'] == 'yes' for row in completed)
    result = {
        'site': 'nolankido.com',
        'month': month,
        'scope': 'manual, unbranded, search-enabled assistant-answer panel only',
        'status': 'no_completed_trials' if not completed else 'complete' if len(completed) == expected_trials else 'partial',
        'coverage': {
            'expected_trials': expected_trials,
            'recorded_rows': len(rows),
            'completed_trials': len(completed),
            'incomplete_trials': sum(row['status'] == 'incomplete' for row in rows),
            'not_checked_rows': sum(row['status'] == 'not_checked' for row in rows),
            'missing_rows': expected_trials - len(rows),
            'uncompleted_or_missing': expected_trials - len(completed),
        },
        'citations': {
            'cited_trials': cited,
            'completed_eligible_trials': len(completed),
            'sample_fraction': (round(cited / len(completed), 6) if completed else None),
            'sample_percent': (round(100 * cited / len(completed), 2) if completed else None),
            'text_only_mentions': mentions,
        },
        'observed_modes': sorted(
            [{'assistant': a, 'mode': m,
              'completed': sum(r['status'] == 'completed' for r in rows if r['assistant'] == a and r['mode'] == m),
              'cited': sum(r['status'] == 'completed' and r['clickable_link_verified'] == 'yes'
                           for r in rows if r['assistant'] == a and r['mode'] == m)}
             for a, m in sorted({(r['assistant'], r['mode']) for r in rows})],
            key=lambda item: (item['assistant'].casefold(), item['mode'].casefold()),
        ),
        'limitations': [
            'Human verification of clickable links is asserted, not independently established by this script.',
            'No automatic assistant searches, internet requests, screenshots, or raw citation URLs are included.',
            'This sampled fraction is not a platform-wide citation rate, ranking, traffic total or causal effect.',
            'Absent and incomplete trials do not enter the citation denominator and are not scored as misses.',
            'Branded prompts, Google AI impressions, Bing AI citations and analytics referrals are separate measures.',
        ],
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--month', required=True, help='Calendar month, YYYY-MM')
    parser.add_argument('--expected-trials', type=int, required=True, help='8 prompts multiplied by the number of planned assistant/mode combinations')
    parser.add_argument('--csv', type=Path, required=True, help='Private observer-completed CSV file')
    args = parser.parse_args(argv)
    try:
        month_check(args.month)
        rows = parse_csv(args.csv, args.month)
        result = summarize(rows, args.month, args.expected_trials)
    except (InvalidPanel, OSError) as exc:
        print('Invalid private citation panel: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
