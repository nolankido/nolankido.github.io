"""Hash-gated preservation of the October 23 source records."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
BASE='fbfd99915d6b11332b0bf771c8ad7103d8be0d93'
IDS={'nj-dge-information','wynn-poker'}
@lru_cache(maxsize=1)
def change():
    r=json.loads((ROOT/'_tests/resource-followup-change.json').read_text())
    if r.get('version')!=1 or r.get('base_commit')!=BASE or set(r['resources'])!=IDS:
        raise ValueError('Unknown exact review predecessor')
    return r
def before(path,data):
    # Newer, separately hash-gated UI changes must be reversed before checking
    # the preserved source-review snapshots from this earlier release.
    import task_brief_disclosure_history
    data=task_brief_disclosure_history.before(path,data)
    item=change()['paths'].get(str(path))
    if item is None:return data
    binary=isinstance(data,bytes);raw=data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest()!=item['new_sha256']:return data
    lines=raw.decode('utf-8').splitlines(keepends=True)
    for n,prior in item['old_lines']:
        if type(n)!=int or n<0 or n>=len(lines):raise ValueError('Invalid historical line')
        lines[n]=prior
    old=''.join(lines).encode('utf-8')
    if sha256(old).hexdigest()!=item['old_sha256']:raise ValueError('Corrupted predecessor')
    return old if binary else old.decode('utf-8')
def resources(records):
    p=change()['resources']
    return [deepcopy(p[r['id']]['old']) if r['id'] in p and r==p[r['id']]['new'] else deepcopy(r) for r in records]
