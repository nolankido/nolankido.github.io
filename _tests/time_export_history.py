"""Restore only the frozen download handler and its one generated cache version."""
from functools import lru_cache
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SCRIPT='assets/workflow-time.js'
PAGE='technology/ai-time-savings/index.html'


@lru_cache(maxsize=1)
def baseline():
    return json.loads((ROOT/'_tests/time-export-baseline.json').read_text())


def before(path,data):
    path=str(path)
    if path not in {SCRIPT,PAGE}:return data
    binary=isinstance(data,bytes);text=data.decode() if binary else data
    b=baseline()
    if path==SCRIPT:
        text=text.replace(b['new_handler'],b['old_handler'],1)
    else:
        text=text.replace('/assets/workflow-time.js?v='+b['new_script_version'],
                          '/assets/workflow-time.js?v='+b['old_script_version'],1)
    return text.encode() if binary else text
