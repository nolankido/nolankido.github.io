#!/usr/bin/env python3
"""Create an unapproved poker draft OUTSIDE this public repository. Never publishes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def create(kind: str, slug: str, destination: Path, root: Path = ROOT) -> Path:
    if kind not in ('episode', 'hand', 'story') or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Use episode, hand, or story and a lower-case hyphenated slug')
    destination = destination.expanduser().resolve()
    if destination.is_relative_to(root.resolve()):
        raise ValueError('Private drafts must be written outside the public website repository')
    if destination.suffix != '.json':
        raise ValueError('The destination must end in .json')
    draft = {'slug': slug, 'kind': kind, 'title': '', 'summary': '', 'published': '', 'approved': False,
             'sections': [{'heading': 'The situation', 'paragraphs': ['']},
                          {'heading': 'The decision worth revisiting', 'paragraphs': ['']},
                          {'heading': 'What remains uncertain', 'paragraphs': ['']}],
             'related': []}
    if kind == 'episode':
        draft.update({'video_url': '', 'duration_seconds': 0, 'chapters': [{'seconds': 0, 'title': ''}]})
    if kind == 'hand':
        draft['record_type'] = 'reconstructed'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as f:
        f.write(json.dumps(draft, ensure_ascii=False, indent=2) + '\n')
    return destination

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['episode','hand','story'])
    parser.add_argument('slug')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        path = create(args.kind, args.slug, args.output)
    except (ValueError, OSError) as exc:
        print('Draft not created: ' + str(exc), file=sys.stderr)
        return 1
    print(f'Private, unapproved draft created: {path}. Nothing was published.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
