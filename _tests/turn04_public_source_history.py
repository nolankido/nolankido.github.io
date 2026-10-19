"""Reconstruct only the exact pre-Turn-04 public-source example inputs.

This SHA-bound adapter runs in tests, not in the public site. Any unrelated
change remains visible. No older release records or fingerprints are changed.
"""
import time_decision_history
import turn10_profile_history
from pathlib import Path
from functools import lru_cache
import base64,hashlib,json

ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT/'_tests/turn04-public-source-change.json').read_text())

def before(path,data):
    data = turn10_profile_history.before(path, data)
    data = time_decision_history.before(path, data)
    entry=change()['paths'].get(str(path))
    if not entry: return data
    binary=isinstance(data,bytes)
    raw=data if binary else data.encode('utf-8')
    if hashlib.sha256(raw).hexdigest()!=entry['new_sha256']:
        return data
    insertion=base64.b64decode(entry['insertion_base64'],validate=True)
    pos=entry['offset']
    if raw[pos:pos+len(insertion)]!=insertion:
        raise ValueError('Turn 04 insertion at wrong offset')
    old=raw[:pos]+raw[pos+len(insertion):]
    if hashlib.sha256(old).hexdigest()!=entry['old_sha256']:
        raise ValueError('Turn 04 predecessor fingerprint mismatch')
    return old if binary else old.decode('utf-8')
