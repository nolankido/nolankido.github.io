"""SHA-gated, test-only predecessor for two practical-AI print stylesheet repairs.

Recognize the exact complete newer file hash, restore one reviewed byte edit,
and independently verify the historical parent hash. Unknown edits remain visible.
This module never runs in the published site.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = '17794dbd423e80215a7c17f50e6606785e8064ba'
PATHS = {
    'assets/summary-review.css',
    'assets/ai-task-choice.css',
    'technology/check-ai-summary/index.html',
    'technology/should-i-use-ai/index.html',
}

@lru_cache(maxsize=1)
def change():
    r = json.loads((ROOT / '_tests/practical-ai-print-change.json').read_text(encoding='utf-8'))
    if (type(r.get('version')) is not int or r['version'] != 1
            or r.get('base_commit') != BASE or set(r.get('paths', {})) != PATHS):
        raise ValueError('Unknown practical-AI print predecessor')
    return r

def before(path, data):
    import study_interest_history
    data = study_interest_history.before(path, data)
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    current = raw.decode('utf-8')
    newer, older = item['new'], item['old']
    if (not isinstance(newer, str) or not isinstance(older, str)
            or not newer or current.count(newer) != 1):
        raise ValueError('Invalid practical-AI print reversal: ' + str(path))
    result = current.replace(newer, older, 1)
    previous = result.encode('utf-8')
    if sha256(previous).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt practical-AI print parent hash: ' + str(path))
    return previous if binary else result
