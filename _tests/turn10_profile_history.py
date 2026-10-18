"""Exact whole-file predecessor view for Turn 10; never rewrite golden baselines."""
import base64,hashlib,json,zlib
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def records():
    return json.loads((ROOT/'_tests/turn10-profile-change.json').read_text())
def before(path,data):
    rec=records().get(str(path))
    if not rec:return data
    binary=isinstance(data,bytes)
    current=data if binary else data.encode('utf-8')
    if hashlib.sha256(current).hexdigest()!=rec['new_sha256']:return data
    original=zlib.decompress(base64.b64decode(rec['old_zlib_b64']))
    if hashlib.sha256(original).hexdigest()!=rec['old_sha256']:
        raise ValueError('Corrupt Turn 10 historical record: '+str(path))
    return original if binary else original.decode('utf-8')
