"""Restore the exact reviewed first-tournament plan predecessor, for tests.

Whole successor hashes, checked reverse spans and whole predecessor hashes
preserve archived comparisons. Unknown bytes and metadata stay visible. The
public build and browser code never import this historical view.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/first-tournament-plan-change.json'
PARENT = '74e064631e59e7659826144390dc77d49d2022ed'
PARENT_TREE = '24495e6156dd0d5abf71c707fb7bbd0f195e4983'
PATHS = frozenset({
    '_source/pages.json', '_source/poker/first-live-tournament.html',
    '_source/poker/tournament-checklists.html', 'downloads/poker-event-planner.md',
    'find/index.html', 'poker/find/index.html',
    'poker/first-live-tournament/index.html', 'poker/library/index.html',
    'poker/poker-access-and-protection/index.html',
    'poker/poker-rules-and-fair-play/index.html',
    'poker/thunder-valley-poker-guide/index.html',
    'poker/topics/places-to-play/index.html',
    'poker/topics/tournaments/index.html',
    'poker/tournament-checklists/index.html', 'sitemap.xml',
})
REVISIONS = {
    'poker-first-live-tournament': (
        'Added a six-step first-event plan, early access to the existing planner '
        'and a record of confirmed details, unresolved questions and the '
        'decision before paying.'),
    'poker-tournament-checklists': (
        'Expanded the existing event planner with a source, date, status and '
        'follow-up record for consequential questions, plus an explicit '
        'entry decision.'),
}


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def change() -> dict:
    record = json.loads(CHANGE.read_text(encoding='utf-8'))
    if (not isinstance(record, dict) or
            set(record) != {'version', 'parent_commit', 'parent_tree', 'paths', 'pages'} or
            type(record['version']) is not int or record['version'] != 1 or
            record['parent_commit'] != PARENT or
            record['parent_tree'] != PARENT_TREE or
            not isinstance(record['paths'], dict) or set(record['paths']) != PATHS or
            not isinstance(record['pages'], dict) or set(record['pages']) != set(REVISIONS)):
        raise ValueError('Unknown first-tournament-plan predecessor')
    for name, item in record['paths'].items():
        if (not isinstance(item, dict) or
                set(item) != {'current_sha256', 'parent_sha256', 'edits'} or
                any(not isinstance(item[field], str) or len(item[field]) != 64 or
                    any(c not in '0123456789abcdef' for c in item[field])
                    for field in ('current_sha256', 'parent_sha256'))):
            raise ValueError('Unknown first-tournament-plan file boundary: ' + name)
    for page_id, pair in record['pages'].items():
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'} or
                not isinstance(pair['old'], dict) or not isinstance(pair['new'], dict)):
            raise ValueError('Unknown first-tournament-plan metadata boundary')
        current = pair['new']
        expected_old = {key: value for key, value in current.items()
                        if key not in {'updated', 'revision'}}
        expected_old['updated'] = '2026-10-08'
        if (current.get('id') != page_id or
                current.get('path') != '/poker/' + page_id.removeprefix('poker-') + '/' or
                current.get('date') != '2026-10-08' or
                current.get('updated') != '2026-10-27' or
                current.get('revision') != REVISIONS[page_id] or
                pair['old'] != expected_old):
            raise ValueError('Unknown first-tournament-plan metadata boundary')
    return record


def key(path: str | Path) -> str:
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def before(path: str | Path, data: bytes | str) -> bytes | str:
    import ranking_practice_history
    data = ranking_practice_history.before(path, data)
    name = key(path)
    item = change()['paths'].get(name)
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if digest(raw) != item['current_sha256']:
        return data
    current = raw.decode('utf-8')
    edits = item['edits']
    if type(edits) is not list or not edits:
        raise ValueError('Invalid first-tournament-plan edits: ' + name)
    previous_end = 0
    for edit in edits:
        if (not isinstance(edit, dict) or
                set(edit) != {'start', 'end', 'current_sha256', 'old'} or
                type(edit['start']) is not int or type(edit['end']) is not int or
                not previous_end <= edit['start'] <= edit['end'] <= len(current) or
                not isinstance(edit['old'], str) or
                digest(current[edit['start']:edit['end']].encode('utf-8')) != edit['current_sha256']):
            raise ValueError('Invalid first-tournament-plan edit span: ' + name)
        previous_end = edit['end']
    restored = current
    for edit in reversed(edits):
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    original = restored.encode('utf-8')
    if digest(original) != item['parent_sha256']:
        raise ValueError('Invalid first-tournament-plan predecessor digest: ' + name)
    return original if binary else restored


def pages(records: list[dict]) -> list[dict]:
    """Restore only complete approved page records without mutating input."""
    import ranking_practice_history
    records = ranking_practice_history.pages(records)
    pairs = change()['pages']
    result = []
    for page in records:
        pair = pairs.get(page.get('id'))
        result.append(deepcopy(pair['old'] if pair and page == pair['new'] else page))
    return result
