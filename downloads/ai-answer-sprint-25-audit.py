#!/usr/bin/env python3
"""Audit a privately observed, frozen 25-prompt AI-answer panel offline.

Download the matching frozen prompts CSV and blank observation CSV from
https://nolankido.com/technology/ai-website-visibility/#ai-answer-sprint-panel

Example on Windows, from the folder containing all three downloads:
    py -3 ai-answer-sprint-25-audit.py --month 2026-11 --expected-modes 2 \
        --prompts ai-answer-sprint-25-prompts.csv --csv my-private-observations.csv

This tool does not run assistants, visit links, write data, verify human
observations or transmit anything. Its JSON contains aggregates, not raw URLs.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


PANEL_SHA256 = 'b9d29feaaea2d4a593ef3e2d9c86fe04d67f076c1c78d53ac7c7ddbf8f491d74'
PROMPT_FIELDS = ('prompt_id', 'segment', 'cluster', 'exact_prompt', 'expected_url_path')
OBSERVATION_FIELDS = (
    'date', 'prompt_id', 'assistant', 'mode', 'status', 'clickable_link_verified',
    'linked_url', 'text_only_mention', 'answer_correctness', 'task_completed',
)
ROSTER_FIELDS = ('assistant', 'mode')
SEGMENT_SIZES = {'nonbranded': 20, 'branded': 5}
HOSTS = {'nolankido.com', 'www.nolankido.com'}
STATUSES = {'completed', 'incomplete', 'not_checked'}
CORRECTNESS = {'verified', 'partial', 'incorrect', 'unverified'}
TASK = {'yes', 'partial', 'no', 'unknown'}
YES_NO = {'yes', 'no'}
LABEL = re.compile(r'^[A-Za-z][A-Za-z0-9 ._+\-]{0,59}$')


class InvalidPanel(ValueError):
    """An observation or prompt source cannot support the named comparison."""


def load_prompts(path: Path) -> dict[str, dict[str, str]]:
    """Refuse a revised or reordered source pretending to be frozen v1."""
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PANEL_SHA256:
        raise InvalidPanel('Prompt file differs from frozen November 17, 2026 v1; restore the original.')
    try:
        reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
        if reader.fieldnames != list(PROMPT_FIELDS):
            raise InvalidPanel('Prompt file has unexpected columns.')
        prompts = {}
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise InvalidPanel('Prompt row has the wrong number of fields.')
            ident = row['prompt_id']
            if ident in prompts:
                raise InvalidPanel('Repeated frozen prompt ID.')
            prompts[ident] = row
    except UnicodeError as exc:
        raise InvalidPanel('Prompt file must be UTF-8.') from exc
    expected_ids = {f'NB{i:02}' for i in range(1, 21)} | {f'BR{i:02}' for i in range(1, 6)}
    if set(prompts) != expected_ids:
        raise InvalidPanel('The frozen panel must contain exactly 20 NB and five BR prompts.')
    for ident, row in prompts.items():
        expected_segment = 'nonbranded' if ident.startswith('NB') else 'branded'
        if (row['segment'] != expected_segment or not row['cluster'] or not row['exact_prompt']
                or not row['expected_url_path'].startswith('/')):
            raise InvalidPanel('Frozen prompt metadata is invalid.')
    return prompts


def month_check(value: str) -> None:
    if not re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', value):
        raise InvalidPanel('Month must be YYYY-MM.')
    try:
        date.fromisoformat(value + '-01')
    except ValueError as exc:
        raise InvalidPanel('Month is not a calendar month.') from exc


def verified_host_url(value: str) -> bool:
    """Syntax and host test only. Humans must verify a genuine cited link."""
    if not value or any(c.isspace() or ord(c) < 32 for c in value):
        return False
    try:
        url = urlsplit(value)
        return (url.scheme == 'https' and url.hostname in HOSTS
                and url.username is None and url.password is None and url.port is None
                and bool(url.netloc))
    except ValueError:
        return False


def on_expected_page(url: str, expected_path: str) -> bool:
    if not verified_host_url(url):
        return False
    observed_path = urlsplit(url).path or '/'
    return observed_path.rstrip('/') + '/' == expected_path.rstrip('/') + '/'



def load_roster(path: Path) -> list[tuple[str, str]]:
    """Load the assistant/search modes frozen before running the prompt panel.

    This is a design check, not proof that a public assistant answer was seen.
    Keep the filled roster private. The public blank template has no results.
    """
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(ROSTER_FIELDS):
                raise InvalidPanel('Mode roster needs assistant,mode columns.')
            rows = []
            seen = set()
            for lineno, raw in enumerate(reader, start=2):
                if None in raw or any(value is None for value in raw.values()):
                    raise InvalidPanel(f'Roster row {lineno}: incorrect number of columns.')
                assistant, mode = (raw[field].strip() for field in ROSTER_FIELDS)
                if not LABEL.fullmatch(assistant) or not LABEL.fullmatch(mode):
                    raise InvalidPanel(f'Roster row {lineno}: invalid assistant or mode label.')
                key = (assistant.casefold(), mode.casefold())
                if key in seen:
                    raise InvalidPanel(f'Roster row {lineno}: duplicate assistant and mode.')
                seen.add(key)
                rows.append((assistant, mode))
    except UnicodeError as exc:
        raise InvalidPanel('Roster file must be UTF-8.') from exc
    if not 1 <= len(rows) <= 20:
        raise InvalidPanel('Roster requires 1 to 20 named assistant/mode combinations.')
    return rows


def load_observations(path: Path, month: str, prompts: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(OBSERVATION_FIELDS):
                raise InvalidPanel('Observation columns must match the downloadable blank CSV exactly.')
            observations = []
            keys = set()
            modes = {}
            for lineno, raw in enumerate(reader, start=2):
                if None in raw or any(value is None for value in raw.values()):
                    raise InvalidPanel(f'Row {lineno}: wrong number of CSV columns.')
                row = {name: value.strip() for name, value in raw.items()}
                if not any(row.values()):
                    continue
                try:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['date']):
                        raise ValueError('Bad ISO date')
                    observed = date.fromisoformat(row['date'])
                except ValueError as exc:
                    raise InvalidPanel(f'Row {lineno}: invalid observation date.') from exc
                if observed.strftime('%Y-%m') != month:
                    raise InvalidPanel(f'Row {lineno}: date outside selected month.')
                if row['prompt_id'] not in prompts:
                    raise InvalidPanel(f'Row {lineno}: prompt ID is not in the frozen panel.')
                for field in ('assistant', 'mode'):
                    if not LABEL.fullmatch(row[field]):
                        raise InvalidPanel(f'Row {lineno}: invalid {field} label.')
                pair = (row['assistant'].casefold(), row['mode'].casefold())
                spelled = (row['assistant'], row['mode'])
                if pair in modes and modes[pair] != spelled:
                    raise InvalidPanel(f'Row {lineno}: inconsistent assistant or mode spelling.')
                modes[pair] = spelled
                trial = (row['prompt_id'], *pair)
                if trial in keys:
                    raise InvalidPanel(f'Row {lineno}: repeated prompt, assistant and mode.')
                keys.add(trial)
                if row['status'] not in STATUSES:
                    raise InvalidPanel(f'Row {lineno}: status must be completed, incomplete or not_checked.')
                if row['status'] == 'completed':
                    for field in ('clickable_link_verified', 'text_only_mention'):
                        if row[field] not in YES_NO:
                            raise InvalidPanel(f'Row {lineno}: {field} must be yes or no.')
                    if row['answer_correctness'] not in CORRECTNESS or row['task_completed'] not in TASK:
                        raise InvalidPanel(f'Row {lineno}: a completed trial needs human quality labels.')
                    cited = row['clickable_link_verified'] == 'yes'
                    if cited and not verified_host_url(row['linked_url']):
                        raise InvalidPanel(f'Row {lineno}: a claimed citation needs a valid exact-host HTTPS URL.')
                    if not cited and row['linked_url']:
                        raise InvalidPanel(f'Row {lineno}: linked URL needs an asserted clickable citation.')
                    if cited and row['text_only_mention'] == 'yes':
                        raise InvalidPanel(f'Row {lineno}: text-only mention cannot also be a clickable citation.')
                elif any(row[field] for field in OBSERVATION_FIELDS[5:]):
                    raise InvalidPanel(f'Row {lineno}: uncompleted trials cannot contain observed outcomes.')
                observations.append(row)
            return observations
    except UnicodeError as exc:
        raise InvalidPanel('Observation file must be UTF-8.') from exc


def segment_metrics(rows: list[dict[str, str]], expected: int,
                    prompts: dict[str, dict[str, str]]) -> dict:
    completed = [r for r in rows if r['status'] == 'completed']
    cited = [r for r in completed if r['clickable_link_verified'] == 'yes']
    expected_matches = sum(on_expected_page(r['linked_url'], prompts[r['prompt_id']]['expected_url_path'])
                           for r in cited)
    return {
        'planned_trials': expected,
        'recorded_rows': len(rows),
        'completed_trials': len(completed),
        'uncompleted_or_missing': expected - len(completed),
        'cited_trials': len(cited),
        'expected_page_cited_trials': expected_matches,
        'other_site_page_cited_trials': len(cited) - expected_matches,
        'text_only_mentions': sum(r['text_only_mention'] == 'yes' for r in completed),
        'human_labeled_verified_answers': sum(r['answer_correctness'] == 'verified' for r in completed),
        'sample_fraction': round(len(cited) / len(completed), 6) if completed else None,
        'sample_percent': round(100 * len(cited) / len(completed), 2) if completed else None,
    }


def summarize(rows: list[dict[str, str]], month: str, modes: int,
              prompts: dict[str, dict[str, str]],
              roster: list[tuple[str, str]] | None = None) -> dict:
    if not 1 <= modes <= 20:
        raise InvalidPanel('Expected modes must be 1 to 20 preselected assistant/mode combinations.')
    if roster is not None:
        if len(roster) != modes:
            raise InvalidPanel('Expected modes must equal the predeclared roster length.')
        planned = {(assistant.casefold(), mode.casefold()): (assistant, mode)
                   for assistant, mode in roster}
        if len(planned) != modes:
            raise InvalidPanel('Predeclared roster contains repeated assistant/mode combinations.')
        for row in rows:
            key = (row['assistant'].casefold(), row['mode'].casefold())
            if key not in planned or planned[key] != (row['assistant'], row['mode']):
                raise InvalidPanel('Observation assistant/mode is not an exact roster entry.')
    expected = modes * len(prompts)
    if len(rows) > expected:
        raise InvalidPanel('More recorded rows than planned trials.')
    actual_modes = {(r['assistant'].casefold(), r['mode'].casefold()) for r in rows}
    if len(actual_modes) > modes:
        raise InvalidPanel('More assistant/mode combinations than planned.')
    segments = {
        name: segment_metrics([r for r in rows if prompts[r['prompt_id']]['segment'] == name],
                              size * modes, prompts)
        for name, size in SEGMENT_SIZES.items()
    }
    completed = sum(d['completed_trials'] for d in segments.values())
    per_mode = None
    if roster is not None:
        per_mode = []
        for assistant, mode in roster:
            trials = [row for row in rows if row['assistant'] == assistant and row['mode'] == mode]
            finished = sum(row['status'] == 'completed' for row in trials)
            per_mode.append({
                'assistant': assistant, 'mode': mode,
                'planned_trials': len(prompts), 'recorded_rows': len(trials),
                'completed_trials': finished, 'missing_rows': len(prompts) - len(trials),
                'uncompleted_or_missing': len(prompts) - finished,
                'verified_link_trials': sum(row['status'] == 'completed'
                    and row['clickable_link_verified'] == 'yes' for row in trials),
            })
    return {
        'site': 'nolankido.com',
        'month': month,
        'panel': 'frozen 2026-11-17 v1, 20 nonbranded and 5 branded exact prompts',
        'panel_sha256': PANEL_SHA256,
        'expected_assistant_mode_combinations': modes,
        'roster_predeclared': roster is not None,
        'per_mode_coverage': per_mode,
        'status': ('no_completed_trials' if completed == 0 else
                   'complete' if completed == expected else 'partial'),
        'coverage': {
            'planned_trials': expected,
            'recorded_rows': len(rows),
            'completed_trials': completed,
            'incomplete_rows': sum(r['status'] == 'incomplete' for r in rows),
            'not_checked_rows': sum(r['status'] == 'not_checked' for r in rows),
            'missing_rows': expected - len(rows),
            'uncompleted_or_missing': expected - completed,
        },
        'segments': segments,
        'limitations': [
            'The tool audits human labels, not actual assistant answers or live URLs.',
            'Only completed eligible trials enter each segment citation denominator.',
            'Branded name recognition is separate from unbranded topic discovery.',
            'A same-domain link on a different page is not an expected-page citation.',
            'This is a fixed observational sample, not traffic, platform-wide ranking or causal uplift.',
            'The older eight-prompt monthly panel is a different method and cannot be pooled with this panel.',
            'An optional predeclared mode roster prevents mode substitutions, but cannot certify a genuine answer.',
            'Raw answers, URLs, user data and first-party analytics must remain private.',
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--month', required=True, help='Observation month YYYY-MM')
    parser.add_argument('--expected-modes', required=True, type=int,
                        help='Number of selected assistant and browsing-mode combinations (1 to 20)')
    parser.add_argument('--prompts', required=True, type=Path,
                        help='Exact frozen 25-prompt CSV downloaded from the public site')
    parser.add_argument('--csv', required=True, type=Path,
                        help='Your privately completed observation log')
    parser.add_argument('--roster', type=Path,
                        help='Predeclared private assistant,mode CSV; enforces exactly the planned modes')
    args = parser.parse_args(argv)
    try:
        month_check(args.month)
        prompts = load_prompts(args.prompts)
        roster = load_roster(args.roster) if args.roster else None
        rows = load_observations(args.csv, args.month, prompts)
        report = summarize(rows, args.month, args.expected_modes, prompts, roster)
    except OSError:
        print('Invalid 25-prompt panel: cannot read a required local file.', file=sys.stderr)
        return 2
    except InvalidPanel as exc:
        print('Invalid 25-prompt panel: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
