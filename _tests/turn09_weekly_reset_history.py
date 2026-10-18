"""Exact SHA-scoped predecessor reconstruction for Turn 09 historical tests only.

Never refresh historical baselines; reject unknown/new bytes by leaving them unchanged.
"""
from pathlib import Path
from functools import lru_cache
from hashlib import sha256
import base64, json
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def change():
    record=json.loads((ROOT/'_tests/turn09-weekly-reset-change.json').read_text())
    if record.get('base_commit')!='e6d61d4070bae76c54e1b676422e716ff8adaac6':
        raise ValueError('Unknown Turn 09 predecessor')
    return record['paths']

def before(path,data):
    item=change().get(str(path))
    if item is None:return data
    binary=isinstance(data,bytes)
    raw=data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest()!=item['new_sha256']:return data
    for edit in reversed(item['edits']):
        old=base64.b64decode(edit['old'],validate=True)
        new=base64.b64decode(edit['new'],validate=True)
        s,e=edit['start'],edit['end']
        if not 0<=s<=e<=len(raw) or raw[s:e]!=new:
            raise ValueError('Turn 09 edit span mismatch: '+str(path))
        raw=raw[:s]+old+raw[e:]
    if sha256(raw).hexdigest()!=item['old_sha256']:
        raise ValueError('Turn 09 original digest mismatch: '+str(path))
    return raw if binary else raw.decode('utf-8')

def pages(records):
    """Restore exactly the approved revised metadata in historical page snapshots."""
    from copy import deepcopy
    result=[]
    for page in records:
        p=deepcopy(page)
        if (p.get('id')=='living-well-weekly-reset'
            and p.get('updated')=='2026-10-17'
            and p.get('revision')=='Put a three-move paper-first reset and fictional filled example before the full guide; preview and download use the existing single worksheet source.'):
            p['updated']='2026-10-09'
            p['revision']='Added a clearly fictional paper-first and optional AI worked example, including the checks needed before using a draft.'
        result.append(p)
    return result


def original_entry(entry):
    """A specific approved guide, restored for the frozen 26-entry digest."""
    from copy import deepcopy
    if entry.get('slug')!='weekly-reset':return deepcopy(entry)
    raw=json.dumps(entry,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    record=json.loads((ROOT/'_tests/turn09-weekly-reset-change.json').read_text())
    if sha256(raw).hexdigest()!=record['new_entry_sha256']:
        return deepcopy(entry)
    prior=deepcopy(entry)
    prior.pop('quick_start')
    prior['updated']='2026-10-09'
    prior['revision']='Added a clearly fictional paper-first and optional AI worked example, including the checks needed before using a draft.'
    restored=json.dumps(prior,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    if sha256(restored).hexdigest()!=record['old_entry_sha256']:
        raise ValueError('Turn 09 source-entry predecessor mismatch')
    return prior
