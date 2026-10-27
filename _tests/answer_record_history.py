"""Restore only the reviewed completed answer-record revision, for tests.

Whole successor hashes, checked reverse spans and whole predecessor hashes
keep earlier release comparisons intact without accepting unknown changes.
The public build and browser code never import this archived view.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / '_tests/answer-record-change.json'
PARENT = 'b8b4bcd45d66178a8aa5868889781ef3311f0a3b'
PARENT_TREE = '80a4a92d914cee30d84e8e807f3b4f847fb66ec6'
PATHS = frozenset({
    '_source/pages.json', '_source/technology/check-ai-answers.html',
    'downloads/ai-answer-review.txt', 'downloads/practical-ai-workbook.txt',
    'technology/check-ai-answers/index.html', 'technology/index.html',
    'sitemap.xml',
})
OLD_REVISION = ('Added a four-step verification procedure and evidence statuses, '
                'separating an unsupported event-status claim from an unfaithful '
                'summary. The six existing exercises remain illustrative; no '
                'outside evaluation or improvement in accuracy is claimed.')
NEW_REVISION = ('Added a completed fictional review record and explicit '
                'evidence-status and reasoning fields in the blank worksheet. '
                'The example separates an unresolved claim from the human '
                'decision about what to do next.')


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def change() -> dict:
    record = json.loads(CHANGE.read_text(encoding='utf-8'))
    if (not isinstance(record, dict) or
            set(record) != {'version', 'parent_commit', 'parent_tree', 'paths', 'page'} or
            type(record['version']) is not int or record['version'] != 1 or
            record['parent_commit'] != PARENT or
            record['parent_tree'] != PARENT_TREE or
            not isinstance(record['paths'], dict) or set(record['paths']) != PATHS):
        raise ValueError('Unknown answer-record predecessor')
    pair = record['page']
    if (not isinstance(pair, dict) or set(pair) != {'old', 'new'} or
            not isinstance(pair['old'], dict) or not isinstance(pair['new'], dict) or
            pair['old'].get('id') != 'ai-answer-review' or
            pair['old'].get('path') != '/technology/check-ai-answers/' or
            pair['old'].get('updated') != '2026-10-19' or
            pair['new'].get('updated') != '2026-10-27' or
            pair['old'].get('revision') != OLD_REVISION or
            pair['new'].get('revision') != NEW_REVISION or
            pair['old'] != {**pair['new'], 'updated': '2026-10-19',
                            'revision': OLD_REVISION}):
        raise ValueError('Unknown answer-record metadata boundary')
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
    import first_tournament_plan_history
    data = first_tournament_plan_history.before(path, data)
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
        raise ValueError('Invalid answer-record edits: ' + name)
    previous_end = 0
    for edit in edits:
        if (not isinstance(edit, dict) or
                set(edit) != {'start', 'end', 'current_sha256', 'old'} or
                type(edit['start']) is not int or type(edit['end']) is not int or
                not previous_end <= edit['start'] <= edit['end'] <= len(current) or
                not isinstance(edit['old'], str) or
                digest(current[edit['start']:edit['end']].encode('utf-8')) != edit['current_sha256']):
            raise ValueError('Invalid answer-record edit span: ' + name)
        previous_end = edit['end']
    restored = current
    for edit in reversed(edits):
        restored = restored[:edit['start']] + edit['old'] + restored[edit['end']:]
    original = restored.encode('utf-8')
    if digest(original) != item['parent_sha256']:
        raise ValueError('Invalid answer-record predecessor digest: ' + name)
    return original if binary else restored


def pages(records: list[dict]) -> list[dict]:
    """Restore only the complete approved guide record, without mutation."""
    import first_tournament_plan_history
    records = first_tournament_plan_history.pages(records)
    pair = change()['page']
    return [deepcopy(pair['old'] if page == pair['new'] else page) for page in records]
