"""Exact, test-only predecessor for Creative Work printable blank brief.

Unknown edits are never masked. The whole new file hash must match before
reverting any recorded byte edit, and the old hash must match afterward.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = 'e30cbee4656917c105724614c6ea8821a21af002'
PATHS = {'assets/first-steps.css', '_source/creative/home.html',
         'creative/index.html', 'index.html'}

@lru_cache(maxsize=1)
def change():
    result = json.loads((ROOT / '_tests/creative-print-change.json').read_text(encoding='utf-8'))
    if (type(result.get('version')) is not int or result['version'] != 1
            or result.get('base_commit') != BASE
            or set(result.get('paths', {})) != PATHS):
        raise ValueError('Unknown creative print predecessor')
    return result

def before(path, data):
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    content = raw.decode('utf-8')
    edits = item['edits']
    previous_end = 0
    for edit in edits:
        if (set(edit) != {'start','new','old'}
                or type(edit['start']) is not int
                or not isinstance(edit['new'], str) or not isinstance(edit['old'], str)
                or not previous_end <= edit['start'] <= len(content)
                or content[edit['start']:edit['start']+len(edit['new'])] != edit['new']):
            raise ValueError('Invalid creative print predecessor edit: ' + str(path))
        previous_end = edit['start']+len(edit['new'])
    for edit in reversed(edits):
        start = edit['start']
        content = content[:start] + edit['old'] + content[start+len(edit['new']):]
    old = content.encode('utf-8')
    if sha256(old).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt creative print predecessor hash: ' + str(path))
    return old if binary else content
