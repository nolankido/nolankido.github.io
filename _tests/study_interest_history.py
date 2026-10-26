"""Immutable, test-only predecessor for the small public volunteer invitation.

Requires an exact complete file hash, removes only the approved added section,
and verifies reconstructed parent bytes. Unknown edits remain visible.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
BASE='1c6a1f1123ce8000ca6f43a016d3bb8714f18d58'
PATHS={'_source/start-here.html','start-here/index.html'}

@lru_cache(maxsize=1)
def change():
    record=json.loads((ROOT/'_tests/study-interest-change.json').read_text(encoding='utf-8'))
    if (type(record.get('version')) is not int or record.get('version')!=1
            or record.get('base_commit')!=BASE or set(record.get('paths',{}))!=PATHS):
        raise ValueError('Unknown study-interest predecessor')
    return record

def before(path,data):
    item=change()['paths'].get(str(path))
    if item is None:return data
    binary=isinstance(data,bytes)
    raw=data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest()!=item['new_sha256']:return data
    string=raw.decode('utf-8')
    newer,prior=item['new'],item['old']
    if not isinstance(newer,str) or not newer or not isinstance(prior,str) or string.count(newer)!=1:
        raise ValueError('Invalid study-interest predecessor')
    previous=string.replace(newer,prior,1)
    old=previous.encode('utf-8')
    if sha256(old).hexdigest()!=item['old_sha256']:
        raise ValueError('Corrupt study-interest parent')
    return old if binary else previous
