"""Remove only the exact reviewed navigation additions on four known pages."""
from functools import lru_cache
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PATHS = frozenset({
    'technology/should-i-use-ai/index.html',
    'technology/task-brief/index.html',
    'technology/check-ai-answers/index.html',
    'technology/ai-time-savings/index.html',
})


@lru_cache(maxsize=1)
def baseline():
    return json.loads((ROOT / '_tests/practical-navigation-baseline.json').read_text())


def before(path, data):
    path = str(path)
    if path not in PATHS:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    addition = baseline()['additions'][path]
    for block in addition['blocks']:
        text = text.replace(block, '', 1)
    text = text.replace(addition['head'], '', 1)
    return text.encode() if binary else text
