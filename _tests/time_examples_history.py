"""Reverse only the frozen example controls, origin note, and script additions."""
import time_decision_history
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
from search_addresses_history import before as before_search_addresses

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'assets/workflow-time.js'
PAGE = 'technology/ai-time-savings/index.html'


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/time-examples-change.json').read_text())


def before(path, data):
    import answer_review_growth_history as guide_growth
    data = guide_growth.before(path, data)
    data = time_decision_history.before(path, data)
    data = before_search_addresses(path, data)
    path = str(path)
    if path not in {SCRIPT, PAGE}:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    c = change()
    if path == SCRIPT:
        for old, new in reversed(c['patches']):
            text = text.replace(new, old, 1)
    else:
        text = re.sub(r'<!-- Editable time examples: start -->.*?<!-- Editable time examples: end -->',
                      lambda m: '' if sha256(m[0].encode()).hexdigest() in c['blocks'] else m[0], text, flags=re.S)
        old, new = c['script_versions']
        text = text.replace('/assets/workflow-time.js?v=' + new, '/assets/workflow-time.js?v=' + old, 1)
    return text.encode() if binary else text
