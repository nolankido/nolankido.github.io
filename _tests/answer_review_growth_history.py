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
    if item is None or sha256(raw).hexdigest()!=item['new_sha256']:
        return data
    value=raw.decode('utf-8')
    for edit in reversed(item['edits']):
        a,b=edit['start'],edit['end']
        if type(a) is not int or type(b) is not int or not 0<=a<=b<=len(value) or value[a:b]!=edit['new']:
            raise ValueError('Corrupt answer checking predecessor offsets')
        value=value[:a]+edit['old']+value[b:]
    prior=value.encode('utf-8')
    git_sha=sha1(b'blob '+str(len(prior)).encode()+b'\0'+prior).hexdigest()
    if git_sha!=item['old_git_sha']:
        raise ValueError('Corrupt answer checking predecessor digest')
    return prior if binary else value
