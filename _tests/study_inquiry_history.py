"""Exact published-parent adapter for the study-interest Contact handoff.

Recognizes full reviewed file hashes only. A changed file is restored using
the exact approved span, then checked against the previous release SHA256.
Never masks unknown edits and is not loaded by production code.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
BASE='7c8185b2660453e797f18dec2f3862aa1521f298'
PATHS={"_source/start-here.html", "start-here/index.html", "_source/contact.html", "contact/index.html", "assets/contact.js"}

@lru_cache(maxsize=1)
def change():
    record=json.loads((ROOT/'_tests/study-inquiry-change.json').read_text(encoding='utf-8'))
    if (type(record.get('version')) is not int or record['version']!=1
            or record.get('base_commit')!=BASE or set(record.get('paths',{}))!=PATHS):
        raise ValueError('Unknown study-inquiry predecessor')
    return record

def before(path,data):
    # Shared predecessor for the independent full-site history chains.
    # The newest regional link turn must be reversed before older fingerprints.
    import regional_link_history
    data=regional_link_history.before(path,data)
    item=change()['paths'].get(str(path))
    if item is None:return data
    binary=isinstance(data,bytes)
    raw=data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest()!=item['new_sha256']:return data
    current=raw.decode('utf-8')
    edits=item['edits']
    if type(edits) is not list or len(edits)!=1:
        raise ValueError('Invalid study-inquiry predecessor edits')
    edit=edits[0]
    if (set(edit)!={'start','old','new'} or type(edit['start']) is not int
            or not isinstance(edit['old'],str) or not isinstance(edit['new'],str)
            or not edit['new'] or not 0<=edit['start']<=len(current)
            or current[edit['start']:edit['start']+len(edit['new'])]!=edit['new']):
        raise ValueError('Corrupt study-inquiry predecessor span')
    start=edit['start']
    restored=current[:start]+edit['old']+current[start+len(edit['new']):]
    result=restored.encode('utf-8')
    if sha256(result).hexdigest()!=item['old_sha256']:
        raise ValueError('Corrupt study-inquiry parent digest')
    return result if binary else restored
