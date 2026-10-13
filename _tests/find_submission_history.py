"""Restore only the frozen finder event block and its single cache version."""
from functools import lru_cache
from pathlib import Path
import json
import poker_finder_submission_history

ROOT=Path(__file__).resolve().parents[1]
SCRIPT='assets/site-find.js'
PAGE='find/index.html'


@lru_cache(maxsize=1)
def baseline():
    return json.loads((ROOT/'_tests/find-submission-baseline.json').read_text())


def before(path,data):
    data=poker_finder_submission_history.before(path,data)
    path=str(path)
    if path not in {SCRIPT,PAGE}:return data
    binary=isinstance(data,bytes);text=data.decode() if binary else data
    b=baseline()
    if path==SCRIPT:text=text.replace(b['new_handler'],b['old_handler'],1)
    else:text=text.replace('/assets/site-find.js?v='+b['new_script_sha256'][:12],
                           '/assets/site-find.js?v='+b['old_script_sha256'][:12],1)
    return text.encode() if binary else text
