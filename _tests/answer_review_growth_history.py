"""Test-only exact-SHA predecessor for Turn 07's AI answer-checking revision."""
from functools import lru_cache
from hashlib import sha1,sha256
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def record():
    data=json.loads((ROOT/'_tests/answer-review-growth-change.json').read_text())
    if data.get('version')!=1 or data.get('base_commit')!='e6d61d4070bae76c54e1b676422e716ff8adaac6':
        raise ValueError('Unknown answer-checking predecessor')
    return data['paths']
def before(path,data):
    item=record().get(str(path))
    binary=isinstance(data,bytes)
    raw=data if binary else data.encode('utf-8')
    if item is None:
        return data
    current_sha=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if (current_sha != item.get('new_git_sha') if item.get('new_git_sha') else sha256(raw).hexdigest() != item['new_sha256']):
        return data
    value=raw.decode('utf-8')
    # The renderer's schema update occurs before all text-body diffs.
    # Remove it first so the recorded body offsets remain stable.
    if str(path)=='technology/check-ai-answers/index.html':
        schema_change='"dateModified": "2026-10-17", '
        if value.count(schema_change)!=1:
            raise ValueError('Unexpected answer checking dateModified count')
        value=value.replace(schema_change,'',1)
    for edit in reversed(item['edits']):
        a,b=edit['start'],edit['end']
        if type(a) is not int or type(b) is not int or not 0<=a<=b<=len(value) or value[a:b]!=edit['new']:
            raise ValueError('Corrupt answer checking predecessor offsets')
        value=value[:a]+edit['old']+value[b:]
    # Recompute-derived reading time changes separately from edited body text.
    # The reviewed guide grew from 10 to 12 minutes; restore the prior header.
    if str(path)=='technology/check-ai-answers/index.html':
        current=' · About 12 min read</p>'
        if value.count(current)!=1:
            raise ValueError('Unexpected answer guide reading-time header')
        value=value.replace(current,' · About 10 min read</p>',1)
    prior=value.encode('utf-8')
    git_sha=sha1(b'blob '+str(len(prior)).encode()+b'\0'+prior).hexdigest()
    if git_sha!=item['old_git_sha']:
        raise ValueError('Corrupt answer checking predecessor digest')
    return prior if binary else value
